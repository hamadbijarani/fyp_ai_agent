from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from src.storage.db import get_connection


class AuditLog:
    def __init__(self, db_path: str = "data/audit.db"):
        self.db_path = db_path
        self._init()

    def _init(self):
        conn = get_connection(self.db_path)
        conn.execute(
            """CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT
            )"""
        )
        conn.commit()
        conn.close()

    def record(self, event_type: str, details: dict | None = None):
        conn = get_connection(self.db_path)
        conn.execute(
            "INSERT INTO events (ts, event_type, details) VALUES (?,?,?)",
            (datetime.now(timezone.utc).isoformat(), event_type, json.dumps(details or {})),
        )
        conn.commit()
        conn.close()

    def recent(self, limit: int = 50) -> list[dict]:
        conn = get_connection(self.db_path)
        rows = conn.execute("SELECT ts, event_type, details FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [{"ts": r["ts"], "event_type": r["event_type"], "details": json.loads(r["details"] or "{}")} for r in rows]
