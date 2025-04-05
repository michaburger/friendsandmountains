from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('about/', views.about, name='about'),
    path('links/', views.links, name='links'),
    path('past/', views.past, name='past'),
    path('future/', views.future, name='future'),
    path('registration/', views.registration, name='registration'),
    ]
