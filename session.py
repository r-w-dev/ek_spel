import os
from config import DB_CONFIG, DEBUG
from sqlalchemy import create_engine, event
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session
from flask_app import db


if os.environ.get("FLASK"):
    _session = db.session

else:
    engine = create_engine(URL.create(**DB_CONFIG), echo=DEBUG)
    _session = Session(bind=engine)

    @event.listens_for(engine, "connect")
    def do_connect(dbapi_connection, connection_record):
        # disable pysqlite's emitting of the BEGIN statement entirely.
        # also stops it from emitting COMMIT before any DDL.
        dbapi_connection.isolation_level = None

        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        # cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA locking_mode=EXCLUSIVE")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


    @event.listens_for(engine, "begin")
    def do_begin(conn):
        # emit our own BEGIN
        conn.exec_driver_sql("BEGIN")


class Sessie:
    sessie = _session

    def commit(self):
        _session.commit()
        _session.close()
        return self

    def flush(self):
        _session.flush()
        return self


def has_table(table):
    return table.__table__.exists(bind=db.engine)


def drop_table(table):
    if has_table(table):
        table.__table__.drop(bind=db.engine)


def create_table(table):
    table.__table__.create(bind=db.engine)


def recreate_table(table):
    drop_table(table)
    create_table(table)
