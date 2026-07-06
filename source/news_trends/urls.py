"""URL stage: extract, validate (httpx) and repair (live web search) links.

Repair is deliberately conservative: a candidate URL is only accepted when it is
both reachable (HTTP < 400) *and* relevant to the article (domain/title/source
overlap). This prevents the classic failure where a generic 200-OK page (e.g. the
``axios`` JavaScript library for a story sourced from the *Axios* news outlet) is
silently written as the canonical link. Section-heading pseudo-articles (e.g.
"Model Releases") are skipped entirely, and previously written low-quality repairs
are reverted on the next run.
"""

from __future__ import annotations

import html
import re
from urllib.parse import unquote, urlparse

from . import db
from .articles_io import iter_articles, write_article
from .config import Config
from .models import Article

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NewsTrendsBot/1.0)"}

# Domains that are almost never the source of a news article. A reachable URL on
# one of these is rejected even if it superficially matches a query token.
_BLOCKED_DOMAIN_SUFFIXES = (
    "github.com", "github.io", "githubusercontent.com", "gitlab.com",
    "bitbucket.org", "sourceforge.net", "pypi.org", "npmjs.com", "npmjs.org",
    "readthedocs.io", "readthedocs.org", "stackoverflow.com", "stackexchange.com",
    "w3schools.com", "developer.mozilla.org", "wikipedia.org",
    # Social networks / user-generated aggregators: a reshared post slug often
    # spuriously matches the headline, but the post is not the canonical source.
    "facebook.com", "fb.com", "linkedin.com", "lnkd.in", "twitter.com", "x.com",
    "t.co", "instagram.com", "threads.net", "threads.com", "reddit.com", "redd.it",
    "tiktok.com", "youtube.com", "youtu.be", "pinterest.com", "tumblr.com",
    "mastodon.social", "bsky.app", "quora.com",
)

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "for", "nor", "with", "from", "into",
    "of", "to", "in", "on", "at", "by", "as", "is", "are", "was", "were", "be",
    "its", "it", "this", "that", "these", "those", "has", "have", "had", "will",
    "new", "update", "updates", "news", "daily", "source",
}

# Generic digest section headings that are not real articles and must not be
# sent to web-search repair (normalized token form).
_SECTION_LABELS = {
    "model releases", "model release", "model releases updates", "model capabilities",
    "research breakthroughs", "research breakthrough", "academic research",
    "products tools", "product tools", "industry news", "market signals",
    "market signals context", "ai safety policy", "ai safety security policy",
    "safety policy", "safety security policy", "policy regulation",
    "company storylines", "what changed", "model releases update",
}

_TITLE_TAG_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def _tokens(text: str) -> list[str]:
    """Lowercase significant tokens (len >= 3, no stopwords). Strips emoji/symbols."""
    out: list[str] = []
    for tok in re.findall(r"[a-z0-9]+", (text or "").lower()):
        if len(tok) >= 3 and tok not in _STOPWORDS:
            out.append(tok)
    return out


def _norm_label(text: str) -> str:
    return " ".join(t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t)


def _registrable_domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def _is_blocked_domain(url: str) -> bool:
    domain = _registrable_domain(url)
    return any(domain == s or domain.endswith("." + s) for s in _BLOCKED_DOMAIN_SUFFIXES)


# Domains blocked by Microsoft corporate networks (IT controls). Requests to
# these hang or time out, falsely marking otherwise-fine links as broken and
# stalling the URL stages. They are excluded from the entire URL rebuild: skipped
# during validation and never accepted as a repaired canonical URL.
_NETWORK_BLOCKED_DOMAIN_SUFFIXES = (
    "yandex.com", "yandex.ru", "yandex.net", "yandex.eu", "ya.ru",
    "softonic.com",
)


def _is_network_blocked_domain(url: str) -> bool:
    domain = _registrable_domain(url)
    return any(
        domain == s or domain.endswith("." + s)
        for s in _NETWORK_BLOCKED_DOMAIN_SUFFIXES
    )


