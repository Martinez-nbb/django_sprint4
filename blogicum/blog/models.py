from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class BaseCreatedAt(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=('Добавлено')
    )

    class Meta:
        abstract = True


class BasePublished(models.Model):
    is_published = models.BooleanField(
        help_text='Снимите галочку, чтобы скрыть.',
        default=True,
        verbose_name=('Опубликовано'),
    )

    class Meta:
        abstract = True


class Category(BasePublished, BaseCreatedAt):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешаются \
символы латиницы, цифры, дефис и подчёркивание.',
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BasePublished, BaseCreatedAt):
    name = models.CharField(max_length=256, verbose_name=('Название места'))

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BasePublished, BaseCreatedAt):
    title = models.CharField(max_length=256, verbose_name=('Заголовок'))
    text = models.TextField(verbose_name=('Текст'))
    author = models.ForeignKey(
        User, verbose_name=('Автор публикации'), on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location,
        verbose_name=('Местоположение'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    pub_date = models.DateTimeField(
        verbose_name=('Дата и время публикации'),
        help_text='Если установить дату и время в будущем — можно дел\
            ать отложенные публикации.',
    )
    image = models.ImageField('Фото', upload_to='post_images', blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name=('Категория'),
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(BasePublished, BaseCreatedAt):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация',
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        text_preview = (
            self.text[:50] + '...' if len(self.text) > 50 else self.text
        )

        return f'{self.author.username}: {text_preview}'
