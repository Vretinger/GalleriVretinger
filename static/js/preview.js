document.addEventListener("DOMContentLoaded", () => {
  const titleInput = document.getElementById("event-title");
  const ShortDescriptionInput = document.getElementById("event-ShortDescription");
  const previewTitle = document.getElementById("preview-title");
  const previewShortDescription = document.getElementById("preview-ShortDescription");
  const previewTimes = document.getElementById("preview-times");

  // Price preview
  const startInput = document.getElementById("rental_start");
  const endInput = document.getElementById("rental_end");
  const basePriceEl = document.getElementById("base-price");
  const discountEl = document.getElementById("discount-amount");
  const totalPriceEl = document.getElementById("total-price");
  const couponInput = document.getElementById("coupon-code");
  const applyBtn = document.getElementById("apply-coupon-btn");
  const feedbackEl = document.getElementById("coupon-feedback");

  const initialPaymentEl = document.getElementById("initial-payment");
  const finalPaymentEl = document.getElementById("final-payment");

  let basePrice = 0;
  let discountAmount = 0;

  // --- Text preview ---
  titleInput.addEventListener("input", () => {
    previewTitle.textContent = titleInput.value || "Event Title";
    validateForm();
  });

  ShortDescriptionInput.addEventListener("input", () => {
    previewShortDescription.textContent = ShortDescriptionInput.value || "Events short description will appear here.";
    validateForm();
  });

  
  // --- Times preview ---
  document.addEventListener("updateTimesPreview", () => {
    const container = document.getElementById("per-day-times");
    if (!container) return previewTimes.textContent = "Event times: Not set";

    const rows = container.querySelectorAll(".row");
    const dayTimes = Array.from(rows).map(row => {
      const date = row.querySelector(".fw-bold").textContent;
      const start = row.querySelector(".per-day-start").value;
      const end = row.querySelector(".per-day-end").value;
      return start && end ? { date, start, end } : null;
    }).filter(Boolean);

    if (!dayTimes.length) return previewTimes.textContent = "Event times: Not set";

    // Group consecutive days with same times
    const groups = [];
    let current = [dayTimes[0]];
    for (let i = 1; i < dayTimes.length; i++) {
      const prev = dayTimes[i - 1], curr = dayTimes[i];
      if (curr.start === prev.start && curr.end === prev.end) current.push(curr);
      else { groups.push(current); current = [curr]; }
    }
    groups.push(current);

    previewTimes.innerHTML = groups.map(g => {
      if (g.length === 1) return `${g[0].date}: ${g[0].start} → ${g[0].end}`;
      return `${g[0].date} to ${g[g.length - 1].date}: ${g[0].start} → ${g[0].end}`;
    }).join("<br>");
  });

  // Price preview
  // Helper
  function daysUntil(date) {
    const today = new Date();
    const diff = date.getTime() - today.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  }

  // Price preview when dates are selected
  document.addEventListener("rentalDatesSelected", (e) => {
    const [start, end] = e.detail;

    function formatLocal(d) {
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      return `${y}-${m}-${day}`;
    }

    const startStr = formatLocal(start);
    const endStr = formatLocal(end);

    fetch(`/booking/calculate_price/?start=${startStr}&end=${endStr}`)
      .then(res => res.json())
      .then(data => {
        if (!isNaN(data.price)) {
          basePrice = parseFloat(data.price);
          const total = basePrice - discountAmount;

          basePriceEl.textContent = basePrice.toFixed(0);
          totalPriceEl.textContent = total.toFixed(0);

          // 💡 Calculate payment stages
          const paymentBreakdownEl = document.getElementById("payment-breakdown");
          if (!paymentBreakdownEl) return;

          paymentBreakdownEl.innerHTML = ""; // Clear previous output

          const days = daysUntil(start);

          if (days > 14) {
            const initial = total * 0.5;
            const final = total - initial;

            paymentBreakdownEl.innerHTML = `
              <p><strong>Initial Payment (50%):</strong> ${initial.toFixed(0)} SEK</p>
              <p><strong>Final Payment:</strong> ${final.toFixed(0)} SEK</p>
              <small class="text-muted">If your booking is within 14 days, the full amount must be paid immediately. More information will be in your contract sent to your email.</small>
            `;
          } else {
            paymentBreakdownEl.innerHTML = `
              <p><strong>Full Payment:</strong> ${total.toFixed(0)} SEK</p>
              <small class="text-muted">Full amount is due immediately for bookings within 14 days. More information will be in your contract sent to your email.</small>
            `;
          }

        } else {
          basePriceEl.textContent = data.price;
          totalPriceEl.textContent = data.price;
          initialPaymentEl.textContent = "0";
          finalPaymentEl.textContent = "0";
        }
      })
      .catch(err => console.error("Price fetch error:", err));
  });

  // Coupon apply button
  applyBtn.addEventListener("click", function() {
    const code = couponInput.value.trim();
    if (!code) return;

    fetch(`/booking/validate_coupon/?code=${code}&base_price=${basePrice}`)
      .then(res => res.json())
      .then(data => {
        if (data.valid) {
          if (data.type === "percent" || data.type === "percentage") {
            discountAmount = basePrice * (Number(data.value) / 100);
            discountEl.textContent = `${Number(data.value)}%`;
          } else {
            discountAmount = Number(data.value);
            discountEl.textContent = `${discountAmount.toFixed(0)} SEK`;
          }

          const total = basePrice - discountAmount;
          totalPriceEl.textContent = total.toFixed(0);

          // 💡 Recalculate payments after coupon
          const rentalStart = document.getElementById("rental_start").value;
          if (rentalStart) {
            const start = new Date(rentalStart);
            const days = daysUntil(start);

            if (days > 14) {
              const initial = total * 0.5;
              const final = total - initial;
              initialPaymentEl.textContent = initial.toFixed(0);
              finalPaymentEl.textContent = final.toFixed(0);
            } else {
              initialPaymentEl.textContent = total.toFixed(0);
              finalPaymentEl.textContent = "0";
            }
          }

          feedbackEl.textContent = "Coupon applied!";
          feedbackEl.classList.remove("text-danger");
          feedbackEl.classList.add("text-success");
        } else {
          discountAmount = 0;
          discountEl.textContent = "0 SEK";
          totalPriceEl.textContent = basePrice.toFixed(0);
          feedbackEl.textContent = "Invalid coupon code";
          feedbackEl.classList.remove("text-success");
          feedbackEl.classList.add("text-danger");
        }
      })
      .catch(err => {
        console.error("Coupon validation error:", err);
        feedbackEl.textContent = "Error validating coupon";
      });
  });
});