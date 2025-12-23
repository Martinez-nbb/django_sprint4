from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import PostEditForm, CommentEditForm, UserEditForm
from .models import Post, Category, Comment  # Уберите User отсюда
from .utils import (
    get_published_posts, get_posts_for_user, 
    paginate_queryset, can_view_post, can_comment_post,
    get_post_with_comments
)


def index(request):
    """Главная страница с пагинацией."""
    template = 'blog/index.html'
    post_list = get_published_posts()
    page_obj = paginate_queryset(request, post_list, 10)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница поста с комментариями."""
    template = 'blog/detail.html'
    
    try:
        post = get_post_with_comments(post_id, request.user)
    except PermissionDenied:
        raise PermissionDenied
    
    comments = post.comments.all().select_related('author')
    can_comment = can_comment_post(post, request.user)
    
    context = {
        'post': post,
        'comments': comments,
        'form': CommentEditForm() if can_comment else None,
        'can_comment': can_comment,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    """Посты категории с пагинацией."""
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_published_posts().filter(category=category)
    page_obj = paginate_queryset(request, post_list, 10)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    """Страница профиля пользователя."""
    template = 'blog/profile.html'
    
    # Импортируем User здесь
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Получаем пользователя, чей профиль смотрим
    profile_user = get_object_or_404(User, username=username)
    
    # Получаем посты для страницы пользователя
    post_list = get_posts_for_user(request.user, username)
    page_obj = paginate_queryset(request, post_list, 10)
    
    # Проверяем, является ли текущий пользователь владельцем профиля
    # Используем id для надежности
    is_owner = False
    if request.user.is_authenticated:
        is_owner = (request.user.id == profile_user.id)
    
    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
        'is_owner': is_owner,
    }
    
    return render(request, template, context)


@login_required
def edit_profile(request):
    """Редактирование профиля."""
    template = 'blog/user.html'
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)
    
    context = {'form': form}
    return render(request, template, context)


@login_required
def create_post(request):
    """Создание нового поста."""
    template = 'blog/create.html'
    if request.method == 'POST':
        form = PostEditForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostEditForm()
    
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    """Редактирование поста."""
    template = 'blog/create.html'
    post = get_object_or_404(Post, pk=post_id)
    
    # Проверяем, что пользователь - автор
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    
    if request.method == 'POST':
        form = PostEditForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostEditForm(instance=post)
    
    context = {'form': form}
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    """Удаление поста."""
    template = 'blog/create.html'
    post = get_object_or_404(Post, pk=post_id)
    
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    
    context = {'post': post}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария."""
    post = get_object_or_404(Post, pk=post_id)
    
    if not can_comment_post(post, request.user):
        return redirect('blog:post_detail', post_id=post.id)
    
    if request.method == 'POST':
        form = CommentEditForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            # Отправляем email автору поста
            if post.author != request.user and post.author.email:
                subject = f'Новый комментарий к посту "{post.title}"'
                message = (
                    f'Пользователь {request.user.username} оставил комментарий '
                    f'к вашему посту "{post.title}".\n\n'
                    f'Текст комментария: {comment.text}\n\n'
                    f'Ссылка на пост: '
                    f'{request.build_absolute_uri(reverse("blog:post_detail", args=[post.id]))}'
                )
                send_mail(
                    subject,
                    message,
                    'noreply@blogicum.ru',
                    [post.author.email],
                    fail_silently=True,
                )
    
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    
    # Для редактирования комментария нужен отдельный шаблон с формой
    template = 'blog/comment.html'
    
    if request.method == 'POST':
        form = CommentEditForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentEditForm(instance=comment)
    
    context = {
        'form': form,
        'comment': comment,
        'post': post,
    }
    return render(request, template, context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    
    # Для удаления комментария нужен отдельный шаблон
    template = 'blog/comment.html'
    
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    
    context = {
        'comment': comment,
        'post': post,
    }
    return render(request, template, context)