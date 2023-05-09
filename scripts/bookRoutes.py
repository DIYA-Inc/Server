#!/usr/bin/env python3

import flask
import os

diya = flask.Blueprint("diyaBooks", __name__, template_folder="templates")


@diya.route("/books/view/<int:bookID>", methods=["GET"])
def viewBook(bookID):
    """View a book."""
    if flask.session.get("user") == None:
        return flask.abort(401, "You must be signed in to access a book.")
    
    try:
        book = db.getBookMetadata(bookID)
    except ValueError:
        raise flask.abort(404, "The book you were looking for was not found.")
        
    return flask.render_template("books/view.html", book=book, user=flask.session["user"])


@diya.route("/books/read/<int:bookID>", methods=["GET"])
def readBook(bookID):
    """View a book."""
    if flask.session.get("user") == None:
        return flask.abort(401, "You must be signed in to read a book.")

    try:
        book = db.getBookMetadata(bookID)
        if not book["fileURL"]:
            raise flask.abort(404, "This book is not readable.")
    except ValueError:
        raise flask.abort(404, "The book you were looking for was not found.")

    return flask.render_template("books/read.html", book=book)


@diya.route("/books/file/<string:bookHash>.epub", methods=["GET"])
def viewBookFile(bookHash):
    """Serve a book file."""
    if flask.session.get("user") == None:
        return flask.abort(401, "You must be signed in to access a book.")
    return flask.send_file(os.path.join(db.directory, bookHash + ".epub"))


@diya.route("/books/cover/<string:bookHash>.jpg", methods=["GET"])
def viewBookImage(bookHash):
    """Serve a book cover if it exists or send the placeholder image."""
    try:
        return flask.send_file(os.path.join(db.directory, bookHash + ".jpg"))
    except FileNotFoundError:
        return flask.send_file("static/img/cover.jpg")


@diya.route("/admin/books/add", methods=["GET", "POST"])
def addBook():
    """Add a books metadata."""
    user = flask.session.get("user")
    if user == None:
        return flask.abort(401, "You do not have permission to add a book.")
    elif not user["admin"]:
        return flask.abort(403, "You do not have permission to add a book.")

    if "POST" != flask.request.method:
        return flask.render_template("admin/books/add.html")
    
    bookID = db.addBookMetadata(**getBookFieldsFromForm())
    addBookFile(bookID, flask.request.files)
    return flask.redirect(flask.url_for("diyaBooks.viewBook", bookID=bookID))


@diya.route("/admin/books/edit/<int:bookID>", methods=["GET", "POST"])
def editBook(bookID):
    """Edit a books metadata."""
    user = flask.session.get("user")
    if user == None:
        return flask.abort(401, "You do not have permission to edit a book.")
    elif not user["admin"]:
        return flask.abort(403, "You do not have permission to edit a book.")

    if "POST" != flask.request.method:
        return flask.render_template("admin/books/edit.html", book=db.getBookMetadata(bookID), bookID=str(bookID))

    db.updateBookMetadata(bookID, **getBookFieldsFromForm())
    addBookFile(bookID, flask.request.files)
    return flask.redirect(flask.url_for("diyaBooks.viewBook", bookID=bookID))


@diya.route("/admin/books/delete/<int:bookID>", methods=["DELETE"])
def deleteBook(bookID):
    """Delete a book."""
    user = flask.session.get("user")
    if user == None:
        return flask.abort(401, "You do not have permission to add a book.")
    elif not user["admin"]:
        return flask.abort(403, "You do not have permission to add a book.")

    db.deleteBook(bookID)
    return "Book deleted"


@diya.route("/api/books/search", methods=["GET"])
def bookSearch():
    """API for searching for books.
    
    URL Parameters:
        query: The query to search for in the title, author, and description.
        genre: The genre to limit the search to.
        language: The language to limit the search to.
        catalogue: The catalogue to limit the search to.
        offset: The offset to start at, default 0.
        limit: The maximum number of results to return, default 10, maximum 50."""
    user = flask.session.get("user")
    if user == None:
        return flask.redirect(flask.url_for("diyaAccounts.loginPage", next=flask.request.url))
    
    query = flask.request.args.get("query", "")
    genre = flask.request.args.get("genre", None) or None
    language = flask.request.args.get("language", None) or None
    catalogue = flask.request.args.get("catalogue", None) or None

    try:
        offset = int(flask.request.args.get("offset", 0))
        limit = int(flask.request.args.get("limit", 10))
    except ValueError: pass
    if limit > 50:
        limit = 50
    
    books = db.searchBooks(query, genre, language, catalogue, offset, limit)

    return books


def getBookFieldsFromForm():
    """Get the fields for a book from a POST"""
    values = {}

    for field in ["title", "author", "isbn", "publisher", "publicationDate", "description", "pageCount", "language", "genre", "readingAge"]:
        values[field] = (flask.request.form[field]
            if field in flask.request.form else None
            ) or None

    if "catalogues" in flask.request.form:
        values["catalogues"] = [c.strip() for c in
            flask.request.form["catalogues"].split(",")
            if c.strip() != ""]
        
    return values


def addBookFile(bookID, files):
    """Add a book file to a book if there is a file in the request."""
    if "file" not in files:
        return

    file = files["file"]
    if file.filename == "" or file.mimetype != "application/epub+zip":
        return
    
    db.addFile(bookID, file.read())


if "__main__" == __name__:
    import scripts.database as database
    db = database.database()