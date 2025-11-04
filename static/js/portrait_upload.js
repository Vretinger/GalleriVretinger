document.addEventListener("DOMContentLoaded", () => {
  const bgWidget = cloudinary.createUploadWidget({
    cloudName: "dcbvjzagi",
    uploadPreset: "GalleriVretinger",
    asset_folder: "artworks/users/{{ user.user }}/events/portrait",
    multiple: false
  }, (err, res) => {
    if (!err && res && res.event === "success") {
      addUploadedPortraitImage(res.info);
    }
  });

  document.getElementById("portrait-upload-btn").addEventListener("click", () => bgWidget.open());

  function addUploadedPortraitImage(info) {
    // Save public_id in hidden input
    const hiddenInput = document.getElementById("portrait-image-hidden");
    hiddenInput.value = info.public_id;
  }
});
