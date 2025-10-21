document.addEventListener("DOMContentLoaded", () => {
  const titleInput = document.getElementById("event-title");
  const descriptionInput = document.getElementById("event-description");
  const previewTitle = document.getElementById("preview-title");
  const previewDescription = document.getElementById("preview-description");
  const previewTimes = document.getElementById("preview-times");

  // --- Elements ---
  const bgColorInput = document.getElementById("event-bg-color"); // hidden input
  const bgBlurCheckbox = document.getElementById("checkDefault");
  const previewBlur = document.getElementById("preview-background-blur");  
  const previewBackground = document.getElementById("preview-background");

  // Color palette + brightness
  const colorSwatches = document.querySelectorAll(".color-swatch");
  const brightnessRange = document.getElementById("brightness-range");

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

  // --- Utility: adjust brightness ---
  function adjustBrightness(hex, percent) {
    const num = parseInt(hex.slice(1), 16);
    let r = (num >> 16) + (255 * (percent / 100 - 1));
    let g = ((num >> 8) & 0x00FF) + (255 * (percent / 100 - 1));
    let b = (num & 0x0000FF) + (255 * (percent / 100 - 1));
    r = Math.min(255, Math.max(0, r));
    g = Math.min(255, Math.max(0, g));
    b = Math.min(255, Math.max(0, b));
    return `#${(1 << 24 | (r << 16) | (g << 8) | b).toString(16).slice(1)}`;
  }

  // Default selected color
  let selectedColor = bgColorInput?.value || "#f5f5f5";

  // --- Text preview ---
  titleInput.addEventListener("input", () => {
    previewTitle.textContent = titleInput.value || "Event Title";
    validateForm();
  });

  descriptionInput.addEventListener("input", () => {
    previewDescription.textContent = descriptionInput.value || "Event description will appear here.";
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

  // --- Color swatch click handler ---
  if (colorSwatches.length) {
    colorSwatches.forEach(btn => {
      btn.addEventListener("click", () => {
        colorSwatches.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        selectedColor = btn.getAttribute("data-color");
        const brightness = brightnessRange ? brightnessRange.value : 100;
        const adjusted = adjustBrightness(selectedColor, brightness);

        bgColorInput.value = adjusted;
        previewBackground.style.backgroundColor = adjusted;
      });
    });
  }

  // --- Brightness range change ---
  if (brightnessRange) {
    brightnessRange.addEventListener("input", () => {
      const adjusted = adjustBrightness(selectedColor, brightnessRange.value);
      bgColorInput.value = adjusted;
      previewBackground.style.backgroundColor = adjusted;
    });
  }

  // --- Blur toggle ---
  bgBlurCheckbox.addEventListener("change", () => {
    previewBlur.style.backdropFilter = bgBlurCheckbox.checked ? "blur(6px)" : "none";
  });

  // --- Background image upload preview ---
  const bgImageInput = document.getElementById("event-bg-image"); // file input
  if (bgImageInput) {
    bgImageInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        const url = URL.createObjectURL(file);
        previewBlur.style.backgroundImage = `url(${url})`;
        previewBlur.style.backgroundColor = bgColorInput.value || "#f5f5f5"; // fallback
      } else {
        previewBackground.style.backgroundImage = "";
        previewBackground.style.backgroundColor = bgColorInput.value || "#f5f5f5";
      }
    });
  }

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
