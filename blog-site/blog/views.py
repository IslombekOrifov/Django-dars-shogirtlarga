from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity


from taggit.models import Tag

from blog.models import Post, Comment as CommentNew
from .forms import EmailPostForm, CommentForm, SearchForm


def post_list(request, tag_slug=None):
    post_list = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post_slug):
    post = get_object_or_404(Post, 
                             slug=post_slug, 
                             publish__year=year, 
                             publish__month=month, 
                             publish__day=day, 
                             status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True, parent__isnull=True)
    # Форма для комментирования пользователями
    form = CommentForm()
    
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    
    return render(request, 'blog/post/detail.html', {'post': post, 
                                                     'comments':comments,
                                                     'form': form,
                                                     'similar_posts': similar_posts})



def post_share(request, post_id):
# Извлечь пост по его идентификатору id
    post = get_object_or_404(Post, 
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            
            post_url = request.build_absolute_uri(post.get_absolute_url())
            
            subject = f"{cd['name']} recommends you read " \
                f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                f"{cd['name']}\'s comments: {cd['comments']}"
                
            send_mail(subject, message, 'your_account@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 
                                                    'form': form, 
                                                    'sent': sent})
    
    
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
    # Создать объект класса Comment, не сохраняя его в базе данных
        comment = form.save(commit=False)
        # Назначить пост комментарию
        comment.post = post
        # Сохранить комментарий в базе данных
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 
                                                      'form': form,
                                                      'comment': comment})
    

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_vector = SearchVector('title', weight='D') + SearchVector('body', weight='A')
            # search_query = SearchQuery(query)
            # results = Post.published.annotate(
            #     search=search_vector,
            #     rank=SearchRank(search_vector, search_query)
            # ).filter(rank__gte=0.3).order_by('-rank')
            
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
            
    return render(request, 'blog/post/search.html', {'form': form,
                                                     'query': query,
                                                     'results': results})
    
# def comment_answer(request, pk):
#     parent = get_object_or_404(Comment, id=pk)
#     form = SearchForm(request.GET)
#     if request.method == 'POST':
#         comment = form.save(commit=False)
#         comment.parent = parent
#         comment.save()
        
#         return redirect(post.get_absolute_url)
#     return render(request, 'blog/posts/detail.html' {.....})