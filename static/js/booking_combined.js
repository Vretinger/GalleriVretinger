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
  const image1Input = document.getElementById("event-image1");
  const addImageBtn = document.getElementById("addImageBtn");
  const extraImagesContainer = document.getElementById("extra-images-container");
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
  flatpickr(rentalInput, {
  mode: "range",
  dateFormat: "Y-m-d",
  minDate: "today",
  appendTo: document.body,
  onClose: function(selectedDates) {
    if (selectedDates.length === 2) {
      const startDate = selectedDates[0];
      const endDate   = selectedDates[1];

      // Store hidden inputs as YYYY-MM-DD (local time)
      const formatLocal = (d) => {
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, "0");
        const day = String(d.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
      };

      rentalStartInput.value = formatLocal(startDate);
      rentalEndInput.value   = formatLocal(endDate);

      // Activate Stage 2
      stage2.classList.add("active");

      // Initialize Stage 2 with actual Date objects
      initEventDays(startDate, endDate);
    }
  }
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
    startInput.type = "time";
    startInput.name = `start_time_${dateStr}`;
    startInput.classList.add("form-control", "per-day-start");
    startCol.appendChild(startInput);
    startInput.step = 900;   // 15-minute intervals
    startInput.min = "06:00"; // optional
    startInput.max = "23:45"; // optional

    const endCol = document.createElement("div");
    endCol.classList.add("col");
    const endInput = document.createElement("input");
    endInput.type = "time";
    endInput.name = `end_time_${dateStr}`;
    endInput.classList.add("form-control", "per-day-end");
    endCol.appendChild(endInput);
    endInput.step = 900;
    endInput.min = "06:00"; // optional
    endInput.max = "23:59"; // optional

    row.appendChild(startCol);
    row.appendChild(endCol);
    container.appendChild(row);

    // Validation + preview update
    startInput.addEventListener("input", () => {
      validateForm();
      updateTimesPreview();
    });
    endInput.addEventListener("input", () => {
      validateForm();
      updateTimesPreview();
    });
  });

  // Update preview right away
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
    if (!start.value || !end.value) {
      allTimesFilled = false;
    }
  });

  if (
    eventDaysInput.value &&
    allTimesFilled &&
    titleInput.value &&
    descriptionInput.value &&
    image1Input.files.length > 0
  ) {
    finishBtn.disabled = false;
  } else {
    finishBtn.disabled = true;
  }
}


[eventDaysInput, eventStartTime, eventEndTime, titleInput, descriptionInput].forEach(el => {
  el.addEventListener("input", validateForm);
});

// --- Event images ---
function handleEventImage(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function (ev) {
    const wrapper = document.createElement("div");
    wrapper.style.position = "relative";
    wrapper.style.display = "inline-block";

    const img = document.createElement("img");
    img.src = ev.target.result;
    img.style.maxWidth = "150px";
    img.style.margin = "6px";
    img.style.borderRadius = "6px";
    img.style.boxShadow = "0 2px 5px rgba(0,0,0,0.2)";

    const removeBtn = document.createElement("button");
    removeBtn.textContent = "×";
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
    removeBtn.addEventListener("click", () => {
      wrapper.remove();
      input.value = ""; // clear input so same file can be reselected
      validateForm();
    });

    wrapper.appendChild(img);
    wrapper.appendChild(removeBtn);
    previewImages.appendChild(wrapper);
  };
  reader.readAsDataURL(file);
}

image1Input.addEventListener("change", function () {
  handleEventImage(this);
  validateForm();
});

addImageBtn.addEventListener("click", () => {
  const newInput = document.createElement("input");
  newInput.type = "file";
  newInput.classList.add("form-control", "mb-2");
  newInput.addEventListener("change", function () {
    handleEventImage(this);
  });
  extraImagesContainer.appendChild(newInput);
});

// --- Preview updates ---
titleInput.addEventListener("input", () => {
  previewTitle.textContent = titleInput.value || "Event Title";
});

descriptionInput.addEventListener("input", () => {
  previewDescription.textContent = descriptionInput.value || "Event description will appear here.";
});

function updateTimesPreview() {
  const container = document.getElementById("per-day-times");
  const rows = container.querySelectorAll(".row");

  if (!rows.length) {
    previewTimes.textContent = "Event times: Not set";
    return;
  }

  const dayTimes = [];
  rows.forEach(row => {
    const date = row.querySelector("div").textContent; // first col has date label
    const start = row.querySelector("input[type='time']").value;
    const end = row.querySelectorAll("input[type='time']")[1].value;
    if (start && end) {
      dayTimes.push({ date, start, end });
    }
  });

  if (!dayTimes.length) {
    previewTimes.textContent = "Event times: Not set";
    return;
  }

  // Group consecutive days with identical times
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

  // Format output
  const parts = groups.map(group => {
    if (group.length === 1) {
      return `${group[0].date}: ${group[0].start} → ${group[0].end}`;
    } else {
      return `${group[0].date} to ${group[group.length - 1].date}: ${group[0].start} → ${group[0].end}`;
    }
  });

  previewTimes.textContent = parts.join("\n");
}


// --- Background customization ---
bgColorInput.addEventListener("input", () => {
  previewBackground.style.backgroundImage = "none";
  previewBackground.style.backgroundColor = bgColorInput.value;
});

bgImageInput.addEventListener("change", () => {
  if (bgImageInput.files.length > 0) {
    const file = bgImageInput.files[0];
    const reader = new FileReader();
    reader.onload = e => {
      previewBackground.style.backgroundImage = `url(${e.target.result})`;
      previewBackground.style.backgroundSize = "cover";
      previewBackground.style.backgroundPosition = "center";
    };
    reader.readAsDataURL(file);
  }
});

bgBlurCheckbox.addEventListener("change", () => {
  if (bgBlurCheckbox.checked) {
    bgBlurBox.style.filter = "blur(4px)";
  } else {
    bgBlurBox.style.filter = "none";
  }
});
});
