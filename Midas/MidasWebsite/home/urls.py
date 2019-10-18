from django.urls import path
from . import views

# this is responsible for mapping views to urls
urlpatterns = [
    path('', views.home, name='Home'),
    path('about/', views.about, name='About'),
]