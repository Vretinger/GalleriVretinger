document.addEventListener("DOMContentLoaded", function() {
    const calendarEl = document.getElementById("event-calendar");
    const eventStartInput = document.getElementById("event_start");
    const eventEndInput = document.getElementById("event_end");
    const finishBtn = document.getElementById("finishBtn");

    // Preview inputs
    const titleInput = document.querySelector('[name="title"]');
    const descInput = document.querySelector('[name="description"]');
    const layoutSelect = document.querySelector('[name="layout"]');
    const extraImagesContainer = document.getElementById("extra-images-container");
    const addImageBtn = document.getElementById("addImageBtn");
    const previewInner = document.getElementById("preview-inner");
    const previewImages = document.getElementById("preview-images");

    let imageCount = 1;

    // Calendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        selectable: true,
        firstDay: 1,
        validRange: {
            start: rentalStart,
            end: rentalEnd
        },
        select: function(info) {
            eventStartInput.value = info.startStr;
            eventEndInput.value = info.endStr;
            finishBtn.disabled = false;

            // Clear old highlights
            calendar.getEvents().forEach(ev => ev.remove());

            calendar.addEvent({
                start: info.start,
                end: info.end,
                display: "background",
                color: "#add8e6"
            });
        }
    });
    calendar.render();

    // Add more image inputs
    function createImageInput(idx) {
        const div = document.createElement("div");
        div.classList.add("mb-2", "d-flex", "align-items-center");
        const input = document.createElement("input");
        input.type = "file";
        input.name = `image${idx+1}`;
        input.classList.add("form-control", "me-2");
        input.addEventListener("change", updatePreview);
        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.classList.add("btn", "btn-danger");
        removeBtn.textContent = "Remove";
        removeBtn.addEventListener("click", () => {
            div.remove();
            updatePreview();
        });
        div.appendChild(input);
        div.appendChild(removeBtn);
        return div;
    }

    addImageBtn.addEventListener("click", () => {
        imageCount++;
        extraImagesContainer.appendChild(createImageInput(imageCount-1));
    });

    // Update preview
    function updatePreview() {
        previewImages.innerHTML = "";

        const layout = layoutSelect.value;

        // Reset styles
        previewInner.style.flexDirection = "row";
        previewImages.style.flexDirection = "column";
        previewImages.style.width = "40%";
        previewImages.style.overflowX = "hidden";

        if (layout === "layout2") { 
            previewInner.style.flexDirection = "column";
            previewImages.style.flexDirection = "row";
            previewImages.style.width = "100%";
            previewImages.style.flexWrap = "wrap";
        } else if (layout === "layout3") {
            previewInner.style.flexDirection = "column";
            previewImages.style.flexDirection = "row";
            previewImages.style.width = "100%";
            previewImages.style.overflowX = "auto";
            previewImages.style.gap = "10px";
        }

        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = e => {
                    const img = document.createElement("img");
                    img.src = e.target.result;
                    img.style.maxHeight = "200px";
                    img.style.objectFit = "cover";
                    img.classList.add("border", "rounded", "mb-2");

                    if (layout === "layout2") {
                        img.style.width = "calc(33% - 10px)";
                        img.style.marginRight = "5px";
                        img.style.marginBottom = "5px";
                    } else if (layout === "layout3") {
                        img.style.height = "200px";
                        img.style.width = "auto";
                    } else {
                        img.style.width = "100%";
                        img.style.marginBottom = "10px";
                    }
                    previewImages.appendChild(img);
                };
                reader.readAsDataURL(input.files[0]);
            }
        });

        document.getElementById("preview-title").textContent = titleInput.value;
        document.getElementById("preview-description").textContent = descInput.value;
    }

    titleInput.addEventListener("input", updatePreview);
    descInput.addEventListener("input", updatePreview);
    layoutSelect.addEventListener("change", updatePreview);
    document.querySelector('[name="image1"]').addEventListener("change", updatePreview);
});
