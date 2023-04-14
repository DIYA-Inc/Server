#!/usr/bin/env python3

import os
import sys
import unittest

directory = os.path.dirname(os.path.realpath(__file__))
if "testing" == directory.split(os.sep)[-1]:
    sys.path.append(os.path.dirname(directory))

from server import createServer
from testing.utils import TestUtils


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
            self.assertTrue(400 <= register.status_code < 500)

        con, cur = self.db.connect()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        self.assertEqual(len(users), 1)

    def testLoginCorrect(self, email="sus@diya.ink", password="Chungus"):
        """Tests logging in with a correct email and password."""
        self.testRegister(email, password)
        login = self.client.post("/account/login", data={
            "email": email,
            "password": password
        })
        self.assertTrue(200 <= login.status_code < 400)
        self.assertTrue(
            self.client.cookie_jar._cookies["localhost.local"]["/"]["session"].value)

    def testLoginIncorrect(self, email="among@diya.ink", password="wordPass12"):
        """Tests logging in with an incorrect email and password."""
        self.testRegister(email, password)
        for email2 in (email, "bruh@diya.ink"):
            login = self.client.post("/account/login", json={
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


if __name__ == "__main__":
    unittest.main()
