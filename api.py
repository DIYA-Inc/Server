#!/usr/bin/env python3

import flask

api = flask.Blueprint("api", __name__)

@api.route("/", methods=["GET"])
def index():
    return "Hello, world!"

if "__main__" == __name__:
    import database
    db = database.database()
