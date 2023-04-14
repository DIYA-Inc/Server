#!/usr/bin/env python3

import flask

diya = flask.Blueprint("diyaBooks", __name__, template_folder="templates")


@diya.route("/books/view/<int:bookID>", methods=["GET"])
def viewBook(bookID):
    """View a book."""
    try:
        book = db.getBookMetadata(bookID)
    except ValueError:
        raise flask.abort(404, "The book you were looking for was not found.")
        
    return flask.render_template("books/view.html", book=book)


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
        return flask.render_template("admin/books/edit.html", book=db.getBookMetadata(bookID), bookID=bookID)

    db.updateBookMetadata(bookID, **getBookFieldsFromForm())
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

if "__main__" == __name__:
    import scripts.database as database
    db = database.database()