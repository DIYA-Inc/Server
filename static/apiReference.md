# D.I.Y.A. Inc. Book Server API Reference 

[TOC]

# Accounts

## Login

HTTP POST [/account/login](/account/login)

Request:

```json
{
    "email": "case insensitive",
    "password": "case sensitive"
}
```

A cookie will be set on the client with the session token.

Response:

```json
{
    "success": true,
    "premium": true,
    "admin": false
}
```

Response Status Codes:
- `200` - Success
- `401` - Not successful
- `422` - Invalid JSON

## Register

HTTP POST [/account/register](/account/register)

Request:

```json
{
    "email": "case insensitive",
    "password": "case sensitive"
}
```

Response:

```json
{
    "success": true
}
```

Response Status Codes:
- `200` - Success
- `409` - User already exists
- `422` - Invalid JSON

## Account Details

HTTP GET [/account/details](/account/details)

Get details about the current logged in user.

Response:

```json
{
    "email": "case insensitive",
    "premium": true,
    "admin": false,
    "created": "2023-03-31 00:00:00",
    "premiumExpires": "2023-05-31 00:00:00"
}
```

Response Status Codes:
- `200` - Success
- `401` - Not Authorized

## Logout

HTTP GET [/account/logout](/account/logout)

Response:

```json
{
    "success": true
}
```

Response Status Codes:
- `200` - Success

## Verify Account [NOT IMPLEMENTED]

HTTP GET [/account/verify](/account/verify)

Request:

```
/account/verify?user=<LowercaseEmailHash>&token=<Token>
```

The request url will be provided to the user via an email, they will need to click the link to verify their account.

Response:

```
Success, your account has been verified!
```

Response Status Codes:
- `200` - Success
- `401` - Not successful

## Update Account [NOT IMPLEMENTED]

HTTP PUT [/account/update](/account/update)

Request:

```json
{
    "oldPassword": "case sensitive",
    "newEmail": "case insensitive",
    "newPassword": "case sensitive"
}
```

Response:

```json
{
    "success": true
}
```

Response Status Codes:
- `200` - Success
- `401` - Not Authorized
- `422` - Invalid JSON

## Delete Account [NOT IMPLEMENTED]

HTTP DELETE [/account/update](/account/update)

Request:

```json
{
    "password": "case sensitive"
}
```

Response:

```json
{
    "success": true
}
```

Response Status Codes:
- `200` - Success
- `401` - Not Authorized
- `422` - Invalid JSON

# Books [NOT IMPLEMENTED]

## Get Book [NOT IMPLEMENTED]

HTTP GET [/book/get/[bookID]](/book/get/0)

Response:

```json
{
    "id": 1,
    "title": "Book Title",
    "author": "Book Author",
    "description": "Book Description",
    "cover": "Book Cover URL",
    "fileURL": "Book File URL",
    "publisher": "Book Publisher",
    "published": "2023-03-31 00:00:00",
    "pages": 100,
    "language": "English",
    "genre": "Book Genre",
    "catalogues": ["Book Catalogue List"],
    "reading age": 18,
    "ISBN": "978-3-16-148410-0"
}
```

Response Status Codes:
- `200` - Success
- `404` - Book not found

## Search [NOT IMPLEMENTED]

HTTP GET [/book/search?q=[query]&c=[catalogue]&g=[genre]](/book/search)

If no query is provided, recommended books will be returned.

Catalogue and Genre are optional.

Response:

```json
[
    {
        "id": 1,
        "title": "Book Title",
        "author": "Book Author",
        "description": "Book Description",
        "cover": "Book Cover URL",
        "fileURL": "Book File URL",
        "publisher": "Book Publisher",
        "published": "2023-03-31 00:00:00",
        "pages": 100,
        "language": "English",
        "genre": "Book Genre",
        "catalogues": ["Book Catalogue List"],
        "reading age": 18,
        "ISBN": "978-3-16-148410-0"
    },
    {
        "id": 2,
        "title": "Book Title",
        "author": "Book Author",
        "description": "Book Description",
        "cover": "Book Cover URL",
        "fileURL": "Book File URL",
        "publisher": "Book Publisher",
        "published": "2023-03-31 00:00:00",
        "pages": 100,
        "language": "English",
        "genre": "Book Genre",
        "catalogues": ["Book Catalogue List"],
        "reading age": 18,
        "ISBN": "978-3-16-148410-0"
    }
]
```

Response Status Codes:
- `200` - Success
- `422` - Invalid JSON

## Add Book [NOT IMPLEMENTED]

HTTP POST [/book/add](/book/add)

```diff
- User must be admin to access this endpoint -
```

Request:
```json
{
    "title": "Book Title",
    "author": "Book Author",
    "description": "Book Description",
    "cover": "Book Cover URL",
    "fileURL": "Book File URL",
    "publisher": "Book Publisher",
    "published": "2023-03-31 00:00:00",
    "pages": 100,
    "language": "English",
    "genre": "Book Genre",
    "catalogues": ["Book Catalogue List"],
    "reading age": 18,
    "ISBN": "978-3-16-148410-0"
}
```

Response:

```json
{
    "success": true,
    "bookID": 1
}
```

Response Status Codes:
- `200` - Success
- `401` - Not Authorized
- `404` - Book not found
- `422` - Invalid JSON

## Edit Book [NOT IMPLEMENTED]

HTTP PUT [/book/edit/[bookID]](/book/edit)

```diff
- User must be admin to access this endpoint -
```

Request:
```json
{
    "title": "Book Title",
    "author": "Book Author",
    "description": "Book Description",
    "cover": "Book Cover URL",
    "fileURL": "Book File URL",
    "publisher": "Book Publisher",
    "published": "2023-03-31 00:00:00",
    "pages": 100,
    "language": "English",
    "genre": "Book Genre",
    "catalogues": ["Book Catalogue List"],
    "reading age": 18,
    "ISBN": "978-3-16-148410-0"
}
```

Only changed fields need to be provided.

Response:

```json
{
    "success": true
}
```

Response Status Codes:
- `200` - Success
- `401` - Not Authorized
- `404` - Book not found
- `422` - Invalid JSON

## Delete Book [NOT IMPLEMENTED]

HTTP DELETE [/book/delete/[bookID]](/book/delete)

```diff
- User must be admin to access this endpoint -
```

Response:

```json
{
    "success": true
}
```

Response Status Codes:
- `200` - Success
- `401` - Not Authorized
- `404` - Book not found
- `422` - Invalid JSON

# Book Files [NOT IMPLEMENTED]

Book files are automatically deleted after a book is deleted at [Delete Book](#delete-book).

## Get Book File [NOT IMPLEMENTED]

HTTP GET [/file/book/[bookID]](/file/book/0)

Responds with the book file in ePub format.

Response Status Codes:
- `200` - Success
- `404` - Book not found

## Get Book Cover [NOT IMPLEMENTED]

HTTP GET [/file/cover/[bookID]](/file/cover/0)

Responds with the book cover in jpeg format.

Response Status Codes:
- `200` - Success
- `404` - Book not found

## Upload Book File [NOT IMPLEMENTED]

HTTP PUT [/file/upload/[bookID]](/file/upload/0)

```diff
- User must be admin to access this endpoint -
```

Request:

The book file as ePub format. The cover will be extracted from the ePub file.

Response:

```json
{
    "success": true,
    "fileURL": "Book File URL"
}
```

Response Status Codes:
- `200` - Success
- `401` - Not Authorized
- `404` - Book not found