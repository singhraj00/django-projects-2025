import razorpay 
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa
from io import BytesIO

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def generate_invoice(booking):
    """Generate PDF invoice and return bytes"""
    html = render_to_string("payment/invoice.html", {"booking": booking})

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        return None

    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


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
