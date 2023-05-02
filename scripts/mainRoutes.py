#!/usr/bin/env python3

import flask

diya = flask.Blueprint("diyaMain", __name__, template_folder="templates")


@diya.route("/static/<path:path>", endpoint="static", methods=["GET"])
def static(path):
    """Send files in the static folder."""
    return flask.send_from_directory("static", path)


@diya.route("/", methods=["GET"])
def welcome():
    """Return the welcome page."""
    if "user" in flask.session:
        return flask.render_template("index.html", user=flask.session["user"], books=db.searchBooks(limit=1000))
    else:
        return flask.render_template("welcome.html")


@diya.errorhandler(404)
def errorPage(error):
    """Return the error page."""
    return flask.render_template("error.html", error=error), error.code


if "__main__" == __name__:
    import scripts.database as database
    db = database.database()
