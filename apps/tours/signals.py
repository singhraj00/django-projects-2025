from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import ContactMessage 
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete 
from .models import Tour
from apps.user.utils import send_sendgrid_email

@receiver(post_save, sender=ContactMessage)
def send_contact_confirmation(sender, instance, created, **kwargs):
    if created:
        html_content = render_to_string(
            'emails/contact_email.html',
            {'name': instance.name, 'message': instance.message}
        )

        send_sendgrid_email(
            subject="🌍 We Received Your Message - Safarnama",
            to_email=instance.email,
            html_content=html_content
        )



@receiver([post_save, post_delete], sender=Tour)
def clear_tour_cache(sender, **kwargs):
    cache.clear() 