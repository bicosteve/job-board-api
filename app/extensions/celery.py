import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

broker_url = "amqp://{user}:{password}@{host}:{port}/{vhost}".format(
    user=RABBITMQ_USER,
    password=RABBITMQ_PASSWORD,
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    vhost=RABBITMQ_VHOST,
)

result_backend = "redis://{host}:{port}/{db}".format(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
)

celery = Celery(__name__, broker=broker_url, backend=result_backend)
flask_app = None  # will be populated by create_app()
