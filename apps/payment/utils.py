import razorpay 
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from apps.user.utils import send_sendgrid_email
from django.utils import timezone
import pdfkit


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

    html_content = render_to_string(
        'payment/email/booking_email.html',
        {
            'user': user,
            'booking': booking,
            'site_url': 'https://django-projects-2025.onrender.com/',
            'now': timezone.now()
        }
    )

    attachment = None
    filename = None

    # Include invoice only if confirmed
    if booking.status == "CONFIRMED":
        pdf_bytes = generate_invoice(booking)
        if pdf_bytes:
            attachment = pdf_bytes
            filename = "invoice.pdf"

    send_sendgrid_email(
        subject=subject,
        to_email=user.email,
        html_content=html_content,
        attachment_bytes=attachment,
        attachment_name=filename
    )
