import stripe
import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Registration

stripe.api_key = settings.STRIPE_SECRET_KEY

def payment_page(request, registration_id):
    """Display payment page for a registration"""
    registration = get_object_or_404(Registration, id=registration_id)
    
    # Check if already paid
    if registration.payment_status == 'paid':
        return redirect('payment_success', registration_id=registration.id)
    
    context = {
        'registration': registration,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
        'amount': int(registration.final_price * 100),  # Convert to cents for Stripe
        'event': registration.event,
    }
    return render(request, 'payment.html', context)

def create_payment_intent(request, registration_id):
    """Create Stripe PaymentIntent for a registration"""
    registration = get_object_or_404(Registration, id=registration_id)
    
    # Option 1: Enhanced metadata
    intent = stripe.PaymentIntent.create(
        amount=int(registration.final_price * 100),  # Convert to cents
        currency='chf',
        # Add customer information that will appear in the Stripe dashboard
        description=f"Payment for {registration.event.title} - {registration.first_name} {registration.last_name}",
        metadata={
            'registration_id': registration.id,
            'event_id': registration.event.id,
            'customer_email': registration.email,
            'customer_name': f"{registration.first_name} {registration.last_name}",
            'event_title': registration.event.title
        }
    )
    
    # Store the payment intent ID
    registration.stripe_payment_intent_id = intent.id
    registration.save()
    
    return JsonResponse({
        'clientSecret': intent.client_secret
    })

def payment_success(request, registration_id):
    """Handle successful payment"""
    registration = get_object_or_404(Registration, id=registration_id)
    
    # This view would be shown after successful payment
    return render(request, 'payment_success.html', {'registration': registration})

def payment_cancel(request, registration_id):
    """Handle canceled payment"""
    registration = get_object_or_404(Registration, id=registration_id)
    
    return render(request, 'payment_cancel.html', {'registration': registration})

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        registration_id = payment_intent.metadata.get('registration_id')
        
        if registration_id:
            try:
                registration = Registration.objects.get(id=registration_id)  #pylint: disable=no-member
                registration.payment_status = 'paid'
                registration.payment_date = timezone.now()  # Add a payment date field if you don't have one
                registration.save()
                
                # Add email to Sender.net lists
                add_email_to_sender_list(
                    email=registration.email,
                    first_name=registration.first_name,
                    last_name=registration.last_name,
                    event=registration.event  # Pass the event
                )
                
            except Registration.DoesNotExist:  #pylint: disable=no-member
                # Log error or handle missing registration
                pass
    
    return HttpResponse(status=200)

def add_email_to_sender_list(email, first_name, last_name, event=None):
    """Add email to Sender.net mailing lists
    
    Adds the email to:
    1. The event-specific list if provided
    2. The general newsletter list
    """
    success = True
    
    # Helper function to add to a specific list
    def add_to_list(list_id):
        url = f"{settings.SENDER_BASE_URL}subscribers"
        
        data = {
            "list_id": list_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
        
        headers = {
            "Authorization": f"Bearer {settings.SENDER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            # Log the error
            return False
    
    # Add to event-specific list if available
    if event and event.sender_list_id:
        event_success = add_to_list(event.sender_list_id)
        success = success and event_success
    
    # Always add to the general newsletter list
    newsletter_success = add_to_list(settings.SENDER_LIST_ID)
    success = success and newsletter_success
    
    return success