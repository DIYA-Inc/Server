#!/usr/bin/env python3

import hashlib
import os
import sys
import unittest

directory = os.path.dirname(os.path.realpath(__file__))
if "testing" == directory.split(os.sep)[-1]:
    sys.path.append(os.path.dirname(directory))

from scripts.database import database
from testing.utils import TestUtils, sampleBookMetadata


class TestDatabase(TestUtils):
    def setUp(self):
        self.db = database(self.tempDataDir, self.randomString() + ".db")
        self.db.executeScript("databaseStructure.sql")

    def testStructure(self):
        """Check that the tabled were created without errors."""
        con, cur = self.db.connect()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        for table in ("users", "verificationTokens", "books", "bookCatalogues", "bookCatalogueLink"):
            self.assertIn((table,), tables)
        con.close()

    def testRegister(self, email="joe@joeblakeb.com", password="Password123"):
        """Check that the add user function works correctly."""
        self.db.addUser(email, password)
        con, cur = self.db.connect()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0][1], email)
        self.assertNotEqual(users[0][2], password)
        con.close()

    def testLogin(self):
        """Check that the login function works correctly."""
        email, password = "floppa@diya.ink", "B1ngus"
        self.testRegister(email, password)
        self.assertEqual(
            self.db.checkUser(email.upper(), password),
            (True, False, False, 1), "Correct login")

        con, cur = self.db.connect()
        cur.execute(
            "UPDATE users SET userAccessLevel = 1 WHERE email = ?", (email,))
        con.commit()
        self.assertEqual(
            self.db.checkUser(email, password),
            (True, True, False, 1), "Premium account")

        cur.execute(
            "UPDATE users SET userAccessLevel = 2 WHERE email = ?", (email,))
        con.commit()
        con.close()
        self.assertEqual(
            self.db.checkUser(email, password),
            (True, True, True, 1), "Admin account")

        self.assertEqual(
            self.db.checkUser(email, password.upper()),
            (False,), "Incorrect password")

        self.assertEqual(
            self.db.checkUser("example@test.com", password),
            (False,), "Incorrect email")

    def testAddBookMetadata(self):
        """Tests getting a book from the database."""
        for i in range(len(sampleBookMetadata)):
            self.assertEqual(i+1,
                             self.db.addBookMetadata(**sampleBookMetadata[i]))
        con, cur = self.db.connect()
        cur.execute("SELECT * FROM books")
        books = cur.fetchall()
        self.assertEqual(len(books), len(sampleBookMetadata))
        con.close()

    def testGetBookMetadata(self):
        """Tests getting a book from the database."""
        self.testAddBookMetadata()
        for i in range(len(sampleBookMetadata)):
            book = self.db.getBookMetadata(i+1)
            for key in sampleBookMetadata[i]:
                self.assertEqual(book[key], sampleBookMetadata[i][key])

    def testUpdateBookMetadata(self):
        """Tests updating a book in the database."""
        self.testAddBookMetadata()
        for i in range(len(sampleBookMetadata)-1):
            newData = {**sampleBookMetadata[i+1]}
            del newData["isbn"]
            self.db.updateBookMetadata(i+1, **newData)
            book = self.db.getBookMetadata(i+1)
            newBook = dict(sampleBookMetadata[i], **newData)
            for key in newBook:
                self.assertEqual(book[key], newBook[key])

    def testDeleteBook(self):
        """Tests deleting a book from the database."""
        self.testAddBookMetadata()
        for i in (1, 2):
            otherBook = self.db.getBookMetadata(i+1)
            self.db.deleteBook(i)
            self.assertRaises(Exception, self.db.getBookMetadata, i)
            self.assertEqual(self.db.getBookMetadata(i+1), otherBook)

    def testCatalogue(self):
        """Checks that catalogues are managed automatically."""
        self.testAddBookMetadata()
        con, cur = self.db.connect()
        cur.execute("SELECT * FROM bookCatalogues")
        catalogues = [c[1] for c in cur.fetchall()]
        self.assertEqual(catalogues, ["Computers", "Programming", "Linux"])
        for i in (2, 1):
            self.db.deleteBook(i)
            cur.execute("SELECT * FROM bookCatalogues")
            catalogues = [c[1] for c in cur.fetchall()]
            self.assertEqual(catalogues, ["Computers", "Linux"])
        self.db.deleteBook(3)
        cur.execute("SELECT * FROM bookCatalogues")
        self.assertEqual(cur.fetchall(), [])
        con.close()

    def testAddFile(self):
        """Tests adding a file to the database"""
        self.testAddBookMetadata()
        with open(os.path.join(os.path.dirname(__file__), "data/book.epub"), "rb") as file:
            fileData = file.read()
        hash = hashlib.md5(fileData).hexdigest()
        self.db.addFile(1, fileData)
        book = self.db.getBookMetadata(1)
        self.assertEqual(book["fileURL"], "/books/file/" + hash + ".epub")
        self.assertEqual(book["coverURL"], "/books/cover/" + hash + ".jpg")
        self.assertTrue(os.path.exists(os.path.join(self.tempDataDir, hash + ".epub")))
        self.assertTrue(os.path.exists(os.path.join(self.tempDataDir, hash + ".jpg")))
        self.assertEqual(fileData, open(os.path.join(self.tempDataDir, hash + ".epub"), "rb").read())
        self.db.deleteBook(1)
        self.assertFalse(os.path.exists(os.path.join(self.tempDataDir, hash + ".epub")))
        self.assertFalse(os.path.exists(os.path.join(self.tempDataDir, hash + ".jpg")))


if __name__ == "__main__":
    unittest.main()