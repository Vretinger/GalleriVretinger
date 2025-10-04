from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Booking
from events.models import Event, EventImage, EventDay
from django.utils.dateparse import parse_date, parse_time
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from cloudinary import Search

def availability_view(request):
    """Public view: show availability but don’t allow booking unless logged in"""
    if request.user.is_authenticated:
        return redirect("booking_page")
    
    # 🔎 fetch images from your premises folder
    try:
        search = Search() \
            .expression("folder:premises/*") \
            .sort_by("public_id", "desc") \
            .max_results(30)
        result = search.execute()
        premises_images = result.get("resources", [])
        print("Fetched premises images:", [img["secure_url"] for img in premises_images])
    except Exception as e:
        print("Cloudinary search error:", e)
        premises_images = []

    if request.method == "POST":
        # your existing booking/event saving code...
        pass

    return render(
        request,
        "bookings/availability.html",
        {"premises_images": premises_images}
    )


from itertools import groupby
from operator import attrgetter

from itertools import groupby
from operator import attrgetter
from datetime import datetime




@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user)
    booking_events = []

    for booking in bookings:
        events = Event.objects.filter(booking=booking)
        for event in events:
            # --- Compute grouped days like in JS preview ---
            days = list(event.days.all().order_by("date"))
            grouped_days = []
            if days:
                current_group = [days[0]]
                for d in days[1:]:
                    prev = current_group[-1]
                    if d.start_time == prev.start_time and d.end_time == prev.end_time:
                        current_group.append(d)
                    else:
                        grouped_days.append(current_group)
                        current_group = [d]
                grouped_days.append(current_group)

            # --- Compute background style ---
            bg_style = ""
            if event.bg_image:
                bg_url, _ = cloudinary_url(event.bg_image.public_id)
                bg_style += f"background-image: url('{bg_url}');"
            else:
                bg_style += f"background-color: {event.bg_color or '#f5f5f5'};"

            bg_style += " background-size: cover; background-position: center; width: 100%; min-height: 300px;"
            if event.blur_bg:
                bg_style += " filter: blur(4px);"

            # --- Append to booking_events ---
            booking_events.append({
                "booking": booking,
                "event": event,
                "grouped_days": grouped_days,
                "bg_style": bg_style,
                "images": event.images.all()
            })

    return render(request, "bookings/my_bookings.html", {
        "booking_events": booking_events
    })






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
    
    if request.method == "POST":

        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            start_date=request.POST.get("start_date"),
            end_date=request.POST.get("end_date"),
            purpose="Event booking",
        )

        # Create event
        event = Event.objects.create(
            booking=booking,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            bg_color=request.POST.get("bg_color"),
            blur_bg=request.POST.get("blur_bg") == "on",
            start_datetime=request.POST.get("event_start"),
            end_datetime=request.POST.get("event_end"),
            is_drop_in=request.POST.get("is_drop_in") == "on",
            max_attendees=request.POST.get("max_attendees") or None,
        )

        # Save background image public_id from hidden input
        bg_image_id = request.POST.get("bg_image_uploaded")
        if bg_image_id:
            event.bg_image = bg_image_id
            event.save(update_fields=["bg_image"])

        for key, value in request.POST.items():
            if key.startswith("start_time_"):
                date_str = key.replace("start_time_", "")
                start_time = value
                end_time = request.POST.get(f"end_time_{date_str}")

                if start_time and end_time:
                    EventDay.objects.create(
                        event=event,
                        date=parse_date(date_str),
                        start_time=parse_time(start_time),
                        end_time=parse_time(end_time),
                    )

        # process uploaded images
        uploaded_ids = request.POST.getlist("uploaded_images")
        for public_id in uploaded_ids:
            new_folder = f"users/{request.user.email}/events/{event.id}"
            new_public_id = f"{new_folder}/{public_id.split('/')[-1]}"  # keep filename

            try:
                result = cloudinary.uploader.rename(
                    public_id,
                    new_public_id,
                    overwrite=True
                )
                # Create EventImage for this event
                EventImage.objects.create(
                    event=event,
                    image=result["public_id"]
                )
            except Exception as e:
                print("Cloudinary move error (event image):", e)
                # fallback: still save EventImage with original public_id
                EventImage.objects.create(
                    event=event,
                    image=public_id
                )


        messages.success(request, "Your booking has been submitted!")
        return redirect("my_bookings")
    

    # 🔎 fetch images from your premises folder
    try:
        search = Search() \
            .expression("folder:premises/*") \
            .sort_by("public_id", "desc") \
            .max_results(30)
        result = search.execute()
        premises_images = result.get("resources", [])
        print("Fetched premises images:", [img["secure_url"] for img in premises_images])
    except Exception as e:
        print("Cloudinary search error:", e)
        premises_images = []

    if request.method == "POST":
        # your existing booking/event saving code...
        pass

    return render(
        request,
        "bookings/booking_calendar.html",
        {"premises_images": premises_images}
    )

