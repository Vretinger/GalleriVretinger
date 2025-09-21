from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Booking
from events.models import Event

def availability_view(request):
    """Public view: show availability but don’t allow booking unless logged in"""
    if request.user.is_authenticated:
        return redirect("booking_page")
    return render(request, "bookings/availability.html")


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "bookings/my_bookings.html", {"bookings": bookings})


def booked_dates(request):
    """Return JSON with booked dates for calendar"""
    bookings = Booking.objects.all()
    events = [
        {
            "title": "Booked",
            "start": str(b.start_date),
            "end": str(b.end_date),
            "color": "red"
        } for b in bookings
    ]
    return JsonResponse(events, safe=False)


@login_required
def booking_page(request):
    """Single page booking flow (Stage 1 + 2)"""
    if request.method == "POST":
        # Grab form data
        rental_start = request.POST.get("start_date")
        rental_end = request.POST.get("end_date")
        event_start = request.POST.get("event_start")
        event_end = request.POST.get("event_end")
        title = request.POST.get("title")
        description = request.POST.get("description")
        layout = request.POST.get("layout")
        bg_color = request.POST.get("bg_color")
        blur_bg = request.POST.get("blur_bg") == "on"

        # Create Booking
        booking = Booking.objects.create(
            user=request.user,
            start_date=rental_start,
            end_date=rental_end,
            purpose="Event booking",
        )

        # Create Event linked to Booking
        event = Event.objects.create(
            booking=booking,
            title=title,
            description=description,
            layout=layout,
            bg_color=bg_color,
            blur_bg=blur_bg,
            start_datetime=event_start,
            end_datetime=event_end,
        )

        # Save uploaded images
        for key in request.FILES:
            file = request.FILES[key]
            event.images.create(image=file)

        messages.success(request, "Your booking has been submitted!")
        return redirect("my_bookings")

    return render(request, "bookings/booking_calendar.html")
