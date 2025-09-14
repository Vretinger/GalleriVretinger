document.addEventListener("DOMContentLoaded", function () {
    var calendarEl = document.getElementById("calendar");

    const bookedDatesUrl = calendarEl.dataset.bookedDatesUrl;
    const continueBtn = document.getElementById("continueBtn");

    let startDate = null;
    let endDate = null;
    let selectionEvent = null;

    const rentalStartInput = document.getElementById('rental_start');
    const rentalEndInput = document.getElementById('rental_end');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        selectable: false,
        firstDay: 1,
        events: bookedDatesUrl,
        eventColor: "red",
        dateClick: function (info) {
            let isBooked = calendar.getEvents().some(ev =>
                info.date >= ev.start && info.date < ev.end
            );
            if (isBooked) return;

            // Third click resets selection if both start and end are set
            if (startDate && endDate) {
                startDate = null;
                endDate = null;
                rentalStartInput.value = '';
                rentalEndInput.value = '';
                continueBtn.disabled = true;

                // remove previous selection highlight
                if (selectionEvent) {
                    selectionEvent.remove();
                    selectionEvent = null;
                }
            }

            if (!startDate) {
                startDate = info.dateStr;

                // Always create a new selection event
                if (selectionEvent) selectionEvent.remove();
                selectionEvent = calendar.addEvent({
                    start: startDate,
                    end: startDate,
                    display: "background",
                    backgroundColor: "blue"
                });
            } else if (!endDate) {
                endDate = info.dateStr;

                if (new Date(endDate) < new Date(startDate)) {
                    [startDate, endDate] = [endDate, startDate];
                }

                // Update the selection event to cover full range
                if (selectionEvent) selectionEvent.remove();
                selectionEvent = calendar.addEvent({
                    start: startDate,
                    end: new Date(new Date(endDate).getTime() + 24 * 60 * 60 * 1000),
                    display: "background",
                    backgroundColor: "blue"
                });

                rentalStartInput.value = startDate;
                rentalEndInput.value = endDate;
                continueBtn.disabled = false;
            }
        }
    });

    calendar.render();
});
