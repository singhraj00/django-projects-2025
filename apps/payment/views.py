from django.shortcuts import render,get_object_or_404,redirect
from apps.tours.models import Tour
from apps.payment.utils import client,send_booking_email,generate_invoice
from .models import Booking,Passenger
from django.forms import modelformset_factory
from django.conf import settings
import json 
from django.http import JsonResponse
from .form import BookingForm,PassengerForm
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa


@login_required
def book_now(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.tour = tour
            booking.save()  # Save to get PK
            booking.update_total_amount()  # total_amount calculated & saved
            return redirect("payment:passenger_details", booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, "payment/book_now.html", {"tour": tour, "form": form})


@login_required
def passenger_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    PassengerFormSet = modelformset_factory(
        Passenger, 
        form=PassengerForm, 
        extra=booking.number_of_people,  # allows adding new if fewer exist
        can_delete=True
    )

    # Use queryset to fetch existing passengers for this booking
    queryset = Passenger.objects.filter(booking=booking)

    if request.method == "POST":
        formset = PassengerFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            instances = formset.save(commit=False)
            # Save each instance and link to booking
            for passenger in instances:
                passenger.booking = booking
                passenger.save()
            # Delete any removed passengers
            for passenger in formset.deleted_objects:
                passenger.delete()
            return redirect("payment:create_payment", booking_id=booking.id)
        else:
            print(formset.errors)
    else:
        formset = PassengerFormSet(queryset=queryset)

    return render(request, "payment/passenger_details.html", {
        "booking": booking,
        "formset": formset
    })


# Create your views here.
@login_required
def create_payment(request, booking_id):
    # Use the existing booking instead of creating a new one
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    total_amount = float(booking.total_amount * 100)  # Amount in paise

    # Create Razorpay order
    razorpay_order = client.order.create({
        'amount': total_amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    booking.payment_order_id = razorpay_order['id']
    booking.save(update_fields=['payment_order_id'])

    context = {
        'tour': booking.tour,
        'booking': booking,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'total_amount': total_amount,
    }

    return render(request, 'payment/checkout.html', context)

@login_required
def payment_success(request):
    data = json.loads(request.body)
    order_id = data.get('razorpay_order_id')
    payment_id = data.get("razorpay_payment_id")
    order_id = data.get("razorpay_order_id")
    signature = data.get("razorpay_signature")

    try:
        booking = Booking.objects.get(payment_order_id=order_id)
        booking.payment_id = payment_id
        booking.payment_signature = signature
        booking.status = "CONFIRMED"
        booking.save()

        # Send email to user
        send_booking_email(booking.user, booking)
        return JsonResponse({"status": "success"})
    
    except Booking.DoesNotExist:
        return JsonResponse({"status": "failed"})

@login_required    
def payment_failed(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    data = json.loads(request.body)
    # Optional: capture failure reason from Razorpay response
    reason = data.get('error', {}).get('description', 'Payment failed')

    # Update booking status
    booking.status = "FAILED"  # ⚠️ add this choice in model
    booking.save()

    # Send failure email
    send_booking_email(booking.user, booking)

    return JsonResponse({"status": "failed", "reason": reason})

@login_required
def failed_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "payment/failed.html", {"booking": booking})

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'payment/success.html', {'booking': booking})

@login_required
def my_bookings(request):
    # logged-in user ki saari bookings
    bookings = request.user.bookings.all().order_by('-created_at')
    return render(request, "payment/my_bookings.html", {"bookings": bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    passenger_details = booking.passengers.all()
    return render(request, "payment/booking_detail.html", {"booking": booking,'passengers':passenger_details})

@login_required
def download_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Invoice HTML template load
    template_path = "payment/invoice.html"  # tumhari template location

    context = {
        "booking": booking,
        "passengers": booking.passengers.all(),
    }

    # HTML render
    template = get_template(template_path)
    html = template.render(context)

    # PDF banane ke liye memory buffer
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking.id}.pdf"'

    pisa_status = pisa.CreatePDF(
        html, dest=response
    )

    if pisa_status.err:
        return HttpResponse("PDF could not be generated, please try again later.")
    return response