document.addEventListener("DOMContentLoaded", () => {
  const eventWidget = cloudinary.createUploadWidget({
    cloudName: "dcbvjzagi",
    uploadPreset: "GalleriVretinger",
    asset_folder: "artworks/users/{{ user.user }}/events/event_image",
    multiple: false
  }, (err, res) => {
    if (!err && res && res.event === "success") {
      updateEventPreview(res.info);
    }
  });

  document.getElementById("event-upload-btn")
    .addEventListener("click", () => eventWidget.open());


  function updateEventPreview(info) {
    // Save public_id
    document.getElementById("event-image-hidden").value = info.public_id;

    // Set preview image
    const previewImg = document.getElementById("event-preview");
    previewImg.src = info.secure_url;
    previewImg.classList.add("image-loaded");
  }
});
