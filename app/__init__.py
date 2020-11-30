"""Entrypoint to the expenses application"""

import os

import flask
from flask import g, Flask
from flask_sqlalchemy import SQLAlchemy

from oso import Oso

from . import authorization, expense, organization, user, graphql
from .models import db

app = Flask(__name__)
oso = Oso()


def log_queries():
    import logging

    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='sqlite:///../expenses.db',
        OSO_POLICIES=["app/authorization.polar"]
    )

    db.init_app(app)

    # register user handlers
    app.register_blueprint(user.bp)
    # register expenses routes
    app.register_blueprint(expense.bp)
    # register organizations routes
    app.register_blueprint(organization.bp)
    # register authorization handlers
    app.register_blueprint(authorization.bp)
    app.register_blueprint(graphql.bp)
    authorization.init_oso(app)

    #### Simple test route
    @app.route("/")
    def hello():
        return f"hello {g.current_user}"

    log_queries()

    return app


def drop_into_pdb(app, exception):
    import sys
    import pdb
    import traceback

    traceback.print_exc()
    pdb.post_mortem(sys.exc_info()[2])


# somewhere in your code (probably if DEBUG is True)
flask.got_request_exception.connect(drop_into_pdb)

app = create_app()
