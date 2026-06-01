"""Parse daily digests into article-atomic records.

Handles two observed digest layouts:
  * tag line ("Hot New") -> headline -> "Source \u00b7 Date" -> summary
  * acronym code -> concatenated tags ("BreakingHot") -> headline <safelink> ->
    "Date \u00b7 Source" -> summary -> "URL: ... <safelink>"
The parser anchors on the source/date line, which is the most reliable signal.
"""

from __future__ import annotations

import re
import urllib.parse
from datetime import date

from . import util
from .config import Config
from .models import Article
from .normalize import normalize_digest
from .articles_io import write_article

TAG_WORDS = ("hot", "new", "trending", "breaking", "updated", "developing", "launch")
_TAG_TOKEN_RE = re.compile("|".join(TAG_WORDS), re.IGNORECASE)
_TAG_LINE_RE = re.compile(r"^(?:\s*(?:" + "|".join(TAG_WORDS) + r"))+\s*$", re.IGNORECASE)
_ACRONYM_RE = re.compile(r"^[A-Z]{2,5}$")
_YEAR_RE = re.compile(r"\b20\d{2}\b")

_URL_RE = re.compile(r"https?://[^\s)>\]]+")
_MD_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)]+)\)")
_ANGLE_URL_RE = re.compile(r"<\s*(https?://[^>]+)>")

# Map digest section keywords -> canonical topic ids.
_THEME_KEYWORDS = {
    "model-capabilities": ("model", "research", "breakthrough", "benchmark", "reasoning"),
    "datacenter-infrastructure": ("datacenter", "data center", "infrastructure", "chip", "gpu", "compute", "power", "cooling", "silicon", "capex"),
    "policy-regulation": ("policy", "regulation", "safety", "law", "legislation", "export", "government", "court", "copyright"),
    "company-storylines": ("industry", "company", "funding", "valuation", "acquisition", "revenue", "earnings", "product", "tool"),
}

_CHINA_KEYWORDS = (
    "china", "chinese", "deepseek", "beijing", "xi jinping", "export control",
    "export rules", "alibaba", "tencent", "huawei", "u.s.\u2013china", "us-china",
)


def _tags_from_line(line: str) -> list[str] | None:
    if _TAG_LINE_RE.match(line.strip()):
        return [t.capitalize() for t in _TAG_TOKEN_RE.findall(line)]
    return None


def _is_acronym_code(line: str) -> bool:
    return bool(_ACRONYM_RE.match(line.strip()))


def _is_source_line(line: str) -> bool:
    # Strip angle-bracket URLs (including safelinks) before checking
    clean = _ANGLE_URL_RE.sub("", line).strip()
    return (
        " \u00b7 " in clean
        and bool(util.MONTH_NAME_RE.search(clean))
        and len(clean) <= 220
        and "http" not in clean
    )


def _is_theme_candidate(line: str) -> bool:
    s = line.strip()
    if _tags_from_line(s) or _is_source_line(s) or _is_acronym_code(s):
        return False
    if _YEAR_RE.search(s) or "http" in s:
        return False
    words = s.split()
    return (
        1 <= len(words) <= 6
        and len(s) <= 48
        and not s.endswith((".", ":", "!", "?"))
        and s[:1].isupper()
    )


def _is_premarker(line: str) -> bool:
    return bool(_tags_from_line(line)) or _is_acronym_code(line) or _is_theme_candidate(line)


def _unwrap_safelink(url: str) -> str:
    if "safelinks.protection.outlook.com" in url:
        match = re.search(r"[?&]url=([^&]+)", url)
        if match:
            return urllib.parse.unquote(match.group(1)).rstrip(".,;")
    return url.rstrip(".,;")


def _extract_url(*parts: str) -> str | None:
    for text in parts:
        for rx in (_MD_LINK_RE, _ANGLE_URL_RE, _URL_RE):
            m = rx.search(text)
            if m:
                raw = m.group(0) if rx is _URL_RE else m.group(1)
                return _unwrap_safelink(raw)
    return None


