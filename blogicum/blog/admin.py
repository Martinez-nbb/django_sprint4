
from .models import Post, Category, Location, Comment
from django.contrib import admin

# Register your models here.

admin.site.register(Location)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
