import os
from pathlib import Path

import pika
from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from . import celery_app

# from .celery_app import celery_app
from .config import DevelopmentConfig, DockerConfig, ProductionConfig
from .db.db import DB
from .db.redis import Cache
from .queues.queue import RabbitMQ
from .routes import register_routes
from .template import swagger_template
from .utils.init import init_dependencies
from .utils.logger import Logger


def create_app():
    app = Flask(__name__)

    env = os.getenv("ENV", "dev").lower()

    config_map = {
        "docker": DockerConfig,
        "prod": ProductionConfig,
        "dev": DevelopmentConfig,
    }

    # Load the correct config
    app.config.from_object(config_map.get(env, DevelopmentConfig))

    # Swagger init
    Swagger(app, template=swagger_template)

    # Enable cross origin requests
    CORS(app)

    init_dependencies(app)

    app.config.setdefault("UPLOAD_FOLDER", app.config.get("UPLOAD_FOLDER", "uploads"))
    upload_folder = app.config["UPLOAD_FOLDER"]
    if not Path(upload_folder).is_absolute():
        upload_folder = str(Path(app.root_path) / upload_folder)
        app.config["UPLOAD_FOLDER"] = upload_folder
    Path(upload_folder).mkdir(parents=True, exist_ok=True)

    # Create rabbitmq connection just once when the app starts
    app.extensions["rabbitmq_connection"] = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=app.config["RABBITMQ_HOST"],
            port=app.config["RABBITMQ_PORT"],
            credentials=pika.PlainCredentials(
                username=app.config["RABBITMQ_USER"],
                password=app.config["RABBITMQ_PASSWORD"],
            ),
        )
    )

    celery_app.conf.update(app.config)

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask

    app.teardown_appcontext(DB.close_db)
    app.teardown_appcontext(Cache.close_redis)
    app.teardown_appcontext(RabbitMQ.close_rabbitmq)

    register_routes(app)

    Logger.info(f"All clear. App running on port {5005}...")

    return app
