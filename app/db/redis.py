import redis
from flask import current_app, g


class Cache:

    @staticmethod
    def connect_redis():
        """
        Return a Redis client bound to the current context
        Reuse it if already exists in global request context (g)
        (g) only exists for a lifetime of a request.
        """
        if "redis" not in g:
            # Supports full URL if provided (Upstash, Railway, Render etc)
            redis_url = current_app.config.get("REDIS_URL")
            if redis_url:
                g.redis = redis.from_url(redis_url, decode_response=True)
            else:
                # Fallback to individul config values (local dev)
                password = current_app.config.get("REDIS_PASSWORD")
                username = current_app.config.get("REDIS_USERNAME", "default")
                host = current_app.config.get("REDIS_HOST", "localhost")
                port = current_app.config.get("REDIS_PORT", 6379)
                db = current_app.config.get("REDIS_DB", 0)
                ssl = current_app.config.get("REDIS_TLS", False)
                g.redis = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    username=username if username else None,
                    password=password if password else None,
                    ssl=ssl,
                    decode_responses=True,
                )
        return g.redis

    @staticmethod
    def close_redis(e=None):
        """Close Redis connection at the end of request"""
        client = g.pop("redis", None)
        if client is not None:
            client.close()
