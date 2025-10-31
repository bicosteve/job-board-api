import os

from dotenv import load_dotenv
from flask import Flask
from flasgger import Swagger

from .db.db import close_db
from .routes import register_routes
from .template import swagger_template
from .utils.init import init_dependencis
from .utils.logger import Loggger

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Swagger init
    Swagger(app, template=swagger_template)

    init_dependencis(app)

    app.teardown_appcontext(close_db)
    register_routes(app)

    Loggger.info(
        f'Allez klarr. Starting app on port {os.getenv('APP_PORT', 5005)}')

    return app
