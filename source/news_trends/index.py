"""Index stage: populate SQLite + FTS5 and build Chroma embeddings."""

from __future__ import annotations

import json
from pathlib import Path

from . import db
from .articles_io import iter_articles, write_article
from .config import Config
from .models import Article

_ARTICLE_COLUMNS = (
    "article_id", "title", "date", "source", "summary", "theme", "tags",
    "url_original", "url_canonical", "url_status", "digest_source",
    "article_path", "content_hash", "normalized_title_hash", "canonical_url_hash",
    "entities", "themes", "cross_cutting_topics", "dedupe_status",
    "canonical_article_id", "related_article_ids", "embedding_id", "event_name",
    "created_at", "updated_at",
)


def _row(cfg: Config, path: Path, art: Article, now: str) -> tuple:
    rel = str(path.relative_to(cfg.root))
    return (
        art.article_id, art.title, art.date, art.source, art.summary, art.theme,
        json.dumps(art.tags), art.url_original, art.url_canonical, art.url_status,
        art.digest_source, rel, art.content_hash, art.normalized_title_hash,
        art.canonical_url_hash, json.dumps(art.entities), json.dumps(art.themes),
        json.dumps(art.cross_cutting_topics), art.dedupe_status,
        art.canonical_article_id, json.dumps(art.related_article_ids),
        art.embedding_id, art.event_name, now, now,
    )


def _embed_text(art: Article) -> str:
    return f"{art.title}\n{art.source}\n{art.summary}".strip()


def _build_embeddings(cfg: Config, articles: list[tuple[Path, Article]]) -> dict:
    import chromadb
    from sentence_transformers import SentenceTransformer

    client = chromadb.PersistentClient(path=str(cfg.chroma_dir))
    coll = client.get_or_create_collection("articles", metadata={"hnsw:space": "cosine"})
    existing = set(coll.get(include=[])["ids"])

    pending = [(p, a) for p, a in articles if a.article_id not in existing]
    if pending:
        model = SentenceTransformer(cfg.embedding_model)
        vectors = model.encode(
            [_embed_text(a) for _, a in pending],
            batch_size=64, normalize_embeddings=True, show_progress_bar=False,
        )
        coll.add(
            ids=[a.article_id for _, a in pending],
            embeddings=[v.tolist() for v in vectors],
            documents=[_embed_text(a) for _, a in pending],
            metadatas=[{"date": a.date or "", "source": a.source} for _, a in pending],
        )

    # ensure embedding_id is recorded on every article (db + md)
    rewritten = 0
    for path, art in articles:
        if art.embedding_id != art.article_id:
            art.embedding_id = art.article_id
            write_article(cfg, art)
            rewritten += 1
    return {"enabled": True, "added": len(pending), "total": len(articles), "md_rewritten": rewritten}


def run_index(cfg: Config, with_embeddings: bool = True) -> dict:
    cfg.ensure_dirs()
    db.init_db(cfg.db_path)
    articles = list(iter_articles(cfg))
    now = db.now_iso()

    placeholders = ",".join("?" for _ in _ARTICLE_COLUMNS)
    insert_sql = f"INSERT OR REPLACE INTO articles ({','.join(_ARTICLE_COLUMNS)}) VALUES ({placeholders})"

    with db.connect(cfg.db_path) as conn:
        conn.execute("DELETE FROM articles_fts")
        for path, art in articles:
            conn.execute(insert_sql, _row(cfg, path, art, now))
            conn.execute(
                "INSERT INTO articles_fts (article_id,title,summary,source,entities,themes) "
                "VALUES (?,?,?,?,?,?)",
                (
                    art.article_id, art.title, art.summary, art.source,
                    " ".join(art.entities), " ".join(art.themes),
                ),
            )

    embeddings = {"enabled": False, "reason": "skipped"}
    if with_embeddings:
        try:
            embeddings = _build_embeddings(cfg, articles)
        except Exception as exc:  # degrade gracefully; keyword index still usable
            embeddings = {"enabled": False, "error": str(exc)}

    return {"articles_indexed": len(articles), "embeddings": embeddings}
