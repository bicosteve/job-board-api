import json


from ..db.redis import Cache
from ..utils.helpers import Helpers


class BaseCache:
    '''
    Has methods that are used to access objects in cache
    '''

    @staticmethod
    def get_client():
        '''
        Load the redis client lazily.
        Prevents the creation of Redis client
        untill it is needed.
        This prevents connecting to Redis at import time
        therefore prevents `Working outside of application
        context`.
        '''
        return Cache.connect_redis()

    @staticmethod
    def store_verification_code(email, code) -> bool:
        client = Cache.connect_redis()
        ttl = 6 * 60 * 60
        res = bool(client.setex(f"verify#{email}", ttl, code))
        return res

    @staticmethod
    def verify_code(email, submitted_code) -> bool:
        client = Cache.connect_redis()
        stored_code = client.get(f"verify#{email}")
        if stored_code is None:
            return False
        if stored_code != submitted_code:
            return False
        client.delete(f"verify#{email}")
        return True

    @staticmethod
    def hold_reset_token(email, data) -> bool:
        ttl = 60 * 60
        client = Cache.connect_redis()
        res = bool(client.setex(
            f'reset#{email}', ttl, json.dumps(data)))
        return res

    @staticmethod
    def retrieve_reset_token(email, submitted_token) -> str | None:
        client = Cache.connect_redis()
        raw = str(client.get(f'reset#{email}'))
        if raw is None:
            return None
        data = json.loads(raw)

        if data['token'] != submitted_token:
            return None

        has_expired = Helpers.compare_token_time(data)
        if has_expired:
            return None

        client.delete(f'reset#{email}')
        return data['token']
