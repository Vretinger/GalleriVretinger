import calendar
import json
from datetime import date
from calendar import HTMLCalendar
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.dateparse import parse_date, parse_time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.db.models import Min, Max
import cloudinary.uploader
from .models import Event, EventDay, EventImage, EventBooking
from .forms import EventBookingForm
from utils.email import send_email

def create_event(request):
    if request.method == "POST":
        title = request.POST.get("event_title")
        description = request.POST.get("event_description")
        bg_image_public_id = request.POST.get("bg_image_uploaded")
        # Save the Event first
        event = Event.objects.create(
            title=title,
            description=description,
            bg_image=bg_image_public_id if bg_image_public_id else None,
        )

        # --- Loop over POST keys to find per-day times ---
        for key, value in request.POST.items():
            if key.startswith("start_time_"):
                date_str = key.replace("start_time_", "")
                start_time = value
                end_time = request.POST.get(f"end_time_{date_str}")

                if start_time and end_time:
                    EventDay.objects.create(
                        event=event,
                        date=parse_date(date_str),           # converts "2025-09-28" → date object
                        start_time=parse_time(start_time),   # converts "10:00" → time object
                        end_time=parse_time(end_time)        # converts "14:00" → time object
                    )

        # --- Create EventImage objects from uploaded_images ---
        uploaded_images = request.POST.getlist("uploaded_images")
        for public_id in uploaded_images:
            EventImage.objects.create(event=event, image=public_id)

        return redirect("event_detail", pk=event.pk)

    return render(request, "events/create_event.html")


@require_POST
def delete_uploaded_image(request):
    data = json.loads(request.body)
    public_id = data.get("public_id")

    if not public_id:
        return JsonResponse({"error": "No public_id provided"}, status=400)

    try:
        result = cloudinary.uploader.destroy(public_id)
        return JsonResponse({"success": True, "result": result})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class EventCalendar(HTMLCalendar):
    def __init__(self, events):
        super().__init__()
        self.events = self.group_by_day(events)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            day_events = self.events.get(day, [])
            events_html = ''.join(
                f'<li>{event.title} ({event.start_datetime.strftime("%H:%M")})</li>'
                for event in day_events
            )
            return f'<td class="{cssclass}"><span class="date">{day}</span><ul>{events_html}</ul></td>'
        return '<td class="noday">&nbsp;</td>'

    def group_by_day(self, events):
        grouped = {}
        for event in events:
            day = event.start_datetime.day
            grouped.setdefault(day, []).append(event)
        return grouped


def calendar_view(request, year=None, month=None):
    today = date.today()
    year = year or today.year
    month = month or today.month

    events = Event.objects.filter(
        start_datetime__year=year,
        start_datetime__month=month
    )

    cal = EventCalendar(events).formatmonth(year, month)

    return render(request, 'events/calendar.html', {
        'calendar': cal,
        'year': year,
        'month': month,
    })


def event_list(request):
    today = now().date()

    # Annotate events with first and last day
    events = Event.objects.annotate(
        first_day=Min('days__date'),
        last_day=Max('days__date')
    ).order_by('first_day')

    # Split into upcoming and past events
    upcoming_events = [e for e in events if e.last_day >= today]
    passed_events = [e for e in events if e.last_day < today]

    # Debug: print events for verification
    print("Upcoming Events:")
    for e in upcoming_events:
        print(e.title, e.first_day, e.last_day)

    print("Passed Events:")
    for e in passed_events:
        print(e.title, e.first_day, e.last_day)

    return render(request, 'events/event_list.html', {
        'upcoming_events': upcoming_events,
        'passed_events': passed_events
    })


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})


def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.is_drop_in:
        messages.info(request, "This event is open for everyone — no sign-up needed.")
        return redirect('event_list')
    
    # Calculate available spots
    total_booked = sum(b.num_guests for b in event.bookings.all())
    spots_left = (event.max_attendees or 0) - total_booked

    if event.max_attendees and spots_left <= 0:
        messages.error(request, "Sorry, this event is fully booked.")
        return redirect('event_list')

    if request.method == 'POST':
        form = EventBookingForm(request.POST)
        if form.is_valid():
            num_guests = form.cleaned_data.get('num_guests', 1)

            # Check for spot availability
            if event.max_attendees and num_guests > spots_left:
                form.add_error('num_guests', f"Only {spots_left} spots left.")
            # Check for duplicate email
            elif EventBooking.objects.filter(event=event, email=form.cleaned_data['email']).exists():
                messages.warning(request, "This email is already registered for the event.")
            else:
                # Save booking
                booking = form.save(commit=False)
                booking.event = event
                booking.num_guests = num_guests
                booking.save()

                messages.success(request, f"You successfully booked {num_guests} spot(s)!")

                # --- Send confirmation email ---
                context = {
                    "guest_name": form.cleaned_data.get('name', form.cleaned_data['email']),
                    "event": event,
                    "event_days": event_days,
                }
                try:
                    send_email(
                        subject=f"Your spot for '{event.title}' is confirmed!",
                        template_name="emails/event_spot_confirmation.html",
                        context=context,
                        recipient_list=[form.cleaned_data['email']],
                        from_email="booking@gallerivretinger.se",
                    )
                except Exception as e:
                    print("Error sending booking confirmation email:", e)

                # Notify the event host
                try:
                    event_days = event.days.all().order_by("date")
                    host = getattr(event.booking, "user", None)
                    if host and host.email:
                        # send host email

                        context = {
                            "host_name": host.get_full_name() or host.username,
                            "event": event,
                            "event_days": event_days,
                            "guest_name": booking.name,
                            "guest_email": booking.email,
                            "num_guests": booking.num_guests,
                        }

                        send_email(
                            subject=f"New booking for your event '{event.title}'",
                            template_name="emails/event_new_booking_notification.html",
                            context=context,
                            recipient_list=[host.email],
                            from_email="booking@gallerivretinger.se",
                        )
                except Exception as e:
                    print("Error sending host notification email:", e)

                # Redirect to a page with modal popup
                url = reverse("event_list") + "?show_modal=1"
                return redirect(url)
    else:
        form = EventBookingForm(initial={'num_guests': 1})

    return render(request, "events/book_event.html", {
        "form": form,
        "event": event,
    })