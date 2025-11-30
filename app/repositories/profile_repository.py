import pymysql
from pymysql.cursors import DictCursor


from ..db.db import DB
from ..utils.exceptions import GenericDatabaseError
from ..utils.logger import Logger


class ProfileRepository:

    @staticmethod
    def add_profile(user_id: int, data: dict[str, str]) -> int:
        conn = None
        try:
            conn = DB.get_db()

            if not isinstance(data, dict):
                Logger.warn(f'Provided data object {data} is not valid')
                raise ValueError(f'Provided data object {data} is not valid')

            with conn.cursor(DictCursor) as cursor:
                query = '''
                INSERT INTO `profile`(first_name,last_name,cv_url,user_id)
                VALUES (%s,%s,%s,%s)
                '''.strip()

                first_name = data['first_name']
                last_name = data['last_name']
                cv_url = data['cv_url'] if data['cv_url'] else ''

                cursor.execute(query, (first_name, last_name, cv_url, user_id))
                conn.commit()

                return cursor.rowcount
        except pymysql.MySQLError as e:
            Logger.warn(f'{str(e)}')
            raise GenericDatabaseError(f'{str(e)}')
        except Exception as e:
            Logger.warn(f'{str(e)}')
            raise GenericDatabaseError(f'{str(e)}')

    @staticmethod
    def get_profile(user_id: int) -> dict | None:
        conn = None
        try:
            conn = DB.get_db()
            with conn.cursor(DictCursor) as cursor:
                query = '''
                SELECT
                    p.first_name,
                    p.last_name,
                    p.cv_url,
                    e.level,
                    e.institution,
                    e.field,
                    e.start_date,
                    e.end_date,
                    e.description
                FROM profile p
                INNER JOIN education e
                    ON p.user_id = e.user_id
                WHERE p.user_id = %s
                LIMIT 1
                '''.strip()
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()

                if not row:
                    Logger.warn(f'No profile for user {user_id}')
                    return None

                return {
                    "first_name": row.get('first_name'),
                    "last_name": row.get('first_name'),
                    "cv_url": row.get('cv_url', ''),
                    "level": row.get('level'),
                    "institution": row.get('institution'),
                    "field": row.get('field', ''),
                    "start_date": str(row.get('start_date')),
                    "end_date": str(row.get('end_date')),
                    "description": row.get('description'),
                }

        except pymysql.MySQLError as e:
            Logger.warn(f'{str(e)}')
            raise GenericDatabaseError(f'{str(e)}')
        except Exception as e:
            Logger.warn(f'{str(e)}')
            raise GenericDatabaseError(f'{str(e)}')
