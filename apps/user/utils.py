from django.dispatch import receiver
from django.template.loader import render_to_string
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Content, Attachment
import base64


def send_sendgrid_email(subject, to_email, html_content, attachment_bytes=None, attachment_name=None):
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )

    # Add attachment if provided
    if attachment_bytes:
        encoded_file = base64.b64encode(attachment_bytes).decode()
        attachedFile = Attachment()
        attachedFile.file_content = encoded_file
        attachedFile.file_type = "application/pdf"
        attachedFile.file_name = attachment_name
        attachedFile.disposition = "attachment"
        message.attachment = attachedFile

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)


def send_welcome_email(user):
    html_content = render_to_string('emails/welcome_email.html', {'user': user})
    send_sendgrid_email(
        subject="🎉 Welcome to Safarnama – Your Adventure Starts Here!",
        to_email=user.email,
        html_content=html_content
    )



def send_password_reset_confirmation(user):
    html_content = render_to_string('emails/password_reset_confirmation_email.html', {'user': user})
    send_sendgrid_email(
        subject="🔐 Your Safarnama Password Was Changed Successfully",
        to_email=user.email,
        html_content=html_content
    )