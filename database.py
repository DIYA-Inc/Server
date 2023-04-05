#!/usr/bin/env python3

import bcrypt
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

    def addUser(self, email, password):
        """Add a user to the database.
        
        Args:
            email (str): The email of the user.
            password (str): The password of the user."""
        email = email.lower()
        hashedPassword = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        con, cur = self.connect()
        cur.execute(
            "INSERT INTO users (email, passwordHash) VALUES (?, ?)",
            (email, hashedPassword))
        con.commit()
        con.close()

    def checkUser(self, email, password):
        """Check if a user exists in the database.
        
        Args:
            email (str): The email of the user.
            password (str): The password of the user.
        
        Returns: (tuple)
            (bool): Whether the user exists
            (bool): If the user has premium
            (bool): If the user is an admin"""
        email = email.lower()
        con, cur = self.connect()
        cur.execute("""
            SELECT passwordHash, userAccessLevel
            FROM users WHERE email = ?""",
            (email,))
        result = cur.fetchone()
        con.close()
        if result and bcrypt.checkpw(password.encode("utf-8"), result[0]):
                return (True, result[1] >= 1, result[1] >= 2)
        return (False, False, False)
            

if __name__ == "__main__":
    db = database(os.path.join(os.path.dirname(__file__), "data"))
    db.executeScript("databaseStructure.sql")
