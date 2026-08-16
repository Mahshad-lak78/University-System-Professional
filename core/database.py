import sqlite3
from contextlib import contextmanager
from pathlib import Path

from core.config import get_settings


def database_path() -> Path:
    return get_settings().database_path


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(database_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def transaction():
    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    from migrations.migrate_v2 import run_migrations

    run_migrations(database_path())
