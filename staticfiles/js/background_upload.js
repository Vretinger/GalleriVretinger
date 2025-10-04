document.addEventListener("DOMContentLoaded", () => {
  const bgWidget = cloudinary.createUploadWidget({
    cloudName: "dcbvjzagi",
    uploadPreset: "GalleriVretinger",
    asset_folder: "artworks/users/{{ user.user }}/events/bg",
    multiple: false
  }, (err, res) => {
    if (!err && res && res.event === "success") {
      addUploadedBGImage(res.info);
    }
  });

  document.getElementById("bg-upload-btn").addEventListener("click", () => bgWidget.open());

  function addUploadedBGImage(info) {
    // Preview
    const bgPreview = document.getElementById("preview-background");
    bgPreview.style.backgroundImage = `url(${info.secure_url})`;

    // Save public_id in hidden input
    const hiddenInput = document.getElementById("bg-image-hidden");
    hiddenInput.value = info.public_id;
  }
});
