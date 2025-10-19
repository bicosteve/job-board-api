import json


from ..db.redis import Redis
from ..utils.helpers import Helpers


class UserCache:
    client = Redis.connect_redis()

    @staticmethod
    def store_verification_code(email, code) -> bool:
        ttl = 6 * 60 * 60
        result = UserCache.client.setex(f"verify#{email}", ttl, code)
        return result

    @staticmethod
    def verify_code(email, submitted_code) -> bool:
        stored_code = UserCache.client.get(f"verify#{email}")
        if stored_code is None:
            return False
        if stored_code != submitted_code:
            return False
        UserCache.client.delete(f"verify#{email}")
        return True

    @staticmethod
    def hold_reset_token(email, data) -> bool:
        ttl = 60 * 60
        result = UserCache.client.setex(
            f'reset#{email}', ttl, json.dumps(data))
        return result

    @staticmethod
    def retrieve_reset_token(email, submitted_token) -> str:
        raw = UserCache.client.get(f'reset#{email}')
        if raw is None:
            return None
        data = json.loads(raw)

        if data['token'] != submitted_token:
            return None

        has_expired = Helpers.compare_token_time(data)
        if has_expired:
            return None

        UserCache.client.delete(f'reset#{email}')
        return data['token']
