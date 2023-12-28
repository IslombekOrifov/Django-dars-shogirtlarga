from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from blog.models import Post


def post_list(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post_slug):
    post = get_object_or_404(Post, 
                             slug=post_slug, 
                             publish__year=year, 
                             publish__month=month, 
                             publish__day=day, 
                             status=Post.Status.PUBLISHED)
    return render(request, 'blog/post/detail.html', {'post': post})

