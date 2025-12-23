# conftest.py
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from blog.models import Post, Category, Location, Comment

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def category():
    return Category.objects.create(
        title='Тестовая категория',
        description='Описание тестовой категории',
        slug='test-category'
    )


@pytest.fixture
def location():
    return Location.objects.create(name='Тестовое местоположение')


@pytest.fixture
def post(user, category, location):
    return Post.objects.create(
        title='Тестовый пост',
        text='Текст тестового поста',
        author=user,
        category=category,
        location=location,
        is_published=True,
        pub_date=timezone.now()  # Добавляем pub_date
    )