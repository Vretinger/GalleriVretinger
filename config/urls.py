from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from django.conf import settings
from django.conf.urls.static import static
from booking.views import admin_dashboard, admin_booking_page

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('events/', include('events.urls')),
    path('gallery/', include('gallery.urls')),
    path('contact/', include('contact.urls')),
    path('booking/', include('booking.urls')),
    path('users/', include('users.urls')),
    path("admin-panel/", admin_dashboard, name="admin_dashboard"),
    path("admin_booking/", admin_booking_page, name="admin_booking_page"),
)
