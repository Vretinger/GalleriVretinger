from django.shortcuts import render
from events.models import Event
from cloudinary.utils import cloudinary_url
from django.db.models import Min


def home_view(request):
    # ✅ Get the current event (if any)
    current_event = Event.objects.filter(is_current_event=True).first()

    grouped_days = []
    bg_style = ""

    if current_event:
        # Group the event days
        days = list(current_event.days.all().order_by("date"))
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

        # ✅ Background style
        if current_event.bg_image:
            bg_url, _ = cloudinary_url(current_event.bg_image.public_id)
            bg_style = (
                f"background-image: url('{bg_url}'); "
                f"background-size: cover; background-position: center; "
                f"width: 100%; min-height: 300px;"
            )
        else:
            bg_style = (
                f"background-color: {current_event.bg_color or '#f5f5f5'}; "
                f"background-size: cover; background-position: center; "
                f"width: 100%; min-height: 300px;"
            )
        if current_event.blur_bg:
            bg_style += " filter: blur(4px);"

    
    upcoming_events = (
        Event.objects.filter(is_upcoming_event=True, is_current_event=False)
        .annotate(first_day=Min("days__date"))  # get earliest day
        .order_by("first_day")  # order by that day
        [:5]  # limit to 5 events
    )


    # 🔍 Debug print to console
    for event in upcoming_events:
        print(f"Event: {event.title} (First day: {event.first_day})")
        for day in event.days.all().order_by("date"):
            print(f"  - Day: {day.date}")

    # Render
    return render(
        request,
        "home.html",
        {
            "current_event": current_event,
            "grouped_days": grouped_days,
            "bg_style": bg_style,
            "upcoming_events": upcoming_events,
        },
    )