def _clean_headline(line: str) -> str:
    line = _ANGLE_URL_RE.sub("", line)
    line = _MD_LINK_RE.sub("", line)
    line = _URL_RE.sub("", line)
    line = re.sub(r"^URL:\s*", "", line)
    line = line.strip().strip("<>").strip(" \u00b7-").strip()
    # strip stray leading/trailing tag tokens left inline on the headline
    tags_alt = "|".join(t.upper() for t in TAG_WORDS)
    line = re.sub(rf"\s+(?:{tags_alt})+\s*$", "", line)
    line = re.sub(rf"^(?:{tags_alt})+\s+", "", line)
    # strip stray 1-3 letter digest section codes at start (e.g. "A X", "I R", "M A B")
    # but preserve real prefixes like AI, EU, US, UK, UC, SK
    _REAL_PREFIXES = {"AI", "EU", "US", "UK", "UC", "SK", "UN", "AR", "VR", "IP"}
    m = re.match(r"^((?:[A-Z]\s+){1,4})", line)
    if m:
        prefix_letters = m.group(1).replace(" ", "")
        if prefix_letters not in _REAL_PREFIXES and len(prefix_letters) <= 4:
            line = line[m.end():]
    return line.strip(" \u00b7-").strip()


def _looks_like_date(seg: str) -> bool:
    seg = seg.strip()
    return bool(util.MONTH_NAME_RE.search(seg)) and bool(_YEAR_RE.search(seg)) and len(seg.split()) <= 4


def _strip_lead_tags(seg: str) -> str:
    return re.sub(r"^(?:(?:" + "|".join(TAG_WORDS) + r")\s+)+", "", seg, flags=re.IGNORECASE).strip()


def _parse_source_line(line: str) -> tuple[str, date | None]:
    # Strip angle-bracket URLs (safelinks) before parsing
    clean = _ANGLE_URL_RE.sub("", line).strip()
    # Remove "read on <Source>" trailing noise
    clean = re.sub(r"\s*\u00b7?\s*read on\b.*$", "", clean, flags=re.IGNORECASE).strip()
    left, _, right = clean.partition(" \u00b7 ")
    art_date = util.extract_date(clean)
    left, right = _strip_lead_tags(left), _strip_lead_tags(right)
    if _looks_like_date(left) and not _looks_like_date(right):
        source = right
    elif _looks_like_date(right) and not _looks_like_date(left):
        source = left
    else:
        source = left or right
    source = re.sub(r"\s*\(.*?\)\s*$", "", source).strip(" \u00b7-")
    return source.strip(), art_date


def _shorten_title(title: str, summary: str) -> tuple[str, str]:
    if len(title) <= 160:
        return title, summary
    head = re.split(r"(?<=[.!?])\s+", title)[0].strip()
    if not head or len(head) > 160:
        head = title[:157].rstrip() + "\u2026"
    new_summary = (title + " " + summary).strip() if summary else title
    return head, new_summary


# Regex to strip leaked tag words from start/end of summaries
_TAG_NOISE_RE = re.compile(
    r"(?:^|\s)(?:" + "|".join(TAG_WORDS) + r")(?:\s+(?:" + "|".join(TAG_WORDS) + r"))*\s*$",
    re.IGNORECASE,
)
_TAG_NOISE_START_RE = re.compile(
    r"^(?:(?:" + "|".join(TAG_WORDS) + r")\s+)+",
    re.IGNORECASE,
)


def _clean_summary(text: str) -> str:
    """Remove leaked tag words and digest noise from summaries."""
    # Strip trailing tag combos: "... LAUNCH TRENDING", "... Hot New"
    text = _TAG_NOISE_RE.sub("", text).strip()
    # Strip leading tag combos (shouldn't normally happen but just in case)
    text = _TAG_NOISE_START_RE.sub("", text).strip()
    # Strip "Sources: ..." trailing attribution blocks
    text = re.sub(r"\s*Sources?:\s+[A-Z][\w\s,/&·\-]*$", "", text).strip()
    return text


def _classify(cfg: Config, title: str, summary: str, theme: str) -> tuple[list[str], list[str], list[str]]:
    haystack = f"{title} {summary} {theme}"
    haystack_lower = haystack.lower()

    # Entities whose names collide with common English/technical words —
    # match only the exact-case label (not lowercased).
    _CASE_SENSITIVE_ENTITIES = {"Perplexity", "Arm", "Cohere"}

    entities = []
    for ent in cfg.entity_list:
        label = ent.get("label", "")
        if not label:
            continue
        if label in _CASE_SENSITIVE_ENTITIES:
            # Case-sensitive match on the original text
            if re.search(rf"\b{re.escape(label)}\b", haystack):
                entities.append(label)
        else:
            keywords = ent.get("keywords", [label.lower()])
            if any(re.search(rf"\b{re.escape(k.lower())}\b", haystack_lower) for k in keywords):
                entities.append(label)

    themes: list[str] = []
    theme_l = theme.lower()
    for topic_id, keywords in _THEME_KEYWORDS.items():
        if any(k in theme_l for k in keywords):
            themes.append(topic_id)
    if not themes:
        for topic_id, keywords in _THEME_KEYWORDS.items():
            if any(k in haystack_lower for k in keywords):
                themes.append(topic_id)
    themes = [t for t in cfg.topic_ids if t in themes] or themes

    cross = ["china-compete"] if any(k in haystack_lower for k in _CHINA_KEYWORDS) else []
    return entities, themes, cross


