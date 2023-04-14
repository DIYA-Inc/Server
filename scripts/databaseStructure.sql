CREATE TABLE IF NOT EXISTS users (
    userID              INTEGER NOT NULL,
    email               VARCHAR(128) NOT NULL,
    passwordHash        VARCHAR(60) NOT NULL,
    userAccessLevel     INTEGER NOT NULL DEFAULT 0,
    created             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    premiumExpires      DATETIME,
    PRIMARY KEY (userID AUTOINCREMENT),
    UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS verificationTokens (
    tokenID             INTEGER NOT NULL,
    userID              INTEGER NOT NULL,
    verificationToken   VARCHAR(32) NOT NULL,
    PRIMARY KEY (tokenID AUTOINCREMENT),
    FOREIGN KEY (userID) REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS books (
    bookID              INTEGER NOT NULL,
    bookName            VARCHAR(128) NOT NULL,
    author              VARCHAR(64) NOT NULL,
    ISBN                VARCHAR(16) NOT NULL,
    publisher           VARCHAR(64),
    publicationDate     DATE,
    pageCount           INTEGER,
    language            VARCHAR(3),
    genre               VARCHAR(32),
    readingAge          INTEGER,
    description         TEXT,
    PRIMARY KEY (bookID AUTOINCREMENT),
    UNIQUE (ISBN)
);

CREATE TABLE IF NOT EXISTS bookCatalogues (
    catalogueID         INTEGER NOT NULL,
    catalogueName       VARCHAR(64) NOT NULL,
    PRIMARY KEY (catalogueID AUTOINCREMENT),
    UNIQUE (catalogueName)
);

CREATE TABLE IF NOT EXISTS bookCatalogueLink (
    bookCatalogueLinkID INTEGER NOT NULL,
    catalogueID         INTEGER NOT NULL,
    bookID              INTEGER NOT NULL,
    PRIMARY KEY (bookCatalogueLinkID AUTOINCREMENT),
    FOREIGN KEY (catalogueID) REFERENCES bookCatalogues(catalogueID),
    FOREIGN KEY (bookID) REFERENCES books(bookID)
);