from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_email(subject, template_name, context, recipient_list, from_email=None):
    """
    Sends an HTML email using a template.
    
    - subject: email subject
    - template_name: path to template (e.g., 'emails/booking_confirmation.html')
    - context: dict with variables for template
    - recipient_list: list of recipient emails
    - from_email: override default from (optional)
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    message_html = render_to_string(template_name, context)
    
    plain_text = f"Hi {context['host_name']},\nYour event '{context['event'].title}' has been created.\n"
    send_mail(
        subject,
        plain_text,
        from_email,
        recipient_list,
        html_message=message_html,
        fail_silently=False,
    )
