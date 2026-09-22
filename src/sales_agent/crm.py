"""Fictional CRM backed by SQLite: leads, appointments, and per-session
conversation history. Simplified from the master plan's Postgres suggestion —
see docs/decisions/0001-sqlite-crm.md."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "crm.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    contato TEXT NOT NULL,
    interesse TEXT,
    status TEXT NOT NULL DEFAULT 'novo',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    hora TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(lead_id) REFERENCES leads(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


class CRM:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def register_lead(self, nome: str, contato: str, interesse: str | None = None) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO leads (nome, contato, interesse, created_at) VALUES (?, ?, ?, ?)",
                (nome, contato, interesse, datetime.now().isoformat()),
            )
            return cur.lastrowid

    def schedule_followup(self, lead_id: int, data: str, hora: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO appointments (lead_id, data, hora, created_at) VALUES (?, ?, ?, ?)",
                (lead_id, data, hora, datetime.now().isoformat()),
            )
            conn.execute("UPDATE leads SET status = 'agendado' WHERE id = ?", (lead_id,))
            return cur.lastrowid

    def log_message(self, session_id: str, role: str, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.now().isoformat()),
            )

    def get_history(self, session_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
                (session_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def list_leads(self, status: str | None = None) -> list[dict]:
        with self._connect() as conn:
            if status:
                rows = conn.execute("SELECT * FROM leads WHERE status = ?", (status,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM leads").fetchall()
            return [dict(r) for r in rows]

    def metrics(self) -> dict:
        with self._connect() as conn:
            total_leads = conn.execute("SELECT COUNT(*) c FROM leads").fetchone()["c"]
            by_status = conn.execute(
                "SELECT status, COUNT(*) c FROM leads GROUP BY status"
            ).fetchall()
            total_appointments = conn.execute(
                "SELECT COUNT(*) c FROM appointments"
            ).fetchone()["c"]
            return {
                "total_leads": total_leads,
                "leads_by_status": {r["status"]: r["c"] for r in by_status},
                "total_appointments": total_appointments,
            }
