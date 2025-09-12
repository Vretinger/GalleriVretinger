from django.shortcuts import render
from events.models import Event
from gallery.models import Artwork
from datetime import date

def home_view(request):
    today = date.today()
    ##upcoming_events = Event.objects.filter(date__gte=today).order_by('date')[:3]
    featured_artworks = Artwork.objects.filter(is_featured=True)[:3]
    return render(request, 'home/home.html', {
        ##'upcoming_events': upcoming_events,
        'featured_artworks': featured_artworks,
        'today': today,
    })
