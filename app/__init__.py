import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from .db import close_db
from .routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    app.teardown_appcontext(close_db)
    register_routes(app)

    return app
