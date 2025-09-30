document.addEventListener("DOMContentLoaded", function () {
  // --- Elements ---
  const rentalInput = document.getElementById("rental-range");
  const rentalStartInput = document.getElementById("rental_start");
  const rentalEndInput = document.getElementById("rental_end");
  const stage2 = document.getElementById("stage2");

  const eventDaysInput = document.getElementById("event-days");
  const eventStartTime = document.getElementById("event-start-time");
  const eventEndTime = document.getElementById("event-end-time");
  const titleInput = document.getElementById("event-title");
  const descriptionInput = document.getElementById("event-description");
  const finishBtn = document.getElementById("finishBtn");

  const bgColorInput = document.getElementById("event-bg-color");
  const bgImageInput = document.getElementById("event-bg-image");
  const bgBlurCheckbox = document.getElementById("checkDefault");
  const bgBlurBox = document.getElementById("preview-section");

  const previewBackground = document.getElementById("preview-background");
  const previewTitle = document.getElementById("preview-title");
  const previewDescription = document.getElementById("preview-description");
  const previewImages = document.getElementById("preview-images");
  const previewTimes = document.getElementById("preview-times");

  // --- Stage 2 is blocked by default ---
  stage2.classList.remove("active"); // make sure it's disabled

  // --- Stage 1: Rental range ---
fetch(bookedDatesUrl)
  .then(response => response.json())
  .then(bookings => {
    // Convert bookings into Flatpickr disable format
    const disabledRanges = bookings.map(b => {
      return { from: b.start, to: b.end || b.start };
    });

    // Flatten all booked days into an array of strings YYYY-MM-DD
    const bookedDates = [];
    bookings.forEach(b => {
      const start = new Date(b.start);
      const end = new Date(b.end || b.start);
      let current = new Date(start);
      while (current <= end) {
        bookedDates.push(current.toISOString().split("T")[0]);
        current.setDate(current.getDate() + 1);
      }
    });

    flatpickr(rentalInput, {
      mode: "range",
      dateFormat: "Y-m-d",
      minDate: "today",
      appendTo: document.body,
      disable: disabledRanges, // not clickable

      // Add a CSS class for booked days
      onDayCreate: function(dObj, dStr, fp, dayElem) {
        const date = dayElem.dateObj.toISOString().split("T")[0];
        if (bookedDates.includes(date)) {
          dayElem.classList.add("booked-day");
        }
      },

      onClose: function(selectedDates) {
        if (selectedDates.length === 2) {
          const startDate = selectedDates[0];
          const endDate   = selectedDates[1];

          const formatLocal = (d) => {
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, "0");
            const day = String(d.getDate()).padStart(2, "0");
            return `${year}-${month}-${day}`;
          };

          rentalStartInput.value = formatLocal(startDate);
          rentalEndInput.value   = formatLocal(endDate);

          stage2.classList.add("active");
          initEventDays(startDate, endDate);
        }
      }
    });
  });




  // --- Stage 2: Event days ---
  function initEventDays(start, end) {
    flatpickr(eventDaysInput, {
      mode: "range",
      dateFormat: "Y-m-d",
      minDate: start, // Date object
      maxDate: end,   // Date object
      appendTo: document.body,
      onClose: function(selectedDates) {
        if (selectedDates.length === 2) {
          createTimeInputs();   // ✅ now the inputs get created
          validateForm();       // keep form validation in sync
        }
      }
    });
  }

  function getEventDays() {
    if (!eventDaysInput.value) return [];
    const [startStr, endStr] = eventDaysInput.value.split(" to ");
    const start = new Date(startStr);
    const end = new Date(endStr);

    const dates = [];
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      dates.push(new Date(d));
    }
    return dates;
  }

  function createTimeInputs() {
  const container = document.getElementById("per-day-times");
  if (!container) return;
  container.innerHTML = ""; // clear old inputs

  const dates = getEventDays();
  dates.forEach(date => {
    const dateStr = date.toISOString().split("T")[0];

    const row = document.createElement("div");
    row.classList.add("row", "mb-2");

    const dayLabel = document.createElement("div");
    dayLabel.classList.add("col-12", "fw-bold", "mb-1");
    dayLabel.textContent = dateStr;
    row.appendChild(dayLabel);

    const startCol = document.createElement("div");
    startCol.classList.add("col");
    const startInput = document.createElement("input");
    startInput.type = "text"; 
    startInput.classList.add("form-control", "per-day-start");

    // hidden input for submission
    const hiddenStart = document.createElement("input");
    hiddenStart.type = "hidden";
    hiddenStart.name = `start_time_${dateStr}`;
    startCol.appendChild(startInput);
    startCol.appendChild(hiddenStart);

    const endCol = document.createElement("div");
    endCol.classList.add("col");
    const endInput = document.createElement("input");
    endInput.type = "text";
    endInput.classList.add("form-control", "per-day-end");

    // hidden input for submission
    const hiddenEnd = document.createElement("input");
    hiddenEnd.type = "hidden";
    hiddenEnd.name = `end_time_${dateStr}`;
    endCol.appendChild(endInput);
    endCol.appendChild(hiddenEnd);

    row.appendChild(startCol);
    row.appendChild(endCol);
    container.appendChild(row);

    // flatpickr init
    flatpickr(startInput, {
      enableTime: true,
      noCalendar: true,
      dateFormat: "H:i",
      time_24hr: true,
      minuteIncrement: 15,
      onChange: (selectedDates, dateStr) => {
        hiddenStart.value = dateStr;  // ✅ sync hidden input
        validateForm();
        updateTimesPreview();
      }
    });

    flatpickr(endInput, {
      enableTime: true,
      noCalendar: true,
      dateFormat: "H:i",
      time_24hr: true,
      minuteIncrement: 15,
      onChange: (selectedDates, dateStr) => {
        hiddenEnd.value = dateStr;  // ✅ sync hidden input
        validateForm();
        updateTimesPreview();
      }
    });
  });

  updateTimesPreview();
}

  // --- Form Validation ---
  function validateForm() {
  const dates = getEventDays();
  let allTimesFilled = true;

  dates.forEach(date => {
    const dateStr = date.toISOString().split("T")[0];
    const start = document.querySelector(`[name="start_time_${dateStr}"]`);
    const end = document.querySelector(`[name="end_time_${dateStr}"]`);
    if (!start || !end || !start.value || !end.value) {
      allTimesFilled = false;
    }
  });

  if (
    eventDaysInput.value &&
    allTimesFilled &&
    titleInput.value.trim() &&
    descriptionInput.value.trim() &&
    document.querySelectorAll('input[name="uploaded_images"]').length > 0
  ) {
    finishBtn.disabled = false;
    console.log("Form is valid, you can submit now.");
  } else {
    finishBtn.disabled = true;
    console.log("Form is incomplete, cannot submit yet.");
  }
}



