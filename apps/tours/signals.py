from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import ContactMessage 
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete 
from .models import Tour

@receiver(post_save, sender=ContactMessage)
def send_contact_confirmation(sender, instance, created, **kwargs):
    if created:
        name = instance.name
        email = instance.email
        message_text = instance.message

        # Email subject
        subject = "🌍 We Received Your Message - Safarnama"

        # Render HTML email
        html_content = render_to_string(
            'emails/contact_email.html',
            {'name': name, 'message': message_text}
        )
        text_content = f"Hello {name},\nThank you for contacting Safarnama. We’ve received your message:\n{message_text}"

        # Create email
        email_message = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=False)

@receiver([post_save, post_delete], sender=Tour)
def clear_tour_cache(sender, **kwargs):
    cache.clear() 