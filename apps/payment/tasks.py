# bookings/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Booking
from django.conf import settings

@shared_task
def send_travel_reminders():
    tomorrow = timezone.now().date() + timedelta(days=1)
    bookings = Booking.objects.filter(travel_date=tomorrow)
    
    for booking in bookings:
        # Render the HTML template
        html_content = render_to_string("payment/email/travel_reminder.html", {
            "user": booking.user,
            "booking": booking,
            "tour_link": f"http://localhost:8000/tours/{booking.tour.id}/",  # Update with your domain in production
            "current_year": timezone.now().year,
        })

        # Send the email
        email = EmailMessage(
            subject="Reminder: Your travel is tomorrow!",
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.user.email],
        )
        email.content_subtype = "html"  # Important for HTML emails
        email.send()
