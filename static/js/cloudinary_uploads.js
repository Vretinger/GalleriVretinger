// cloudinary_uploads.js
document.addEventListener("DOMContentLoaded", () => {
  const myWidget = cloudinary.createUploadWidget({
    cloudName:"dcbvjzagi", uploadPreset:"GalleriVretinger", asset_folder:"artworks/users/{{ user.user }}/events/temp", multiple:true, maxFiles:10
  }, (err,res)=>{ if(!err && res && res.event==="success") addUploadedImage(res.info); });

  document.getElementById("upload_widget").addEventListener("click", ()=>myWidget.open());

  function addUploadedImage(info){
    const container=document.getElementById("preview-images");
    const wrapper=document.createElement("div"); wrapper.style.position="relative"; wrapper.style.display="inline-block"; wrapper.style.margin="5px";
    const img=document.createElement("img"); img.src=info.secure_url; img.style.maxWidth="150px"; img.style.borderRadius="6px"; img.style.boxShadow="0 2px 5px rgba(0,0,0,0.2)";
    const input=document.createElement("input"); input.type="hidden"; input.name="uploaded_images"; input.value=info.public_id; document.querySelector("form").appendChild(input);

    const removeBtn=document.createElement("button"); removeBtn.textContent="×"; removeBtn.type="button";
    removeBtn.style.position="absolute"; removeBtn.style.top="2px"; removeBtn.style.right="2px";
    removeBtn.style.background="rgba(0,0,0,0.6)"; removeBtn.style.color="white"; removeBtn.style.border="none";
    removeBtn.style.borderRadius="50%"; removeBtn.style.width="22px"; removeBtn.style.height="22px"; removeBtn.style.cursor="pointer";
    removeBtn.addEventListener("click", ()=>{
      fetch("/delete_uploaded_image/",{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":getCookie("csrftoken")},body:JSON.stringify({public_id:info.public_id})});
      wrapper.remove();
    });

    wrapper.append(img, removeBtn, input); container.appendChild(wrapper);
    validateForm();
  }

  // Background upload
  const bgWidget=cloudinary.createUploadWidget({
    cloudName:"dcbvjzagi", uploadPreset:"GalleriVretinger", asset_folder:"artworks/users/{{ user.user }}/events/bg", multiple:false
  }, (err,res)=>{
    if(!err && res && res.event==="success"){
      const bgPreview=document.getElementById("preview-background");
      bgPreview.style.backgroundImage=`url(${res.info.secure_url})`;
      bgPreview.style.backgroundSize="cover";
      bgPreview.style.backgroundPosition="center";
      let input=document.querySelector('input[name="bg_image_uploaded"]');
      if(!input){ input=document.createElement("input"); input.type="hidden"; input.name="bg_image_uploaded"; document.querySelector("form").appendChild(input); }
      input.value=res.info.public_id;
    }
  });
  document.getElementById("bg-upload-btn").addEventListener("click",()=>bgWidget.open());

  function getCookie(name){ let cookieValue=null;if(document.cookie && document.cookie!==""){document.cookie.split(";").forEach(c=>{const cookie=c.trim();if(c.startsWith(name+"=")) cookieValue=decodeURIComponent(c.substring(name.length+1));});}return cookieValue;}
});
