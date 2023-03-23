#!/usr/bin/env python3

import flask

api = flask.Blueprint("api", __name__)

# TODO: Add API routes here

if "__main__" == __name__:
    import database
    db = database.database()
