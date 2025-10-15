from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from .forms import ContactForm

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            subject = f"New contact form message from {name}"
            body = (
                f"You've received a new message from the contact form on your website:\n\n"
                f"👤 Name: {name}\n"
                f"📧 Email: {email}\n\n"
                f"💬 Message:\n{message}"
            )

            from_email = settings.DEFAULT_FROM_EMAIL  # usually something like "no-reply@gallerivretinger.se"
            to_email = ["support@gallerivretinger.se"]  # or your admin address

            try:
                send_mail(subject, body, from_email, to_email, fail_silently=False)
                messages.success(request, "Thank you! Your message has been sent successfully.")
            except BadHeaderError:
                messages.error(request, "Invalid header found. Please try again.")
            except Exception as e:
                print("Error sending contact email:", e)
                messages.error(request, "There was an issue sending your message. Please try again later.")

            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})
