"""Configuration loading and path resolution for the News Trends pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIRNAME = "config"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


@dataclass
class Config:
    """Resolved pipeline configuration rooted at the Obsidian directory."""

    root: Path
    source_dir: Path
    sources: dict[str, Any] = field(default_factory=dict)
    topics: dict[str, Any] = field(default_factory=dict)
    entities: dict[str, Any] = field(default_factory=dict)
    dedupe: dict[str, Any] = field(default_factory=dict)
    publishing: dict[str, Any] = field(default_factory=dict)
    embeddings: dict[str, Any] = field(default_factory=dict)
    retention: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, root: Path) -> "Config":
        root = Path(root).resolve()
        source_dir = root / "source"
        config_dir = source_dir / CONFIG_DIRNAME
        return cls(
            root=root,
            source_dir=source_dir,
            sources=_load_yaml(config_dir / "sources.yaml"),
            topics=_load_yaml(config_dir / "topics.yaml"),
            entities=_load_yaml(config_dir / "entities.yaml"),
            dedupe=_load_yaml(config_dir / "dedupe-thresholds.yaml"),
            publishing=_load_yaml(config_dir / "publishing.yaml"),
            embeddings=_load_yaml(config_dir / "embeddings.yaml"),
            retention=_load_yaml(config_dir / "retention.yaml"),
        )

    def _resolved(self, key: str, default: str) -> Path:
        value = self.sources.get(key, default)
        candidate = Path(value)
        return candidate if candidate.is_absolute() else self.root / candidate

    @cached_property
    def news_dir(self) -> Path:
        return self._resolved("news_dir", "news")

    @cached_property
    def raw_digest_archive_dir(self) -> Path:
        return self._resolved("raw_digest_archive_dir", "digests/raw")

    @cached_property
    def articles_dir(self) -> Path:
        return self._resolved("articles_dir", "articles")

    @cached_property
    def site_dir(self) -> Path:
        return self._resolved("site_dir", "site")

    @cached_property
    def hubs_dir(self) -> Path:
        return self._resolved("hubs_dir", "hubs")

    @cached_property
    def indexes_dir(self) -> Path:
        return self._resolved("indexes_dir", "indexes")

    @cached_property
    def db_path(self) -> Path:
        return self.indexes_dir / "news_trends.db"

    @cached_property
    def chroma_dir(self) -> Path:
        return self.indexes_dir / "chroma"

    @cached_property
    def runs_dir(self) -> Path:
        return self.indexes_dir / "runs"

    def ensure_dirs(self) -> None:
        for path in (
            self.raw_digest_archive_dir,
            self.articles_dir,
            self.site_dir,
            self.hubs_dir,
            self.indexes_dir,
            self.chroma_dir,
            self.runs_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

    # --- typed config helpers -------------------------------------------------
    @property
    def topic_ids(self) -> list[str]:
        return [t["id"] for t in self.topics.get("topics", [])]

    @property
    def cross_cutting_ids(self) -> list[str]:
        return [t["id"] for t in self.topics.get("cross_cutting_topics", [])]

    @property
    def entity_list(self) -> list[dict[str, str]]:
        return list(self.entities.get("entities", []))

    @property
    def dup_threshold(self) -> float:
        return float(self.dedupe.get("same_day_duplicate_commonality", 0.90))

    @property
    def near_dup_threshold(self) -> float:
        return float(self.dedupe.get("same_day_near_duplicate_commonality", 0.70))

    @property
    def embedding_model(self) -> str:
        return self.embeddings.get("default_model", "BAAI/bge-small-en-v1.5")

    @property
    def retention_days(self) -> int:
        return int(self.retention.get("daily_snapshot_retention_days", 31))
