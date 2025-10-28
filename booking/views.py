from datetime import datetime, timedelta
import base64, json

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from django.utils.translation import gettext as _
from django.utils.dateparse import parse_date, parse_time
from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4


from itertools import groupby
from operator import attrgetter

from cloudinary import Search, uploader
from cloudinary.utils import cloudinary_url

import stripe

# Local imports
from utils.email import send_email
from .models import Booking, Coupon
from events.models import Event, EventImage, EventDay
from .utils.pricing import calculate_booking_price, apply_discount_code


# ---------------------------------------------------------------------
# 🖋 CONTRACT SIGNING
# ---------------------------------------------------------------------

@login_required
def sign_contract(request, booking_id):
    """Display contract signing page."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, "bookings/contract_sign.html", {"booking": booking})


@csrf_exempt
@login_required
def save_signature(request, booking_id):
    """Save signature and then redirect to payment."""
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        request.session["pending_booking_id"] = booking.id
        data_url = request.POST.get("signature")

        format, imgstr = data_url.split(";base64,")
        image_data = ContentFile(base64.b64decode(imgstr), name=f"signature_{booking.id}.png")

        booking.contract_signature.save(f"signature_{booking.id}.png", image_data)
        booking.contract_signed = True
        booking.save()

        # ✅ Automatically create Stripe session after contract signing
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "sek",
                        "product_data": {
                            "name": f"Gallery Rental {booking.start_date} → {booking.end_date}",
                        },
                        "unit_amount": int(booking.initial_payment_amount * 100),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=request.build_absolute_uri(reverse("payment_success")) + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri(reverse("payment_cancel")),
                metadata={"booking_id": str(booking.id), "payment_stage": "initial"},
            )
            return JsonResponse({"success": True, "redirect_url": session.url})
        except Exception as e:
            print("Stripe error:", e)
            return JsonResponse({"success": False, "error": "Stripe session failed."})

    return JsonResponse({"success": False}, status=400)


# ---------------------------------------------------------------------
# 📅 AVAILABILITY VIEW (for non-logged users)
# ---------------------------------------------------------------------

def availability_view(request):
    """Public view: show gallery availability."""
    if request.user.is_authenticated:
        return redirect("booking_page")

    # Fetch images from Cloudinary folder "premises"
    try:
        premises_images = (
            Search()
            .expression("folder:premises/*")
            .sort_by("public_id", "desc")
            .max_results(30)
            .execute()
            .get("resources", [])
        )
    except Exception as e:
        print("Cloudinary search error:", e)
        premises_images = []

    return render(request, "bookings/availability.html", {"premises_images": premises_images})


# ---------------------------------------------------------------------
# 💼 USER BOOKINGS (Dashboard)
# ---------------------------------------------------------------------

@login_required
def my_bookings_view(request):
    """Display user's current and past bookings."""
    bookings = Booking.objects.filter(user=request.user)
    booking_events = []

    for booking in bookings:
        events = Event.objects.filter(booking=booking)
        for event in events:
            # Group event days with same times
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

            # Background style (image or color)
            bg_url = event.bg_image and cloudinary_url(event.bg_image.public_id)[0]
            bg_style = (
                f"background-image: url('{bg_url}');"
                if bg_url
                else f"background-color: {event.bg_color or '#f5f5f5'};"
            )
            bg_style += "background-size: cover; background-position: center; width:100%; min-height:300px;"
            if event.blur_bg:
                bg_style += "filter: blur(4px);"

            booking_events.append({
                "booking": booking,
                "event": event,
                "grouped_days": grouped_days,
                "bg_style": bg_style,
                "images": event.images.all(),
            })

    return render(request, "bookings/my_bookings.html", {"booking_events": booking_events})


# ---------------------------------------------------------------------
# 🗓 JSON: Booked Dates for Calendar
# ---------------------------------------------------------------------

def booked_dates(request):
    """Return JSON with booked dates for calendar display."""
    events = [
        {"title": _("Booked"), "start": str(b.start_date), "end": str(b.end_date), "color": "red"}
        for b in Booking.objects.all()
    ]
    return JsonResponse(events, safe=False)


# ---------------------------------------------------------------------
# 💰 PRICE + COUPON CALCULATION
# ---------------------------------------------------------------------

@require_GET
def calculate_price(request):
    """AJAX endpoint to calculate price between two dates."""
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return JsonResponse({"price": 0, "error": "Missing dates"}, status=400)

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()

        if end_date < start_date:
            return JsonResponse({"price": 0, "error": "End date before start date"}, status=400)

        price = calculate_booking_price(start_date, end_date)
        return JsonResponse({"price": round(price, 2)})
    except ValueError:
        return JsonResponse({"price": 0, "error": "Invalid date format"}, status=400)


def validate_coupon(request):
    """AJAX endpoint for validating coupon codes."""
    code = request.GET.get("code")
    base_price = float(request.GET.get("base_price", 0))
    try:
        coupon = Coupon.objects.get(code__iexact=code, active=True)
        discount = (
            base_price * (coupon.discount_value / 100)
            if coupon.discount_type == "percentage"
            else coupon.discount_value
        )
        return JsonResponse({
            "valid": True,
            "discount": discount,
            "type": coupon.discount_type,
            "value": coupon.discount_value,
        })
    except Coupon.DoesNotExist:
        return JsonResponse({"valid": False, "discount": 0, "type": None, "value": None})


# ---------------------------------------------------------------------
# 💳 BOOKING FLOW — Creation + Stripe Payment
# ---------------------------------------------------------------------

