import json
import os
import sqlite3

from utils import now_iso


_database_path = None


# Initializes the SQLite database file and creates required tables.
def init_db(database_path):
    global _database_path
    _database_path = database_path
    directory = os.path.dirname(database_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                raw_payload TEXT
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                command_type TEXT NOT NULL,
                target TEXT NOT NULL,
                payload TEXT NOT NULL
            )
        """)
        connection.commit()


# Opens a SQLite connection using the configured database path.
def get_connection():
    if not _database_path:
        raise RuntimeError("Database has not been initialized")
    connection = sqlite3.connect(_database_path)
    connection.row_factory = sqlite3.Row
    return connection


# Inserts one event record into the events table and returns its database id.
def insert_event(event):
    raw_payload = event.get("raw_payload")
    if raw_payload is not None and not isinstance(raw_payload, str):
        raw_payload = json.dumps(raw_payload)

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO events (timestamp, source, event_type, severity, message, raw_payload)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event.get("timestamp") or now_iso(),
            event.get("source", "system"),
            event.get("event_type", "status_update"),
            event.get("severity", "low"),
            event.get("message", ""),
            raw_payload
        ))
        connection.commit()
        return cursor.lastrowid


# Reads the most recent event records for the dashboard event log.
def get_recent_events(limit=50):
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, timestamp, source, event_type, severity, message
            FROM events
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [dict(row) for row in rows]


# Inserts one command record into the command history table.
def insert_command(command_type, target, payload):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO commands (timestamp, command_type, target, payload)
            VALUES (?, ?, ?, ?)
        """, (
            now_iso(),
            command_type,
            target,
            json.dumps(payload)
        ))
        connection.commit()
        return cursor.lastrowid
