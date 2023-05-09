"use strict";

/**
 * Ask the user to confirm that they want to delete the book.
 * 
 * @param {bookID} id The ID of the book to delete.
 */
function deleteBookButton(bookID) {
    androidCompat.showConfirmDialog("Are you sure you want to delete this book?", () => {
        deleteBook(bookID);
    }, () => {
        androidCompat.showToast("Book was not deleted");
    });
}

/**
 * Delete the the book with the given ID.
 */
function deleteBook(bookID) {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/admin/books/delete/"+bookID, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            androidCompat.showToast("Book deleted");
            window.location.href = "/";
        }
    };
    xhr.send();
}