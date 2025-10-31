import sys
import os


import pymysql
import redis
from dotenv import load_dotenv


from .logger import Loggger

load_dotenv()


def init_dependencis(app):
    '''
    Verify core services like (DB, Redis, RabbitMQ or Kafka) are reachable
    '''

    Loggger.info("Checking dependencies...")

    # ==== 1. Check MySQL ====
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            connect_timeout=5
        )
        conn.close()
        Loggger.info('DB connection success')
    except Exception as e:
        Loggger.error(f'DB connection failed becase of: {str(e)}')
        sys.exit(1)

    # ==== 2. Check Redis ====
    try:
        client = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            db=os.getenv('REDIS_DB'),
            socket_connect_timeout=5
        )

        client.ping()
        Loggger.info('Redis connection successful...')
    except Exception as e:
        Loggger.error(f'Redis connection failed because of {str(e)}')
        sys.exit(1)
