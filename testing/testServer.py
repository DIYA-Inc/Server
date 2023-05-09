#!/usr/bin/env python3

import os
import re
import sys
import unittest

directory = os.path.dirname(os.path.realpath(__file__))
if "testing" == directory.split(os.sep)[-1]:
    sys.path.append(os.path.dirname(directory))

from server import createServer
from testing.utils import TestUtils, sampleBookMetadata


class TestServer(TestUtils):
    def setUp(self):
        app = createServer(self.tempDataDir, self.randomString() + ".db")
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.db = app.db

    def testRegister(self, email="joe@joeblakeb.com", password="Password123"):
        """Tests registering a new."""
        register = self.client.post("/account/register", data={
            "email": email,
            "password": password
        })
        self.assertTrue(200 <= register.status_code < 400)

    def testRegisterInvalid(self, email="mung@diya.ink", password="Amungus2"):
        """Server should not allow two users with the same email address."""
        self.testRegister(email, password)
        for email2 in (email, email.upper(), "invalid"):
            register = self.client.post("/account/register", data={
                "email": email2,
                "password": password
            })
            self.assertTrue(400 <= register.status_code <
                            500, register.status_code)

        con, cur = self.db.connect()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        con.close()
        self.assertEqual(len(users), 1)

    def testLoginCorrect(self, email="sus@diya.ink", password="Chungus"):
        """Tests logging in with a correct email and password."""
        self.testRegister(email, password)
        login = self.client.post("/account/login", data={
            "email": email,
            "password": password
        })
        self.assertTrue(200 <= login.status_code < 400)
        try:
            self.assertTrue(
                self.client.cookie_jar._cookies["localhost.local"]["/"]["session"].value)
        except AttributeError:
            self.assertTrue(len(self.client._cookies))

    def testLoginAdmin(self, email="admintest@diya.ink", password="Ligma222"):
        """Tests logging in as an admin"""
        self.testRegister(email, password)
        con, cur = self.db.connect()
        cur.execute(
            "UPDATE users SET userAccessLevel=2 WHERE email=?", (email,))
        con.commit()
        con.close()
        login = self.client.post("/account/login", data={
            "email": email,
            "password": password
        })
        self.assertTrue(200 <= login.status_code < 400)

    def testLoginIncorrect(self, email="among@diya.ink", password="wordPass12"):
        """Tests logging in with an incorrect email and password."""
        self.testRegister(email, password)
        for email2 in (email, "bruh@diya.ink"):
            login = self.client.post("/account/login", data={
                "email": email2,
                "password": password.upper()
            })
            self.assertTrue(400 <= login.status_code < 500)

    def testLogout(self, email="test@example.com", password="PassWord123"):
        """Tests logging in and then out."""
        self.testLoginCorrect(email, password)
        logout = self.client.get("/account/logout")
        self.assertTrue(200 <= logout.status_code < 400)
        details = self.client.get("/account/details")
        self.assertTrue(300 <= details.status_code < 500)

    def testDetails(self, email="joe@diya.ink", password="CorrectHorseBatteryStaple"):
        """Tests getting user details."""
        self.testLoginCorrect(email, password)
        details = self.client.get("/account/details")
        self.assertEqual(details.status_code, 200)

    def testDeleteAccount(self, email="delete@account.com", password="Password123"):
        """Tests deleting an account."""
        self.testLoginCorrect(email, password)
        delete = self.client.delete("/account/delete")
        self.assertTrue(200 <= delete.status_code < 400)
        details = self.client.get("/account/details")
        self.assertTrue(300 <= details.status_code < 500)
        loginAgain = self.client.post("/account/login", data={
            "email": email,
            "password": password
        })
        self.assertTrue(400 <= loginAgain.status_code < 500)
        self.testLoginCorrect(email, password)

    def testAddBook(self):
        """Tests adding and viewing a book."""
        self.testLoginCorrect()
        addBook = self.client.post("/admin/books/add",
            data=sampleBookMetadata[1])
        self.assertTrue(400 <= addBook.status_code < 500)
        self.testLoginAdmin()
        for book in sampleBookMetadata:
            if "catalogues" in book:
                book = book.copy()
                book["catalogues"] = ", ".join(book["catalogues"])
            addBook = self.client.post("/admin/books/add", data=book)
            self.assertTrue(300 <= addBook.status_code < 400)
            viewBook = self.client.get(addBook.headers["Location"])
            self.assertTrue(200 <= viewBook.status_code < 300)
            page = viewBook.data.decode()
            for field in book:
                if (type(book[field]) == str and
                        re.match(r'^[ a-zA-Z0-9]+$', book[field])):
                    self.assertIn(book[field], page)

    def testEditBook(self):
        """Tests editing a book."""
        self.testLoginAdmin()
        addBook = self.client.post("/admin/books/add", data={
            **sampleBookMetadata[1],
            "catalogues": ", ".join(sampleBookMetadata[1]["catalogues"])})
        self.assertTrue(200 <= addBook.status_code < 400)
        editBook = self.client.post("/admin/books/edit/1", data={
            **sampleBookMetadata[2],
            "catalogues": ", ".join(sampleBookMetadata[2]["catalogues"])})
        self.assertTrue(200 <= editBook.status_code < 400)
        book = self.db.getBookMetadata(1)
        del book["fileURL"]
        del book["coverURL"]
        bookShouldBe = {
            **sampleBookMetadata[1],
            **sampleBookMetadata[2],
            "bookID": 1}
        self.assertEqual(book, bookShouldBe)

    def testDeleteBook(self):
        """Tests deleting a book."""
        self.testAddBook()
        deleteBook = self.client.delete("/admin/books/delete/1")
        self.assertEqual(deleteBook.status_code, 200)
        self.assertRaises(ValueError, self.db.getBookMetadata, 1)

    def testSearch(self):
        """Tests searching for books."""
        self.testAddBook()
        for query, expectedBooks in (
            ("", [1, 2, 3]),
            ("query=learning", [2]),
            ("query=learning&catalogue=computers", [2]),
            ("query=learning&genre=programming", [2]),
            ("query=learning&catalogue=mung", []),
            ("catalogue=computers", [2, 3]),
            ("query=ORWELL", [1]),
            ("query=ORWELL&catalogue=computers", []),
            ("language=en", [2]),
            ("language=en&catalogue=computers", [2]),
            ("catalogue=linux", [3]),
            ("genre=programming", [2]),
            ("limit=1", [1]),
            ("limit=1&offset=1", [2]),
            ("limit=1&offset=2", [3]),
        ):
            search = self.client.get("/api/books/search?" + query)
            self.assertEqual(search.status_code, 200)
            responseBookIDs = [book["bookID"] for book in search.json]
            self.assertEqual(responseBookIDs, expectedBooks, query)

    def testAddFileNew(self):
        """Tests uploading a file to a new book."""
        self.testLoginAdmin()
        with open(os.path.join(os.path.dirname(
                __file__), "data/book.epub"), "rb") as file:
            addBook = self.client.post("/admin/books/add", data={
                **sampleBookMetadata[1],
                "catalogues": ", ".join(sampleBookMetadata[1]["catalogues"]),
                "file": file},
                content_type="multipart/form-data")
        
        return self.verifyFileAdded(addBook)

    def testAddFileEdit(self):
        """Tests uploading a file to an existing book."""
        self.testAddBook()
        with open(os.path.join(os.path.dirname(
                __file__), "data/book.epub"), "rb") as file:
            editBook = self.client.post("/admin/books/edit/1", data={
            "file": file},
            content_type="multipart/form-data")

        self.verifyFileAdded(editBook)

    def verifyFileAdded(self, response):
        """Check that an epub file was added correctly."""
        self.assertTrue(300 <= response.status_code < 400)
        getBook = self.client.get(response.headers["Location"])
        self.assertTrue(200 <= getBook.status_code < 300)
        imageUrl = re.search(r'src="/books/cover/.*?\.jpg"', getBook.data.decode()).group(0)[5:-1]

        getImage = self.client.get(imageUrl)
        self.assertTrue(200 <= getImage.status_code < 300)

        getEpub = self.client.get(imageUrl.replace(
            "cover", "file").replace(".jpg", ".epub"))
        self.assertTrue(200 <= getEpub.status_code < 300)

        return imageUrl

    def testFileDelete(self):
        """Tests adding a book with a file, then deleting to verify the file is gone."""
        imageUrl = self.testAddFileNew()
        imageBeforeDelete = self.client.get(imageUrl).data
        deleteBook = self.client.delete("/admin/books/delete/1")
        self.assertTrue(200 <= deleteBook.status_code < 400)
        imageAfterDelete = self.client.get(imageUrl)
        self.assertNotEqual(imageBeforeDelete, imageAfterDelete.data)


if __name__ == "__main__":
    unittest.main()
