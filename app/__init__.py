from flask import Flask
from flasgger import Swagger

from .db.db import DB
from .db.redis import Cache
from .routes import register_routes
from .template import swagger_template
from .utils.init import init_dependencies
from .utils.logger import Loggger


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Swagger init
    Swagger(app, template=swagger_template)

    init_dependencies(app)

    app.teardown_appcontext(DB.close_db)
    app.teardown_appcontext(Cache.close_redis)

    register_routes(app)

    Loggger.info(f"All clear. App running on port {5005}...")

    return app
