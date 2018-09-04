from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic.base import TemplateView, RedirectView
from django.http import HttpResponse, HttpResponseRedirect
from .models import Post, Comments, defualt_user, User
from .form import PostForm, CommentForm
from django.contrib.auth import authenticate, login, logout

from warnings import warn

# TODO: implement user session, sign in/up logout and stuff

"""""
View Method Flow Chart:
    dispatch(): accepts a request argument plus arguments, and returns a HTTP response.
    http_method_not_allowed(): If the view was called with a HTTP method it doesn’t support, 
                                this method is called instead.
    (TemplateView) get_context_data(): Returns a dictionary representing the template context.
    (RedirectView) get_redirect_url(): Constructs the target URL for redirection.

    https://docs.djangoproject.com/en/2.1/ref/class-based-views/base/
"""""

class IndexView(TemplateView):

    template_name = "forum/index.html"

    def get_context_data(self, **kwargs):
        # **kwargs is context variable from template
        context = super().get_context_data(**kwargs)
        context['latest_post_list'] = Post.objects.order_by('-date')
        return context


class PostFormView(View):
    # TODO: is this the best way to pass class variables?
    def __init__(self):
        self.form_class = PostForm
        self.template_name = 'forum/edit.html'
        self.action = '/forum/edit/'

    def get_post_data(self, post_id):
        if post_id:
            self.action = '/forum/' + str(post_id) + '/edit/'
            self.current_post = get_object_or_404(Post, pk=post_id)
            return {
            'title' : self.current_post.title,
            'content' : self.current_post.content,
        }
        else:
            return {'title':'', 'content':''}

    def get(self, request, post_id=0):
        initial = self.get_post_data(post_id)
        form = self.form_class(initial)
        return render(request, self.template_name, {'form': form, 'post_id': post_id})

    def post(self, request, post_id=0):
        initial = self.get_post_data(post_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if post_id:
                warn("updating form!")
                self.current_post.title=data['title']
                self.current_post.content = data['content']
                self.current_post.save()
            else:
                Post.objects.create(title=data['title'], content=data['content'], author=defualt_user)
            return HttpResponseRedirect('/forum/')


# function view because fuck it
def delete(request, post_id):
    Post.objects.get(pk=post_id).delete()
    return HttpResponseRedirect('/forum/')


class ContentView(TemplateView):
    # equivalent to: return render(request, template_name, context)
    template_name = 'forum/content.html'

    def get_context_data(self, post_id=0, **kwargs):
        context = super().get_context_data(**kwargs)
        this_post = get_object_or_404(Post, pk=post_id)
        context['list_of_comments'] = Comments.objects.filter(post = this_post)
        context['form'] = CommentForm()
        context['post'] = this_post
        return context

class CommentView(View):
    def post(self, request, post_id, comment_id=0):
        comment_post = get_object_or_404(Post, pk=post_id)
        replay_to = None
        if comment_id:
            replay_to = get_object_or_404(Comments, pk=comment_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # TODO: insert currently logged in user as 'name'
            Comments.objects.create(content=data['content'],
                                    parent_comment=replay_to,
                                    post=comment_post,
                                    name=defualt_user)
        return HttpResponseRedirect('/forum/' + str(post_id) + '/')



def user(request):
    pass

def user_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect('/forum/')
    else:
        return HttpResponse('invalid login')

def user_logout(request):
    logout(request)
    return HttpResponse("You're logged out.")

def user_sign_up(request):
    pass

