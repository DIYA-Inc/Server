#!/usr/bin/env python3

import os
import sqlite3


class database:
    def __init__(self, directory, filename):
        """Set up database.
        
        Args:
            directory (str): The directory to store the database in.
            filename (str): The name of the database file."""
        self.directory = directory
        self.filename = os.path.join(self.directory, filename)
        os.makedirs(self.directory, exist_ok=True)

    def connect(self):
        """Access the database.
        
        Returns:
            con (sqlite3.Connection): The connection to the database.
            cur (sqlite3.Cursor): The cursor to the database."""
        con = sqlite3.connect(self.filename)
        cur = con.cursor()
        return con, cur

    def executeScript(self, filename):
        """Execute a script file.
        
        Args:
            filename (str): The name of the script file."""
        with open(os.path.join(os.path.dirname(__file__), filename), "r") as f:
            script = f.read()
        con, cur = self.connect()
        cur.executescript(script)
        con.commit()
        con.close()


if __name__ == "__main__":
    db = database(os.path.join(os.path.dirname(__file__), "data"))
    db.executeScript("databaseStructure.sql")
