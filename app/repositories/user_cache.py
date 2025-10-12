from ..db.redis import Redis


class UserCache:

    @staticmethod
    def store_verification_code(email, code) -> bool:
        redis_client = Redis.connect_redis()
        ttl = 6 * 60 * 60
        result = redis_client.setex(f"verify#{email}", ttl, code)
        return result

    @staticmethod
    def verify_code(email, submitted_code) -> bool:
        redis_client = Redis.connect_redis()
        stored_code = redis_client.get(f"verify#{email}")
        if stored_code is None:
            return False
        if stored_code != submitted_code:
            return False
        redis_client.delete(f"verify#{email}")
        return True
