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

    # Calculate final price based on friend status
    final_price = registration.final_price
    if registration.bring_a_friend:  # Changed from bringing_friend to bring_a_friend
        final_price = final_price * 2

    # Prepare name display for checkout page
    display_name = registration.first_name + " " + registration.last_name
    if registration.bring_a_friend:  # Changed from bringing_friend to bring_a_friend
        # If friend fields exist, use them; otherwise use generic friend label
        if hasattr(registration, 'friend_first_name') and hasattr(registration, 'friend_last_name'):
            friend_name = registration.friend_first_name + " " + registration.friend_last_name
            display_name = f"{display_name} + {friend_name}"
        else:
            display_name = f"{display_name} + friend"

    context = {
        'registration': registration,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
        'amount': int(final_price * 100),  # Convert to cents for Stripe
        'event': registration.event,
        'display_name': display_name,  # Add this to your template context
    }
    return render(request, 'payment.html', context)

def create_payment_intent(request, registration_id):
    """Create Stripe PaymentIntent for a registration"""
    registration = get_object_or_404(Registration, id=registration_id)

    # Calculate final price based on friend status
    final_price = registration.final_price
    if registration.bring_a_friend:  # Changed from bringing_friend to bring_a_friend
        final_price = final_price * 2

    # Prepare customer name for payment description
    customer_name = f"{registration.first_name} {registration.last_name}"
    if registration.bring_a_friend:  # Changed from bringing_friend to bring_a_friend
        if hasattr(registration, 'friend_first_name') and hasattr(registration, 'friend_last_name'):
            friend_name = f"{registration.friend_first_name} {registration.friend_last_name}"
            customer_display = f"{customer_name} + {friend_name}"
        else:
            customer_display = f"{customer_name} + friend"
    else:
        customer_display = customer_name

    # Option 1: Enhanced metadata
    intent = stripe.PaymentIntent.create(
        amount=int(final_price * 100),  # Convert to cents
        currency='chf',
        # Add customer information that will appear in the Stripe dashboard
        description=f"Payment for {registration.event.title} - {customer_display}",
        metadata={
            'registration_id': registration.id,
            'event_id': registration.event.id,
            'customer_email': registration.email,
            'customer_name': customer_display,
            'event_title': registration.event.title,
            'bringing_friend': str(registration.bring_a_friend)  # Changed from bringing_friend to bring_a_friend
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

    # Get Stripe payment parameters
    payment_intent_id = request.GET.get('payment_intent')
    payment_intent_client_secret = request.GET.get('payment_intent_client_secret')
    redirect_status = request.GET.get('redirect_status')

    # If this is a redirect from Stripe with a successful payment
    if redirect_status == 'succeeded' and payment_intent_id:
        # Verify this payment belongs to this registration
        if registration.stripe_payment_intent_id != payment_intent_id:
            # This is suspicious, log it or handle accordingly
            # For now, we'll just show the success page anyway
            pass
        
        # Update payment status if not already done via webhook
        if registration.payment_status != 'paid':
            registration.payment_status = 'paid'
            registration.payment_date = timezone.now()
            registration.save()
            
            # Add email to Sender.net lists
            add_email_to_sender_list(
                email=registration.email,
                first_name=registration.first_name,
                last_name=registration.last_name,
                event=registration.event
            )

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
    import logging
    from django.db import connections
    
    logger = logging.getLogger(__name__)
    logger.info("Webhook received")
    
    # Close any stale database connections
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"Webhook event type: {event['type']}")
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        registration_id = payment_intent.metadata.get('registration_id')
        
        logger.info(f"Payment succeeded for registration: {registration_id}")
        
        if registration_id:
            try:
                # Get a fresh DB connection
                from django.db import connection
                connection.ensure_connection()
                
                registration = Registration.objects.get(id=registration_id)  # pylint: disable=no-member
                registration.payment_status = 'paid'
                registration.payment_date = timezone.now()
                registration.save()
                
                # Add email to Sender.net lists
                sender_result = add_email_to_sender_list(
                    email=registration.email,
                    first_name=registration.first_name,
                    last_name=registration.last_name,
                    event=registration.event
                )
                logger.info(f"Email added to Sender list result: {sender_result}")
                
            except Registration.DoesNotExist:  # pylint: disable=no-member
                logger.error(f"Registration {registration_id} not found")
                return HttpResponse(status=404)
            except Exception as e:
                logger.error(f"Error processing webhook: {str(e)}")
                return HttpResponse(status=500)
    
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