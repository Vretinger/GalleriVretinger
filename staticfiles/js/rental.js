// rental.js
document.addEventListener("DOMContentLoaded", function () {
  const rentalInput = document.getElementById("rental-range");
  const rentalStartInput = document.getElementById("rental_start");
  const rentalEndInput = document.getElementById("rental_end");
  const stage2 = document.getElementById("stage2");


  // Hide max attendees if drop-in is checked
  const isDropInCheckbox = document.getElementById("is_drop_in");
  const maxAttendeesWrapper = document.getElementById("maxAttendeesWrapper");

  function toggleMaxAttendees() {
    maxAttendeesWrapper.style.display = isDropInCheckbox.checked ? "none" : "block";
  }

  isDropInCheckbox.addEventListener("change", toggleMaxAttendees);
  toggleMaxAttendees();


  fetch(bookedDatesUrl)
    .then(response => response.json())
    .then(bookings => {
      const disabledRanges = bookings.map(b => ({ from: b.start, to: b.end || b.start }));
      const bookedDates = [];
      bookings.forEach(b => {
        const start = new Date(b.start), end = new Date(b.end || b.start);
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
          const y = d.getFullYear(), m = String(d.getMonth() + 1).padStart(2, "0"), day = String(d.getDate()).padStart(2, "0");
          bookedDates.push(`${y}-${m}-${day}`);
        }
      });

      flatpickr(rentalInput, {
        mode: "range",
        dateFormat: "Y-m-d",
        minDate: "today",
        appendTo: document.body,
        disable: disabledRanges,
        locale: "{{ LANGUAGE_CODE }}",
        onDayCreate: (dObj, dStr, fp, dayElem) => {
          const y = dayElem.dateObj.getFullYear(), m = String(dayElem.dateObj.getMonth() + 1).padStart(2, "0"), d = String(dayElem.dateObj.getDate()).padStart(2, "0");
          if (bookedDates.includes(`${y}-${m}-${d}`)) dayElem.classList.add("booked-day");
        },
        onClose: (selectedDates) => {
          if (selectedDates.length === 2) {
            rentalStartInput.value = formatDate(selectedDates[0]);
            rentalEndInput.value = formatDate(selectedDates[1]);
            stage2.classList.add("active");
            document.dispatchEvent(new CustomEvent("rentalDatesSelected", { detail: selectedDates }));
          }
        }
      });

      function formatDate(d) {
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
      }
    });
});
