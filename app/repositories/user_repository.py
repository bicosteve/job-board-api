from ..db import get_db


class UserRepository:
    @staticmethod
    def find_user():
        connection = get_db()
