from typing import Any
from datetime import date, datetime

import pymysql
from pymysql.cursors import DictCursor


from ..db.db import DB
from ..utils.logger import Logger
from ..utils.exceptions import (
    GenericDatabaseError
)


def serialize_application(row: dict) -> dict:
    application = dict(row)
    for field in ('created_at', 'modified_at'):
        if field in application and isinstance(application[field], (date, datetime)):
            application[field] = application[field].isoformat()
    return application


class ApplicationRepository:

    @staticmethod
    def create_application(user_id, data: dict[str, Any]) -> int:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = '''
                INSERT INTO job_applications(user_id,job_id,status,cover_letter,resume_url)
                VALUES(%s,%s,%s,%s,%s)
                '''.strip()

                job_id = data['job_id']
                status = int(data['status'])
                c_letter = data['cover_letter'] if data['cover_letter'] else ''
                resume_url = data['resume_url'] if data['resume_url'] else ''

                Logger.info(f'Creating job applicationf or {user_id}')
                cursor.execute(
                    query, (user_id, job_id, status, c_letter, resume_url))
                conn.commit()
                return cursor.lastrowid
        except pymysql.MySQLError as e:
            Logger.warn(f'Pymysql error {str(e)} occurred')
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Logger.warn(f'Generic error {str(e)} occurred')
            raise GenericDatabaseError(str(e))

    @staticmethod
    def get_jobs_applications(job_id: int, limit: int, offset: int) -> list:
        conn = None
        try:
            Logger.info(f'Job id -> {job_id}')
            Logger.info(f'Job limit -> {limit}')
            Logger.info(f'Job offset -> {offset}')
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = '''
                SELECT * FROM job_applications
                WHERE job_id = %s
                ORDER BY created_at
                LIMIT %s OFFSET %s
                '''.strip()

                cursor.execute(query, (job_id, limit, offset))
                res = cursor.fetchall()

                job_apps = [serialize_application(
                    row) for row in res or []]
                return job_apps
        except pymysql.MySQLError as e:
            Logger.warn(f'PYMYSQL: an error {str(e)} occurred')
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Logger.warn(f'PYMYSQL: an error {str(e)} occurred')
            raise GenericDatabaseError(str(e))

    @staticmethod
    def get_user_application(user_id: int, job_id: int) -> dict:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = '''
                SELECT * FROM job_applications
                WHERE user_id = %s
                AND job_id = %s
                LIMIT 1
                '''.strip()

                cursor.execute(query, (user_id, job_id))
                row = cursor.fetchone()
                if not row:
                    return {}
                return serialize_application(row)

        except pymysql.MySQLError as e:
            Logger.warn(f'PYMYSQL: {str(e)}')
            raise GenericDatabaseError(f'{str(e)}')
        except Exception as e:
            Logger.warn(f'EXCEPTION: {str(e)}')
            raise GenericDatabaseError(f'{str(e)}')

    @staticmethod
    def get_user_applications(user_id: int) -> list:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = '''
                SELECT * FROM job_applications
                WHERE user_id = %s
                '''.strip()

                cursor.execute(query, (user_id,))
                res = cursor.fetchall()

                applications = [serialize_application(
                    row) for row in res or []]
                return applications
        except pymysql.MySQLError as e:
            Logger.warn(f'PYMYSQL: {str(e)}')
            raise GenericDatabaseError(f'{str(e)}')
        except Exception as e:
            Logger.warn(f'EXCEPTION: {str(e)}')
            raise GenericDatabaseError(f'{str(e)}')

    @staticmethod
    def update_application(application_id: int, admin_id: int, status: int) -> bool:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = '''
                UPDATE job_applications ja
                INNER JOIN jobs j ON ja.job_id = j.job_id
                SET ja.status = %s, ja.modified_at = CURRENT_TIMESTAMP
                WHERE ja.application_id = %s AND j.admin_id = %s
                '''.strip()

                Logger.info(
                    f'Updating job {application_id} by user {admin_id}')
                cursor.execute(
                    query, (status, application_id, admin_id))

                conn.commit()
                Logger.info(
                    f'Update by {admin_id} for application {application_id} success')
                return cursor.rowcount > 0
        except pymysql.MySQLError as e:
            Logger.warn(f'Pymysql error {str(e)} occurred')
            raise GenericDatabaseError(str(e))
        except Exception as e:
            Logger.warn(f'Generic error {str(e)} occurred')
            raise GenericDatabaseError(str(e))
        return 0
