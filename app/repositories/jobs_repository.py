import pymysql
from pymysql.cursors import DictCursor

from ..db.db import DB
from ..utils.exceptions import GenericDatabaseError
from ..utils.logger import Logger


class JobRepository:
    @staticmethod
    def insert_job(data: dict[str, str]) -> int | None:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:

                query = '''
                INSERT INTO jobs(admin_id,title,description,requirements,location,employment_type,salary_range,company_name,application_url,deadline,status)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                '''.strip()

                employment_type = None
                status = None
                admin_id = data['admin_id']
                title = data['title']
                description = data['description']
                requirements = data['requirements']
                location = data['location']
                if data['employment_type'].lower() == 'full time':
                    employment_type = '1'
                elif data['employment_type'].lower() == 'part time':
                    employment_type = '2'
                elif data['employment_type'].lower() == 'contract':
                    employment_type = '3'
                elif data['employment_type'].lower() == 'internship':
                    employment_type = '4'
                else:
                    employment_type = '1'
                salary_range = data['salary_range']
                company_name = data['company_name']
                application_url = data['application_url']
                deadline = data['deadline']

                status = data['status']
                if data['status'] == 'Open':
                    status = '5'
                elif data['status'] == 'Closed':
                    status = '6'
                elif data['status'] == 'Draft':
                    status = '7'
                else:
                    status = '5'

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