def parse_digest(cfg: Config, text: str, issue_date: date | None, digest_source: str) -> list[Article]:
    normalized = normalize_digest(text)
    items = [
        ln.strip()
        for ln in normalized.splitlines()
        if ln.strip()
        and not ln.strip().startswith("Daily Brief")
        and ln.strip() not in {"Daily AI News Digest", "Daily Briefing"}
    ]
    n = len(items)
    sources = [idx for idx in range(n) if _is_source_line(items[idx])]

    articles: list[Article] = []
    seen_ids: set[str] = set()
    current_theme = ""

    for pos, s in enumerate(sources):
        if s == 0:
            continue
        headline_idx = s - 1
        raw_headline = items[headline_idx]
        if _is_premarker(raw_headline) and not _ANGLE_URL_RE.search(raw_headline):
            continue  # no real headline before this source line

        # backward scan for tags + nearest theme (theme is sticky across sources)
        tags: list[str] = []
        j = headline_idx - 1
        while j >= 0 and _is_premarker(items[j]):
            t = _tags_from_line(items[j])
            if t:
                tags = t + tags
            elif _is_theme_candidate(items[j]):
                current_theme = items[j]
            j -= 1

        # summary spans from after this source up to the next article's marker block
        next_s = sources[pos + 1] if pos + 1 < len(sources) else n
        summary_end = next_s - 1 if next_s < n else next_s
        while summary_end - 1 > s and _is_premarker(items[summary_end - 1]):
            summary_end -= 1

        summary_lines: list[str] = []
        url_line_url: str | None = None
        for idx in range(s + 1, max(s + 1, summary_end)):
            ln = items[idx]
            is_url_line = ln.startswith("URL:") or (
                bool(_ANGLE_URL_RE.search(ln)) and len(ln.split()) <= 6
            )
            if is_url_line:
                url_line_url = url_line_url or _extract_url(ln)
                continue
            summary_lines.append(ln)

        headline = _clean_headline(raw_headline)
        if not headline:
            continue
        summary = _clean_summary(" ".join(summary_lines).strip())
        headline, summary = _shorten_title(headline, summary)
        source, art_date = _parse_source_line(items[s])
        art_date = art_date or issue_date
        url = _extract_url(raw_headline) or url_line_url

        base_id = f"{util.iso(art_date) or 'undated'}-{util.slugify(headline)}"
        article_id, suffix = base_id, 2
        while article_id in seen_ids:
            article_id = f"{base_id}-{suffix}"
            suffix += 1
        seen_ids.add(article_id)

        entities, themes, cross = _classify(cfg, headline, summary, current_theme)
        article = Article(
            article_id=article_id,
            title=headline,
            date=util.iso(art_date),
            source=source,
            summary=summary,
            theme=current_theme,
            tags=tags,
            url_original=url,
            url_canonical=url,
            url_status="found" if url else "missing",
            digest_source=digest_source,
            entities=entities,
            themes=themes,
            cross_cutting_topics=cross,
        )
        article.compute_hashes()
        articles.append(article)

    return articles


def run_split(cfg: Config) -> dict:
    """Parse every archived raw digest into article-atomic markdown notes."""
    cfg.ensure_dirs()
    digests = sorted(cfg.raw_digest_archive_dir.glob("*.md"))
    written = 0
    for path in digests:
        text = path.read_text(encoding="utf-8", errors="replace")
        issue_date = util.extract_date(path.stem.replace("_", " ")) or util.extract_date(text)
        digest_source = str((cfg.raw_digest_archive_dir / path.name).relative_to(cfg.root))
        for article in parse_digest(cfg, text, issue_date, digest_source):
            write_article(cfg, article)
            written += 1
    return {"digests_parsed": len(digests), "articles_written": written}
