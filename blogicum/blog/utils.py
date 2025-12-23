from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Post, Category, Location


def get_published_posts():
    """Получить опубликованные посты с аннотацией количества комментариев."""
    queryset = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')  # Сортировка после annotate
    return queryset


def get_posts_for_user(request_user, username):
    """Получить посты для страницы пользователя."""
    User = get_user_model()
    author = get_object_or_404(User, username=username)
    
    # Набор постов зависит от того кто смотрит
    if request_user.is_authenticated and request_user == author:
        # Автор видит все свои посты (включая неопубликованные и отложенные)
        queryset = author.posts.all()
    else:
        # Другие пользователи видят только опубликованные посты
        queryset = author.posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    
    # Аннотируем и сортируем
    return queryset.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def paginate_queryset(request, queryset, per_page=10):
    """Пагинация для queryset."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def can_view_post(post, user):
    """Проверяет, может ли пользователь видеть пост."""
    # Пост виден если:
    # 1. Он опубликован И дата публикации наступила И категория опубликована
    # 2. ИЛИ пользователь - автор поста
    if post.is_published and post.pub_date <= timezone.now() and post.category.is_published:
        return True
    if user.is_authenticated and user == post.author:
        return True
    return False


def can_comment_post(post, user):
    """Проверяет, может ли пользователь комментировать пост."""
    # Комментировать могут авторизованные пользователи,
    # если пост виден (может быть отложенный, но автор может комментировать)
    return user.is_authenticated and can_view_post(post, user)


def get_post_with_comments(post_id, user):
    """Получить пост с комментариями с проверкой прав доступа."""
    post = get_object_or_404(Post, pk=post_id)
    
    if not can_view_post(post, user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    
    return post