var myWidget = cloudinary.createUploadWidget(
  {
    cloudName: "dcbvjzagi",
    uploadPreset: "GalleriVretinger",
    folder: "users/{{ user.username }}/events/temp",
    multiple: true,
    maxFiles: 10,
  },
  (error, result) => {
    if (!error && result && result.event === "success") {
      console.log("Upload successful:", result.info);

      const container = document.getElementById("preview-images");

      // wrapper div
      const wrapper = document.createElement("div");
      wrapper.style.position = "relative";
      wrapper.style.display = "inline-block";
      wrapper.style.margin = "5px";

      // preview image
      const img = document.createElement("img");
      img.src = result.info.secure_url;
      img.style.maxWidth = "150px";
      img.style.borderRadius = "6px";
      img.style.boxShadow = "0 2px 5px rgba(0,0,0,0.2)";

      // hidden input for Django
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = "uploaded_images";
      input.value = result.info.public_id;
      document.querySelector("form").appendChild(input);

      // remove button
      const removeBtn = document.createElement("button");
      removeBtn.textContent = "×";
      removeBtn.type = "button";
      removeBtn.style.position = "absolute";
      removeBtn.style.top = "2px";
      removeBtn.style.right = "2px";
      removeBtn.style.background = "rgba(0,0,0,0.6)";
      removeBtn.style.color = "white";
      removeBtn.style.border = "none";
      removeBtn.style.borderRadius = "50%";
      removeBtn.style.width = "22px";
      removeBtn.style.height = "22px";
      removeBtn.style.cursor = "pointer";
      removeBtn.style.lineHeight = "18px";
      removeBtn.style.fontSize = "16px";

      // remove handler → also delete from Cloudinary
      removeBtn.addEventListener("click", () => {
        fetch("/delete_uploaded_image/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ public_id: result.info.public_id }),
        }).then(res => res.json()).then(data => {
          console.log("Cloudinary delete:", data);
        });

        wrapper.remove();
      });

      // assemble
      wrapper.appendChild(img);
      wrapper.appendChild(removeBtn);
      wrapper.appendChild(input);
      container.appendChild(wrapper);

      validateForm();
    }
});

