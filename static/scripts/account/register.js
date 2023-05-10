/**
 * Verifies that the password is strong enough, if not, it will display a message.
 */

var passwordInput = document.getElementById("password");

document.getElementsByTagName("form")[0].addEventListener("submit", function (event) {
    if (verifyPassword(passwordInput.value)) {
        return form.submit();
    } else {
        androidCompat.showToast("Password is not strong enough.");
    }
    event.preventDefault();
});

/**
 * Verifies that the password is strong enough.
 * 
 * @param {string} password The password to verify.
 * @returns {boolean} True if the password is strong enough.
 */
function verifyPassword(password) {
    return !(password.length < 12 ||
            !password.match(/[A-Z]/) ||
            !password.match(/[a-z]/) ||
            !password.match(/[0-9]/) ||
            !password.match(/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/))
}