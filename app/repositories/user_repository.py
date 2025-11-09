import pymysql
from pymysql.cursors import DictCursor

from ..db.db import DB
from ..utils.exceptions import GenericDatabaseError
from ..utils.logger import Loggger


class UserRepository:
    @staticmethod
    def find_user_by_mail(email: str) -> dict | None:
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = """
                SELECT u.user_id,u.email,u.hash,u.status,
                u.created_at,us.is_deactivated
                FROM user u
                INNER JOIN user_setting us
                ON u.user_id = us.user_id
                WHERE email = %s
                """
                cursor.execute(query, (email,))
                row = cursor.fetchone()

            if not row:
                Loggger.warn(f"no user found for {email}")
                return None

            user = {
                "user_id": row.get("user_id"),
                "email": row.get("email"),
                "hash": row.get("hash"),
                "status": row.get("status"),
                "is_deactivated": row.get("is_deactivated"),
                "created_at": str(row.get("created_at")),
            }
            return user
        except pymysql.MySQLError as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))

    @staticmethod
    def find_user_by_id(user_id: int) -> dict | None:
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = """
                SELECT * FROM user WHERE user_id = %s
                LIMIT 1
                """
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()

            if not row:
                Loggger.error(f"no user with user_id {user_id}")
                return None

            user = {
                "user_id": row.get("user_id"),
                "email": row.get("email"),
                "hash": row.get("hash"),
                "status": row.get("status"),
                "reset_token": row.get("reset_token"),
                "created_at": str(row.get("created_at")),
                "updated_at": str(row.get("updated_at")),
            }

            return user
        except pymysql.MySQLError as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))

    @staticmethod
    def add_user(email: str, hash: str, status: int) -> int:
        try:
            conn = DB.get_db()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO user(hash,email,status)
                VALUES (%s,%s,%s)
                """.strip()
                cursor.execute(query, (hash, email, status))
                conn.commit()

                return cursor.rowcount

        except pymysql.MySQLError as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))

    @staticmethod
    def update_user_status(email: str) -> int:
        conn = None
        try:
            conn = DB.get_db()
            conn.autocommit(False)
            with conn.cursor() as cursor:
                # 1. Get user_id
                query_one = "SELECT user_id FROM user WHERE email = %s"
                cursor.execute(query_one, (email,))
                result = cursor.fetchone()
                if not result:
                    return 0
                user_id = result.get("user_id")

                # 2. Update Status
                query_two = """
                UPDATE user SET status = 1 WHERE email = %s
                """
                cursor.execute(query_two, (email,))
                update_count = cursor.rowcount

                # 3. Insert into user_setting
                query_three = """
                INSERT INTO user_setting(is_deactivated, user_id)
                VALUES (%s,%s)
                """.strip()
                cursor.execute(query_three, (0, user_id))
                insert_count = cursor.rowcount
                conn.commit()

                return insert_count + update_count

        except pymysql.MySQLError as e:
            if conn:
                conn.rollback()
            Loggger.error(f"MySQLError: {str(e)}")
            raise GenericDatabaseError(str(e))
        except Exception as e:
            if conn:
                conn.rollback()
            Loggger.error(f"General error: {str(e)}")
            raise GenericDatabaseError(str(e))

    @staticmethod
    def store_reset_token(email: str, token: str) -> int:
        try:
            conn = DB.get_db()
            with conn.cursor() as cursor:
                query = """
                UPDATE user SET reset_token = %s
                WHERE email = %s
                """.strip()
                cursor.execute(query, (token, email))
                conn.commit()
                return cursor.rowcount
        except pymysql.MySQLError as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))

    @staticmethod
    def get_reset_token(email: str) -> dict | None:
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = """
                SELECT reset_token, updated_at
                FROM user WHERE email = %s
                """.strip()
                cursor.execute(query, (email,))
                row = cursor.fetchone()

                if not row:
                    return None

                data = {
                    "reset-token": row.get("reset_token"),
                    "time": str(row.get("updated_at")),
                }
                return data
        except pymysql.MySQLError as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))

    @staticmethod
    def update_password(email: str, password: str) -> int:
        try:
            conn = DB.get_db()
            with conn.cursor() as cursor:
                query = """
                UPDATE user SET hash = %s
                WHERE email = %s
                """
                cursor.execute(query, (password, email))
                conn.commit()
                return cursor.rowcount
        except pymysql.MySQLError as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Loggger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))
