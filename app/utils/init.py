import ssl
import sys
import time
from urllib.parse import urlparse

import pika
import pymysql
import redis

from .logger import Logger


def retry_connection(func, retries=10, delay=3, backoff=2):
    """
    A wrapper for connection attempts.
    - retries: number of retry attempts
    - delay: initial delay in seconds
    - backoff: multiplier for exponential backoff
    """
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == retries:
                raise e
            Logger.warn(f"Attempt {attempt} failed. Retrying in {delay}s..")
            time.sleep(delay)
            delay *= backoff


def check_db(app):
    def connect_db():
        conn = None
        try:
            conn = pymysql.connect(
                host=app.config["DB_HOST"],
                port=int(app.config["DB_PORT"]),
                user=app.config["DB_USER"],
                password=app.config["DB_PASSWORD"],
                database=app.config["DB_NAME"],
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                ssl={},
                connect_timeout=5,
            )

            Logger.info("DB connection success")

        except Exception as e:
            Logger.exception(f"An error occured {str(e)}")
            raise
        finally:
            if conn is not None:
                conn.close()

    retry_connection(connect_db)


def check_cache(app):
    def connect_redis():
        client = None
        try:
            redis_url = app.config.get("REDIS_URL")
            if not redis_url:
                raise ValueError("REDIS_URL not provided")
            if redis_url:
                client = redis.from_url(
                    redis_url, decode_responses=True, socket_connect_timeout=5
                )
            else:
                # Fallback to individual ocnfig values (local dev)
                # password = app.config.get("REDIS_PASSWORD")
                client = redis.Redis(
                    host=app.config.get("REDIS_HOST", "localhost"),
                    port=app.config.get("REDIS_PORT", 6379),
                    db=app.config.get("REDIS_DB", 0),
                    # password=password if password else None,
                    socket_connect_timeout=5,
                )

            if client is not None:
                result = client.ping()
                Logger.info(f"Redis connection success with {result}")
            else:
                Logger.error("Redis connection not success")
        except Exception as e:
            Logger.exception(f"Something went wrong {str(e)}")
            raise
        finally:
            if client is not None:
                client.close()

    retry_connection(connect_redis)


def check_broker(app):
    def connect_rabbitmq():
        connection = None
        channel = None

        try:
            # Use full broker URL if provided
            broker_url = app.config.get("CELERY_BROKER_URL")
            if not broker_url:
                raise ValueError("RABBITMQ_URL is missing!")

            if broker_url:
                parsed = urlparse(broker_url)

                print(f"DEBUG: Parsed host={parsed.host}, port={parsed.port}")

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
                password = app.config["RABBITMQ_PASSWORD"]
                if password:
                    credentials = pika.PlainCredentials(
                        username=app.config["RABBITMQ_USER"],
                        password=password,
                    )
                    parameters = pika.ConnectionParameters(
                        host=app.config.get("RABBITMQ_HOST", "localhost"),
                        port=app.config.get("RABBITMQ_PORT", 5672),
                        virtual_host=app.config.get("RABBITMQ_VHOST", "/"),
                        credentials=credentials,
                    )
                else:
                    parameters = pika.ConnectionParameters(
                        host=app.config.get("RABBITMQ_HOST", "localhost"),
                        port=app.config.get("RABBITMQ_PORT", 5672),
                    )

            connection = pika.BlockingConnection(parameters=parameters)
            channel = connection.channel()

            if channel.is_open:
                Logger.info("RabbitMQ connection success")
            else:
                Logger.error("RabbitMQ connection not successful")
        except Exception as e:
            Logger.exception(f"Something went wrong {str(e)}")
            raise
        finally:
            if connection is not None and connection.is_open:
                connection.close()

    retry_connection(connect_rabbitmq)


def init_dependencies(app):
    """
    Verify core services like (DB, Redis, Message Brokers)
    are reachable with retry logic.
    """

    Logger.info("Checking dependencies...")

    # ==== 1. Check MySQL ====
    try:
        check_db(app)
    except Exception as e:
        Logger.error(f"DB connection failed becase of: {str(e)}")
        sys.exit(1)

    # ==== 2. Check Redis ====
    try:
        check_cache(app)
    except Exception as e:
        Logger.error(f"Redis connection failed because of {str(e)}")
        sys.exit(1)

    # ==== 3. Check RabbitMQ ====
    try:
        check_broker(app)
    except Exception as e:
        Logger.error(f"RabbitMQ connection failed because of {str(e)}")
        sys.exit(1)
