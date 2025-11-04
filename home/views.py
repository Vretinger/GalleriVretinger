from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Min
from events.models import Event

def home_view(request):
    today = now().date()

    # ✅ Fetch up to 4 upcoming events (including any marked current)
    events = (
        Event.objects.annotate(first_day=Min("days__date"))
        .filter(first_day__gte=today)
        .order_by("first_day")[:4]
    )

    # 🔍 Debug log to console
    for e in events:
        print(f"Event: {e.title} | First day: {e.first_day}")

    return render(request, "home.html", {"events": events})
