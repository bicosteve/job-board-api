import pymysql
from pymysql.cursors import DictCursor

from ..db.db import DB
from ..utils.exceptions import GenericDatabaseError
from ..utils.logger import Logger


class AdminRepository:
    '''Has methods to perform repo operation for admin user'''

    @staticmethod
    def find_admin_by_email(email: str) -> dict | None:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = """
                    SELECT
                        a.admin_id,
                        a.email,
                        a.username,
                        a.hash,
                        a.created_at,
                        aset.is_deactivated
                    FROM admins a
                    LEFT JOIN admin_setting aset
                        ON a.admin_id = aset.admin_id
                    WHERE a.email = %s
                    LIMIT 1
                """

                cursor.execute(query, (email,))
                row = cursor.fetchone()

                if not row:
                    Logger.warn(f"No admin user found for {email}")
                    return None

                admin = {
                    "id": row.get("admin_id"),
                    "email": row.get("email"),
                    "username": row.get("username"),
                    "password_hash": row.get("hash"),
                    "created_at": row.get("created_at"),
                    "is_deactivated": row.get("is_deactivated") if row.get("is_deactivated") is not None else False
                }

                return admin
        except Exception as e:
            Logger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))

    @staticmethod
    def find_admin_by_id(admin_id: int) -> dict | None:
        conn = None
        row = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = """
                SELECT * FROM admins WHERE admin_id = %s
                LIMIT 1
                """
                cursor.execute(query, (admin_id,))
                row = cursor.fetchone()

            if not row:
                Logger.warn(f"no admin with id {admin_id}")
                return None

            admin = {
                "id": row.get("admin_id"),
                "email": row.get("email"),
                "username": row.get("username"),
                "created_at": str(row.get("created_at")),
                "updated_at": str(row.get("updated_at"))
            }

            return admin

        except pymysql.MySQLError as e:
            Logger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Logger.error(f"{str(e)}")
            raise GenericDatabaseError(str(e))

    @staticmethod
    def add_admin(data: dict) -> int | None:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = """
                INSERT INTO admins(email,username,hash)
                VALUES (%s,%s,%s)
                """.strip()

                cursor.execute(
                    query, (data['email'], data['username'], data['password_hash']))
                conn.commit()

                return cursor.rowcount
        except pymysql.MySQLError as e:
            Logger.error(f"{str(e)}")
            raise GenericDatabaseError(f"{str(e)}")
        except Exception as e:
            Logger.error(f"{str(e)}")
            raise GenericDatabaseError(f"{str(e)}")

    @staticmethod
    def update_admin_status(email: str, active_status: int) -> int | None:
        conn = None
        try:
            conn = DB.get_db()
            conn.autocommit(False)

            with conn.cursor(DictCursor) as cursor:
                # 1. Get admin by id

                query_one = """SELECT admin_id FROM admins WHERE email = %s"""
                cursor.execute(query_one, (email,))
                result = cursor.fetchone()

                if not result:
                    return None

                user_id = result.get("admin_id")

                # 2. Update Admin Active Status
                query_two = """
                INSERT INTO admin_setting(is_deactivated,admin_id)
                VALUES (%s,%s)
                ON DUPLICATE KEY UPDATE is_deactivated = VALUES(is_deactivated)
                """.strip()

                cursor.execute(query_two, (active_status, user_id))
                rows = cursor.rowcount
                conn.commit()

                return rows
        except pymysql.MySQLError as e:
            if conn:
                conn.rollback()
            Logger.error(f"MySQLError: {str(e)}")
            raise GenericDatabaseError(str(e))
        except Exception as e:
            if conn:
                conn.rollback()
            Logger.error(f"General Error: {str(e)}")
            raise GenericDatabaseError(str(e))
