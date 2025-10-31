import pymysql

from flask import current_app, g
from app.utils.logger import Loggger
from app.utils.exceptions import GenericDatabaseError


def get_db():
    if "db" not in g:
        try:
            g.db = pymysql.connect(
                host=current_app.config["DB_HOST"],
                user=current_app.config["DB_USER"],
                password=current_app.config["DB_PASSWORD"],
                database=current_app.config["DB_NAME"],
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                ssl_disabled=False,
                connect_timeout=10
            )
        except pymysql.MySQLError as e:
            Loggger.error(f'MySQL connection error: {str(e)}')
            raise GenericDatabaseError(
                f'Database connection because of {str(e)}')
    else:
        try:
            g.db.ping(reconnect=True)
        except Exception:
            Loggger.wart('Reconnecting to MySQL ...')
            g.pop('db')
            return get_db()
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
