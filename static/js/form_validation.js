function validateForm() {
  let valid = true;
  let errors = [];

  // Check rental start/end
  const startDate = document.getElementById("rental_start").value;
  const endDate = document.getElementById("rental_end").value;
  if (!startDate || !endDate) {
    valid = false;
    errors.push("Please select rental dates.");
  }

  const event_days = document.getElementById("event-days")?.value;
  if (!event_days) {
    valid = false;
    errors.push("Please select event days.");
 }


  // Check event title
  const title = document.getElementById("event-title")?.value.trim();
  if (!title) {
    valid = false;
    errors.push("Please enter an event title.");
  }

  // Check event title
  const description = document.getElementById("event-ShortDescription")?.value.trim();
  if (!description) {
    valid = false;
    errors.push("Please enter an short event description.");
  }

  // Check per-day times
  const timeInputs = document.querySelectorAll("input[name^='start_time_'], input[name^='end_time_']");
  for (let input of timeInputs) {
    if (!input.value) {
      valid = false;
      errors.push("Please fill all start and end times.");
      break;
    }
  }

  // Show errors
  const errorBox = document.getElementById("form-errors");
  if (errorBox) {
    errorBox.innerHTML = errors.map(e => `<div class="alert alert-danger">${e}</div>`).join("");
  }

  // Enable/disable submit button
  const finishBtn = document.getElementById("finishBtn");
  if (finishBtn) finishBtn.disabled = !valid;

  return valid;
}

// Attach validation on form submit
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", (e) => {
      if (!validateForm()) {
        e.preventDefault(); // stop submission
        window.scrollTo({ top: 0, behavior: "smooth" }); // scroll to errors
      }
    });
  }
});
