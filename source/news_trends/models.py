"""Article data model and frontmatter serialization."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path

import yaml

from . import util


@dataclass
class Article:
    article_id: str
    title: str
    date: str | None
    source: str
    summary: str
    theme: str = ""
    tags: list[str] = field(default_factory=list)
    url_original: str | None = None
    url_canonical: str | None = None
    url_status: str = "unknown"
    digest_source: str = ""
    content_hash: str = ""
    normalized_title_hash: str = ""
    canonical_url_hash: str = ""
    entities: list[str] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    cross_cutting_topics: list[str] = field(default_factory=list)
    dedupe_status: str = "canonical"
    canonical_article_id: str | None = None
    related_article_ids: list[str] = field(default_factory=list)
    embedding_id: str | None = None

    def compute_hashes(self) -> None:
        from .normalize import normalize_title

        self.content_hash = util.sha256(f"{self.title}\n{self.summary}")
        self.normalized_title_hash = util.short_hash(normalize_title(self.title))
        if self.url_canonical:
            self.canonical_url_hash = util.short_hash(self.url_canonical.strip().lower())

    def frontmatter(self) -> dict:
        return {
            "article_id": self.article_id,
            "title": self.title,
            "date": self.date,
            "source": self.source,
            "url_original": self.url_original,
            "url_canonical": self.url_canonical,
            "url_status": self.url_status,
            "digest_source": self.digest_source,
            "content_hash": self.content_hash,
            "normalized_title_hash": self.normalized_title_hash,
            "canonical_url_hash": self.canonical_url_hash,
            "tags": self.tags,
            "entities": self.entities,
            "themes": self.themes,
            "cross_cutting_topics": self.cross_cutting_topics,
            "dedupe_status": self.dedupe_status,
            "canonical_article_id": self.canonical_article_id,
            "related_article_ids": self.related_article_ids,
            "embedding_id": self.embedding_id,
        }

    def to_markdown(self) -> str:
        fm = yaml.safe_dump(self.frontmatter(), sort_keys=False, allow_unicode=True).strip()
        return f"---\n{fm}\n---\n\n# {self.title}\n\n{self.summary}\n"