def _is_homepage(url: str) -> bool:
    """A site root / section landing page is never an article-specific source."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return True  # e.g. https://replit.com/ or https://thebulletin.org/
    # Single bare segment with no article-identifying detail (no slug words, id,
    # date, or file) is a section landing page, e.g. /news, /blog, /press.
    if "/" not in path and "." not in path and not any(c.isdigit() for c in path):
        return len(path) <= 12
    return False


def _clean_query(art: Article) -> str:
    """Build a search query from significant title tokens plus the source name."""
    title = " ".join(_tokens(art.title))
    source = (art.source or "").strip()
    return f"{title} {source}".strip()


def _is_repairable(art: Article) -> bool:
    """Reject digest section headings and other titles too generic to search safely."""
    title = (art.title or "").strip()
    toks = _tokens(title)
    if not toks:
        return False
    if title.lower().startswith("source"):
        return False
    if _norm_label(title) in _SECTION_LABELS:
        return False
    has_digit = any(c.isdigit() for c in title)
    # Short, generic, URL-less titles are almost always section headings: do not
    # fabricate a link for them.
    if not art.url_original and not has_digit and len(toks) <= 4:
        return False
    return True


def _source_domain_match(art: Article, url: str) -> bool:
    domain = _registrable_domain(url)
    for tok in _tokens(art.source):
        if len(tok) >= 4 and tok in domain:
            return True
    return False


def _is_relevant(art: Article, url: str, page_title: str) -> bool:
    """A candidate must clearly relate to the article, not merely return HTTP 200."""
    if _is_blocked_domain(url):
        return False
    if _is_homepage(url):
        return False
    title_tokens = set(_tokens(art.title))
    if not title_tokens:
        return False
    hay = set(_tokens(page_title)) | set(_tokens(unquote(urlparse(url).path))) | set(
        _tokens(_registrable_domain(url))
    )
    overlap = len(title_tokens & hay)
    if overlap >= 2:
        return True
    return overlap >= 1 and _source_domain_match(art, url)


def _is_bad_repair(art: Article) -> bool:
    """Offline check: does an existing 'repaired' link look wrong (no network)?"""
    url = art.url_canonical or ""
    if not url:
        return True
    if _is_blocked_domain(url):
        return True
    if _is_homepage(url):
        return True
    title_tokens = set(_tokens(art.title))
    hay = set(_tokens(unquote(urlparse(url).path))) | set(_tokens(_registrable_domain(url)))
    overlap = len(title_tokens & hay)
    return not (overlap >= 2 or (overlap >= 1 and _source_domain_match(art, url)))


def _persist(cfg: Config, conn, art: Article) -> None:
    write_article(cfg, art)
    conn.execute(
        "UPDATE articles SET url_original=?, url_canonical=?, url_status=?, http_status=?, "
        "checked_at=?, repair_method=?, updated_at=? WHERE article_id=?",
        (
            art.url_original, art.url_canonical, art.url_status,
            getattr(art, "_http_status", None), db.now_iso(),
            getattr(art, "_repair_method", None), db.now_iso(), art.article_id,
        ),
    )
    conn.execute(
        "INSERT OR REPLACE INTO url_status "
        "(article_id, url_original, url_canonical, url_status, http_status, checked_at, repair_method) "
        "VALUES (?,?,?,?,?,?,?)",
        (
            art.article_id, art.url_original, art.url_canonical, art.url_status,
            getattr(art, "_http_status", None), db.now_iso(),
            getattr(art, "_repair_method", None),
        ),
    )


def _check(client, url: str) -> tuple[bool, int | None]:
    for method in ("head", "get"):
        try:
            resp = getattr(client, method)(url, headers=_HEADERS)
            if resp.status_code < 400:
                return True, resp.status_code
            if method == "get":
                return False, resp.status_code
        except Exception:
            if method == "get":
                return False, None
    return False, None


def _fetch(client, url: str) -> tuple[bool, int | None, str]:
    """Like _check, but also returns the page <title> for relevance scoring."""
    try:
        resp = client.get(url, headers=_HEADERS)
    except Exception:
        return False, None, ""
    if resp.status_code >= 400:
        return False, resp.status_code, ""
    page_title = ""
    try:
        match = _TITLE_TAG_RE.search(resp.text)
        if match:
            page_title = html.unescape(match.group(1)).strip()
    except Exception:
        page_title = ""
    return True, resp.status_code, page_title


def run_validate_urls(cfg: Config, limit: int | None = None) -> dict:
    import httpx

    cfg.ensure_dirs()
    db.init_db(cfg.db_path)
    articles = [a for _, a in iter_articles(cfg)]
    checked = ok = broken = missing = skipped = 0

    with httpx.Client(timeout=10.0, follow_redirects=True) as client, db.connect(cfg.db_path) as conn:
        for art in articles:
            if not art.url_canonical:
                art.url_status = "missing"
                missing += 1
                continue
            if _is_network_blocked_domain(art.url_canonical):
                # Treat as reachable without an HTTP request: keeps the link in
                # the site and prevents the repair stage from touching it.
                art.url_status = "ok"
                art._http_status = None
                skipped += 1
                _persist(cfg, conn, art)
                continue
            if limit is not None and checked >= limit:
                break
            checked += 1
            valid, status = _check(client, art.url_canonical)
            art._http_status = status
            if valid:
                art.url_status = "ok"
                ok += 1
            else:
                art.url_status = "broken"
                broken += 1
                db.queue_review(conn, art.article_id, "broken-url", art.url_canonical or "")
            _persist(cfg, conn, art)

    return {"checked": checked, "ok": ok, "broken": broken, "missing": missing, "skipped": skipped}


# Search backends to skip during URL repair. Yandex is unreachable behind some
# corporate networks (e.g. Microsoft IT controls) and the ddgs backend rotation
# blocks on it until timeout, stalling the whole repair stage.
_EXCLUDED_SEARCH_BACKENDS = {"yandex"}

# Fallback backend list (yandex deliberately omitted) used if the installed ddgs
# version does not expose its engine registry for introspection.
_FALLBACK_SEARCH_BACKENDS = "duckduckgo,google,brave,mojeek,startpage,yahoo,wikipedia"


def _search_backends() -> str:
    """Comma-delimited text backends for ddgs, excluding blocked engines."""
    try:
        from ddgs.ddgs import ENGINES

        keys = [k for k in ENGINES["text"].keys() if k not in _EXCLUDED_SEARCH_BACKENDS]
        if keys:
            return ",".join(keys)
    except Exception:
        pass
    return _FALLBACK_SEARCH_BACKENDS


def _search_candidates(query: str, max_results: int = 5) -> list[str]:
    from ddgs import DDGS

    hrefs: list[str] = []
    try:
        with DDGS(timeout=10) as ddgs:
            for result in ddgs.text(
                query, backend=_search_backends(), max_results=max_results
            ):
                href = result.get("href") or result.get("url")
                if href and href not in hrefs:
                    hrefs.append(href)
    except Exception:
        return hrefs
    return hrefs


def _revert(art: Article) -> None:
    """Drop a wrong canonical URL and reset to the (usually empty) original."""
    art.url_canonical = art.url_original
    art._http_status = None
    art._repair_method = None
    art.url_status = "broken" if art.url_original else "missing"


DEFAULT_REPAIR_TIME_BUDGET_S = 3600.0  # 60 minutes
DEFAULT_REPAIR_WORKERS = 10


def run_repair_urls(
    cfg: Config,
    limit: int | None = None,
    time_budget_s: float | None = DEFAULT_REPAIR_TIME_BUDGET_S,
    max_workers: int = DEFAULT_REPAIR_WORKERS,
    stop_file: str | Path | None = None,
) -> dict:
    """Repair broken/missing URLs via parallel, time-boxed live web search.

    The stage is cooperative and resumable:

    * ``max_workers`` (>= 10 by default) search/fetch threads run concurrently.
      Only the network-bound search+fetch happens off-thread; every SQLite write
      stays on the main thread (single writer, no lock contention).
    * ``time_budget_s`` (default 60 min) caps the network phase. Once the budget
      is spent the stage stops dispatching new results and drains in-flight work.
    * A ``stop_file`` sentinel (default ``indexes/repair.stop``) lets an operator
      request early graceful termination: create the file and the stage finishes
      the current results, then exits.
    * Progress is durable: each repaired/reverted article is persisted and
      committed immediately, and a rolling snapshot is written to
      ``indexes/repair-status.json``. An interrupted run therefore loses nothing —
      already-repaired links are skipped on the next invocation, and still-broken
      ones are simply retried.
    """
    import httpx
    import json
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed

    cfg.ensure_dirs()
    db.init_db(cfg.db_path)
    max_workers = max(1, int(max_workers))
    stop_path = Path(stop_file) if stop_file else (cfg.indexes_dir / "repair.stop")
    status_path = cfg.indexes_dir / "repair-status.json"
    started = time.monotonic()
    deadline = started + time_budget_s if time_budget_s and time_budget_s > 0 else None

    articles = [a for _, a in iter_articles(cfg)]
    repaired = unresolved = attempted = skipped = reverted = 0
    to_repair: list[Article] = []

    def _write_status(state: str) -> None:
        payload = {
            "state": state,
            "to_repair": len(to_repair),
            "attempted": attempted,
            "deferred": max(0, len(to_repair) - attempted),
            "repaired": repaired,
            "unresolved": unresolved,
            "reverted": reverted,
            "skipped": skipped,
            "elapsed_s": round(time.monotonic() - started, 1),
            "time_budget_s": time_budget_s,
            "max_workers": max_workers,
            "updated_at": db.now_iso(),
        }
        try:
            status_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            pass

    # Phase 1 (offline, serial): self-heal bad repairs, drop non-repairable
    # headings, and collect the articles that still need a live web search.
    with db.connect(cfg.db_path) as conn:
        for art in articles:
            dirty = False
            if art.url_status == "repaired":
                if _is_bad_repair(art):
                    _revert(art)
                    reverted += 1
                    dirty = True
                    db.queue_review(conn, art.article_id, "repair-reverted", art.url_canonical or "")
                else:
                    continue  # keep a good existing repair
            if art.url_status in ("ok", "found"):
                continue
            if not _is_repairable(art):
                if dirty:
                    _persist(cfg, conn, art)
                skipped += 1
                continue
            if dirty:
                _persist(cfg, conn, art)
            to_repair.append(art)

    if limit is not None:
        to_repair = to_repair[:limit]
    _write_status("running")

    def _stop_requested() -> bool:
        if stop_path.exists():
            return True
        return deadline is not None and time.monotonic() >= deadline

    def _worker(client, art: Article) -> tuple[str, int | None] | None:
        for candidate in _search_candidates(_clean_query(art)):
            if _is_network_blocked_domain(candidate):
                continue  # never accept a network-blocked URL as a repaired link
            valid, status, page_title = _fetch(client, candidate)
            if valid and _is_relevant(art, candidate, page_title):
                return (candidate, status)
        return None

    terminated = "completed"
    # Phase 2 (parallel, network): search/fetch off-thread, persist on-thread.
    with httpx.Client(timeout=10.0, follow_redirects=True) as client, db.connect(cfg.db_path) as conn:
        executor = ThreadPoolExecutor(max_workers=max_workers)
        futures = {executor.submit(_worker, client, art): art for art in to_repair}
        try:
            for fut in as_completed(futures):
                art = futures[fut]
                attempted += 1
                try:
                    chosen = fut.result()
                except Exception:
                    chosen = None
                if chosen:
                    art.url_canonical, art._http_status = chosen
                    art._repair_method = "web-search"
                    art.url_status = "repaired"
                    repaired += 1
                else:
                    # Do not fabricate: keep the original (often empty) and flag it.
                    _revert(art)
                    unresolved += 1
                    db.queue_review(conn, art.article_id, "repair-failed", _clean_query(art))
                _persist(cfg, conn, art)
                conn.commit()  # durable, incremental progress
                if attempted % 10 == 0:
                    _write_status("running")
                # Stop *after* banking the just-completed result so no search is
                # wasted; in-flight work is then drained by shutdown() below.
                if _stop_requested():
                    terminated = "stop-file" if stop_path.exists() else "timeout"
                    break
        finally:
            # Drain in-flight searches, cancel any not yet started.
            executor.shutdown(wait=True, cancel_futures=True)

    deferred = max(0, len(to_repair) - attempted)
    _write_status(terminated)
    if terminated == "stop-file":  # consume the honoured sentinel
        try:
            stop_path.unlink()
        except OSError:
            pass

    return {
        "attempted": attempted, "repaired": repaired, "unresolved": unresolved,
        "skipped": skipped, "reverted": reverted, "deferred": deferred,
        "terminated": terminated, "elapsed_s": round(time.monotonic() - started, 1),
        "max_workers": max_workers,
    }


def run_clean_repairs(cfg: Config) -> dict:
    """Offline pass: revert existing 'repaired' links that fail the relevance gate."""
    cfg.ensure_dirs()
    db.init_db(cfg.db_path)
    reverted = kept = 0

    with db.connect(cfg.db_path) as conn:
        for _, art in iter_articles(cfg):
            if art.url_status != "repaired":
                continue
            if _is_bad_repair(art):
                _revert(art)
                reverted += 1
                db.queue_review(conn, art.article_id, "repair-reverted", art.url_canonical or "")
                _persist(cfg, conn, art)
            else:
                kept += 1

    return {"reverted": reverted, "kept": kept}
