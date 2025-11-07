import pymysql
from pymysql.cursors import DictCursor

from ..db.db import DB
from ..utils.exceptions import GenericDatabaseError
from ..utils.logger import Loggger


class UserRepository:
    @staticmethod
    def find_user_by_mail(email: str) -> dict:
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = """
                SELECT profile_id,email,hash,status,created_at
                FROM profile
                WHERE email = %s
                """
                cursor.execute(query, (email,))
                row = cursor.fetchone()

            if not row:
                Loggger.warn(f'no user found for {email}')
                return None

            user = {
                "profile_id": row.get("profile_id"),
                "email": row.get("email"),
                "hash": row.get("hash"),
                "status": row.get("status"),
                "created_at": str(row.get("created_at")),
            }
            return user
        except pymysql.MySQLError as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))

    @staticmethod
    def find_user_by_id(profile_id: int) -> dict:
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = """
                SELECT * FROM profile WHERE profile_id = %s
                LIMIT 1
                """
                cursor.execute(query, (profile_id,))
                row = cursor.fetchone()

            if not row:
                Loggger.error(
                    f'no user with profile id {profile_id}')
                return None

            profile = {
                "profile_id": row.get("profile_id"),
                "email": row.get("email"),
                "hash": row.get("hash"),
                "photo": row.get("photo"),
                "status": row.get("status"),
                "reset_token": row.get("reset_token"),
                "created_at": str(row.get("created_at")),
                "modified_at": str(row.get("modified_at")),
            }

            return profile
        except pymysql.MySQLError as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))

    @staticmethod
    def add_user(email: str, hash: str, status: int) -> int:
        try:
            conn = DB.get_db()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO profile(email,hash,status)
                VALUES (%s,%s,%s)
                """
                cursor.execute(query, (email, hash, status))
                conn.commit()

                return cursor.rowcount

        except pymysql.MySQLError as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))

    @staticmethod
    def update_user_status(email: str) -> int:
        try:
            conn = DB.get_db()
            with conn.cursor() as cursor:
                query = """
                UPDATE profile SET status = 1 WHERE email = %s
                """
                cursor.execute(query, (email,))
                conn.commit()

                return cursor.rowcount

        except pymysql.MySQLError as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))

    @staticmethod
    def store_reset_token(email: str, token: str) -> int:
        try:
            conn = DB.get_db()
            with conn.cursor() as cursor:
                query = '''
                UPDATE profile SET reset_token = %s
                WHERE email = %s
                '''
                cursor.execute(query, (token, email))
                conn.commit()
                return cursor.rowcount
        except pymysql.MySQLError as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))

    @staticmethod
    def get_reset_token(email: str) -> dict:
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = '''
                SELECT reset_token, modified_at
                FROM profile WHERE email = %s
                '''
                cursor.execute(query, (email,))
                row = cursor.fetchone()

                if not row:
                    return None

                data = {
                    'reset-token': row.get('reset_token'),
                    'time': str(row.get('modified_at')),
                }
                return data
        except pymysql.MySQLError as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))

    @staticmethod
    def update_password(email: str, password: str) -> int:
        try:
            conn = DB.get_db()
            with conn.cursor() as cursor:
                query = '''
                UPDATE profile SET hash = %s
                WHERE email = %s
                '''
                cursor.execute(query, (password, email))
                conn.commit()
                return cursor.rowcount
        except pymysql.MySQLError as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f'{str(e)}')
            raise GenericDatabaseError(str(e))
