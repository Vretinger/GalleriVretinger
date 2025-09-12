from django.shortcuts import render, redirect
from .forms import BookingEventForm
from .models import Booking
from events.models import Event

def booking_with_event(request):
    if request.method == 'POST':
        form = BookingEventForm(request.POST, request.FILES)
        if form.is_valid():
            # Save Booking
            booking = Booking.objects.create(
                user=request.user,
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                purpose=form.cleaned_data['purpose'],
                approved=False
            )

            # Save Event linked to booking
            Event.objects.create(
                booking=booking,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                layout=form.cleaned_data['layout'],
                image1=form.cleaned_data['image1'],
                image2=form.cleaned_data.get('image2'),
                image3=form.cleaned_data.get('image3'),
            )

            return redirect('booking_success')  # make this template
    else:
        form = BookingEventForm()

    return render(request, 'bookings/booking_with_event.html', {'form': form})
