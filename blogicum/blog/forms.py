from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        field = '__all__'
        exclude = ('author', 'pub_date', 'post')

class PostForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        exclude = ('author',)
        model = Post
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            )
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
