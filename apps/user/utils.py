from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_welcome_email(user):
    """Send a welcome email to new registered users."""
    subject = "🎉 Welcome to Safarnama – Your Adventure Starts Here!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string('emails/welcome_email.html', {'user': user})
    msg = EmailMultiAlternatives(subject, '', from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_password_reset_confirmation(user):
    """Send email confirmation after password reset."""
    subject = "🔐 Your Safarnama Password Was Changed Successfully"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string('emails/password_reset_confirmation_email.html', {'user': user})
    msg = EmailMultiAlternatives(subject, '', from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
