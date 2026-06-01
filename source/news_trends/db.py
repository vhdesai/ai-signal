"""SQLite schema, FTS5 keyword index, and run-history helpers."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS digests (
    digest_path     TEXT PRIMARY KEY,
    raw_archive_path TEXT,
    issue_date      TEXT,
    file_hash       TEXT,
    ingested_at     TEXT,
    last_seen_at    TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    article_id            TEXT PRIMARY KEY,
    title                 TEXT,
    date                  TEXT,
    source                TEXT,
    summary               TEXT,
    theme                 TEXT,
    tags                  TEXT,
    url_original          TEXT,
    url_canonical         TEXT,
    url_status            TEXT,
    http_status           INTEGER,
    checked_at            TEXT,
    repair_method         TEXT,
    digest_source         TEXT,
    article_path          TEXT,
    content_hash          TEXT,
    normalized_title_hash TEXT,
    canonical_url_hash    TEXT,
    entities              TEXT,
    themes                TEXT,
    cross_cutting_topics  TEXT,
    dedupe_status         TEXT DEFAULT 'canonical',
    canonical_article_id  TEXT,
    related_article_ids   TEXT,
    embedding_id          TEXT,
    event_name            TEXT DEFAULT '',
    created_at            TEXT,
    updated_at            TEXT
);

CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(date);
CREATE INDEX IF NOT EXISTS idx_articles_dedupe ON articles(dedupe_status);
CREATE INDEX IF NOT EXISTS idx_articles_canonical ON articles(canonical_article_id);

CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
    article_id UNINDEXED,
    title,
    summary,
    source,
    entities,
    themes,
    tokenize = 'porter unicode61'
);

CREATE TABLE IF NOT EXISTS url_status (
    article_id    TEXT PRIMARY KEY,
    url_original  TEXT,
    url_canonical TEXT,
    url_status    TEXT,
    http_status   INTEGER,
    checked_at    TEXT,
    repair_method TEXT
);

CREATE TABLE IF NOT EXISTS review_queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id  TEXT,
    kind        TEXT,
    detail      TEXT,
    created_at  TEXT,
    resolved    INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS run_history (
    run_id      TEXT PRIMARY KEY,
    started_at  TEXT,
    finished_at TEXT,
    summary     TEXT
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: Path) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        # Migrate: add event_name column if missing (pre-existing DBs)
        cols = {r[1] for r in conn.execute("PRAGMA table_info(articles)")}
        if "event_name" not in cols:
            conn.execute("ALTER TABLE articles ADD COLUMN event_name TEXT DEFAULT ''")


def queue_review(conn: sqlite3.Connection, article_id: str, kind: str, detail: str) -> None:
    conn.execute(
        "INSERT INTO review_queue (article_id, kind, detail, created_at) VALUES (?,?,?,?)",
        (article_id, kind, detail, now_iso()),
    )


def record_run(db_path: Path, run_id: str, started_at: str, summary: dict) -> None:
    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO run_history (run_id, started_at, finished_at, summary) "
            "VALUES (?,?,?,?)",
            (run_id, started_at, now_iso(), json.dumps(summary)),
        )
