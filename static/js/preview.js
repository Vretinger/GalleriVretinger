document.addEventListener("DOMContentLoaded", () => {
  const titleInput = document.getElementById("event-title");
  const descriptionInput = document.getElementById("event-description");
  const previewTitle = document.getElementById("preview-title");
  const previewDescription = document.getElementById("preview-description");
  const previewTimes = document.getElementById("preview-times");

    // --- Elements ---
  const bgColorInput = document.getElementById("event-bg-color");
  const bgBlurCheckbox = document.getElementById("checkDefault");
  const previewBackground = document.getElementById("preview-background-blur");
  const previewBlur = document.getElementById("preview-background-blur");  


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
    for (let i=1;i<dayTimes.length;i++){
      const prev = dayTimes[i-1], curr = dayTimes[i];
      if (curr.start===prev.start && curr.end===prev.end) current.push(curr);
      else { groups.push(current); current=[curr]; }
    }
    groups.push(current);

    previewTimes.innerHTML = groups.map(g=>{
      if(g.length===1) return `${g[0].date}: ${g[0].start} → ${g[0].end}`;
      return `${g[0].date} to ${g[g.length-1].date}: ${g[0].start} → ${g[0].end}`;
    }).join("<br>");
  });

  // --- Update background color live ---
  bgColorInput.addEventListener("input", () => {
    // Apply color to blur overlay (so it blends if image exists)
    previewBlur.style.backgroundColor = bgColorInput.value;
  });
  // --- Blur toggle ---
  bgBlurCheckbox.addEventListener("change", () => {
    previewBlur.style.filter = bgBlurCheckbox.checked ? "blur(4px)" : "none";
  });
  // Optional: if you want to also dynamically show a background image
  const bgImageInput = document.getElementById("event-bg-image"); // file input
  if (bgImageInput) {
    bgImageInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        const url = URL.createObjectURL(file);
        previewBlur.style.backgroundImage = `url(${url})`;
        previewBlur.style.backgroundSize = "fit";
        previewBlur.style.backgroundPosition = "center";
      }
    });
  }
});