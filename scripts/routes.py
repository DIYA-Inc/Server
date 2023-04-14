#!/usr/bin/env python3

import flask

import scripts.accountRoutes as accountRoutes
import scripts.mainRoutes as mainRoutes

def setUpRoutes(app):
    for route in [accountRoutes, mainRoutes]:
        app.register_blueprint(route.diya)
        route.db = app.db
    
    app.register_error_handler(404, mainRoutes.errorPage)

    return app


if "__main__" == __name__:
    import scripts.database as database
    db = database.database()
