#!/usr/bin/env python3

import random
import os
import shutil
import unittest
import warnings


sampleBookMetadata = [
    {
        "title": "1984",
        "author": "George Orwell",
        "isbn": "978-0451524935"
    },
    {
        "title": "Learning Android",
        "author": "Marko Gargenta",
        "isbn": "978-1449331818",
        "publisher": "O'Reilly Media, Inc.",
        "publicationDate": "2011-12-19",
        "description": "Make android apps innit",
        "pageCount": 400,
        "language": "en",
        "genre": "Programming",
        "readingAge": 16,
        "catalogues": ["Computers", "Programming"]
    },
    {
        "title": "Linux Bible",
        "author": "Christopher Negus",
        "isbn": "978-1118999875",
        "catalogues": ["Computers", "Linux"]
    }
]


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
