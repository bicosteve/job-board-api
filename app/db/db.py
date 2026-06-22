import pymysql
from flask import current_app, g

from app.utils.exceptions import GenericDatabaseError
from app.utils.logger import Logger


class DB:
    @staticmethod
    def get_db():
        if "db" not in g:
            try:
                g.db = pymysql.connect(
                    host=current_app.config["DB_HOST"],
                    port=int(current_app.config["DB_PORT"]),
                    user=current_app.config["DB_USER"],
                    password=current_app.config["DB_PASSWORD"],
                    database=current_app.config["DB_NAME"],
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=False,
                    ssl={"ssl",{}},
                    connect_timeout=10,
                )
            except pymysql.MySQLError as e:
                Logger.error(f"MySQL connection error: {str(e)}")
                raise GenericDatabaseError(
                    f"Database connection error because of {str(e)}"
                )
        else:
            try:
                g.db.ping(reconnect=True)
            except Exception:
                Logger.warn("Reconnecting to MySQL ...")
                g.pop("db")
                return DB.get_db()
        return g.db

    @staticmethod
    def close_db(e=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()
