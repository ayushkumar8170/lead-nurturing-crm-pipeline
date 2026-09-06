"""
De-duplication store backed by SQLite.

Tracks a fingerprint (normalized email or phone) per lead so re-submissions
from the same person don't create duplicate CRM records or re-trigger nurture
sequences they're already enrolled in.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS seen_leads (
    fingerprint TEXT PRIMARY KEY,
    first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
    times_seen INTEGER DEFAULT 1,
    last_stage TEXT
);
"""


@contextmanager
def _connect(db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def is_duplicate(db_path: str, fingerprint: str) -> bool:
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_leads WHERE fingerprint = ?", (fingerprint,)
        ).fetchone()
        return row is not None


def record_lead(db_path: str, fingerprint: str, stage: str) -> None:
    """Record a lead as seen, or bump its seen-count if it already exists."""
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO seen_leads (fingerprint, last_stage)
            VALUES (?, ?)
            ON CONFLICT(fingerprint) DO UPDATE SET
                times_seen = times_seen + 1,
                last_stage = excluded.last_stage
            """,
            (fingerprint, stage),
        )
