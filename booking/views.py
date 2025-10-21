from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import JsonResponse
from utils.email import send_email
from django.conf import settings
from .models import Booking, Coupon
from events.models import Event, EventImage, EventDay
from django.utils.dateparse import parse_date, parse_time
from django.utils.translation import gettext as _
from cloudinary.utils import cloudinary_url
from cloudinary import Search
from io import BytesIO
from django.core.mail import EmailMessage
from itertools import groupby
from operator import attrgetter
from datetime import datetime
from django.views.decorators.http import require_GET
from .utils.pricing import calculate_booking_price

import cloudinary.uploader
import stripe

def availability_view(request):
    """Public view: show availability but don’t allow booking unless logged in"""
    if request.user.is_authenticated:
        return redirect("booking_page")
    
    # 🔎 fetch images from your premises folder
    try:
        search = Search() \
            .expression("folder:premises/*") \
            .sort_by("public_id", "desc") \
            .max_results(30)
        result = search.execute()
        premises_images = result.get("resources", [])
        print("Fetched premises images:", [img["secure_url"] for img in premises_images])
    except Exception as e:
        print("Cloudinary search error:", e)
        premises_images = []

    if request.method == "POST":
        # your existing booking/event saving code...
        pass

    return render(
        request,
        "bookings/availability.html",
        {"premises_images": premises_images}
    )


@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user)
    booking_events = []

    for booking in bookings:
        events = Event.objects.filter(booking=booking)
        for event in events:
            # --- Compute grouped days like in JS preview ---
            days = list(event.days.all().order_by("date"))
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

            # --- Compute background style ---
            bg_style = ""
            if event.bg_image:
                bg_url, _ = cloudinary_url(event.bg_image.public_id)
                bg_style += f"background-image: url('{bg_url}');"
            else:
                bg_style += f"background-color: {event.bg_color or '#f5f5f5'};"

            bg_style += " background-size: cover; background-position: center; width: 100%; min-height: 300px;"
            if event.blur_bg:
                bg_style += " filter: blur(4px);"

            # --- Append to booking_events ---
            booking_events.append({
                "booking": booking,
                "event": event,
                "grouped_days": grouped_days,
                "bg_style": bg_style,
                "images": event.images.all()
            })

    return render(request, "bookings/my_bookings.html", {
        "booking_events": booking_events
    })


def booked_dates(request):
    """Return JSON with booked dates for calendar"""
    bookings = Booking.objects.all()
    events = [
        {
            "title": _("Booked"), 
            "start": str(b.start_date),
            "end": str(b.end_date),
            "color": "red"
        } for b in bookings
    ]
    return JsonResponse(events, safe=False)


