import ssl
from urllib.parse import urlparse

import pika
from flask import current_app, g


class RabbitMQ:

    @staticmethod
    def connect_rabbitmq():
        """
        Returns a rabbitmq channel bound to the current context.
        Reuse it if already exists in global request context (g).
        (g) only exists for a lifetime of a request
        """

        if "rabbitmq_channel" not in g:
            broker_url = (
                current_app.config["CELERY_BROKER_URL"]
                or current_app.config["RABBITMQ_URL"]
            )

            if broker_url:
                parsed = urlparse(broker_url)
                use_tls = parsed.scheme == "amqps"
                credentials = pika.PlainCredentials(
                    username=parsed.username,
                    password=parsed.password,
                )

                parameters = pika.ConnectionParameters(
                    host=parsed.hostname,
                    port=parsed.port or (5671 if use_tls else 5672),
                    virtual_host=parsed.path.lstrip("/") or "/",
                    credentials=credentials,
                    ssl_options=(
                        pika.SSLOptions(ssl.create_default_context())
                        if use_tls
                        else None
                    ),
                )

            else:
                # Fallback to individual config values (local dev)
                credentials = pika.PlainCredentials(
                    username=current_app.config.get("RABBITMQ_USER", "guest"),
                    password=current_app.config.get("RABBITMQ_PASSWORD", "guest"),
                )
                parameters = pika.ConnectionParameters(
                    host=current_app.config.get("RABBITMQ_HOST", "localhost"),
                    port=current_app.config.get("RABBITMQ_PORT", 5672),
                    virtual_host=current_app.config.get("RABBITMQ_VHOST", "/"),
                    credentials=credentials,
                )

            connection = pika.BlockingConnection(parameters=parameters)

            g.rabbitmq_connection = connection
            g.rabbitmq_channel = connection.channel()

        return g.rabbitmq_channel

    @staticmethod
    def close_rabbitmq(e=None):
        """Close RabbitMQ connection at the end of the request"""
        connection = g.pop("rabbitmq_connection", None)
        g.pop("rabbitmq_channel", None)
        if connection is not None and connection.is_open:
            connection.close()
