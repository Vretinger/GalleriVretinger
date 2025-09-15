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

  const previewTitle = document.getElementById("preview-title");
  const previewDescription = document.getElementById("preview-description");
  const previewImages = document.getElementById("preview-images");

  // --- Stage 1: Rental range ---
  flatpickr(rentalInput, {
    mode: "range",
    dateFormat: "Y-m-d",
    minDate: "today",
    onClose: function(selectedDates) {
      if (selectedDates.length === 2) {
        rentalStartInput.value = selectedDates[0].toISOString().split("T")[0];
        rentalEndInput.value = selectedDates[1].toISOString().split("T")[0];

        // Activate stage 2
        stage2.classList.add("active");

        // Initialize Stage 2 event days
        initEventDays(rentalStartInput.value, rentalEndInput.value);
      }
    }
  });

  // --- Stage 2: Event days ---
  function initEventDays(start, end) {
    flatpickr(eventDaysInput, {
      mode: "range",
      dateFormat: "Y-m-d",
      minDate: start,
      maxDate: end,
      onClose: validateForm
    });
  }

  // --- Form Validation ---
  function validateForm() {
    if (
      eventDaysInput.value &&
      eventStartTime.value &&
      eventEndTime.value &&
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

  // --- Image Preview ---
  function updateImages() {
    previewImages.innerHTML = "";
    document.querySelectorAll("input[type='file']").forEach(input => {
      if (input.files.length > 0) {
        const file = input.files[0];
        const reader = new FileReader();
        reader.onload = e => {
          const img = document.createElement("img");
          img.src = e.target.result;
          img.style.maxWidth = "150px";
          img.classList.add("mb-2", "rounded");
          previewImages.appendChild(img);
        };
        reader.readAsDataURL(file);
      }
    });
    validateForm();
  }

  image1Input.addEventListener("change", updateImages);
  addImageBtn.addEventListener("click", () => {
    const newInput = document.createElement("input");
    newInput.type = "file";
    newInput.name = "extra_images";
    newInput.classList.add("form-control", "mb-2");
    newInput.addEventListener("change", updateImages);
    extraImagesContainer.appendChild(newInput);
  });

  // --- Preview title & description ---
  titleInput.addEventListener("input", () => {
    previewTitle.textContent = titleInput.value || "Event Title";
  });
  descriptionInput.addEventListener("input", () => {
    previewDescription.textContent = descriptionInput.value || "Event description will appear here.";
  });

  // --- Preview event times ---
  function updateTimesPreview() {
    const start = eventStartTime.value;
    const end = eventEndTime.value;
    const timesText = start || end ? `Event times: ${start || "??"} → ${end || "??"}` : "Event times: Not set";
    document.getElementById("preview-times").textContent = timesText;
  }
  [eventStartTime, eventEndTime].forEach(el => el.addEventListener("input", updateTimesPreview));
});
