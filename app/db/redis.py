import os
import redis
from flask import current_app, g


class Cache:

    @staticmethod
    def connect_redis():
        '''
        Return a Redis client bound to the current context
        Reuse it if already exists in global request context (g)
        (g) only exists for a lifetime of a request.
        '''
        if 'redis' not in g:
            g.redis = redis.Redis(
                host=current_app.config["REDIS_HOST"],
                port=current_app.config["REDIS_PORT"],
                db=current_app.config["REDIS_DB"],
                password=current_app.config['REDIS_PASSWORD'],
                decode_responses=True,
            )
        return g.redis

    @staticmethod
    def close_redis(e=None):
        '''Close Redis connection at the end of request'''
        client = g.pop('redis', None)
        if client is not None:
            client.close()
