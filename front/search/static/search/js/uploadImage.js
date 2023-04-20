/** 
 * アップロードされた画像をサーバに送信する関数。
 */
function uploadImage() {
    const imageInput = document.getElementById('uploadImage');
    // for camera: setting a event which a file input was changed.
    imageInput.addEventListener(
        "change",
        (e) => {// when the file uploaded, the form is posted py this code.
            const imageForm = document.getElementById('imageForm');
            imageForm.submit();
        }
    )
    imageInput.click();
}
