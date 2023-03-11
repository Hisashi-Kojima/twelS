function uploadImage() {
    const uploadImageBtn = document.getElementById('uploadImage');
    // for camera: setting a event which a file input was changed.
    uploadImageBtn.addEventListener(
        "change",
        (e) => {// when the file uploaded, the form is posted py this code.
            const imageForm = document.getElementById('imageForm');
            imageForm.submit();
        }
    )
    uploadImageBtn.click();
}

module.exports = uploadImage;