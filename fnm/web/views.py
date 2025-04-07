from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.utils import timezone
from .models import Event, GeneralEventInfo

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
        context['program_days'] = self.object.program_days.all()
        return context

def registration(request):
    return render(request, 'registration.html')
