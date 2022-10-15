from cgitb import text
from re import template
from django.shortcuts import get_object_or_404, render

from .models import Group, Post, User
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    page_obj = author.posts.all()
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)

    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request, post_id):
    template = 'posts/create_post.html'
    group = get_object_or_404(Group, slug=slug)
    context = {
        'text': text,
        'group': group,
    }
    return render(request, template, context)
