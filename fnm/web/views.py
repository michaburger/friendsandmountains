from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import DetailView, ListView
from django.utils import timezone
from .models import Event, GeneralEventInfo, Registration
from .forms import RegistrationForm

# Keep your existing simple views
def welcome(request):
    return render(request, 'welcome.html')

def about(request):
    return render(request, 'about.html')

def links(request):
    return render(request, 'links.html')

# Replace these with class-based views
class PastEventsView(ListView):
    model = Event
    template_name = 'past.html'
    context_object_name = 'events'
    
    def get_queryset(self):
        # Get events with start_date in the past
        return Event.objects.filter(start_date__lt=timezone.now()).order_by('-start_date')  #pylint: disable=no-member
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['general_info'] = GeneralEventInfo.load()
        return context

class FutureEventsView(ListView):
    model = Event
    template_name = 'future.html'
    context_object_name = 'events'
    
    def get_queryset(self):
        # Get events with start_date in the future
        return Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')  #pylint: disable=no-member
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['general_info'] = GeneralEventInfo.load()
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['general_info'] = GeneralEventInfo.load()
        # Load related data
        context['gallery_images'] = self.object.images.all()
        context['accommodation_images'] = self.object.accommodation_images.all()
        context['surroundings_images'] = self.object.surroundings_images.all()
        context['program_days'] = self.object.program_days.all()
        
        # Add today's date for comparison
        context['today'] = timezone.now().date()
        
        # Check if event is in the future or ongoing
        is_active_event = self.object.end_date.date() >= timezone.now().date()
        context['is_active_event'] = is_active_event
        
        # Add participants data for future events
        if is_active_event:
            # Get paid registrations for this event
            paid_registrations = self.object.registrations.filter(payment_status='paid')
            
            participants = []
            participant_count = 0
            
            # Process each registration
            for registration in paid_registrations:
                participant_info = {
                    'name': registration.first_name,
                    'country': registration.country,
                    'friend_name': registration.friend_name if registration.bring_a_friend else None
                }
                
                # Count participants (person + friend if applicable)
                if registration.bring_a_friend and registration.friend_name:
                    participant_count += 2
                else:
                    participant_count += 1
                    
                participants.append(participant_info)
            
            context['event_participants'] = participants
            context['participant_count'] = participant_count
            context['max_participants'] = self.object.max_participants
            
        return context

def registration(request):
    return render(request, 'registration.html')

def event_registration(request, slug):
    """Handle event registration form submission"""
    event = get_object_or_404(Event, slug=slug)
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            # Add any other necessary fields
            registration.save()
            
            # Redirect to payment page
            return redirect('payment_page', registration_id=registration.id)
    else:
        form = RegistrationForm()
    
    return render(request, 'event_registration.html', {
        'event': event,
        'form': form
    })