document.getElementById("upload_widget").addEventListener("click", function () {
  myWidget.open();
}, false);


// --- Background image upload via Cloudinary ---
const bgUploadBtn = document.getElementById("bg-upload-btn"); // create a new button in your template
const bgInput = document.getElementById("event-bg-image-hidden"); // hidden input to store public_id
const bgPreview = document.getElementById("preview-background-blur");

// Cloudinary background upload
bgUploadBtn.addEventListener("click", function () {
  bgWidget.open();
});

// Cloudinary widget for background image (single upload)
var bgWidget = cloudinary.createUploadWidget(
  {
    cloudName: "dcbvjzagi",
    uploadPreset: "GalleriVretinger",
    folder: "users/{{ user.username }}/events/bg",
    multiple: false, // only one image allowed
  },
  (error, result) => {
    if (!error && result && result.event === "success") {
      console.log("Background upload successful:", result.info);

      // Set background image in the preview layer
      const bg = document.getElementById("preview-background-blur");
      bg.style.backgroundImage = `url(${result.info.secure_url})`;
      bg.style.backgroundSize = "cover";
      bg.style.backgroundPosition = "center";

      // Optional: store public_id in hidden input for form submission
      let input = document.querySelector('input[name="bg_image_uploaded"]');
      if (!input) {
        input = document.createElement("input");
        input.type = "hidden";
        input.name = "bg_image_uploaded";
        document.querySelector("form").appendChild(input);
      }
      input.value = result.info.public_id;
    }
  }
);

// Blur toggle
bgBlurCheckbox.addEventListener("change", () => {
  if (bgBlurCheckbox.checked) {
    bgPreview.style.filter = "blur(4px)";
  } else {
    bgPreview.style.filter = "none";
  }
});

// --- Open widget on button click ---
bgUploadBtn.addEventListener("click", function () {
  bgWidget.open();
}, false);

// Helper to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// --- TITLE + DESCRIPTION LIVE PREVIEW ---
titleInput.addEventListener("input", function () {
  const value = this.value.trim();
  previewTitle.textContent = value || "Event Title";
  validateForm();
});

descriptionInput.addEventListener("input", function () {
  const value = this.value.trim();
  previewDescription.textContent =
    value || "Event description will appear here.";
  validateForm();
});

function updateTimesPreview() {
  const container = document.getElementById("per-day-times");
  if (!container) {
    previewTimes.textContent = "Event times: Not set";
    return;
  }

  const rowNodes = container.querySelectorAll(".row");
  const dayTimes = [];

  rowNodes.forEach(row => {
    // date label we put in .fw-bold
    const dateLabelEl = row.querySelector(".fw-bold");
    if (!dateLabelEl) return;
    const date = dateLabelEl.textContent.trim();

    const startInput = row.querySelector("input.per-day-start");
    const endInput = row.querySelector("input.per-day-end");
    const start = startInput ? startInput.value.trim() : "";
    const end = endInput ? endInput.value.trim() : "";

    if (start && end) {
      dayTimes.push({ date, start, end });
    }
  });

  if (!dayTimes.length) {
    previewTimes.textContent = "Event times: Not set";
    return;
  }

    // Group consecutive days that have identical times
    const groups = [];
    let currentGroup = [dayTimes[0]];

    for (let i = 1; i < dayTimes.length; i++) {
      const prev = dayTimes[i - 1];
      const curr = dayTimes[i];
      if (curr.start === prev.start && curr.end === prev.end) {
        currentGroup.push(curr);
      } else {
        groups.push(currentGroup);
        currentGroup = [curr];
      }
    }
    groups.push(currentGroup);

    // Build display strings; use <br> so browser shows new lines
    const parts = groups.map(group => {
      if (group.length === 1) {
        return `${group[0].date}: ${group[0].start} → ${group[0].end}`;
      } else {
        return `${group[0].date} to ${group[group.length - 1].date}: ${group[0].start} → ${group[0].end}`;
      }
    });

    // Use innerHTML to keep the line breaks (or set textContent with \n if you prefer)
    previewTimes.innerHTML = parts.join("<br>");
  }


  // --- Background customization ---
  bgColorInput.addEventListener("input", () => {
    previewBackground.style.backgroundImage = "none";
    previewBackground.style.backgroundColor = bgColorInput.value;
  });
});
