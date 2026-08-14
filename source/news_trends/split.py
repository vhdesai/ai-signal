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
_ACRONYM_RE = re.compile(r"^[A-Z][A-Za-z]?$|^[A-Z]{2,5}$")
_YEAR_RE = re.compile(r"\b20\d{2}\b")

_URL_RE = re.compile(r"https?://[^\s)>\]]+")
_MD_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)]+)\)")
_ANGLE_URL_RE = re.compile(r"<\s*(https?://[^>]+)>")

# Digest-level attribution/footer boilerplate (e.g. "Compiled by Microsoft
# Copilot · 10 verified items · Source window: last 24 hours ..."). These lines
# contain " · " and a month name, so without this guard they get mistaken for an
# article's "Source · Date" line and anchor a bogus article.
_DIGEST_FOOTER_RE = re.compile(r"^\s*compiled by\b", re.IGNORECASE)

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

# --- Markdown cleanup -------------------------------------------------------
# Clawpilot-style digests use '#/##/###' headings, '**bold**', '`code`' tag
# chips, '---' horizontal rules and '- [Source](url)' citation lines. These are
# structural markers for parsing but must never leak into reader-facing fields.
_MD_HEADING_RE = re.compile(r"^\s*#{1,6}\s+")
_SECTION_HEADING_RE = re.compile(r"^\s*#{1,2}\s+\S")  # h1/h2 only (h3+ = headline)
_SEPARATOR_RE = re.compile(r"^\s*[-_*]{3,}\s*$")
_MD_LINK_TEXT_RE = re.compile(r"\[([^\]]+)\]\(\s*https?://[^)]+\)")
_MD_BULLET_LINK_RE = re.compile(r"^\s*[-*]?\s*\[[^\]]+\]\(\s*https?://")
_BACKTICK_RE = re.compile(r"`([^`]*)`")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_US_RE = re.compile(r"__([^_]+)__")

# Editorial / attribution boilerplate that some digests append to article
# bodies. These convey no article information and must be stripped from
# reader-facing summaries. Each is removed wherever it appears in the flattened
# summary text (newlines already collapsed to spaces upstream).
_EDITORIAL_BOILERPLATE_RES = [
    # "URL not verified.", "URL not verified (MSN redirect from Business Insider).",
    # "URL not verified — announcement posted on ...": strip to end of the line.
    re.compile(r"\s*URL not verified\b[^\n]*", re.IGNORECASE),
    re.compile(r"\s*Items verified against original sources(?:\s+where accessible)?\s*\.?", re.IGNORECASE),
    re.compile(r"\s*Stories ordered by editorial significance(?:\s+within each theme)?\s*\.?", re.IGNORECASE),
    re.compile(r"\s*(?:Stories covered:\s*)?\b\d+\s+items\s+across\s+\d+\s+themes\s*\.?", re.IGNORECASE),
    re.compile(r"\s*Compiled\b[^.\n]*\bP[DS]T\b\s*\.?", re.IGNORECASE),
    # Editorial-process / authorship footers (no source names or URLs). These
    # are terminal notes, so strip marker-to-end. Source / publication citation
    # lists (e.g. "Sources compiled from: The Decoder, TechCrunch, ...",
    # "Publication Newsletter Sources ...", "Additional coverage from newsletter
    # subscriptions ...") are intentionally PRESERVED per user direction.
    re.compile(r"\s*\bCompiled by Microsoft Copilot\b.*", re.IGNORECASE),
    re.compile(r"\s*\bThis digest covers\b.*", re.IGNORECASE),
    re.compile(r"\s*\bPrepared for Vik Desai\b.*", re.IGNORECASE),
    re.compile(r"\s*\)?\s*\.?\s*\bItems reflect original-publication reporting\b.*", re.IGNORECASE),
    # Bounded: this aggregation note precedes a preserved source list, so strip
    # only the note sentence(s) — stop at end-of-paragraph or before a kept
    # "Publication Newsletter Sources" / "Additional coverage ..." source list.
    re.compile(r"\s*\*?\s*This digest aggregates\b.*?(?=\s*Publication Newsletter Sources|\s*\*?\s*Additional coverage from newsletter subscriptions|$)", re.IGNORECASE),
    # Broken relevant-link search-error dumps (technical artifacts, no real URL).
    re.compile(r"\s*(?:Sources noted:\s*)?(?:Hot\s*[-\u2013]\s*)?Relevant links:\s*_?Search failed:.*", re.IGNORECASE),
]


