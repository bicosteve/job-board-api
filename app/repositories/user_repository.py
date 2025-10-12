from ..db.db import get_db
from ..utils.exceptions import GenericDatabaseError


class UserRepository:
    @staticmethod
    def find_user_by_mail(email):
        try:
            conn = get_db()
            cursor = conn.cursor()
            query = """
                SELECT profile_id,email,hash,status,created_at FROM profile WHERE email = %s
            """
            cursor.execute(query, (email,))
            data = cursor.fetchone()

            cursor.close()

            if not data:
                return None

            user = {
                "profile_id": data[0],
                "email": data[1],
                "hash": data[2],
                "photo": data[3],
                "status": data[4],
                "created_at": data[5],
            }

            return user

        except Exception as e:
            raise GenericDatabaseError(str(e))

    @staticmethod
    def find_user_by_id(profile_id):
        try:
            conn = get_db()
            cursor = conn.cursor()
            query = """SELECT * FROM profile WHERE profile_id = %s"""
            cursor.execute(query, (profile_id,))
            data = cursor.fetchone()

            cursor.close()

            if not data:
                return None

            profile = {
                "profile_id": data[0],
                "email": data[1],
                "hash": data[2],
                "photo": data[3],
                "status": data[4],
                "reset_token": data[5],
                "created_at": data[6],
                "modified_at": data[7],
            }

            return profile

        except Exception as e:
            raise GenericDatabaseError(str(e))

    @staticmethod
    def add_user(email, hash, status):
        try:
            conn = get_db()
            cursor = conn.cursor()
            query = """
            INSERT INTO profile(email,hash,status)
            VALUES (%s,%s,%s)
            """

            rows = cursor.execute(query, (email, hash, status))
            conn.commit()
            cursor.close()

            return rows

        except Exception as e:
            raise GenericDatabaseError(str(e))
