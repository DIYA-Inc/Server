#!/usr/bin/env python3

import os
import sqlite3


class database:
    def __init__(self, directory="data"):
        """Set up database."""
        self.directory = directory
        self.filename = os.path.join(self.directory, "database.db")
        os.makedirs(self.directory, exist_ok=True)

    def connect(self):
        """Access the database."""
        con = sqlite3.connect(self.filename)
        cur = con.cursor()
        return con, cur

    def executeScript(self, filename):
        """Execute a script file."""
        with open(os.path.join(os.path.dirname(__file__), filename), "r") as f:
            script = f.read()
        con, cur = self.connect()
        cur.executescript(script)
        con.commit()
        con.close()


if __name__ == "__main__":
    db = database(os.path.join(os.path.dirname(__file__), "data"))
    db.executeScript("databaseStructure.sql")
