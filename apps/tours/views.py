from django.shortcuts import render
from .models import Tour

# Create your views here.
def home(request):
    return render(request, 'tours/home.html') 



def tours_list_view(request):
    tours = Tour.objects.all().order_by('-created_at')
    return render(request, 'tours/tours_list.html', {'tours': tours})

def about(request):
    return render(request, 'tours/about.html')

def contact(request):
    return render(request, 'tours/contact.html')
