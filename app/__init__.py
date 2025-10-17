from dotenv import load_dotenv
from flask import Flask

from .db.db import close_db
from .routes import register_routes

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    app.teardown_appcontext(close_db)
    register_routes(app)

    return app
