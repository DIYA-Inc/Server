"use strict";

/**
 * Ask the user to confirm that they want to delete their account.
 */
function deleteAccountButton() {
    androidCompat.showConfirmDialog("Are you sure you want to delete your account?", () => {
        deleteAccount();
    }, () => {
        androidCompat.showToast("Account was not deleted");
    });
}

/**
 * Delete the user's account.
 */
function deleteAccount() {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/account/delete", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            androidCompat.showToast("Account deleted");
            window.location.href = "/";
        }
    };
    xhr.send();
}