@login_required
def booking_page(request):
    """Booking creation page + Stripe payment initialization."""
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.method == "POST":
        # Extract form data
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        discount_code = request.POST.get("discount_code", "").strip()

        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        total_price = calculate_booking_price(start_date_obj, end_date_obj)

        # Apply discount if valid
        discount_amount = 0
        if discount_code:
            discount_amount = apply_discount_code(discount_code, total_price) or 0
            total_price -= discount_amount

        # Determine payment stages
        today = datetime.today().date()
        days_until_event = (start_date_obj - today).days
        if days_until_event > 14:
            initial_payment = round(total_price * 0.5, 2)
            final_payment = total_price - initial_payment
            final_due_date = start_date_obj - timedelta(days=14)
            is_confirmed = False
        else:
            initial_payment = total_price
            final_payment = 0
            final_due_date = None
            is_confirmed = True

        booking = Booking.objects.create(
            user=request.user,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            initial_payment_amount=initial_payment,
            final_payment_amount=final_payment,
            final_payment_due_date=final_due_date,
            discount_code=discount_code or None,
            is_confirmed=False,
        )

        # ✅ redirect to contract signing page
        messages.info(request, "Please sign the rental agreement before proceeding to payment.")
        return redirect("sign_contract", booking_id=booking.id)

    # GET: show available premises images
    try:
        premises_images = (
            Search().expression("folder:premises/*").sort_by("public_id", "desc").max_results(30).execute()
        ).get("resources", [])
    except Exception as e:
        print("Cloudinary search error:", e)
        premises_images = []

    return render(request, "bookings/booking_calendar.html", {"premises_images": premises_images})


# ---------------------------------------------------------------------
# 💰 FINAL PAYMENT (Remaining Balance)
# ---------------------------------------------------------------------

@login_required
def pay_remaining_balance(request, booking_id):
    """Handle second (final) payment for 50% remainder."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.final_payment_done:
        messages.info(request, "This booking is already fully paid.")
        return redirect("my_bookings")

    remaining = booking.final_payment_amount or 0
    if remaining <= 0:
        messages.info(request, "No remaining balance to pay.")
        return redirect("my_bookings")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "sek",
                    "product_data": {"name": f"Final Payment for {booking.start_date} → {booking.end_date}"},
                    "unit_amount": int(remaining * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("payment_success")) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("payment_cancel")),
            metadata={"booking_id": str(booking.id), "payment_stage": "final"},
        )
        return redirect(session.url)
    except Exception as e:
        print("Stripe error:", e)
        messages.error(request, "Could not create payment session for final payment.")
        return redirect("my_bookings")


# ---------------------------------------------------------------------
# ✅ STRIPE SUCCESS & CANCEL
# ---------------------------------------------------------------------

def payment_success(request):
    """Handle post-payment success for both initial and final payments."""
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "Missing payment session ID.")
        return redirect("booking_page")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        metadata = session.metadata
        booking = Booking.objects.get(id=metadata["booking_id"], user=request.user)

        stage = metadata.get("payment_stage", "initial")
        if stage == "initial":
            booking.initial_payment_done = True
        elif stage == "final":
            booking.final_payment_done = True

        if booking.final_payment_amount == 0 or (booking.initial_payment_done and booking.final_payment_done):
            booking.is_confirmed = True

        booking.save()

        messages.success(request, "Payment received and booking updated successfully!")
        return redirect("my_bookings")
    except Exception as e:
        print("Payment success error:", e)
        messages.error(request, "Payment succeeded but processing failed.")
        return redirect("booking_page")


@login_required
def payment_cancel(request):
    """Handle Stripe payment cancellation and remove unpaid booking."""
    booking_id = request.session.get("pending_booking_id")

    if booking_id:
        try:
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            # Only delete if payment not completed or confirmed
            if not booking.is_confirmed and not booking.initial_payment_done:
                booking.delete()
                messages.warning(request, "Payment was cancelled. Your booking has been released.")
            else:
                messages.info(request, "Payment cancelled, but your booking is already confirmed.")
        except Exception as e:
            print("Error deleting cancelled booking:", e)
            messages.error(request, "Payment was cancelled, but we couldn’t release your booking properly.")
        finally:
            # Clean up the session key
            if "pending_booking_id" in request.session:
                del request.session["pending_booking_id"]
    else:
        messages.warning(request, "Payment was cancelled. No active booking found.")

    return redirect("booking_page")


@csrf_exempt
@login_required
@require_POST
def cancel_unpaid_booking(request, booking_id):
    """Delete an unpaid booking if user leaves or cancels."""
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        if not booking.is_confirmed and not booking.initial_payment_done:
            booking.delete()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "message": "Booking already paid or confirmed."})
    except Exception as e:
        print("Cancel unpaid booking error:", e)
        return JsonResponse({"success": False}, status=500)


@csrf_exempt
@login_required
def cancel_unpaid_booking(request, booking_id):
    """Delete unpaid, unconfirmed booking if user leaves before payment."""
    if request.method not in ["POST", "GET"]:
        return JsonResponse({"success": False, "message": "Invalid method."}, status=405)

    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        print(f"⚠️ Booking {booking_id} not found for user {request.user}")
        return JsonResponse({"success": False, "message": "Booking not found."}, status=404)

    if not booking.is_confirmed and not booking.initial_payment_done:
        print(f"🗑 Deleting unpaid booking {booking.id} for {request.user}")
        booking.delete()
        return JsonResponse({"success": True})
    else:
        print(f"❌ Booking {booking.id} already confirmed or paid — not deleting.")
        return JsonResponse({"success": False, "message": "Booking already confirmed or paid."})



