document.addEventListener("DOMContentLoaded", function() {
  const discountInput = document.getElementById("discount_code");
  const feedback = document.getElementById("coupon-feedback");
  const totalEl = document.getElementById("total-price");
  const discountEl = document.getElementById("discount-amount");
  const newPriceEl = document.getElementById("new-price");

  if (!discountInput) return;  // Exit if element not present

  function updateCoupon() {
    const code = discountInput.value.trim();
    const start_date = document.getElementById("rental_start").value;
    const end_date = document.getElementById("rental_end").value;

    if (!code) {
      feedback.textContent = "";
      totalEl.textContent = "0 SEK";
      discountEl.textContent = "0 SEK";
      newPriceEl.textContent = "0 SEK";
      return;
    }

    fetch(`/validate-coupon/?code=${encodeURIComponent(code)}&start_date=${start_date}&end_date=${end_date}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          feedback.textContent = "Coupon applied!";
          feedback.classList.remove("text-danger");
          feedback.classList.add("text-success");

          totalEl.textContent = `${data.original_price.toFixed(2)} SEK`;
          discountEl.textContent = `- ${data.discount_amount.toFixed(2)} SEK`;
          newPriceEl.textContent = `${data.new_total.toFixed(2)} SEK`;
        } else {
          feedback.textContent = data.error;
          feedback.classList.remove("text-success");
          feedback.classList.add("text-danger");

          totalEl.textContent = "0 SEK";
          discountEl.textContent = "0 SEK";
          newPriceEl.textContent = "0 SEK";
        }
      })
      .catch(err => {
        console.error("Error validating coupon:", err);
      });
  }

  discountInput.addEventListener("input", updateCoupon);
  document.getElementById("rental_start").addEventListener("change", updateCoupon);
  document.getElementById("rental_end").addEventListener("change", updateCoupon);
});
