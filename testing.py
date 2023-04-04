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


if __name__ == "__main__":
    unittest.main()
