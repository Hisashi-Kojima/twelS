function mask_oldpassword() {
    var x = document.getElementById("OldPassword");
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}