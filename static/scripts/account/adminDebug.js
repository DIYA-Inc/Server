"use strict";

/**
 * Temporary function for debugging admin functionality.
 * 
 * Ask the user to confirm that they want to toggle admin status.
 * 
 * @param {boolean} isAdmin Whether the user is currently an admin.
 */
function toggleAdminButton(isAdmin) {
    if (isAdmin) {
        var message = "Are you sure you want to no longer be an admin? (you will be signed out)";
    } else {
        var message = "Are you sure you want to become an admin? (you will be signed out)";
    }

    androidCompat.showConfirmDialog(message, () => {
        toggleAdmin();
    }, () => {
        androidCompat.showToast("Account was not changed");
    });
}

/**
 * Temporary function for debugging admin functionality.
 *
 * Delete the user's account.
 */
function toggleAdmin() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/account/toggleAdmin", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            androidCompat.showToast(xhr.responseText + ", please sign in again.");
            var xhrLogout = new XMLHttpRequest();
            xhrLogout.open("GET", "/account/logout", true);
            xhrLogout.onreadystatechange = function () {
                if (xhrLogout.readyState === 4 && xhrLogout.status === 200) {
                    window.location.href = "/account/login";
                }
            };
            xhrLogout.send();
        }
    };
    xhr.send();
}