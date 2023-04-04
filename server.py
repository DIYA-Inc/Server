#!/usr/bin/env python3

import flask
import logging
import markdown
import os
from pygments.formatters import HtmlFormatter
import sys

from api import api
from database import database

# Get variables from argv or use the defaults
argv = {}
for arg, var, default in [
    ("--host",      "host",     "0.0.0.0"),
    ("--port",      "port",     "80"),
    ("--data-dir",  "dataDir",  os.path.join(os.path.dirname(__file__), "data"))
]:
    if arg in sys.argv:
        argv[var] =  sys.argv[sys.argv.index(arg) + 1]
    else:
        argv[var] = default

mdCache = {}
def getMarkdown(filename):
    """Get the markdown from a file and return it as HTML."""
    if filename in mdCache:
        return mdCache[filename]

    with open("static/" + filename, "r") as f:
        file = f.read()

    if not filename.endswith(".md"):
        mdCache[filename] = file
        return file

    md = markdown.markdown(file, extensions=[
        "fenced_code", "codehilite", "toc", "nl2br"])

    formatter = HtmlFormatter(style="emacs", full=True, cssclass="codehilite")
    css = formatter.get_style_defs() + getMarkdown("style.css")

    mdCache[filename] = "<style>" + css + "</style>" + md
    return mdCache[filename]


static = flask.Blueprint("static", __name__)

@static.route("/", methods=["GET"])
def index():
    """Return the index page"""
    return getMarkdown("index.md")


@static.app_errorhandler(404)
def page_not_found(e):
    """Return the api reference"""
    return getMarkdown("apiReference.md"), 404


def createServer(dataDir=argv["dataDir"], filename="database.db"):
    """Create a database and server object.
    
    Returns:
        flask.Flask: The server object."""
    app = flask.Flask(__name__)

    db = database(dataDir, filename)
    db.executeScript("databaseStructure.sql")
    api.db = db
    
    app.register_blueprint(api)
    app.register_blueprint(static)
    return app


# Use waitress as the WSGI server if it is installed,
# but use built-in if it isnt, or if --werkzeug argument.
useWaitress = False
if not "--werkzeug" in sys.argv:
    try:
        import waitress
        useWaitress = True
    except:
        print("Waitress is not installed, using built-in WSGI server (werkzeug).")

if __name__ == "__main__":
    if "--help" in sys.argv:
        print("DIYA Inc Book Server")
        print("All Rights Reserved Copyright (c) 2023")
        print("Usage: ./server.py [options]")
        print("Options:")
        print("  --help            Display this help and exit")
        print("  --host HOST       Set the servers host IP")
        print("  --port PORT       Set the servers port")
        print("  --werkzeug        Use werkzeug instead of waitress")
        print("  --data-dir DIR    Set the directory where data is stored")
        exit(0)

    app = createServer()

    # Run server
    if useWaitress:
        logging.getLogger("waitress.queue").setLevel(logging.CRITICAL)
        waitress.serve(app, host=argv["host"], port=argv["port"], threads=8)
    else:
        app.run(host=argv["host"], port=argv["port"])
