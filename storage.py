"""Schema storage backed by PostgreSQL.

Replaces load_schemas()/save_schemas() and the schemas.json file.
Each schema is one row: its title, and its definition stored as JSONB.
"""
import os
import time

import psycopg
from psycopg.types.json import Jsonb

DATABASE_URL = os.environ["DATABASE_URL"]  # e.g. postgresql://user:pass@host:5432/dbname


def get_conn():
    # A new connection per call is fine at this size. Switch to psycopg_pool if traffic grows.
    return psycopg.connect(DATABASE_URL)


def wait_for_db(attempts=10, delay=2):
    """Retry connecting at startup, so the app doesn't crash if Postgres is still booting."""
    for attempt in range(1, attempts + 1):
        try:
            with get_conn() as conn:
                conn.execute("SELECT 1")
            return
        except psycopg.OperationalError:
            if attempt == attempts:
                raise
            print(f"Database not ready (attempt {attempt}/{attempts}), retrying in {delay}s")
            time.sleep(delay)


def init_db(default_schemas):
    """Create the table if needed and insert the starter schemas without overwriting existing ones."""
    wait_for_db()
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schemas (
                title      TEXT PRIMARY KEY,
                definition JSONB NOT NULL
            )
            """
        )
        for title, definition in default_schemas.items():
            conn.execute(
                "INSERT INTO schemas (title, definition) VALUES (%s, %s) "
                "ON CONFLICT (title) DO NOTHING",
                (title, Jsonb(definition)),
            )


def get_all_schemas():
    """Return every schema as {title: definition}, the same shape load_schemas() returned."""
    with get_conn() as conn:
        rows = conn.execute("SELECT title, definition FROM schemas ORDER BY title").fetchall()
    return {title: definition for title, definition in rows}


def get_schema(title):
    """Return one schema's definition, or None if it doesn't exist."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT definition FROM schemas WHERE title = %s", (title,)
        ).fetchone()
    return row[0] if row else None


def add_schema(title, definition):
    """Insert a schema. Returns False if a schema with that title already exists."""
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO schemas (title, definition) VALUES (%s, %s) "
            "ON CONFLICT (title) DO NOTHING",
            (title, Jsonb(definition)),
        )
        return cur.rowcount == 1


def delete_schema(title):
    """Delete a schema. Returns False if it didn't exist."""
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM schemas WHERE title = %s", (title,))
        return cur.rowcount == 1


def db_healthy():
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False
