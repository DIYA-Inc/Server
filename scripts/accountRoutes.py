#!/usr/bin/env python3

import flask
import re
from sqlite3 import IntegrityError

diya = flask.Blueprint("diyaAccounts", __name__, template_folder="templates")


@diya.route("/account/login", methods=["POST"])
def login():
    """Log in a user."""
    email = flask.request.form["email"]
    password = flask.request.form["password"]

    if email == None or password == None:
        return flask.render_template("account/login.html",
            error="Invalid email or password."), 422

    user = db.checkUser(email, password)

    if user[0] == False:
        return flask.render_template("account/login.html",
            email=email, error="Invalid email or password."), 401

    flask.session["user"] = {
        "id": user[3],
        "email": email,
        "premium": user[1],
        "admin": user[2]
    }

    return flask.redirect("/account/details")


@diya.route("/account/login", methods=["GET"])
def loginPage():
    """Return the login page."""
    if "email" in flask.session:
        email = flask.session["email"]
        del flask.session["email"]
    else:
        email = None

    return flask.render_template("account/login.html",
        email=email, new=flask.request.args.get("new") != None)


@diya.route("/account/register", methods=["POST"])
def register():
    """Register a new user."""
    email = flask.request.form["email"]
    password = flask.request.form["password"]

    if email == None or password == None or len(email) > 128 or (
            not re.match("[a-zA-Z0-9][^@]+[a-zA-Z0-9]@[a-zA-Z0-9\-\.]+\.[a-zA-Z0-9\-\.]+[a-zA-Z0-9]$", email)):
        return flask.render_template("account/register.html", error="Invalid email or password."), 422

    try:
        db.addUser(email, password)
    except IntegrityError:
        return flask.render_template("account/register.html",
            email=email, error="Email already in use."), 409

    flask.session["email"] = email

    return flask.redirect("/account/login?new=1")


@diya.route("/account/register", methods=["GET"])
def registerPage():
    """Return the register page."""
    return flask.render_template("account/register.html")


@diya.route("/account/details", methods=["GET"])
def accountDetails():
    """Get the details of the logged in user."""
    if "user" not in flask.session:
        return flask.redirect("/account/login")

    try:
        return flask.render_template("account/details.html", user=db.getUserByID(flask.session["user"]["id"]))
    except ValueError:
        flask.session.clear()
        return flask.redirect("/")


@diya.route("/account/logout", methods=["GET"])
def logout():
    """Log out the logged in user."""
    flask.session.clear()
    return flask.redirect("/")


@diya.route("/account/delete", methods=["DELETE"])
def deleteAccount():
    """Delete the logged in user."""
    if "user" not in flask.session:
        return flask.redirect("/account/login")

    db.deleteUser(flask.session["user"]["id"])
    flask.session.clear()
    return flask.redirect("/")


if "__main__" == __name__:
    import scripts.database as database
    db = database.database()
