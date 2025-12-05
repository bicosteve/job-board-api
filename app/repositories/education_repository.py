import pymysql
from pymysql.cursors import DictCursor


from ..db.db import DB
from ..utils.exceptions import GenericDatabaseError
from ..utils.logger import Logger


class EducationRepository:
    '''Contains methods to perform operations on education table'''

    @staticmethod
    def add_education(user_id: int, data: dict[str, str]) -> int:
        conn = None
        try:
            conn = DB.get_db()
            if not isinstance(data, dict):
                Logger.warn(f'Provided data {data} is not valid')
                raise ValueError(f'Provided data {data} is not valid')
            with conn.cursor(DictCursor) as cursor:
                query = '''
                INSERT INTO `education`(`user_id`,`level`,`institution`,`field`,`start_date`,`end_date`,`description`)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                '''.strip()

                level = data['level']
                institution = data['institution']
                field = data['field'] if data['field'] else ''
                start_date = data['start_date']
                end_date = data['end_date']
                description = data['description']

                cursor.execute(query, (user_id, level, institution,
                               field, start_date, end_date, description))

                conn.commit()

                return cursor.rowcount
        except pymysql.MySQLError as e:
            Logger.error(f'{str(e)}')
            raise GenericDatabaseError(f'{str(e)}')
        except Exception as e:
            Logger.warn(f'{str(e)}')
            raise GenericDatabaseError(f'{str(e)}')
