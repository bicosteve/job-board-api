from dotenv import load_dotenv
from flask import Flask
from flasgger import Swagger

from .db.db import close_db
from .routes import register_routes
from .template import swagger_template

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Swagger init
    Swagger(app, template=swagger_template)

    app.teardown_appcontext(close_db)
    register_routes(app)

    return app