@require_GET
def calculate_price(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return JsonResponse({"price": 0, "error": "Missing dates"}, status=400)

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()

        # 🔹 Ensure correct inclusive range (end date included)
        if end_date < start_date:
            return JsonResponse({"price": 0, "error": "End date before start date"}, status=400)

        price = calculate_booking_price(start_date, end_date)
        return JsonResponse({"price": round(price, 2)})

    except ValueError:
        return JsonResponse({"price": 0, "error": "Invalid date format"}, status=400)


def validate_coupon(request):
    code = request.GET.get("code")
    base_price = float(request.GET.get("base_price", 0))
    try:
        coupon = Coupon.objects.get(code__iexact=code, active=True)
        discount = 0
        if coupon.discount_type == "percent":
            discount = base_price * (coupon.discount_value / 100)
        else:  # fixed amount
            discount = coupon.discount_value
        return JsonResponse({
            "valid": True,
            "discount": discount,
            "type": coupon.discount_type,
            "value": coupon.discount_value
        })
    except Coupon.DoesNotExist:
        return JsonResponse({"valid": False, "discount": 0, "type": None, "value": None})



@login_required
def booking_page(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.method == "POST":

        # Extract form data
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        title = request.POST.get("title")
        description = request.POST.get("description")
        bg_color = request.POST.get("bg_color")
        blur_bg = request.POST.get("blur_bg") == "on"
        event_start = request.POST.get("event_start")
        event_end = request.POST.get("event_end")
        bg_image_id = request.POST.get("bg_image_uploaded")
        discount_code = request.POST.get("discount_code", "").strip()
        uploaded_images = request.POST.getlist("uploaded_images")

        from .utils.pricing import calculate_booking_price, apply_discount_code
        from datetime import datetime, timedelta
        import json

        # --- Calculate total price ---
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        total_price = calculate_booking_price(start_date_obj, end_date_obj)

        # Apply discount if code is valid
        discount_amount = 0
        if discount_code:
            discount_amount = apply_discount_code(discount_code, total_price)
            if discount_amount is None:
                messages.error(request, "Invalid discount code!")
                return redirect("booking_page")
            total_price -= discount_amount

        # --- Determine first and second payment ---
        today = datetime.today().date()
        days_until_event = (start_date_obj - today).days

        if days_until_event > 14:
            initial_payment = round(total_price * 0.5, 2)
            final_payment = round(total_price - initial_payment, 2)
            final_payment_due_date = start_date - timedelta(days=14)
            is_confirmed = False
        else:
            initial_payment = round(total_price, 2)
            final_payment = 0
            final_payment_due_date = None
            is_confirmed = True

        # Save initial booking (unconfirmed if only 50% paid)
        booking = Booking.objects.create(
            user=request.user,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            initial_payment_amount=initial_payment,
            final_payment_amount=final_payment,
            final_payment_due_date=final_payment_due_date,
            is_confirmed=is_confirmed,
            discount_code=discount_code or None
        )

        # Collect EventDays and uploaded images
        event_days_data = []
        for key, value in request.POST.items():
            if key.startswith("start_time_"):
                date_str = key.replace("start_time_", "")
                start_time = value
                end_time = request.POST.get(f"end_time_{date_str}")
                if start_time and end_time:
                    event_days_data.append({
                        "date": date_str,
                        "start_time": start_time,
                        "end_time": end_time,
                    })

        # --- Store metadata for Stripe ---
        metadata = {
            "booking_id": str(booking.id),
            "user_id": str(request.user.id),
            "title": title,
            "description": description or "",
            "bg_color": bg_color or "",
            "blur_bg": str(blur_bg),
            "event_start": event_start or "",
            "event_end": event_end or "",
            "total_price": str(total_price),
            "initial_payment_amount": str(initial_payment),
            "final_payment_amount": str(final_payment),
            "final_payment_due_date": str(final_payment_due_date) if final_payment_due_date else "",
            "uploaded_images": json.dumps(uploaded_images),
            "event_days": json.dumps(event_days_data),
            "discount_code": discount_code or "",
        }

        # Stripe checkout for **initial payment**
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "sek",
                        "product_data": {
                            "name": f"Gallery Rental: {request.POST.get('title')}",
                            "description": f"{start_date} → {end_date}",
                        },
                        "unit_amount": int(initial_payment * 100),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=request.build_absolute_uri(reverse("payment_success")) + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri(reverse("payment_cancel")),
                metadata={**metadata, "payment_stage": "initial"},
            )
            return redirect(session.url)
        except Exception as e:
            print("Stripe error:", e)
            messages.error(request, "Could not create payment session.")
            return redirect("booking_page")

    # GET request: show booking calendar
    try:
        search = Search().expression("folder:premises/*").sort_by("public_id", "desc").max_results(30)
        premises_images = search.execute().get("resources", [])
    except Exception as e:
        print("Cloudinary search error:", e)
        premises_images = []

    return render(request, "bookings/booking_calendar.html", {"premises_images": premises_images})


def payment_success(request):
    import json
    from cloudinary import uploader

    session_id = request.GET.get("session_id")
    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.retrieve(session_id)
    metadata = session.metadata

    if not session_id:
        messages.error(request, "Missing payment session ID.")
        return redirect("booking_page")


    try:
        # Retrieve Stripe session and metadata
        session = stripe.checkout.Session.retrieve(session_id)
        metadata = session.metadata
        user = request.user

        booking_id = metadata.get("booking_id")
        payment_stage = metadata.get("payment_stage", "initial")

        booking = Booking.objects.get(id=booking_id, user=user)

        # --- Handle payment stages ---
        if payment_stage == "initial":
            booking.initial_payment_completed = True
            payment_msg = "Initial payment (50%) received."
        elif payment_stage == "final":
            booking.final_payment_completed = True
            payment_msg = "Final payment (remaining 50%) received."
        else:
            payment_msg = "Full payment received."

        # --- Confirm booking when full amount is paid ---
        if (booking.final_payment_amount == 0) or (
            booking.initial_payment_completed and booking.final_payment_completed
        ):
            booking.is_confirmed = True
            confirmation_msg = "Your booking is now fully confirmed!"
        else:
            confirmation_msg = (
                "Your booking is partially paid. Please complete your final payment before the due date."
            )

        booking.save()

        # --- Create event (only if not already created) ---
        existing_event = Event.objects.filter(booking=booking).first()
        if not existing_event:
            start_date = booking.start_date
            end_date = booking.end_date

            # Parse event details from metadata
            title = metadata.get("title", "Untitled Event")
            description = metadata.get("description", "")
            bg_color = metadata.get("bg_color", "#ffffff")
            blur_bg = metadata.get("blur_bg") == "True"
            event_start = metadata.get("event_start")
            event_end = metadata.get("event_end")
            bg_image_id = metadata.get("bg_image")

            def safe_parse_datetime(dt_str):
                if not dt_str:
                    return None
                for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
                    try:
                        return datetime.strptime(dt_str, fmt)
                    except ValueError:
                        continue
                return None

            start_dt = safe_parse_datetime(event_start)
            end_dt = safe_parse_datetime(event_end)

            event = Event.objects.create(
                booking=booking,
                title=title,
                description=description,
                bg_color=bg_color,
                blur_bg=blur_bg,
                start_datetime=start_dt,
                end_datetime=end_dt,
                bg_image=bg_image_id or None,
            )

            # Create EventDays
            event_days_data = json.loads(metadata.get("event_days", "[]"))
            for day_data in event_days_data:
                EventDay.objects.create(
                    event=event,
                    date=parse_date(day_data["date"]),
                    start_time=parse_time(day_data["start_time"]),
                    end_time=parse_time(day_data["end_time"]),
                )

            # Move uploaded images into event folder
            uploaded_images = json.loads(metadata.get("uploaded_images", "[]"))
            for public_id in uploaded_images:
                new_folder = f"users/{user.email}/events/{event.id}"
                new_public_id = f"{new_folder}/{public_id.split('/')[-1]}"
                try:
                    result = uploader.rename(public_id, new_public_id, overwrite=True)
                    EventImage.objects.create(event=event, image=result["public_id"])
                except Exception as e:
                    print("Cloudinary move error:", e)
                    EventImage.objects.create(event=event, image=public_id)

        else:
            event = existing_event

        # --- Send confirmation or update email ---
        context = {
            "host_name": user.get_full_name() or user.username,
            "event": event,
            "booking": booking,
            "confirmation_msg": confirmation_msg,
            "payment_msg": payment_msg,
        }

        email = EmailMessage(
            subject=f"Payment received for your booking '{event.title}'",
            body=render_to_string("emails/payment_confirmation.html", context),
            from_email="booking@gallerivretinger.se",
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send()

        messages.success(request, f"{payment_msg} {confirmation_msg}")
        return redirect("my_bookings")

    except Booking.DoesNotExist:
        messages.error(request, "Booking not found.")
    except Exception as e:
        print("Payment success error:", e)
        messages.error(request, "Payment was successful, but processing failed.")

    return redirect("booking_page")


def payment_cancel(request):
    messages.warning(request, "Payment was cancelled. Your booking has not been confirmed.")
    return redirect("booking_page")
