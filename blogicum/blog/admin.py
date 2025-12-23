from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Location, Post, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'text', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
    list_display = (
        'title', 'is_published', 'pub_date', 
        'author', 'location', 'category', 
        'comment_count', 'image_preview'
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'text')
    list_filter = ('category', 'location', 'author', 'is_published', 'pub_date')
    
    readonly_fields = ('image_preview',)
    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'image', 'image_preview')
        }),
        ('Дополнительная информация', {
            'fields': ('author', 'category', 'location', 'pub_date', 'is_published')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return 'Нет изображения'
    image_preview.short_description = 'Превью'

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Комментарии'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'slug', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title', 'description')
    list_filter = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'text_preview')
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('created_at', 'post')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'