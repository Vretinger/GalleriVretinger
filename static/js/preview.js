// preview.js
document.addEventListener("DOMContentLoaded", () => {
  const titleInput = document.getElementById("event-title");
  const descriptionInput = document.getElementById("event-description");
  const previewTitle = document.getElementById("preview-title");
  const previewDescription = document.getElementById("preview-description");
  const previewTimes = document.getElementById("preview-times");

  titleInput.addEventListener("input", () => { previewTitle.textContent = titleInput.value || "Event Title"; validateForm(); });
  descriptionInput.addEventListener("input", () => { previewDescription.textContent = descriptionInput.value || "Event description will appear here."; validateForm(); });

  document.addEventListener("updateTimesPreview", () => {
    const container = document.getElementById("per-day-times");
    if (!container) return previewTimes.textContent="Event times: Not set";

    const rows = container.querySelectorAll(".row");
    const dayTimes = Array.from(rows).map(row => {
      const date = row.querySelector(".fw-bold").textContent;
      const start = row.querySelector(".per-day-start").value;
      const end = row.querySelector(".per-day-end").value;
      return start && end ? { date, start, end } : null;
    }).filter(Boolean);

    if (!dayTimes.length) return previewTimes.textContent="Event times: Not set";

    const groups = [];
    let current = [dayTimes[0]];
    for (let i=1;i<dayTimes.length;i++){
      const prev=dayTimes[i-1], curr=dayTimes[i];
      if (curr.start===prev.start && curr.end===prev.end) current.push(curr);
      else { groups.push(current); current=[curr]; }
    }
    groups.push(current);

    previewTimes.innerHTML = groups.map(g=>{
      if(g.length===1) return `${g[0].date}: ${g[0].start} → ${g[0].end}`;
      return `${g[0].date} to ${g[g.length-1].date}: ${g[0].start} → ${g[0].end}`;
    }).join("<br>");
  });
});
