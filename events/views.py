import calendar
from datetime import date
from calendar import HTMLCalendar
from django.shortcuts import render, get_object_or_404
from .models import Event


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
