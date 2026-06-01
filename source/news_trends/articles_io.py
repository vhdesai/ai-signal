"""Read/write article-atomic markdown notes with YAML frontmatter."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

import yaml

from .config import Config
from .models import Article

_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
_GRAPH_BLOCK_RE = re.compile(
    r"\n*<!-- graph:start -->.*?<!-- graph:end -->\n*", re.DOTALL
)


def article_path(cfg: Config, article: Article) -> Path:
    year, month = "0000", "00"
    if article.date:
        year, month = article.date[:4], article.date[5:7]
    return cfg.articles_dir / year / month / f"{article.article_id}.md"


def write_article(cfg: Config, article: Article) -> Path:
    path = article_path(cfg, article)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = article.to_markdown()
    # Preserve an existing build-graph connections block so URL/dedupe rewrites
    # don't clobber the graph edges appended by the build-graph stage.
    if path.exists():
        match = _GRAPH_BLOCK_RE.search(path.read_text(encoding="utf-8"))
        if match:
            text = text.rstrip() + "\n\n" + match.group(0).strip() + "\n"
    path.write_text(text, encoding="utf-8")
    return path


def read_article(path: Path) -> Article:
    raw = path.read_text(encoding="utf-8")
    match = _FM_RE.match(raw)
    fm = yaml.safe_load(match.group(1)) if match else {}
    body = match.group(2) if match else raw
    body = _GRAPH_BLOCK_RE.sub("\n", body).strip()
    body = re.sub(r"^#\s+.*\n+", "", body, count=1).strip()
    fm = fm or {}
    return Article(
        article_id=fm.get("article_id", path.stem),
        title=fm.get("title", ""),
        date=fm.get("date"),
        source=fm.get("source", ""),
        summary=body,
        tags=fm.get("tags", []) or [],
        url_original=fm.get("url_original"),
        url_canonical=fm.get("url_canonical"),
        url_status=fm.get("url_status", "unknown"),
        digest_source=fm.get("digest_source", ""),
        content_hash=fm.get("content_hash", ""),
        normalized_title_hash=fm.get("normalized_title_hash", ""),
        canonical_url_hash=fm.get("canonical_url_hash", ""),
        entities=fm.get("entities", []) or [],
        themes=fm.get("themes", []) or [],
        cross_cutting_topics=fm.get("cross_cutting_topics", []) or [],
        dedupe_status=fm.get("dedupe_status", "canonical"),
        canonical_article_id=fm.get("canonical_article_id"),
        related_article_ids=fm.get("related_article_ids", []) or [],
        embedding_id=fm.get("embedding_id"),
        event_name=fm.get("event_name", ""),
    )


def iter_articles(cfg: Config) -> Iterator[tuple[Path, Article]]:
    for path in sorted(cfg.articles_dir.rglob("*.md")):
        yield path, read_article(path)
