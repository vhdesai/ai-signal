"""Ingest stage: scan the news directory, archive raw digests, track changes."""

from __future__ import annotations

import shutil
from pathlib import Path

from . import db, util
from .config import Config


def _file_hash(path: Path) -> str:
    return util.sha256(path.read_text(encoding="utf-8", errors="replace"))


def ingest(cfg: Config) -> dict:
    cfg.ensure_dirs()
    db.init_db(cfg.db_path)

    changed: list[str] = []
    total = 0
    with db.connect(cfg.db_path) as conn:
        existing = {
            row["digest_path"]: row["file_hash"]
            for row in conn.execute("SELECT digest_path, file_hash FROM digests")
        }
        for path in sorted(cfg.news_dir.glob("*.md")):
            total += 1
            rel = str(path.relative_to(cfg.root))
            file_hash = _file_hash(path)
            issue_date = util.extract_date(path.stem.replace("_", " "))
            archive_path = cfg.raw_digest_archive_dir / path.name
            now = db.now_iso()

            if existing.get(rel) == file_hash:
                conn.execute(
                    "UPDATE digests SET last_seen_at=? WHERE digest_path=?", (now, rel)
                )
                continue

            shutil.copy2(path, archive_path)
            conn.execute(
                "INSERT OR REPLACE INTO digests "
                "(digest_path, raw_archive_path, issue_date, file_hash, ingested_at, last_seen_at) "
                "VALUES (?,?,?,?,?,?)",
                (
                    rel,
                    str(archive_path.relative_to(cfg.root)),
                    util.iso(issue_date),
                    file_hash,
                    now,
                    now,
                ),
            )
            changed.append(rel)

    return {"digests_total": total, "digests_changed": len(changed), "changed": changed}
