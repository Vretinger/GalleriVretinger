from django.shortcuts import render
from django.utils.timezone import now
from events.models import Event, EventDay
from cloudinary.utils import cloudinary_url


def home_view(request):
    # Get the first current event
    current_event = Event.objects.filter(is_current_event=True).first()

    if current_event:
        # Group days like in your bookings preview
        days = list(current_event.days.all().order_by("date"))
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

        # Prepare background style
        bg_style = ""
        if current_event.bg_image:
            bg_url, _ = cloudinary_url(current_event.bg_image.public_id)
            bg_style += f"background-image: url('{bg_url}');"
        else:
            bg_style += f"background-color: {current_event.bg_color or '#f5f5f5'};"

        bg_style += " background-size: cover; background-position: center; width: 100%; min-height: 300px;"
        if current_event.blur_bg:
            bg_style += " filter: blur(4px);"
    else:
        grouped_days = []
        bg_style = ""

    # ✅ Get upcoming events (max 5)
    today = now().date()
    upcoming_events = (
        Event.objects.filter(days__date__gte=today, is_current_event=False)
        .distinct()
        .order_by("days__date")[:5]
    )

    return render(request, "home.html", {
        "current_event": current_event,
        "grouped_days": grouped_days,
        "bg_style": bg_style,
        "upcoming_events": upcoming_events,  # ✅ pass to template
    })
