import os
import ssl
from pathlib import Path
from urllib.parse import urlparse

import pika
from flasgger import Swagger
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import DevelopmentConfig, DockerConfig, ProductionConfig
from .db.db import DB
from .db.redis import Cache
from .extensions.celery import celery
from .extensions.limiter import init_limiter
from .queues.queue import RabbitMQ
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
    app.config["APPLICATION_ROOT"] = "/job-board-api/v1/api"
    app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1, x_host=1)
    Swagger(
        app,
        config={
            "specs_route": "/job-board-api/v1/api/apidocs/",
            "url_prefix": "/job-board-api/v1/api",
        },
        template=swagger_template,
    )

    # Enable cross origin requests
    CORS(app)

    # Rate limiting (Redis-backed) for sensitive auth endpoints
    init_limiter(app)

    init_dependencies(app)

    app.config.setdefault("UPLOAD_FOLDER", app.config.get("UPLOAD_FOLDER", "uploads"))
    upload_folder = app.config["UPLOAD_FOLDER"]
    if not Path(upload_folder).is_absolute():
        upload_folder = str(Path(app.root_path) / upload_folder)
        app.config["UPLOAD_FOLDER"] = upload_folder
    Path(upload_folder).mkdir(parents=True, exist_ok=True)

    # Create rabbitmq connection just once when the app starts
    broker_url = app.config.get("CELERY_BROKER_URL")
    if not broker_url:
        raise ValueError("RABBITMQ_URI not provided...!")

    if broker_url:
        parsed = urlparse(broker_url)
        use_tls = parsed.scheme == "amqps"
        parameters = (
            pika.ConnectionParameters(
                host=parsed.hostname,
                port=parsed.port or (5671 if use_tls else 5672),
                virtual_host=parsed.path.lstrip("/") or "/",
                credentials=pika.PlainCredentials(
                    username=parsed.username, password=parsed.password
                ),
                ssl_options=(
                    pika.SSLOptions(ssl.create_default_context()) if use_tls else None
                ),
            ),
        )

    else:
        # Fallback plan for local dev env
        parameters = pika.ConnectionParameters(
            host=app.config.get("RABBITMQ_HOST", "localhost"),
            port=app.config.get("RABBITMQ_PORT", 5672),
            virtual_host=app.config.get("RABBITMQ_VHOST", "/"),
            credentials=pika.PlainCredentials(
                username=app.config.get("RABBITMQ_USER", "guest"),
                password=app.config.get("RABBITMQ_PASSWORD", "guest"),
            ),
        )

    app.extensions["rabbitmq_connection"] = pika.BlockingConnection(parameters)

    # celery.conf.update(app.config)
    # celery_ext.flask_app = app

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask  # must be before mails.py is imported!

    app.teardown_appcontext(DB.close_db)
    app.teardown_appcontext(Cache.close_redis)
    app.teardown_appcontext(RabbitMQ.close_rabbitmq)

    from .routes import register_routes

    # here because of celery as it import mails.py!

    register_routes(app)

    Logger.info(f"All clear. App running on port {5005}...")

    return app
