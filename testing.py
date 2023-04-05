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
        self.db = app.blueprints["api"].db

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

    def testRegister(self, email="joe@joeblakeb.com", password="Password123"):
        """Tests registering a new."""
        register = self.client.post("/account/register", json={
            "email": email,
            "password": password
        })
        self.assertEqual(register.status_code, 200)
        self.assertEqual(register.get_json()["success"], True)

    def testRegisterInvalid(self, email="mung@diya.ink", password="Amungus2"):
        """Server should not allow two users with the same email address."""
        self.testRegister(email, password)
        for email2 in (email, email.upper(), "invalid"):
            register = self.client.post("/account/register", json={
                "email": email2,
                "password": password
            })
            self.assertIn(register.status_code, (409, 422))
            self.assertEqual(register.get_json()["success"], False)

        con, cur = self.db.connect()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        self.assertEqual(len(users), 1)

    def testLoginCorrect(self, email="sus@diya.ink", password="Chungus"):
        """Tests logging in with a correct email and password."""
        self.testRegister(email, password)
        login = self.client.post("/account/login", json={
            "email": email,
            "password": password
        })
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.get_json(), {
            "success": True,
            "premium": False,
            "admin": False
        })
        self.assertTrue(self.client.cookie_jar._cookies["localhost.local"]["/"]["session"].value)

    def testLoginIncorrect(self, email="among@diya.ink", password="wordPass12"):
        """Tests logging in with an incorrect email and password."""
        self.testRegister(email, password)
        for email2 in (email, "bruh@diya.ink"):
            login = self.client.post("/account/login", json={
                "email": email2,
                "password": password.upper()
            })
            self.assertEqual(login.status_code, 401)
            self.assertFalse(login.get_json()["success"])
            self.assertNotIn("localhost.local", self.client.cookie_jar._cookies)

    def testLogout(self, email="test@example.com", password="PassWord123"):
        """Tests logging in and then out."""
        self.testLoginCorrect(email, password)
        logout = self.client.get("/account/logout")
        self.assertEqual(logout.status_code, 200)
        details = self.client.get("/account/details")
        self.assertEqual(details.status_code, 401)

    def testDetails(self, email="joe@diya.ink", password="CorrectHorseBatteryStaple"):
        """Tests getting user details."""
        self.testLoginCorrect(email, password)
        details = self.client.get("/account/details")
        self.assertEqual(details.status_code, 200)
        json = details.get_json()
        self.assertEqual(json["email"], email)
        self.assertFalse(json["premium"])
        self.assertFalse(json["admin"])
        self.assertIn("created", json)

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
            (True, False, False, 1), "Correct login")
        
        con, cur = self.db.connect()
        cur.execute("UPDATE users SET userAccessLevel = 1 WHERE email = ?", (email,))
        con.commit()
        self.assertEqual(
            self.db.checkUser(email, password),
            (True, True, False, 1), "Premium account")

        cur.execute("UPDATE users SET userAccessLevel = 2 WHERE email = ?", (email,))
        con.commit()
        self.assertEqual(
            self.db.checkUser(email, password),
            (True, True, True, 1), "Admin account")

        self.assertEqual(
            self.db.checkUser(email, password.upper()),
            (False,), "Incorrect password")
        
        self.assertEqual(
            self.db.checkUser("example@test.com", password),
            (False,), "Incorrect email")


if __name__ == "__main__":
    unittest.main()
