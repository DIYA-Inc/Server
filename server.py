#!/usr/bin/env python3

import flask
import logging
import os
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

# Set up database
db = database(argv["dataDir"])
db.executeScript("databaseStructure.sql")

# Set up flask
app = flask.Flask(__name__)
api.db = db
app.register_blueprint(api)

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

    # Run server
    if useWaitress:
        logging.getLogger("waitress.queue").setLevel(logging.CRITICAL)
        waitress.serve(app, host=argv["host"], port=argv["port"], threads=8)
    else:
        app.run(host=argv["host"], port=argv["port"])
