"use strict";

/** Android compatibility layer for the website and app compatibility. */
class AndroidCompat {
    android = typeof Android != "undefined";

    /**
     * Show a toast message, if in a web browser show a normal alert.
     * 
     * @param {string} message The message to show.
     */
    showToast(message) {
        if (this.android) {
            Android.showToast(message);
        } else {
            alert(message);
        }
    }

    /**
     * Show a confirmation dialog, and call the appropriate function based on the user's response.
     * 
     * @param {string} message The message to show in the dialog.
     * @param {function} yesFunc The function to call if the user clicks yes.
     * @param {function} noFunc The function to call if the user clicks no.
     */
    showConfirmDialog(message, yesFunc, noFunc) {
        if (this.android) {
            Android.showConfirmDialog(message, this.usableFunction(yesFunc), this.usableFunction(noFunc));
        } else {
            if (confirm(message)) {
                yesFunc();
            } else {
                noFunc();
            }
        }
    }

    /**
     * Convert an anonymous function to a string, and remove the function declaration.
     * 
     * @param {function} func The function to convert.
     * @returns {string} The function as a string, without the function declaration.
     */
    usableFunction(func) {
        let funcStr = func.toString();
        if (funcStr.startsWith("function () {")) {
            return funcStr.replace("function () {", "").replace("}", "");
        } else if (funcStr.startsWith("() => {")) {
            return funcStr.replace("() => {", "").replace("}", "");
        } else {
            return funcStr;
        }
    }
}

const androidCompat = new AndroidCompat();