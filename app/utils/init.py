import sys
import time

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
            Logger.info(f"db-host {current_app.config["DB_HOST"]}")
            Logger.info(f"db-port {current_app.config["DB_PORT"]}")
            Logger.info(f"db-user {current_app.config["DB_USER"]}")
            Logger.info(f"db-password {current_app.config["DB_PASSWORD"]}")
            Logger.info(f"db-name {current_app.config["DB_NAME"]}")
            conn = pymysql.connect(
                host=current_app.config["DB_HOST"],
                port=int(current_app.config["DB_PORT"]),
                user=current_app.config["DB_USER"],
                password=current_app.config["DB_PASSWORD"],
                database=current_app.config["DB_NAME"],
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                ssl={"ssl",{}},
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
            if app.config["REDIS_PASSWORD"]:
                client = redis.Redis(
                    host=app.config["REDIS_HOST"],
                    port=app.config["REDIS_PORT"],
                    db=app.config["REDIS_DB"],
                    password=app.config["REDIS_PASSWORD"],
                    socket_connect_timeout=5,
                )
            else:
                client = redis.Redis(
                    host=app.config["REDIS_HOST"],
                    port=app.config["REDIS_PORT"],
                    db=app.config["REDIS_DB"],
                    socket_connect_timeout=5,
                )

            if client is not None:
                client.ping()
                Logger.info("Redis connection success")
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
            if app.config["RABBITMQ_PASSWORD"]:
                credentials = pika.PlainCredentials(
                    username=app.config["RABBITMQ_USER"],
                    password=app.config["RABBITMQ_PASSWORD"],
                )
                parameters = pika.ConnectionParameters(
                    host=app.config["RABBITMQ_HOST"],
                    port=app.config["RABBITMQ_PORT"],
                    credentials=credentials,
                )
            else:
                parameters = pika.ConnectionParameters(
                    host=app.config["RABBITMQ_HOST"],
                    port=app.config["RABBITMQ_PORT"],
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
