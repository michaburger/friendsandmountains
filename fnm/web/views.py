from django.shortcuts import render
from .models import TodoItem

# Create your views here.
def welcome(request):
    return render(request, 'welcome.html')

def about(request):
    return render(request, 'about.html')

def links(request):
    return render(request, 'links.html')

def past(request):
    return render(request, 'past.html')

def future(request):
    return render(request, 'future.html')

def registration(request):
    return render(request, 'registration.html')

def todos(request):
    items = TodoItem.objects.all()  #pylint: disable=no-member
    return render(request, 'todos.html', {"todos": items})
