from django.shortcuts import render
from .models import Tour,Review
from django.shortcuts import get_object_or_404

# Create your views here.
def home(request):
    return render(request, 'tours/home.html') 



def tours_list_view(request):
    tours = Tour.objects.all().order_by('-created_at')

    # Filters
    query = request.GET.get('q')
    location = request.GET.get('location')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    if query:
        tours = tours.filter(title__icontains=query)
    if location:
        tours = tours.filter(location__icontains=location)
    if price_min:
        tours = tours.filter(price__gte=price_min)
    if price_max:
        tours = tours.filter(price__lte=price_max)

    # For dropdowns (unique locations)
    locations = Tour.objects.values_list('location', flat=True).distinct()

    context = {
        'tours': tours,
        'locations': locations,
    }
    return render(request, 'tours/tours_list.html', context)

def tour_detail_view(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    reviews = tour.reviews.all().order_by('-created_at')
    return render(request, 'tours/tour_detail.html', {'tour': tour, 'reviews': reviews})

def about(request):
    return render(request, 'tours/about.html')

def contact(request):
    return render(request, 'tours/contact.html')
