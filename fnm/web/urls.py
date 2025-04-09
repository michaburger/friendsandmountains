from django.urls import path
from . import views
from . import payments

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('about/', views.about, name='about'),
    path('links/', views.links, name='links'),
    path('past/', views.PastEventsView.as_view(), name='past'),
    path('future/', views.FutureEventsView.as_view(), name='future'),
    path('registration/', views.registration, name='registration'),
    path('events/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<slug:slug>/register/', views.event_registration, name='event_registration'),
    path('payment/<int:registration_id>/', payments.payment_page, name='payment_page'),
    path('payment/<int:registration_id>/create-payment-intent/', payments.create_payment_intent, name='create_payment_intent'),
    path('payment/<int:registration_id>/success/', payments.payment_success, name='payment_success'),
    path('payment/<int:registration_id>/cancel/', payments.payment_cancel, name='payment_cancel'),
    path('payment/webhook/', payments.stripe_webhook, name='stripe_webhook'),
]
