from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Tour,Review,ContactMessage
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Tour, Review 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage
import re

# Create your views here.
def home(request):
    return render(request, 'tours/home.html') 


@login_required 
@cache_page(60 * 15)  
def tours_list_view(request):
    print("Fetching tours list from database...")

    tours = (
        Tour.objects
        .only("id", "title", "location", "price")        # Only needed fields
        .prefetch_related("images")                      # Load all TourImages in single query
        .order_by("-created_at")
    )

    # === Filters ===
    query = request.GET.get("q")
    destination = request.GET.get("destination")
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")

    if query:
        tours = tours.filter(title__icontains=query)
    if destination:
        tours = tours.filter(location__icontains=destination)
    if price_min:
        tours = tours.filter(price__gte=price_min)
    if price_max:
        tours = tours.filter(price__lte=price_max)

    # === Unique destinations for dropdown ===
    destinations = (
        Tour.objects
        .values_list("location", flat=True)
        .distinct()
    )

    # === Pagination ===
    paginator = Paginator(tours, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "tours/tours_list.html",
        {
            "tours": page_obj,
            "destinations": destinations,
            "page_obj": page_obj,
        },
    )


@login_required
def tour_detail_view(request, tour_id):
    # clear messages 
    list(messages.get_messages(request))
    tour = get_object_or_404(Tour, pk=tour_id)
    images = tour.images.all()
    reviews = Review.objects.filter(tour=tour).order_by('-created_at')
   
    
    paginator = Paginator(reviews, 5)
    page_number = request.GET.get('page', 1)
    reviews = paginator.get_page(page_number)

    already_booked = False
    if request.user.is_authenticated:
        from apps.payment.models import Booking
        already_booked = Booking.objects.filter(user=request.user, tour=tour, status='CONFIRMED').exists()

    return render(request, 'tours/tour_detail.html', {'tour': tour, 'reviews': reviews,'images': images,'already_booked': already_booked})




@login_required
def add_review(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    if request.method == "POST":
        rating = int(request.POST.get("rating", 0))
        comment = request.POST.get("comment", "").strip()

        # ✅ Validate rating
        if rating <= 0 or rating > 5:
            messages.error(request, "Please select a valid rating between 1 and 5.")
            return redirect("tours:tour_detail", tour_id=tour.id)

        # ✅ Check if user has already reviewed this tour
        # existing_review = Review.objects.filter(user=request.user, tour=tour).first()
        # if existing_review:
        #     # Optional: allow update instead of blocking
        #     if existing_review.comment == comment and existing_review.rating == rating:
        #         messages.warning(request, "You've already submitted this review.")
        #         return redirect("tours:tour_detail", tour_id=tour.id)

        #     # Update existing review instead of creating a duplicate
        #     existing_review.rating = rating
        #     existing_review.comment = comment
        #     existing_review.save()
        #     messages.success(request, "Your review has been updated successfully!")
        #     return redirect("tours:tour_detail", tour_id=tour.id)

        # ✅ Prevent duplicate review content globally (optional)
        duplicate_text = Review.objects.filter(tour=tour, comment__iexact=comment).exclude(user=request.user).exists()
        if duplicate_text:
            messages.error(request, "A similar review already exists. Please write something unique.")
            return redirect("tours:tour_detail", tour_id=tour.id)

        # ✅ Create new review
        Review.objects.create(
            user=request.user,
            tour=tour,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Your review has been added successfully!")

    return redirect("tours:tour_detail", tour_id=tour.id)


@login_required
def about(request):
    return render(request, 'tours/about.html')



def contact(request):

    # Clear old leftover messages (important)
    list(messages.get_messages(request))

    """Handles user contact form submissions."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        # ✅ Basic validations
        if not name or not email or not message:
            messages.error(request, "⚠️ Please fill in all fields before submitting.")
            return redirect('tours:contact')

        # ✅ Email format validation
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_pattern, email):
            messages.error(request, "⚠️ Please enter a valid email address.")
            return redirect('tours:contact')

        # ✅ Prevent duplicate messages within 5 minutes (spam protection)
        from datetime import timedelta, datetime
        recent_message = ContactMessage.objects.filter(
            email=email,
            message=message
        ).order_by('-created_at').first()

        if recent_message and (datetime.now() - recent_message.created_at.replace(tzinfo=None)) < timedelta(minutes=5):
            messages.warning(request, "⚠️ You have already sent a similar message recently.")
            return redirect('tours:contact')

        # ✅ Save the message
        ContactMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
            message=message
        )

        messages.success(request, "✅ Thank you! We’ve received your message. Please check your email for confirmation.")
        return redirect('tours:contact')

    return render(request, 'tours/contact.html')

def load_more_reviews(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    reviews_list = Review.objects.filter(tour=tour).order_by('-created_at')

    page = request.GET.get('page', 1)
    paginator = Paginator(reviews_list, 5)  # 5 reviews per load
    reviews = paginator.get_page(page)

    # Render only the review cards
    html = render(request, 'tours/review_cards.html', {'reviews': reviews}).content.decode('utf-8')
    return JsonResponse({
        'html': html,
        'has_next': reviews.has_next()
    })