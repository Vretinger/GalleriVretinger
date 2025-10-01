from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # process form data (e.g. send email or save to DB)
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            # Example: just show success message
            messages.success(request, "Thank you! Your message has been sent.")
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})
