"use strict";

var bookIDToDelete = 0;

/**
 * Ask the user to confirm that they want to delete the book.
 * 
 * @param {bookID} id The ID of the book to delete.
 */
function deleteBookButton(bookID) {
    bookIDToDelete = bookID
    androidCompat.showConfirmDialog("Are you sure you want to delete this book?", () => {
        deleteBook();
    }, () => {
        androidCompat.showToast("Book was not deleted");
    });
}

/**
 * Delete the the book with the given ID.
 */
function deleteBook() {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/admin/books/delete/" + bookIDToDelete, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            androidCompat.showToast("Book deleted");
            window.location.href = "/";
        }
    };
    xhr.send();
}