import pymysql
from pymysql.cursors import DictCursor

from ..db.db import get_db
from ..utils.exceptions import GenericDatabaseError


class UserRepository:
    @staticmethod
    def find_user_by_mail(email):
        try:
            conn = get_db()
            with conn.cursor(DictCursor) as cursor:
                query = """
                SELECT profile_id,email,hash,status,created_at 
                FROM profile WHERE email = %s
                """
                cursor.execute(query, (email,))
                row = cursor.fetchone()

            if not row:
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
            raise GenericDatabaseError(str(e))
        except Exception as e:
            raise GenericDatabaseError(str(e))

    @staticmethod
    def find_user_by_id(profile_id):
        try:
            conn = get_db()
            with conn.cursor(DictCursor) as cursor:
                query = """
                SELECT * FROM profile WHERE profile_id = %s
                LIMIT 1
                """
                cursor.execute(query, (profile_id,))
                row = cursor.fetchone()

            if not row:
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
            raise GenericDatabaseError(str(e))
        except Exception as e:
            raise GenericDatabaseError(str(e))

    @staticmethod
    def add_user(email, hash, status):
        try:
            conn = get_db()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO profile(email,hash,status)
                VALUES (%s,%s,%s)
                """
                rows_affected = cursor.execute(query, (email, hash, status))
                conn.commit()

                return rows_affected

        except pymysql.MySQLError as e:
            raise GenericDatabaseError(str(e))
        except Exception as e:
            raise GenericDatabaseError(str(e))

    @staticmethod
    def update_user_status(email):
        try:
            conn = get_db()
            with conn.cursor() as cursor:
                query = """
                UPDATE profile SET status = 1 WHERE email = %s
                """
                rows_affected = cursor.execute(query, (email,))
                conn.commit()

                return rows_affected

        except pymysql.MySQLError as e:
            raise GenericDatabaseError(str(e))
        except Exception as e:
            raise GenericDatabaseError(str(e))
