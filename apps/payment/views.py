from django.shortcuts import render,get_object_or_404
from apps.tours.models import Tour
from .utils import client,send_booking_email,generate_invoice
from .models import Booking
from django.conf import settings
import json 
from django.http import JsonResponse

# Create your views here.
def create_payment(request,tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    user = request.user

    total_amount = float(tour.price * 100) #Amount in paise

    # craete booking first
    booking = Booking.objects.create(
        user=user,
        tour=tour,
        total_amount=float(total_amount / 100),  # Store in rupees
        status='PENDING'
    )

    # Create Razorpay order
    razorpay_order = client.order.create({
        'amount': total_amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    booking.payment_order_id = razorpay_order['id']
    booking.save()

    context = {
        'tour': tour,
        'booking': booking,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'total_amount': total_amount,
    }

    return render(request, 'payment/checkout.html', context)


def payment_success(request):
    data = json.loads(request.body)
    order_id = data.get('razorpay_order_id')

    try:
        booking = Booking.objects.get(payment_order_id=order_id)
        booking.status = "CONFIRMED"
        booking.save()

        # Send email to user
        send_booking_email(booking.user, booking)
        return JsonResponse({"status": "success"})
    
    except Booking.DoesNotExist:
        return JsonResponse({"status": "failed"})
    
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


def failed_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "payment/failed.html", {"booking": booking})

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'payment/success.html', {'booking': booking})