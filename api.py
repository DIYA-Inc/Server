#!/usr/bin/env python3

import flask
import re
from sqlite3 import IntegrityError

api = flask.Blueprint("api", __name__)


@api.route("/account/login", methods=["POST"])
def login():
    """Log in a user."""
    if flask.request.json == None or flask.request.json == {}:
        return {"success": False}, 422
    
    email = flask.request.json.get("email")
    password = flask.request.json.get("password")

    if email == None or password == None:
        return {"success": False}, 422
    
    user = api.db.checkUser(email, password)

    if user[0] == False:
        return {"success": False}, 401
    
    flask.session["user"] = {
        "id": user[3],
        "email": email,
        "premium": user[1],
        "admin": user[2]
    }

    return {
        "success": user[0],
        "premium": user[1],
        "admin": user[2]
    }


@api.route("/account/register", methods=["POST"])
def register():
    """Register a new user."""
    if flask.request.json == None or flask.request.json == {}:
        return {"success": False}, 422
    
    email = flask.request.json.get("email")
    password = flask.request.json.get("password")

    if email == None or password == None or len(email) > 128 or (
        not re.match("[a-zA-Z0-9][^@]+[a-zA-Z0-9]@[a-zA-Z0-9\-\.]+\.[a-zA-Z0-9\-\.]+[a-zA-Z0-9]$", email)):
        return {"success": False}, 422
    
    try:
        api.db.addUser(email, password)
    except IntegrityError:
        return {"success": False}, 409
    
    return {"success": True}


@api.route("/account/details", methods=["GET"])
def accountDetails():
    """Get the details of the logged in user."""
    if "user" not in flask.session:
        return {"success": False}, 401
    
    try:
        return api.db.getUserByID(flask.session["user"]["id"])
    except ValueError:
        flask.session.clear()
        return {"success": False}, 401


@api.route("/account/logout", methods=["GET"])
def logout():
    """Log out the logged in user."""
    flask.session.clear()
    return {"success": True}


if "__main__" == __name__:
    import database
    db = database.database()
