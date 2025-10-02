import calendar
import json
from datetime import date
from calendar import HTMLCalendar
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.dateparse import parse_date, parse_time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import cloudinary.uploader
from .models import Event, EventDay, EventImage

def create_event(request):
    if request.method == "POST":
        title = request.POST.get("event_title")
        description = request.POST.get("event_description")
        bg_image_public_id = request.POST.get("bg_image_uploaded")
        print("Background image public_id:", bg_image_public_id)  # Debugging line

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
    today = date.today()
    events = Event.objects.filter(
        start_datetime__gte=today
    ).order_by('start_datetime')
    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})