def _strip_md_inline(text: str) -> str:
    """Remove inline markdown decoration while keeping the readable text."""
    text = _MD_LINK_TEXT_RE.sub(r"\1", text)  # [label](url) -> label
    text = _BOLD_RE.sub(r"\1", text)          # **bold** -> bold
    text = _ITALIC_US_RE.sub(r"\1", text)     # __italic__ -> italic
    text = _BACKTICK_RE.sub(r"\1", text)      # `code` -> code
    return text.replace("**", "").replace("`", "")


def _is_separator(line: str) -> bool:
    return bool(_SEPARATOR_RE.match(line))


def _is_section_heading(line: str) -> bool:
    return bool(_SECTION_HEADING_RE.match(line))


def _is_md_tags_line(line: str) -> bool:
    s = line.strip().lower()
    return s.startswith(("**tags", "tags:")) and bool(
        re.search(r"`|hot|new|trending|breaking|updated|developing|launch", s)
    )


def _tags_from_md_line(line: str) -> list[str] | None:
    """Extract tag chips from a '**Tags:** `HOT` `NEW`' markdown line."""
    if not _is_md_tags_line(line):
        return None
    toks = re.findall(r"`([^`]+)`", line)
    if not toks:
        toks = _TAG_TOKEN_RE.findall(line)
    out = [t.strip().capitalize() for t in toks if t.strip()]
    return out or None


def _tags_from_line(line: str) -> list[str] | None:
    if _TAG_LINE_RE.match(line.strip()):
        return [t.capitalize() for t in _TAG_TOKEN_RE.findall(line)]
    # Also treat lines starting with a tag word + category keywords as tag lines
    # e.g. "HOT CHINA FRONTIER MODELS", "BREAKING REGULATION EU AI ACT"
    words = line.strip().split()
    if words and words[0].lower() in TAG_WORDS and 2 <= len(words) <= 8:
        # All words are uppercase-like (tags are typically ALL CAPS)
        if all(w.isupper() or w == "&" or w.replace("-", "").isupper() for w in words):
            return [words[0].capitalize()]
    # Concatenated tag lines like "HOTAI MONETIZATIONBIG TECH", "TRENDINGORACLEAI CAPEX"
    s = line.strip()
    if s and any(s.lower().startswith(tw) for tw in TAG_WORDS) and len(s) <= 60:
        # If the line starts with a tag word (possibly concatenated) and is mostly uppercase
        upper_ratio = sum(1 for c in s if c.isupper()) / max(len(s.replace(" ", "")), 1)
        if upper_ratio > 0.6:
            for tw in TAG_WORDS:
                if s.lower().startswith(tw):
                    return [tw.capitalize()]
    return None


def _is_acronym_code(line: str) -> bool:
    return bool(_ACRONYM_RE.match(line.strip()))


def _is_source_line(line: str) -> bool:
    # Strip angle-bracket URLs (including safelinks) before checking
    clean = _ANGLE_URL_RE.sub("", line).strip()
    if _DIGEST_FOOTER_RE.match(clean):
        return False  # digest attribution/footer, not an article source line
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
    # Reject very short lines (single/double chars are email formatting artifacts)
    if len(s) <= 2:
        return False
    words = s.split()
    # Reject lines that start with a tag word (e.g. "HOT CHINA FRONTIER MODELS")
    if words and words[0].lower() in TAG_WORDS:
        return False
    # Reject concatenated tag lines (e.g. "HOTAI MONETIZATIONBIG TECH")
    if any(s.lower().startswith(tw) for tw in TAG_WORDS):
        return False
    # Reject mostly-uppercase lines (tag patterns, not section headers)
    alpha_chars = [c for c in s if c.isalpha()]
    if alpha_chars and sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars) > 0.7:
        return False
    return (
        1 <= len(words) <= 6
        and len(s) <= 48
        and not s.endswith((".", ":", "!", "?"))
        and s[:1].isupper()
    )


