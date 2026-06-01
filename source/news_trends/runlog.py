"""Run logging: JSON run summaries written to indexes/runs/ and run_history."""

from __future__ import annotations

import json
import uuid

from . import db
from .config import Config


def write_run(cfg: Config, started_at: str, summary: dict) -> str:
    cfg.ensure_dirs()
    run_id = f"{started_at.replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:6]}"
    payload = {"run_id": run_id, "started_at": started_at, "finished_at": db.now_iso(), "summary": summary}
    out = cfg.runs_dir / f"run-{run_id}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    db.init_db(cfg.db_path)
    db.record_run(cfg.db_path, run_id, started_at, summary)
    return str(out.relative_to(cfg.root))
