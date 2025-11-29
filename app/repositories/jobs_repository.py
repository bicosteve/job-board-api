from datetime import date, datetime
from typing import Any

import pymysql
from pymysql.cursors import DictCursor

from ..db.db import DB
from ..utils.exceptions import GenericDatabaseError
from ..utils.logger import Logger
from ..utils.data import (
    VALID_EMPLOYMENT_TYPES,
    VALID_JOB_STATUSES,
    ALLOWED_JOB_FIELDS
)


# Helpers
def serialize_job(row: dict) -> dict:
    job = dict(row)
    for field in ('deadline', 'created_at', 'updated_at'):
        if field in job and isinstance(job[field], (date, datetime)):
            job[field] = job[field].isoformat()
    return job


def convert_employment_type(employment: str) -> str:
    employment_type = None

    if employment not in VALID_EMPLOYMENT_TYPES:
        raise ValueError(f'Employment type {employment} not allowed')

    if employment.lower() == 'full time':
        employment_type = '1'
    elif employment.lower() == 'part time':
        employment_type = '2'
    elif employment.lower() == 'contract':
        employment_type = '3'
    elif employment.lower() == 'internship':
        employment_type = '4'
    else:
        employment_type = '1'
    return employment_type


def convert_job_status(job_status: str) -> str:
    status = None

    if job_status not in VALID_JOB_STATUSES:
        raise ValueError(f'Job status {job_status} not allowed')

    if job_status.lower() == 'open':
        status = '5'
    elif job_status.lower() == 'closed':
        status = '6'
    elif job_status.lower() == 'draft':
        status = '7'
    else:
        status = '5'
    return status


class JobRepository:
    @staticmethod
    def insert_job(data: dict[str, str]) -> int | None:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:

                query = '''
                INSERT INTO `jobs`(`admin_id`,`title`,`description`,`requirements`,`location`,`employment_type`,`salary_range`,`company_name`,`application_url`,`deadline`,`status`)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                '''.strip()

                employment_type = None
                status = None

                admin_id = data['admin_id']
                title = data['title']
                description = data['description']
                requirements = data['requirements']
                location = data['location']
                employment_type = convert_employment_type(
                    data['employment_type'])
                salary_range = data['salary_range']
                company_name = data['company_name']
                application_url = data['application_url']
                deadline = data['deadline']
                status = convert_job_status(data['status'])
                cursor.execute(query, (admin_id, title, description, requirements, location,
                               employment_type, salary_range, company_name, application_url, deadline, status))
                conn.commit()
                Logger.info(f"Job {title} by {admin_id} created successfully")
                return cursor.lastrowid
        except pymysql.MySQLError as e:
            Logger.error(f"An error because of {str(e)} occurred")
            raise GenericDatabaseError({str(e)})
        except Exception as e:
            Logger.error(f"An error because of {str(e)} occurred")
            raise GenericDatabaseError({str(e)})

    @staticmethod
    def get_jobs(limit: int, offset: int) -> list:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = '''
                SELECT * FROM jobs
                ORDER BY job_id
                LIMIT %s OFFSET %s
                '''.strip()
                cursor.execute(query, (limit, offset))
                result = cursor.fetchall()

                jobs = [serialize_job(row) for row in result or []]
                return jobs
        except pymysql.MySQLError as e:
            Logger.error(f'Database error: {str(e)}')
            raise GenericDatabaseError(f"{str(e)}")
        except Exception as e:
            Logger.error(f'Unexpected error: {str(e)}')
            raise GenericDatabaseError(f'{str(e)}')

    @staticmethod
    def get_job(job_id: int) -> dict:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = '''SELECT * FROM jobs WHERE job_id = %s'''
                cursor.execute(query, (job_id,))
                row = cursor.fetchone()
                if not row:
                    return {}
                return row
        except pymysql.MySQLError as e:
            Logger.error(f'Database error: {str(e)}')
            raise GenericDatabaseError(f'{str(e)}')
        except Exception as e:
            Logger.error(f'Unexpected error: {str(e)}')
            raise GenericDatabaseError(f'{str(e)}')

    @staticmethod
    def update_job(job_id: int, admin_id: int, data: dict[str, Any]) -> bool:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                # 1. Filter only allowed fields
                valid_data = {k: v for k,
                              v in data.items() if k in ALLOWED_JOB_FIELDS}

                if not valid_data:
                    raise ValueError('No valid fields provided for updates')

                # 2. Build dynamic SET clause for UPDATE
                set_clauses = [f'`{key}` = %s' for key in valid_data.keys()]
                values = list(valid_data.values())

                # 3. Set the query
                query = f'''
                UPDATE `jobs`
                SET {', '.join(set_clauses)}, `updated_at` = CURRENT_TIMESTAMP
                WHERE `job_id` = %s
                AND `admin_id` = %s
                '''.strip()

                # 4. Add the job_id and admin_id to values list
                values.append(job_id)
                values.append(admin_id)

                # 5. Execute the query & commit
                cursor.execute(query, tuple(values))
                conn.commit()

                # 6. Log and return bool
                Logger.info(f'Job {job_id} updated sucessfully with {values}')
                return cursor.rowcount > 0
        except pymysql.MySQLError as e:
            Logger.error(f'Database error: {str(e)}')
            raise GenericDatabaseError(f'DB error {str(e)}')
        except Exception as e:
            Logger.error(f'Unexpected error: {str(e)}')
            raise GenericDatabaseError({str(e)})
