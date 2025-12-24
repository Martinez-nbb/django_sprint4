from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm
from django.urls import reverse
from blog.forms import UserUpdateForm
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.models import Post, Category, Comment
from django.db import models
from .utils import annotate_pub_coms, order_date




User = get_user_model()


class ProfileListView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = 10
    model = Post

    def get_queryset(self):
        qs = super().get_queryset()
        self.profile = get_object_or_404(
            User, username=self.kwargs['username']
        )

        if (
            self.request.user.is_authenticated
            and self.request.user == self.profile
        ):
            queryset = qs.filter(author=self.profile)
        else:
            queryset = qs.filter(
                author=self.profile,
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True,
            )

        queryset = queryset.select_related('author', 'category')
        queryset = annotate_pub_coms(queryset)
        return order_date(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        if not post_id:
            return redirect('blog:index')

        post = get_object_or_404(Post, pk=post_id)
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=post_id)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post_id = self.kwargs['post_id']
        return get_object_or_404(Post, pk=post_id, author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        queryset = qs.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ).select_related('author', 'category')
        queryset = annotate_pub_coms(queryset)
        return order_date(queryset)


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        self.category = get_object_or_404(
            Category, slug=category_slug, is_published=True
        )
        qs = super().get_queryset()
        queryset = qs.filter(
            category=self.category,
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ).select_related('author', 'category')
        queryset = annotate_pub_coms(queryset)
        return order_date(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    fields = ['text']
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        post_id = self.kwargs['post_id']
        comment_id = self.kwargs['comment_id']
        comment = get_object_or_404(
            Comment, pk=comment_id, post_id=post_id, author=self.request.user
        )
        return comment

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['text']
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment_id = self.kwargs['comment_id']
        post_id = self.kwargs['post_id']
        return get_object_or_404(
            Comment, pk=comment_id, post_id=post_id, author=self.request.user
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        base_qst = Post.objects.select_related('author', 'category')

        if self.request.user.is_staff:
            return base_qst

        if self.request.user.is_authenticated:
            return base_qst.filter(
                models.Q(
                    is_published=True,
                    pub_date__lte=timezone.now(),
                    category__is_published=True
                )
                | models.Q(author=self.request.user)
            )
        else:
            return base_qst.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )

    def get_context_data(self, **kwargs):
        post = self.object
        context = super().get_context_data(**kwargs)

        context['comments'] = (
            post.comments.filter(is_published=True).select_related('author')
            .order_by('created_at')
        )

        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
        else:
            context['form'] = None

        return context
