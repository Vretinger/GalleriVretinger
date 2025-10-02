// event_days.js
document.addEventListener("rentalDatesSelected", (e) => {
  const [startDate, endDate] = e.detail;
  const eventDaysInput = document.getElementById("event-days");

  flatpickr(eventDaysInput, {
    mode: "range",
    dateFormat: "Y-m-d",
    minDate: startDate,
    maxDate: endDate,
    appendTo: document.body,
    onClose: () => {
      createTimeInputs();
      validateForm();
    }
  });

  function getEventDays() {
    if (!eventDaysInput.value) return [];
    const [startStr, endStr] = eventDaysInput.value.split(" to ");
    const start = new Date(startStr), end = new Date(endStr);
    const dates = [];
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) dates.push(new Date(d));
    return dates;
  }

  function createTimeInputs() {
    const container = document.getElementById("per-day-times");
    if (!container) return;
    container.innerHTML = "";

    getEventDays().forEach(date => {
      const dateStr = date.toISOString().split("T")[0];
      const row = document.createElement("div"); row.classList.add("row","mb-2");

      // Date label
      const dayLabel = document.createElement("div");
      dayLabel.classList.add("col-12","fw-bold","mb-1");
      dayLabel.textContent = dateStr;
      row.appendChild(dayLabel);

      ["start","end"].forEach(type => {
        const col = document.createElement("div"); col.classList.add("col");
        const input = document.createElement("input"); input.type="text"; input.classList.add(`per-day-${type}`);
        const hidden = document.createElement("input"); hidden.type="hidden"; hidden.name=`${type}_time_${dateStr}`;
        col.appendChild(input); col.appendChild(hidden); row.appendChild(col);

        flatpickr(input, {
          enableTime: true, noCalendar:true, dateFormat:"H:i", time_24hr:true, minuteIncrement:15,  defaultHour: 12, defaultMinute: 0,
          onReady: (selectedDates, dateStr) => {
            hidden.value = dateStr;   // set initial hidden value
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
