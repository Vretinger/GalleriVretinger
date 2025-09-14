from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import BookingEventForm, DateSelectionForm
from .models import Booking
from events.models import Event


def booking_date_selection(request):
    return render(request, "bookings/booking_calendar.html")


def booked_dates(request):
    """Return existing bookings as JSON for FullCalendar"""
    bookings = Booking.objects.all()
    events = [
        {
            "title": "Booked",
            "start": str(b.start_date),
            "end": str(b.end_date),
            "color": "red"
        }
        for b in bookings
    ]
    return JsonResponse(events, safe=False)


def save_selected_dates(request):
    """AJAX endpoint when user selects a date range"""
    if request.method == "POST":
        start = request.POST.get("start")
        end = request.POST.get("end")

        # Store dates in session for Step 2
        request.session["start_date"] = start
        request.session["end_date"] = end

        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


def booking_date_selection(request):
    if request.method == "POST":
        form = DateSelectionForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Check for conflicts
            if Booking.objects.filter(start_date__lte=end_date, end_date__gte=start_date).exists():
                form.add_error(None, "Those dates are already booked.")
            else:
                # Temporarily store in session before step 2
                request.session['start_date'] = str(start_date)
                request.session['end_date'] = str(end_date)
                return redirect("booking_details")
    else:
        form = DateSelectionForm()
    return render(request, "bookings/booking_calendar.html", {"form": form})


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

def final_booking_submit(request):
    if request.method == "POST":
        rental_start = request.POST.get("rental_start")
        rental_end = request.POST.get("rental_end")
        event_start = request.POST.get("event_start")
        event_end = request.POST.get("event_end")
        title = request.POST.get("title")
        description = request.POST.get("description")
        layout = request.POST.get("layout")

        # TODO: link to actual logged in user
        booking = Booking.objects.create(
            start_date=rental_start,
            end_date=rental_end,
            purpose="Event booking",  # Or grab from form
            user=request.user if request.user.is_authenticated else None,
        )

        event = Event.objects.create(
            booking=booking,
            title=title,
            description=description,
            layout=layout,
            start_datetime=event_start,
            end_datetime=event_end,
        )

        # Save uploaded images
        for file in request.FILES.getlist("image1"):
            event.images.create(image=file)
        for key in request.FILES:
            if key.startswith("image") and key != "image1":
                event.images.create(image=request.FILES[key])

        messages.success(request, "Your booking has been submitted!")
        return redirect("home")  # Or a "booking confirmation" page

    return redirect("booking_with_event")
