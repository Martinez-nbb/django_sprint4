
from . import views
from django.urls import path


app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutTemplateView.as_view(), name='about'),
    path('rules/', views.RulesTemplateView.as_view(), name='rules'),
]