def _is_premarker(line: str) -> bool:
    return (
        bool(_tags_from_line(line))
        or _is_acronym_code(line)
        or _is_theme_candidate(line)
        or _is_separator(line)
        or _is_section_heading(line)
        or _is_md_tags_line(line)
    )


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
                url = _unwrap_safelink(raw)
                # Skip Bing thumbnail URLs — they're image previews, not article links
                if "bing.net/th" in url:
                    continue
                return url
    return None


def _clean_headline(line: str) -> str:
    line = _MD_HEADING_RE.sub("", line)
    line = _ANGLE_URL_RE.sub("", line)
    line = _MD_LINK_RE.sub("", line)
    line = _URL_RE.sub("", line)
    line = re.sub(r"^URL:\s*", "", line)
    line = _strip_md_inline(line)
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
    return _strip_md_inline(line).strip(" \u00b7-").strip()


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
    # Titles are kept in full; the UI wraps them across lines.
    return title, summary


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
    """Remove markdown decoration, leaked tag words and digest noise."""
    text = _strip_md_inline(text)
    # Drop structural leftovers that can leak in from adjacent sections.
    text = re.sub(r"\s*-{3,}\s*", " ", text)          # '---' horizontal rules
    text = re.sub(r"(?:^|\s)#{1,6}\s+", " ", text)    # stray heading marks (## / ###)
    text = re.sub(
        r"(?i)\bTags?:\s*(?:" + "|".join(TAG_WORDS) + r")\b[\s,]*", "", text
    )
    # Strip trailing tag combos: "... LAUNCH TRENDING", "... Hot New"
    text = _TAG_NOISE_RE.sub("", text).strip()
    # Strip leading tag combos (shouldn't normally happen but just in case)
    text = _TAG_NOISE_START_RE.sub("", text).strip()
    # Strip "Sources: ..." trailing attribution blocks
    text = re.sub(r"\s*Sources?:\s+[A-Z][\w\s,/&·\-]*$", "", text).strip()
    # Strip editorial/attribution boilerplate that leaks in from digest footers
    # (e.g. "URL not verified (MSN redirect ...).", "Compiled ... PDT.",
    # "Items verified against original sources ...", "N items across M themes").
    for pat in _EDITORIAL_BOILERPLATE_RES:
        text = pat.sub(" ", text)
    text = text.strip()
    # Drop a leading list bullet and collapse whitespace.
    text = re.sub(r"^[\-\*\u2022]\s+", "", text).strip()
    return re.sub(r"\s{2,}", " ", text).strip()


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
            t = _tags_from_line(items[j]) or _tags_from_md_line(items[j])
            if t:
                tags = t + tags
            elif _is_theme_candidate(items[j]):
                current_theme = items[j]
            elif _is_section_heading(items[j]):
                current_theme = _MD_HEADING_RE.sub("", items[j]).strip()
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
            is_url_line = (
                ln.startswith("URL:")
                or bool(_MD_BULLET_LINK_RE.match(ln))
                or (bool(_ANGLE_URL_RE.search(ln)) and len(ln.split()) <= 6)
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


# --- Narrative digest format (July 2026+) -----------------------------------
# Newer digests drop the per-article "Source \u00b7 Date" line and safelinks in
# favour of a narrative layout: a short section-theme line followed by one or
# more summary paragraphs, each paragraph describing a single news item, e.g.
#
#   Infrastructure, chips, and physical AI
#
#   TSMC added another $100B in Arizona capacity ...
#
#   NVIDIA released Cosmos 3 Edge ...
#
# There are no URLs. parse_narrative_digest() is used as a fallback when the
# source-line parser (parse_digest) finds nothing.
_NARRATIVE_SKIP_RE = re.compile(
    r"^\s*(?:executive summary|primary sections represented|export note)\b",
    re.IGNORECASE,
)


def _looks_like_theme_line(block: str) -> bool:
    """A short section header (not a sentence) that groups the items below it."""
    if "\n" in block:
        return False
    s = block.strip()
    if not s or len(s) > 80:
        return False
    if s[-1] in ".!?:":            # themes never end with sentence punctuation
        return False
    if _SEPARATOR_RE.match(s):
        return False
    if re.search(r"daily ai news digest", s, re.IGNORECASE):
        return False               # restated digest title, not a theme
    if _YEAR_RE.search(s):
        return False               # dated restated-title lines, not a theme
    if len(s.split()) > 9:         # themes are short phrases
        return False
    return True


def _narrative_title(summary: str) -> str:
    """Derive a headline from the first sentence of an item paragraph.

    Skips abbreviation dots ("U.S.", "Inc.") by only accepting a sentence
    break once a reasonable headline length has accumulated.
    """
    first = summary
    for m in re.finditer(r"[.!?](?:\s|$)", summary):
        if m.start() >= 40:
            first = summary[: m.start() + 1]
            break
    first = first.strip().rstrip(".")
    if len(first) > 120:
        first = first[:120].rsplit(" ", 1)[0] + "\u2026"
    return first


def parse_narrative_digest(cfg: Config, text: str, issue_date: date | None,
                           digest_source: str) -> list[Article]:
    normalized = normalize_digest(text)
    blocks = [b.strip() for b in re.split(r"\n\s*\n", normalized) if b.strip()]
    articles: list[Article] = []
    seen_ids: set[str] = set()
    current_theme = ""

    for block in blocks:
        if _SEPARATOR_RE.match(block):
            continue
        if _looks_like_theme_line(block):
            current_theme = block.strip()
            continue
        if not current_theme:
            continue  # skip restated title / "version:" preface before first theme
        if _NARRATIVE_SKIP_RE.match(block):
            continue  # meta preface / export note, not a news item

        summary = _clean_summary(block.replace("\n", " "))
        if len(summary) < 25:
            continue

        # "Publication email additions" items read "The Information: a; b; c." —
        # use the leading label as the source.
        source = "Daily AI News Digest"
        if "publication" in current_theme.lower() and ": " in summary:
            prefix, _, rest = summary.partition(": ")
            if 0 < len(prefix) <= 40 and rest.strip():
                source, summary = prefix.strip(), rest.strip()

        title = _narrative_title(summary)
        if not title:
            continue

        base_id = f"{util.iso(issue_date) or 'undated'}-{util.slugify(title)}"
        article_id, suffix = base_id, 2
        while article_id in seen_ids:
            article_id = f"{base_id}-{suffix}"
            suffix += 1
        seen_ids.add(article_id)

        entities, themes, cross = _classify(cfg, title, summary, current_theme)
        article = Article(
            article_id=article_id,
            title=title,
            date=util.iso(issue_date),
            source=source,
            summary=summary,
            theme=current_theme,
            tags=[],
            url_original=None,
            url_canonical=None,
            url_status="missing",
            digest_source=digest_source,
            entities=entities,
            themes=themes,
            cross_cutting_topics=cross,
        )
        article.compute_hashes()
        articles.append(article)

    return articles


def _is_event_file(filename: str) -> bool:
    """Event files don't start with a date prefix like daily digests do."""
    return not re.match(r"^\d{4}-\d{2}-\d{2}", filename)


def parse_event(cfg: Config, text: str, digest_source: str) -> list[Article]:
    """Parse an event summary markdown file into individual announcement articles.

    Event files have a standard structure:
        # Event Title
        ## Executive summary (one overview article)
        ## Detailed announcements
        ### Sub-section heading (one article per sub-section)
        ## Strategic implications (one article)
        ## Companies and products (extracted for entity tagging)
        ## Source links → ### External sources and corroborating URLs
    """
    lines = text.splitlines()
    if not lines:
        return []

    # Extract event title
    event_name = lines[0].lstrip("# ").strip()
    if not event_name:
        return []

    # Extract companies mentioned in the "Companies and products" section
    companies_text = ""
    in_companies = False
    for line in lines:
        if re.match(r"^##\s+Companies\b", line, re.IGNORECASE):
            in_companies = True
            continue
        if in_companies:
            if line.startswith("## "):
                break
            companies_text += " " + line

    # Extract external URLs from source links section
    ext_urls: list[tuple[str, str]] = []
    in_ext = False
    for line in lines:
        if "external sources" in line.lower() or "corroborating url" in line.lower():
            in_ext = True
            continue
        if in_ext:
            if line.startswith("## ") or line.startswith("### Source corpus"):
                break
            m = re.search(r"(https?://[^\s)]+)", line)
            if m:
                label = line.split("http")[0].strip("- :").strip()
                ext_urls.append((label, m.group(1).rstrip(".,;")))

    # Extract dates from the Dates and venue section
    event_date_str = ""
    event_date = None
    in_dates = False
    for line in lines:
        if re.match(r"^##\s+Dates\b", line, re.IGNORECASE):
            in_dates = True
            continue
        if in_dates:
            if line.startswith("## "):
                break
            if "**Dates:**" in line or "**dates:**" in line.lower():
                event_date_str = line.split("**Dates:**")[-1].strip().strip("*").strip()
                event_date = util.extract_date(event_date_str)
                break
            # Try extracting a date from any line in this section
            if not event_date:
                event_date = util.extract_date(line)

    articles: list[Article] = []
    seen_ids: set[str] = set()

    def _make_article(title: str, summary: str, section_theme: str,
                      urls: list[tuple[str, str]] | None = None) -> Article | None:
        title = _strip_md_inline(title).strip()
        # Convert markdown list items ("- Label: ...") into readable bullets,
        # then strip remaining inline markdown / decoration from the summary.
        summary = re.sub(r"(?:^|\s)[-*]\s+(?=[A-Z][^:\n]{0,48}:)", " \u2022 ", summary)
        summary = _clean_summary(summary)
        if not title or not summary:
            return None
        full_text = f"{title} {summary} {companies_text}"
        entities, themes, cross = _classify(cfg, title, full_text, section_theme)

        # Find best URL for this article
        url = None
        if urls:
            url = urls[0][1]
        elif ext_urls:
            # Try to find a URL that matches something in the title
            title_lower = title.lower()
            for label, u in ext_urls:
                if any(w in label.lower() for w in title_lower.split()[:3] if len(w) > 3):
                    url = u
                    break

        base_id = f"event-{util.slugify(event_name)}-{util.slugify(title)}"
        article_id = base_id
        suffix = 2
        while article_id in seen_ids:
            article_id = f"{base_id}-{suffix}"
            suffix += 1
        seen_ids.add(article_id)

        art = Article(
            article_id=article_id,
            title=title,
            date=util.iso(event_date),
            source=event_name,
            summary=summary.strip(),
            theme=section_theme,
            tags=["Event"],
            url_original=url,
            url_canonical=url,
            url_status="found" if url else "missing",
            digest_source=digest_source,
            entities=entities,
            themes=themes,
            cross_cutting_topics=cross,
            event_name=event_name,
        )
        art.compute_hashes()
        return art

    # 1. Executive summary → one overview article
    exec_summary = []
    in_exec = False
    for line in lines[1:]:
        if re.match(r"^##\s+Executive summary\b", line, re.IGNORECASE):
            in_exec = True
            continue
        if in_exec:
            if line.startswith("## "):
                break
            if line.strip():
                exec_summary.append(line.strip())
    if exec_summary:
        art = _make_article(
            f"{event_name} \u2014 Overview",
            " ".join(exec_summary),
            "company-storylines",
        )
        if art:
            articles.append(art)

    # 2. Detailed announcements → one article per ### subsection
    in_detail = False
    current_h3 = ""
    current_body: list[str] = []
    for line in lines:
        if re.match(r"^##\s+Detailed announcements\b", line, re.IGNORECASE):
            in_detail = True
            continue
        if in_detail:
            if line.startswith("## ") and not line.startswith("### "):
                # Flush last subsection
                if current_h3 and current_body:
                    art = _make_article(
                        f"{event_name}: {current_h3}",
                        " ".join(current_body),
                        current_h3.lower(),
                    )
                    if art:
                        articles.append(art)
                break
            if line.startswith("### "):
                # Flush previous subsection
                if current_h3 and current_body:
                    art = _make_article(
                        f"{event_name}: {current_h3}",
                        " ".join(current_body),
                        current_h3.lower(),
                    )
                    if art:
                        articles.append(art)
                current_h3 = line.lstrip("# ").strip()
                current_body = []
            elif line.strip():
                current_body.append(line.strip())

    # 3. Strategic implications → one article
    strat_lines: list[str] = []
    in_strat = False
    for line in lines:
        if re.match(r"^##\s+Strategic implications\b", line, re.IGNORECASE):
            in_strat = True
            continue
        if in_strat:
            if line.startswith("## "):
                break
            if line.strip():
                strat_lines.append(line.strip())
    if strat_lines:
        art = _make_article(
            f"{event_name} \u2014 Strategic Implications",
            " ".join(strat_lines),
            "company-storylines",
        )
        if art:
            articles.append(art)

    return articles


def _is_curated_analysis_file(filename: str) -> bool:
    """Curated FY27 strategy / comparison analysis docs are rendered directly as
    site pages (see site.py) and must NOT be parsed into digest articles, which
    would otherwise pollute the daily pages with narrative fragments."""
    return bool(re.search(r"_(?:Strategy|Strategy_Signals|Comparison)\.md$", filename)) \
        and bool(re.match(r"^\d{4}-\d{2}-\d{2}_", filename))


def _is_publication_sources_file(filename: str) -> bool:
    """`*_Publication-Sources.md` digests only list newsletter email subject
    lines and "no emails found" placeholders. They carry no substantive article
    content, so they must never be parsed into articles."""
    return filename.endswith("_Publication-Sources.md") or "Publication-Sources" in filename


# Every published article must carry real information. Digest entries that yield
# only a headline (empty or near-empty body) are dropped rather than written as
# contentless stubs. ~30 words ≈ 4-5 rendered lines of prose.
_MIN_BODY_WORDS = 30


def _has_min_content(article: Article) -> bool:
    return len((article.summary or "").split()) >= _MIN_BODY_WORDS


def _is_masthead_article(article: Article) -> bool:
    """Digest mastheads/overview headers (recipient line, "Corp Dev · Tech
    Assessment", "Compiled 7:00 AM PDT" source) sometimes get mis-parsed into an
    article whose body is the whole-digest overview rather than a single story.
    Their tell is a `source` that begins with "Compiled" or "Prepared for"
    instead of a real publication name. These are dropped."""
    src = (article.source or "").strip().lower()
    return src.startswith("compiled") or src.startswith("prepared for")


def run_split(cfg: Config) -> dict:
    """Parse every archived raw digest into article-atomic markdown notes."""
    cfg.ensure_dirs()
    digests = sorted(cfg.raw_digest_archive_dir.glob("*.md"))
    written = 0
    events_written = 0
    skipped_publication = 0
    skipped_thin = 0
    for path in digests:
        if _is_curated_analysis_file(path.name):
            continue
        if _is_publication_sources_file(path.name):
            skipped_publication += 1
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        digest_source = str((cfg.raw_digest_archive_dir / path.name).relative_to(cfg.root))

        if _is_event_file(path.name):
            for article in parse_event(cfg, text, digest_source):
                write_article(cfg, article)
                events_written += 1
        else:
            issue_date = util.extract_date(path.stem.replace("_", " ")) or util.extract_date(text)
            articles = parse_digest(cfg, text, issue_date, digest_source)
            if not articles:
                articles = parse_narrative_digest(cfg, text, issue_date, digest_source)
            for article in articles:
                if _is_masthead_article(article):
                    skipped_thin += 1
                    continue
                if not _has_min_content(article):
                    skipped_thin += 1
                    continue
                write_article(cfg, article)
                written += 1
    return {"digests_parsed": len(digests), "articles_written": written,
            "events_parsed": sum(1 for d in digests if _is_event_file(d.name)),
            "event_articles_written": events_written,
            "skipped_publication_sources": skipped_publication,
            "skipped_thin_articles": skipped_thin}
