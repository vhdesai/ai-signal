"""Build an interconnected Obsidian graph from the article-atomic notes.

This stage is purely additive and idempotent: it (re)writes a delimited
``<!-- graph:start --> ... <!-- graph:end -->`` block at the foot of every
article note containing Obsidian ``[[wikilinks]]`` for the article's entities,
topics/themes, cross-cutting topics, and related/canonical articles. It also
regenerates a set of hub / Map-of-Content (MOC) notes under ``hubs/`` so each
entity and topic becomes a real, navigable node that connects its members.

Because the links live inside a clearly delimited block (and ``read_article``
strips that block before deriving an article's summary), re-running ``index``
or ``dedupe`` after this stage never pollutes embeddings or hashes.
"""

from __future__ import annotations

import re
import time
from collections import defaultdict
from pathlib import Path

from .articles_io import iter_articles
from .config import Config
from .models import Article

GRAPH_BLOCK_RE = re.compile(
    r"\n*<!-- graph:start -->.*?<!-- graph:end -->\n*", re.DOTALL
)


def _rmtree_resilient(path: Path, attempts: int = 5) -> None:
    """Clear a directory tree, tolerating transient sync-client locks.

    OneDrive (and similar sync clients) can momentarily re-open a just-emptied
    directory, making ``os.rmdir`` race and raise ``PermissionError``. We delete
    files individually (retrying briefly) and treat directory-removal failures as
    non-fatal: a lingering empty directory is harmless because hubs are recreated
    on every run. Stale *files* are what must go, and those are removed.
    """
    if not path.exists():
        return
    for entry in sorted(path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        for attempt in range(attempts):
            try:
                if entry.is_dir():
                    entry.rmdir()
                else:
                    entry.unlink()
                break
            except FileNotFoundError:
                break
            except OSError:
                if entry.is_dir():
                    break  # empty-dir lock is harmless; leave it
                time.sleep(0.4 * (attempt + 1))
    try:
        path.rmdir()
    except OSError:
        pass  # top-level dir may be transiently locked; recreated below

_UNSAFE_LINK = re.compile(r'[\\/:*?"<>|\[\]#^]')


def _safe_name(text: str) -> str:
    """Return a vault-safe note basename / wikilink target."""
    cleaned = _UNSAFE_LINK.sub(" ", str(text)).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "untitled"


def _topic_labels(cfg: Config) -> dict[str, str]:
    labels: dict[str, str] = {}
    for group in ("topics", "cross_cutting_topics"):
        for topic in cfg.topics.get(group, []) or []:
            tid = topic.get("id")
            if tid:
                labels[tid] = topic.get("label", tid)
    return labels


def _link(target: str, alias: str | None = None) -> str:
    target = _safe_name(target)
    if alias and _safe_name(alias) != target:
        return f"[[{target}|{alias}]]"
    return f"[[{target}]]"


def _topic_targets(article: Article, labels: dict[str, str]) -> list[str]:
    ids: list[str] = []
    for tid in list(article.themes) + list(article.cross_cutting_topics):
        if tid and tid not in ids:
            ids.append(tid)
    return [labels.get(tid, tid) for tid in ids]


def _build_block(article: Article, labels: dict[str, str]) -> str:
    lines = ["<!-- graph:start -->", "## Connections", ""]

    entities = [_link(e) for e in article.entities if str(e).strip()]
    if entities:
        lines.append("**Entities:** " + " · ".join(entities))

    topics = [_link(t) for t in _topic_targets(article, labels)]
    if topics:
        lines.append("**Topics:** " + " · ".join(topics))

    if article.dedupe_status == "duplicate" and article.canonical_article_id:
        lines.append("**Canonical:** " + _link(article.canonical_article_id))

    related = [
        _link(rid)
        for rid in article.related_article_ids
        if rid and rid != article.canonical_article_id
    ]
    if related:
        shown = related[:25]
        more = len(related) - len(shown)
        suffix = f" _(+{more} more)_" if more > 0 else ""
        lines.append("**Related:** " + " · ".join(shown) + suffix)

    lines.append("<!-- graph:end -->")
    return "\n".join(lines)


def _apply_block(path: Path, block: str) -> None:
    raw = path.read_text(encoding="utf-8")
    raw = GRAPH_BLOCK_RE.sub("\n", raw).rstrip()
    path.write_text(raw + "\n\n" + block + "\n", encoding="utf-8")


def _write_hub(
    directory: Path,
    name: str,
    hub_type: str,
    members: list[tuple[str, str, str]],
) -> None:
    safe = _safe_name(name)
    directory.mkdir(parents=True, exist_ok=True)
    members = sorted(members, key=lambda m: (m[2] or "", m[1]), reverse=True)
    body = [
        "---",
        f"type: {hub_type}",
        f"hub: {safe}",
        f"member_count: {len(members)}",
        "---",
        "",
        f"# {safe}",
        "",
        f"> Auto-generated {hub_type.replace('-', ' ')}. "
        f"{len(members)} connected article(s).",
        "",
    ]
    for article_id, title, date in members:
        prefix = f"- `{date}` " if date else "- "
        body.append(f"{prefix}{_link(article_id, title)}")
    body.append("")
    (directory / f"{safe}.md").write_text("\n".join(body), encoding="utf-8")


def _write_index(
    cfg: Config,
    entity_names: list[str],
    topic_names: list[str],
    article_count: int,
) -> None:
    lines = [
        "---",
        "type: vault-index",
        "---",
        "",
        "# News Trends — Knowledge Graph",
        "",
        f"> {article_count} article notes · {len(entity_names)} entity hubs · "
        f"{len(topic_names)} topic hubs. Open **Graph view** to explore.",
        "",
        "## Entities",
        "",
        " · ".join(_link(n) for n in sorted(entity_names)) or "_none_",
        "",
        "## Topics",
        "",
        " · ".join(_link(n) for n in sorted(topic_names)) or "_none_",
        "",
    ]
    (cfg.root / "_Index.md").write_text("\n".join(lines), encoding="utf-8")


def run_build_graph(cfg: Config) -> dict:
    labels = _topic_labels(cfg)

    entity_members: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    topic_members: dict[str, list[tuple[str, str, str]]] = defaultdict(list)

    linked = 0
    edges = 0
    for path, article in iter_articles(cfg):
        block = _build_block(article, labels)
        _apply_block(path, block)
        linked += 1
        edges += block.count("[[")

        member = (article.article_id, article.title, article.date or "")
        for entity in article.entities:
            if str(entity).strip():
                entity_members[_safe_name(entity)].append(member)
        for topic in _topic_targets(article, labels):
            topic_members[_safe_name(topic)].append(member)

    hubs_dir = cfg.hubs_dir
    if hubs_dir.exists():
        _rmtree_resilient(hubs_dir)
    entities_dir = hubs_dir / "entities"
    topics_dir = hubs_dir / "topics"

    for name, members in entity_members.items():
        _write_hub(entities_dir, name, "entity-hub", members)
    for name, members in topic_members.items():
        _write_hub(topics_dir, name, "topic-hub", members)

    _write_index(
        cfg,
        list(entity_members.keys()),
        list(topic_members.keys()),
        linked,
    )

    return {
        "status": "ok",
        "articles_linked": linked,
        "wikilinks_emitted": edges,
        "entity_hubs": len(entity_members),
        "topic_hubs": len(topic_members),
        "hubs_dir": str(hubs_dir),
    }
