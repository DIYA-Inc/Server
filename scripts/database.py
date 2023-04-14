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

    def addBookMetadata(self, title, author, isbn,
            publisher=None, publicationDate=None, description=None,
            pageCount=None, language=None, genre=None,
            readingAge=None, catalogues=[]):
        """Add book metadata to the database.

        Args:
            title(str): The title of the book.
            author(str): The author of the book.
            isbn(str): The ISBN of the book.
            publisher(str): The publisher of the book. (optional)
            publicationDate(str): The publication date of the book. (optional)
            description(str): The description of the book. (optional)
            pageCount(int): The number of pages in the book. (optional)
            language(str): The language of the book. (optional)
            genre(str): The genre of the book. (optional)
            readingAge(int): The recommended reading age of the book. (optional)
            catalogues(list of str): The catalogues the book is in. (optional)
        Returns:
            int: The ID of the book."""
        for field in [title, author, isbn]:
            if not field:
                raise ValueError("Required argument not provided.")
        con, cur = self.connect()
        cur.execute("""
            INSERT INTO books (
                bookName, author, ISBN, publisher, publicationDate,
                description, pageCount, language, genre, readingAge
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, author, isbn, publisher, publicationDate,
                description, pageCount, language, genre, readingAge))
        bookID = cur.lastrowid
        for catalogue in catalogues:
            cur.execute("""INSERT OR IGNORE INTO bookCatalogues (
                catalogueName) VALUES (?)""", (catalogue,))
            cur.execute("""
                INSERT INTO bookCatalogueLink (
                    bookID, catalogueID
                ) VALUES ( ?,
                    (SELECT catalogueID FROM bookCatalogues WHERE catalogueName = ?)
                )""", (bookID, catalogue))
        con.commit()
        con.close()
        return bookID
    
    def updateBookMetadata(self, bookID, title=None, author=None, isbn=None,
                           publisher=None, publicationDate=None, description=None,
                           pageCount=None, language=None, genre=None,
                           readingAge=None, catalogues=[]):
        """Edit book metadata in the database."""
        con, cur = self.connect()
        cur.execute("""
            UPDATE books SET
                bookName = COALESCE(?, bookName),
                author = COALESCE(?, author),
                ISBN = COALESCE(?, ISBN),
                publisher = COALESCE(?, publisher),
                publicationDate = COALESCE(?, publicationDate),
                description = COALESCE(?, description),
                pageCount = COALESCE(?, pageCount),
                language = COALESCE(?, language),
                genre = COALESCE(?, genre),
                readingAge = COALESCE(?, readingAge)
            WHERE bookID = ?""",
                    (title, author, isbn, publisher, publicationDate,
                     description, pageCount, language, genre, readingAge, bookID))
        cur.execute("DELETE FROM bookCatalogueLink WHERE bookID = ?", (bookID,))
        for catalogue in catalogues:
            cur.execute("""INSERT OR IGNORE INTO bookCatalogues (
                catalogueName) VALUES (?)""", (catalogue,))
            cur.execute("""
                INSERT INTO bookCatalogueLink (
                    bookID, catalogueID
                ) VALUES ( ?,
                    (SELECT catalogueID FROM bookCatalogues WHERE catalogueName = ?)
                )""", (bookID, catalogue))
        con.commit()
        con.close()
    
    def getBookMetadata(self, bookID):
        """Get book metadata from the database.

        Args:
            bookID(int): The ID of the book.
        Returns:
            dict: The book's metadata."""
        con, cur = self.connect()
        cur.execute("""
            SELECT bookName, author, ISBN, publisher, publicationDate,
                description, pageCount, language, genre, readingAge
            FROM books WHERE bookID = ?""", (bookID,))
        result = cur.fetchone()
        if result:
            cur.execute("""
                SELECT catalogueName
                FROM bookCatalogues
                INNER JOIN bookCatalogueLink ON bookCatalogues.catalogueID = bookCatalogueLink.catalogueID
                WHERE bookID = ?""", (bookID,))
            catalogues = [catalogue[0] for catalogue in cur.fetchall()]
        con.close()
        if result:
            return {
                "bookID": bookID,
                "title": result[0],
                "author": result[1],
                "isbn": result[2],
                "publisher": result[3],
                "publicationDate": result[4],
                "description": result[5],
                "pageCount": result[6],
                "language": result[7],
                "genre": result[8],
                "readingAge": result[9],
                "catalogues": catalogues
            }
        raise ValueError("404: Book does not exist.")
    
    def deleteBook(self, bookID):
        """Delete book metadata from the database.

        Args:
            bookID(int): The ID of the book."""
        con, cur = self.connect()
        cur.execute("DELETE FROM books WHERE bookID = ?", (bookID,))
        cur.execute("DELETE FROM bookCatalogueLink WHERE bookID = ?", (bookID,))
        cur.execute("DELETE FROM bookCatalogues WHERE catalogueID NOT IN (SELECT catalogueID FROM bookCatalogueLink)")
        con.commit()
        con.close()


if __name__ == "__main__":
    db = database(os.path.join(os.path.dirname(__file__), "data"))
    db.executeScript("databaseStructure.sql")
