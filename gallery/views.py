from django.shortcuts import render
from .models import Artwork

def gallery_view(request):
    artworks = Artwork.objects.all().order_by('-created_at')
    return render(request, 'gallery/gallery.html', {'artworks': artworks})
