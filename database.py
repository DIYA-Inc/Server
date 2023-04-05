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
            (bool): If the user is an admin
            (int): The user's ID"""
        email = email.lower()
        con, cur = self.connect()
        cur.execute("""
            SELECT userID, passwordHash, userAccessLevel
            FROM users WHERE email = ?""",
            (email,))
        result = cur.fetchone()
        con.close()
        if result and bcrypt.checkpw(password.encode("utf-8"), result[1]):
                return (True, result[2] >= 1, result[2] >= 2, result[0])
        return (False,)
    
    def getUserByID(self, userID):
        """Get a user's details by their ID.
        
        Args:
            userID (int): The ID of the user.
        
        Returns:
            dict: The user's details."""
        con, cur = self.connect()
        cur.execute("""
            SELECT email, userAccessLevel, created, premiumExpires
            FROM users WHERE userID = ?""",
            (userID,))
        result = cur.fetchone()
        con.close()
        if result:
            return {
                "email": result[0],
                "premium": result[1] >= 1,
                "admin": result[1] >= 2,
                "created": result[2],
                "premiumExpires": result[3]
            }
        raise ValueError("User does not exist.")

if __name__ == "__main__":
    db = database(os.path.join(os.path.dirname(__file__), "data"))
    db.executeScript("databaseStructure.sql")
