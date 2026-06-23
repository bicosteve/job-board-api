import os
import ssl

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# ===== RabbitMQ / Broker =====
broker_url = os.getenv("CELERY_BROKER_URL") or os.getenv("RABBITMQ_URL")
if not broker_url:
    user = RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    password = RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    host = RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    port = RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
    vhost = RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
    scheme = "amqps" if os.getenv("RABBITMQ_TLS", "false").lower() == "true" else "amqp"
    broker_url = f"{scheme}://{user}:{password}@{host}:{port}/{vhost}"


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_PASSWORD = os.getenv("REDDIS_PASSWORD", "")

# ====== Redis / Result Backend

result_backend = os.getenv("CELERY_RESULT_BACKEND") or os.getenv("REDIS_URL")
if not result_backend:
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    db = os.getenv("REDIS_DB", "0")
    password = os.getenv("REDIS_PASSWORD", "")
    username = os.getenv("REDIS_USERNAME", "default")
    scheme = "rediss" if password else "redis"
    auth = f"{username}:{password}@" if password else ""
    result_backend = f"{scheme}://{auth}{host}:{port}/{db}"


celery = Celery(
    __name__,
    broker=broker_url,
    backend=result_backend,
)

if broker_url.startswith("amqps://"):
    # SSL settings for
    celery.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}

if result_backend.startswith("rediss://"):
    celery.conf.redis_backend_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}


flask_app = None  # will be populated by create_app()
