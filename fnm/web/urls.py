from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('about/', views.about, name='about'),
    path('links/', views.links, name='links'),
    path('past/', views.PastEventsView.as_view(), name='past'),
    path('future/', views.FutureEventsView.as_view(), name='future'),
    path('registration/', views.registration, name='registration'),
    path('events/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<slug:slug>/register/', views.event_registration, name='event_registration'),
]
