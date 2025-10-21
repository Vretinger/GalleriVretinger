document.addEventListener("DOMContentLoaded", () => {
    const modalButtons = document.querySelectorAll(".open-modal-btn");

    modalButtons.forEach(button => {
        button.addEventListener("click", (e) => {
            e.preventDefault();

            const modalId = button.dataset.bsTarget;
            const modalElement = document.querySelector(modalId);
            if (!modalElement) return;

            const title = button.dataset.title || "Notice";
            const message = button.dataset.message || "";

            modalElement.querySelector("#dynamicModalTitle").textContent = title;
            modalElement.querySelector("#dynamicModalMessage").textContent = message;

            const modalInstance = new bootstrap.Modal(modalElement);
            modalInstance.show();
        });
    });
});