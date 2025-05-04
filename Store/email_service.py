# email_service.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email_response(name, email, subject, ai_response):
    """
    Send an email with the AI-generated response using an HTML template
    """
    try:
        email_subject = f"Re: {subject}" if subject else "Response to your inquiry"
        
        # Prepare the context for the email template
        context = {
            'customer_name': name,
            'ai_generated_content': ai_response
        }
        
        # Render the HTML email template
        html_message = render_to_string('emails/email_template.html', context)
        
        # Create a plain text version of the email
        plain_message = strip_tags(html_message)
        
        # Send the email
        send_mail(
            email_subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email response sent to {email}")
        return True
        
    except Exception as e:
        logger.exception(f"Error sending email: {str(e)}")
        return False
