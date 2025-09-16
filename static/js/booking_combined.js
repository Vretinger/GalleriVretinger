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
    appendTo: document.body, // ensures calendar is always on top
    onClose: function(selectedDates) {
      if (selectedDates.length === 2) {
        rentalStartInput.value = selectedDates[0].toISOString().split("T")[0];
        rentalEndInput.value = selectedDates[1].toISOString().split("T")[0];

        // Activate Stage 2
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
      appendTo: document.body, // ensures calendar is always on top
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
    const start = eventStartTime.value;
    const end = eventEndTime.value;
    const timesText = start || end ? `Event times: ${start || "??"} → ${end || "??"}` : "Event times: Not set";
    previewTimes.textContent = timesText;
  }
  [eventStartTime, eventEndTime].forEach(el => el.addEventListener("input", updateTimesPreview));

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
