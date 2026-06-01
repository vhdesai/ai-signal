"""Deduplication: exact (hash) + semantic near-duplicate clustering via Chroma."""

from __future__ import annotations

import json
from pathlib import Path

from . import db
from .articles_io import iter_articles, write_article
from .config import Config
from .models import Article


def _persist(cfg: Config, conn, art: Article) -> None:
    write_article(cfg, art)
    conn.execute(
        "UPDATE articles SET dedupe_status=?, canonical_article_id=?, related_article_ids=?, updated_at=? "
        "WHERE article_id=?",
        (
            art.dedupe_status, art.canonical_article_id,
            json.dumps(art.related_article_ids), db.now_iso(), art.article_id,
        ),
    )


def _semantic_links(cfg: Config, by_id: dict[str, Article], dup_t: float, near_t: float) -> dict:
    import chromadb

    client = chromadb.PersistentClient(path=str(cfg.chroma_dir))
    coll = client.get_or_create_collection("articles")
    duplicates = 0
    related = 0

    for art in by_id.values():
        if art.dedupe_status == "duplicate":
            continue
        got = coll.get(ids=[art.article_id], include=["embeddings"])
        if not got["ids"] or got["embeddings"] is None or len(got["embeddings"]) == 0:
            continue
        res = coll.query(query_embeddings=[got["embeddings"][0]], n_results=6)
        ids = res["ids"][0]
        dists = res["distances"][0]
        for other_id, dist in zip(ids, dists):
            if other_id == art.article_id or other_id not in by_id:
                continue
            sim = 1.0 - dist
            other = by_id[other_id]
            if sim >= dup_t and art.date and art.date == other.date:
                # keep the earliest article_id as canonical; mark the later as duplicate
                loser, winner = sorted([art, other], key=lambda a: a.article_id)[::-1]
                if loser.dedupe_status != "duplicate":
                    loser.dedupe_status = "duplicate"
                    loser.canonical_article_id = winner.article_id
                    if loser.article_id not in winner.related_article_ids:
                        winner.related_article_ids.append(loser.article_id)
                    duplicates += 1
            elif sim >= near_t:
                if other_id not in art.related_article_ids and other.dedupe_status != "duplicate":
                    art.related_article_ids.append(other_id)
                    related += 1
    return {"semantic_duplicates": duplicates, "related_links": related}


def run_dedupe(cfg: Config) -> dict:
    cfg.ensure_dirs()
    db.init_db(cfg.db_path)
    articles = [a for _, a in iter_articles(cfg)]
    by_id = {a.article_id: a for a in articles}

    # reset prior dedupe state so the stage is idempotent
    for art in articles:
        art.dedupe_status = "canonical"
        art.canonical_article_id = None
        art.related_article_ids = []

    # 1) exact duplicates by normalized title hash within the same date
    exact = 0
    seen: dict[tuple[str, str], Article] = {}
    for art in sorted(articles, key=lambda a: a.article_id):
        key = (art.date or "", art.normalized_title_hash)
        if not art.normalized_title_hash:
            continue
        if key in seen:
            canonical = seen[key]
            art.dedupe_status = "duplicate"
            art.canonical_article_id = canonical.article_id
            if art.article_id not in canonical.related_article_ids:
                canonical.related_article_ids.append(art.article_id)
            exact += 1
        else:
            seen[key] = art

    # 2) semantic duplicates / related stories
    semantic = {"semantic_duplicates": 0, "related_links": 0}
    try:
        semantic = _semantic_links(cfg, by_id, cfg.dup_threshold, cfg.near_dup_threshold)
    except Exception as exc:
        semantic = {"enabled": False, "error": str(exc)}

    with db.connect(cfg.db_path) as conn:
        for art in articles:
            _persist(cfg, conn, art)

    canonical = sum(1 for a in articles if a.dedupe_status == "canonical")
    return {
        "articles": len(articles),
        "exact_duplicates": exact,
        "canonical": canonical,
        **semantic,
    }
