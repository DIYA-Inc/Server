#!/usr/bin/env python3

import bcrypt
import hashlib
import os
import PIL.Image
import re
import sqlite3
import zipfile


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
        try:
            cur.execute(
                "INSERT INTO users (email, passwordHash) VALUES (?, ?)",
                (email, hashedPassword))
            con.commit()
        except sqlite3.OperationalError:
            con.close()
            raise sqlite3.IntegrityError("Invalid argument.")
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
        try:
            cur.execute("""
                SELECT userID, passwordHash, userAccessLevel
                FROM users WHERE email = ?""",
                (email,))
            result = cur.fetchone()
        except sqlite3.OperationalError:
            result = None
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
        try:
            cur.execute("""
                SELECT email, userAccessLevel, created, premiumExpires
                FROM users WHERE userID = ?""",
                (userID,))
            result = cur.fetchone()
        except sqlite3.OperationalError:
            result = None
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
    
    def deleteUser(self, userID):
        """Delete a user from the database.
        
        Args:
            userID (int): The ID of the user."""
        con, cur = self.connect()
        try:
            cur.execute("DELETE FROM users WHERE userID = ?", (userID,))
            con.commit()
        except sqlite3.OperationalError:
            con.rollback()
        con.close()

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
        try:
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
        except sqlite3.OperationalError:
            con.rollback()
            con.close()
            raise ValueError("Invalid argument.")
        con.close()
        return bookID
    
    def updateBookMetadata(self, bookID, title=None, author=None, isbn=None,
                           publisher=None, publicationDate=None, description=None,
                           pageCount=None, language=None, genre=None,
                           readingAge=None, catalogues=[]):
        """Edit book metadata in the database."""
        con, cur = self.connect()
        try:
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
        except sqlite3.OperationalError:
            con.rollback()
        con.close()
    
    def getBookMetadata(self, bookID):
        """Get book metadata from the database.

        Args:
            bookID(int): The ID of the book.
        Returns:
            dict: The book's metadata."""
        con, cur = self.connect()
        try:
            cur.execute("""
                SELECT bookName, author, ISBN, publisher, publicationDate,
                    description, pageCount, language, genre, readingAge, fileHash
                FROM books WHERE bookID = ?""", (bookID,))
            result = cur.fetchone()
            if result:
                cur.execute("""
                    SELECT catalogueName
                    FROM bookCatalogues
                    INNER JOIN bookCatalogueLink ON bookCatalogues.catalogueID = bookCatalogueLink.catalogueID
                    WHERE bookID = ?""", (bookID,))
                catalogues = [catalogue[0] for catalogue in cur.fetchall()]
        except sqlite3.OperationalError:
            result = None
        con.close()
        if result:
            book = {
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
                "catalogues": catalogues,
                "fileURL": None,
                "coverURL": "/static/img/cover.jpg"
            }

            if result[10]:
                book["fileURL"] = "/books/file/" + result[10] + ".epub"
                book["coverURL"] = "/books/cover/" + result[10] + ".jpg"

            return book
        raise ValueError("404: Book does not exist.")
    
    def deleteBook(self, bookID):
        """Delete book metadata from the database.

        Args:
            bookID(int): The ID of the book."""
        con, cur = self.connect()
        try:
            cur.execute("SELECT fileHash FROM books WHERE bookID = ?", (bookID,))
            fileHash = cur.fetchone()[0]
            if fileHash:
                try:
                    os.remove(os.path.join(self.directory, fileHash + ".epub"))
                    os.remove(os.path.join(self.directory, fileHash + ".jpg"))
                except FileNotFoundError:
                    pass
            
            cur.execute("DELETE FROM books WHERE bookID = ?", (bookID,))
            cur.execute("DELETE FROM bookCatalogueLink WHERE bookID = ?", (bookID,))
            cur.execute("DELETE FROM bookCatalogues WHERE catalogueID NOT IN (SELECT catalogueID FROM bookCatalogueLink)")
            con.commit()
            con.close()
        except sqlite3.OperationalError:
            con.close()

    def searchBooks(self, query="", genre=None, language=None, catalogue=None, offset=0, limit=10, sort="bookName"):
        """Search for books in the database.

        Args:
            query(str): The query to search for in the title, author, and description. (optional)
            genre(str): The genre to limit the search to. (optional)
            language(str): The language to limit the search to. (optional)
            catalogue(str): The catalogue to limit the search to. (optional)
            offset(int): The offset to start at, default 0. (optional)
            limit(int): The maximum number of results to return, default 10. (optional)
        Returns:
            list of dict: The books that match the search."""
        con, cur = self.connect()
        sql = """
            SELECT DISTINCT books.bookID, bookName, author, ISBN, publisher, publicationDate,
                description, pageCount, language, genre, readingAge, fileHash
            FROM books  LEFT JOIN bookCatalogueLink ON books.bookID = bookCatalogueLink.bookID
                        LEFT JOIN bookCatalogues ON bookCatalogueLink.catalogueID = bookCatalogues.catalogueID
            WHERE   (bookName LIKE ? OR author LIKE ? OR description LIKE ?) """
        values = ("%" + query + "%", "%" + query + "%", "%" + query + "%")

        if genre is not None:
            sql += " AND genre LIKE ? "
            values += (genre,)
        if language is not None:
            sql += " AND language LIKE ? "
            values += (language,)
        if catalogue is not None:
            sql += " AND bookCatalogues.catalogueName LIKE ? "
            values += (catalogue,)

        sql += " ORDER BY " + sort + " LIMIT ? OFFSET ?"
        values += (limit, offset)
        try:
            cur.execute(sql, values)
        
            results = []
            for result in cur.fetchall():
                results.append({
                    "bookID": result[0],
                    "title": result[1],
                    "author": result[2],
                    "isbn": result[3],
                    "publisher": result[4],
                    "publicationDate": result[5],
                    "description": result[6],
                    "pageCount": result[7],
                    "language": result[8],
                    "genre": result[9],
                    "readingAge": result[10],
                    "coverURL": "/static/img/cover.jpg" if not result[11] else "/books/cover/" + result[11] + ".jpg"
                })
            con.close()
            return results
        except sqlite3.OperationalError:
            con.close()
    
    def addFile(self, bookID, file):
        """Save the file and update the database.

        Args:
            bookID(int): The ID of the book.
            file(bytes): The file to save."""
        hash = hashlib.md5(file).hexdigest()
        epubPath = os.path.join(self.directory, hash + ".epub")
        with open(epubPath, "wb") as f:
            f.write(file)

        with zipfile.ZipFile(epubPath) as epubFile:
            cover = None
            for item in epubFile.infolist():
                if re.match(r".*cover\.(png|jpg|jpeg)$", item.filename, re.IGNORECASE):
                    cover = item
                    break
            if not cover:
                for item in epubFile.infolist():
                    if re.match(r".*\.(png|jpg|jpeg)$", item.filename, re.IGNORECASE):
                        cover = item
                        break
            
            if cover:
                PIL.Image.open(epubFile.open(cover)
                    ).convert('RGB').resize((400, 600), PIL.Image.ANTIALIAS
                    ).save(os.path.join(self.directory, hash + ".jpg"), "JPEG")
                
        con, cur = self.connect()
        try:
            cur.execute("UPDATE books SET fileHash = ? WHERE bookID = ?", (hash, bookID))
        except sqlite3.IntegrityError:
            os.remove(epubPath)
            os.remove(os.path.join(self.directory, hash + ".jpg"))
            raise ValueError("Book does not exist.")
        finally:
            con.commit()
            con.close()


if __name__ == "__main__":
    db = database(os.path.join(os.path.dirname(__file__), "data"))
    db.executeScript("databaseStructure.sql")
