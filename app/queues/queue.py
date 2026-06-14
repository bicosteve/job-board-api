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

        print("celery url", current_app.config["CELERY_BROKER_URL"])

        if "rabbitmq_channel" not in g:
            credentials = pika.PlainCredentials(
                username=current_app.config["RABBITMQ_USER"],
                password=current_app.config["RABBITMQ_PASSWORD"],
            )

            parameters = pika.ConnectionParameters(
                host=current_app.config["RABBITMQ_HOST"],
                port=current_app.config["RABBITMQ_PORT"],
                virtual_host=current_app.config["RABBITMQ_VHOST"],
                credentials=credentials,
            )

            connection = pika.BlockingConnection(parameters=parameters)

            g.rabbitmq_connection = connection
            g.rabbitmq_channel = connection.channel()

        return g.rabbimq_channel

    @staticmethod
    def close_rabbitmq(e=None):
        """Close RabbitMQ connection at the end of the request"""
        connection = g.pop("rabbimtmq_connection", None)
        g.pop("rabbitmq_channel", None)
        if connection is not None and connection.is_open:
            connection.close()
