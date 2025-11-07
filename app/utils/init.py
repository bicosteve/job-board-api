import sys
import time


import pymysql
import redis


from .logger import Loggger


def retry_connection(func, retries=3, delay=2, backoff=2):
    '''
    A wrapper for connection attempts.
    - retires: number of retry attempts
    - delay: initial delay in seconds
    - backoff: multiplier for exponential backoff
    '''
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == retries:
                raise e
            Loggger.warn(f"Attempt {attempt} failed. Retrying in {delay}s..")
            time.sleep(delay)
            delay *= backoff


def check_db(app):
    def connect_db():
        try:
            conn = pymysql.connect(
                host=app.config['DB_HOST'],
                user=app.config['DB_USER'],
                password=app.config['DB_PASSWORD'],
                database=app.config['DB_NAME'],
                connect_timeout=5
            )

            Loggger.info('DB connection success')
        except Exception as e:
            Loggger.exception(f'An error occured {str(e)}')
        finally:
            conn.close()

    retry_connection(connect_db)


def check_cache(app):
    def connect_redis():
        try:
            client = redis.Redis(
                host=app.config['REDIS_HOST'],
                port=app.config['REDIS_PORT'],
                db=app.config['REDIS_DB'],
                password=app.config['REDIS_PASSWORD'],
                socket_connect_timeout=5
            )

            client.ping()
            Loggger.info('Redis connection success')
        except Exception as e:
            Loggger.exception(f'Something went wrong {str(e)}')

    retry_connection(connect_redis)


def init_dependencies(app):
    '''
    Verify core services like (DB, Redis, Message Brokers)
    are reachable with retry logic.
    '''

    Loggger.info("Checking dependencies...")

    # ==== 1. Check MySQL ====
    try:
        check_db(app)
    except Exception as e:
        Loggger.error(f'DB connection failed becase of: {str(e)}')
        sys.exit(1)

    # ==== 2. Check Redis ====
    try:
        check_cache(app)
    except Exception as e:
        Loggger.error(f'Redis connection failed because of {str(e)}')
        sys.exit(1)
