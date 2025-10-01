from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns, set_language
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('events/', include('events.urls')),
    path('gallery/', include('gallery.urls')),
    path('contact/', include('contact.urls')),
    path('booking/', include('booking.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('i18n/setlang/', set_language, name='set_language'),
    path("users/", include("users.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
