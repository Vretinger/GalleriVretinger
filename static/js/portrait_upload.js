document.addEventListener("DOMContentLoaded", () => {
  const portraitWidget = cloudinary.createUploadWidget({
    cloudName: "dcbvjzagi",
    uploadPreset: "GalleriVretinger",
    asset_folder: "artworks/users/{{ user.user }}/events/portrait",
    multiple: false
  }, (err, res) => {
    if (!err && res && res.event === "success") {
      updatePortraitPreview(res.info);
    }
  });

  document.getElementById("portrait-upload-btn")
    .addEventListener("click", () => portraitWidget.open());


  function updatePortraitPreview(info) {

    document.getElementById("portrait-image-hidden").value = info.public_id;

    const button = document.getElementById("portrait-upload-btn");
    const img = document.getElementById("portrait-preview");

    // Remove the placeholder image (so it doesn't resize)
    img.style.display = "none";

    // Apply full-cover background image
    button.style.backgroundImage = `url(${info.secure_url})`;
    button.style.backgroundSize = "cover";
    button.style.backgroundPosition = "center";
    button.style.backgroundRepeat = "no-repeat";
  }

  document.getElementById("event-upload-btn")
    .addEventListener("click", () => eventWidget.open());


  function updateEventPreview(info) {

    document.getElementById("event-image-hidden").value = info.public_id;

    const button = document.getElementById("event-upload-btn");
    const img = document.getElementById("event-preview");

    // Remove the placeholder image (so it doesn't resize)
    img.style.display = "none";

    // Apply full-cover background image
    button.style.backgroundImage = `url(${info.secure_url})`;
    button.style.backgroundSize = "cover";
    button.style.backgroundPosition = "center";
    button.style.backgroundRepeat = "no-repeat";
  }

});
