import razorpay 
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML, CSS
import os
import pdfkit
from decimal import Decimal

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def generate_invoice(booking):
    base_amount = booking.calculate_base_amount()
    gst_amount = booking.calculate_gst()
    total_amount = booking.calculate_total() 

    # Passenger details fetch karna
    passengers = booking.passengers.all()  # adjust according to your model

    html = render_to_string("payment/invoice.html", {
        "booking": booking,
        "passengers": passengers,
        "base_amount": base_amount,
        "gst_amount": gst_amount,
        "total_amount": total_amount,
    })

    pdf = pdfkit.from_string(html, False, options={
        "page-size": "A4",
        "encoding": "UTF-8",
        "enable-local-file-access": None,
    })

    return pdf


def send_booking_email(user, booking):
    subject = f"Booking {'Confirmed' if booking.status=='CONFIRMED' else 'Failed'} - {booking.tour.title}"
    
    # Email HTML template
    message = render_to_string('payment/email/booking_email.html', {
        'user': user,
        'booking': booking,
        'site_url': 'https://www.safarnama.com',
        'now': timezone.now()
    })

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = 'html'

    # ⭐ Attach invoice only if booking success
    if booking.status == "CONFIRMED":
        pdf_bytes = generate_invoice(booking)
        if pdf_bytes:
            email.attach("invoice.pdf", pdf_bytes, "application/pdf")

    email.send(fail_silently=False)
