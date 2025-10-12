import os
import redis
from dotenv import load_dotenv

load_dotenv()


class Redis:

    @staticmethod
    def connect_redis():
        return redis.StrictRedis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=os.getenv("REDIS_DB"),
            decode_responses=True,
        )
