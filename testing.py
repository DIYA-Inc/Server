#!/usr/bin/env python3

import random
import os
import shutil
import unittest
import warnings

from database import database
from server import createServer


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """Create temporary directory."""
        tempDataDir = "DIYA-Server-Test-" + self.randomString()

        if os.name == "posix":
            self.tempDataDir = "/tmp/" + tempDataDir + "/"
        else:
            self.tempDataDir = "./" + tempDataDir + "/"
        
        os.makedirs(self.tempDataDir, exist_ok=True)
        warnings.filterwarnings("ignore", category=Warning)

    @classmethod
    def tearDownClass(self):
        """Remove temporary directory for each set of tests."""
        shutil.rmtree(self.tempDataDir)

    def randomString(self=None): return str(hex(random.randint(0, 2**32)))[2:]


class TestServer(TestUtils):
    def setUp(self):
        app = createServer(self.tempDataDir, self.randomString() + ".db")
        app.config["TESTING"] = True
        self.client = app.test_client()

    def testMarkdownPages(self):
        """Check that the index and api reference pages are returned correctly."""
        index = self.client.get("/")
        self.assertEqual(index.status_code, 200)
        self.assertIn(b"D.I.Y.A. Inc.", index.data)
        self.assertIn(b"Team Members", index.data)
        apiRef = self.client.get("/api")
        self.assertEqual(apiRef.status_code, 404)
        self.assertIn(b"API Reference", apiRef.data)
        self.assertNotIn(b"[TOC]", apiRef.data)


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

    def testRegister(self, email="joe@joeblakeb.com", password="Password123"):
        """Check that the add user function works correctly."""
        self.db.addUser(email, password)
        con, cur = self.db.connect()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0][1], email)
        self.assertNotEqual(users[0][2], password)

    def testLogin(self):
        """Check that the login function works correctly."""
        email, password = "floppa@diya.ink", "B1ngus"
        self.testRegister(email, password)
        self.assertEqual(
            self.db.checkUser(email.upper(), password),
            (True, False, False), "Correct login")
        
        con, cur = self.db.connect()
        cur.execute("UPDATE users SET userAccessLevel = 1 WHERE email = ?", (email,))
        con.commit()
        self.assertEqual(
            self.db.checkUser(email, password),
            (True, True, False), "Premium account")

        cur.execute("UPDATE users SET userAccessLevel = 2 WHERE email = ?", (email,))
        con.commit()
        self.assertEqual(
            self.db.checkUser(email, password),
            (True, True, True), "Admin account")

        self.assertEqual(
            self.db.checkUser(email, password.upper()),
            (False, False, False), "Incorrect password")
        
        self.assertEqual(
            self.db.checkUser("example@test.com", password),
            (False, False, False), "Incorrect email")


if __name__ == "__main__":
    unittest.main()
