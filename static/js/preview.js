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
});
