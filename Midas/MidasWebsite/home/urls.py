from django.urls import path
from . import views

# this is responsible for mapping views to urls
urlpatterns = [
    path('', views.home, name='Home'),
    path('about/', views.about, name='About'),
    path('train/', views.train, name='Train'),
    path('run/', views.run, name='Run'),
]
