document.addEventListener("rentalDatesSelected", (e) => {
  const [startDate, endDate] = e.detail;
  const eventDaysInput = document.getElementById("event-days");
  const container = document.getElementById("per-day-times");

  if (!eventDaysInput || !container) return;

  // Initialize flatpickr for date range (or single day)
  flatpickr(eventDaysInput, {
    mode: "range",
    dateFormat: "Y-m-d",
    minDate: startDate,
    maxDate: endDate,
    appendTo: document.body,
    locale: "{{ LANGUAGE_CODE }}",
    onClose: () => {
      createTimeInputs();
      validateForm();
    }
  });

  function getEventDays() {
    if (!eventDaysInput.value) return [];
    let startStr, endStr;

    // Handle single day vs range
    if (eventDaysInput.value.includes(" to ")) {
      [startStr, endStr] = eventDaysInput.value.split(" to ");
    } else {
      startStr = endStr = eventDaysInput.value;
    }

    const start = new Date(startStr);
    const end = new Date(endStr);
    const dates = [];

    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      dates.push(new Date(d));
    }
    return dates;
  }

  function createTimeInputs() {
  container.innerHTML = "";

  getEventDays().forEach(date => {
    const dateStr = date.toISOString().split("T")[0];

    const row = document.createElement("div");
    row.classList.add("row", "mb-2");

    // Label for the day
    const dayLabel = document.createElement("div");
    dayLabel.classList.add("col-12", "fw-bold", "mb-1");
    dayLabel.textContent = dateStr;
    row.appendChild(dayLabel);

    // Create Start and End columns
    ["start", "end"].forEach(type => {
      const col = document.createElement("div");
      col.classList.add("col");

      // Add a label for each input
      const label = document.createElement("label");
      label.textContent = type === "start" ? "Start Time: " : "End Time: ";
      label.classList.add("px-2", "d-inline-block", "w-auto", "ms-2");

      const input = document.createElement("input");
      input.type = "text";
      input.classList.add(`per-day-${type}`);
      input.placeholder = type === "start" ? "e.g. 12:00" : "e.g. 17:00";

      const hidden = document.createElement("input");
      hidden.type = "hidden";
      hidden.name = `${type}_time_${dateStr}`;

      col.appendChild(label);
      col.appendChild(input);
      col.appendChild(hidden);
      row.appendChild(col);

        flatpickr(input, {
          enableTime: true,
          noCalendar: true,
          dateFormat: "H:i",
          time_24hr: true,
          minuteIncrement: 15,
          defaultHour: 12,
          defaultMinute: 0,
          onReady: (_, dateStrValue) => {
            hidden.value = dateStrValue || "12:00";
          },
          onChange: (_, value) => {
            hidden.value = value;
            validateForm();
            document.dispatchEvent(new Event("updateTimesPreview"));
          }
        });
      });

      container.appendChild(row);
    });

    document.dispatchEvent(new Event("updateTimesPreview"));
  }
});
