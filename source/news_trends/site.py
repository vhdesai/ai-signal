"""Static site generation (Jinja2) for the public-facing AI Signal site."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from jinja2 import Template

from . import db
from .config import Config

# ---------------------------------------------------------------------------
# Display-name mappings
# ---------------------------------------------------------------------------
TOPIC_LABELS: dict[str, str] = {
    "model-capabilities": "\U0001f9e0 Model Breakthroughs",
    "datacenter-infrastructure": "\u26a1 Infrastructure & Compute",
    "policy-regulation": "\U0001f4dc Policy & Regulation",
    "company-storylines": "\U0001f3e2 Corporate Moves",
    "what-changed": "\U0001f504 What Changed",
    "related-stories": "\U0001f517 Related Stories",
    "china-compete": "\U0001f30f Global AI Race",
}

NAV_LABELS: dict[str, str] = {
    "index": "Daily Brief",
    "archive": "Timeline",
    "topics": "Themes",
    "entities": "Players",
    "search": "Search",
}

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
_BASE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} \u00b7 AI Signal</title>
<style>
 :root{--brand:#0d6b5e;--brand-light:#0f9983;--accent:#f59e0b;--bg:#f0f5f4;--card:#fff;--text:#1b1f24;--muted:#5a6b7b;--border:#e2e6ea;--radius:10px}
 *{box-sizing:border-box}
 body{font-family:'Segoe UI',system-ui,-apple-system,Roboto,sans-serif;margin:0;background:var(--bg);color:var(--text);line-height:1.6}

 /* ---- header / nav ---- */
 header{background:linear-gradient(135deg,#0d6b5e 0%,#0f9983 50%,#2dd4a8 100%);color:#fff;padding:0 24px;display:flex;align-items:center;gap:0;box-shadow:0 2px 12px rgba(0,0,0,.18)}
 .brand{font-size:20px;font-weight:800;letter-spacing:-.5px;padding:16px 0;margin-right:40px;white-space:nowrap;
        background:linear-gradient(90deg,#fff 0%,#94ffd8 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
 nav{display:flex;gap:4px;flex-wrap:wrap}
 nav a{color:rgba(255,255,255,.78);text-decoration:none;font-size:14px;font-weight:500;padding:10px 14px;border-radius:6px;transition:all .2s}
 nav a:hover,nav a.active{background:rgba(255,255,255,.15);color:#fff}

 /* ---- main ---- */
 main{max-width:1020px;margin:0 auto;padding:28px 24px 48px}
 h1{font-size:24px;font-weight:700;margin:0 0 4px}
 .subtitle{color:var(--muted);font-size:14px;margin:0 0 24px}
 h2{font-size:18px;margin-top:32px;color:var(--brand)}

 /* ---- cards ---- */
 .card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin:14px 0;
       transition:box-shadow .2s,transform .15s}
 .card:hover{box-shadow:0 4px 16px rgba(0,0,0,.08);transform:translateY(-1px)}
 a.t{color:var(--brand);text-decoration:none;font-weight:600;font-size:15px;line-height:1.4}
 a.t:hover{color:var(--brand-light);text-decoration:underline}
 .meta{color:var(--muted);font-size:12.5px;margin:6px 0 8px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
 .meta-dot::before{content:'\u00b7';margin:0 2px}
 .summary{font-size:14px;color:#333;margin:8px 0}
 .dupe{opacity:.5;border-left:3px solid #ccc}

 /* ---- tags / badges ---- */
 .tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
 .tag{display:inline-block;border-radius:12px;padding:2px 10px;font-size:11.5px;font-weight:500}
 .tag-label{background:#eef3f8;color:#2c5282}
 .tag-entity{background:#fef3c7;color:#92400e}
 .tag-topic{background:#e0e7ff;color:#3730a3}
 .tag-hot{background:#fee2e2;color:#991b1b}

 /* ---- grid cards for index pages ---- */
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin-top:16px}
 .grid .card{margin:0}
 .card .count{font-size:24px;font-weight:700;color:var(--brand)}
 .card .label{font-size:13px;color:var(--muted);margin-top:2px}

 /* ---- letter nav ---- */
 .letter-nav{display:flex;flex-wrap:wrap;gap:4px;margin:16px 0;padding:12px 16px;background:var(--card);border-radius:var(--radius);border:1px solid var(--border)}
 .letter-nav a{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:6px;font-weight:600;font-size:13px;
               color:var(--brand);text-decoration:none;transition:all .15s}
 .letter-nav a:hover{background:var(--brand);color:#fff}
 .letter-nav a.disabled{color:#ccc;pointer-events:none}

 /* ---- search ---- */
 .search-box{position:relative;margin-bottom:20px}
 .search-box input{width:100%;padding:14px 18px 14px 44px;font-size:15px;border:2px solid var(--border);border-radius:var(--radius);
                    transition:border-color .2s;outline:none;background:var(--card)}
 .search-box input:focus{border-color:var(--brand)}
 .search-box::before{content:'\U0001f50d';position:absolute;left:14px;top:50%;transform:translateY(-50%);font-size:18px;opacity:.5}
 .search-count{color:var(--muted);font-size:13px;margin-bottom:12px}

 /* ---- footer ---- */
 footer{color:var(--muted);font-size:12px;padding:32px 24px;text-align:center;border-top:1px solid var(--border);margin-top:32px}

 /* ---- responsive ---- */
 @media(max-width:640px){
   header{flex-direction:column;align-items:flex-start;gap:4px;padding:12px 16px}
   .brand{margin-right:0;padding:8px 0 4px}
   nav{gap:0}
   main{padding:16px}
   .grid{grid-template-columns:1fr}
 }
</style></head><body>
<header>
 <div class="brand">\U0001f4e1 AI Signal</div>
 <nav>
  <a href="{{ rel }}index.html"{% if active=='index' %} class="active"{% endif %}>Daily Brief</a>
  <a href="{{ rel }}archive.html"{% if active=='archive' %} class="active"{% endif %}>Timeline</a>
  <a href="{{ rel }}topics.html"{% if active=='topics' %} class="active"{% endif %}>Themes</a>
  <a href="{{ rel }}entities.html"{% if active=='entities' %} class="active"{% endif %}>Players</a>
  <a href="{{ rel }}search.html"{% if active=='search' %} class="active"{% endif %}>Search</a>
 </nav>
</header><main>
<h1>{{ title }}</h1>
{% if subtitle %}<p class="subtitle">{{ subtitle }}</p>{% endif %}
{{ body }}
</main><footer>\u00a9 AI Signal \u00b7 Public \u00b7 ai-signal</footer>
</body></html>"""

_CARD = """<div class="card {{ 'dupe' if a.dedupe_status=='duplicate' else '' }}">
  <a class="t" href="{{ a.url_canonical or '#' }}">{{ a.title }}</a>
  <div class="meta">
    <span>{{ a.date }}</span>
    {% if a.source %}<span class="meta-dot">{{ a.source }}</span>{% endif %}
    {% if a.url_status and a.url_status != 'missing' %}<span class="meta-dot">{{ a.url_status }}</span>{% endif %}
    {% if a.theme_label %}<span class="meta-dot">{{ a.theme_label }}</span>{% endif %}
  </div>
  <div class="summary">{{ a.summary }}</div>
  <div class="tags">
  {%- for t in a.tags %}<span class="tag tag-hot">{{ t }}</span>{% endfor -%}
  {%- for e in a.entities %}<span class="tag tag-entity">{{ e }}</span>{% endfor -%}
  {%- for c in a.cross_cutting %}<span class="tag tag-topic">{{ c }}</span>{% endfor -%}
  </div>
</div>"""


def _render(title: str, body: str, rel: str = "", active: str = "",
            subtitle: str = "") -> str:
    return Template(_BASE).render(title=title, body=body, rel=rel,
                                  active=active, subtitle=subtitle)


def _topic_label(slug: str) -> str:
    """Return a human-friendly display name for a topic slug."""
    return TOPIC_LABELS.get(slug, slug.replace("-", " ").title())


def _cards(articles: list[dict]) -> str:
    tmpl = Template(_CARD)
    out = []
    for a in articles:
        a = dict(a)
        a["theme_label"] = _topic_label(a.get("theme", "")) if a.get("theme") else ""
        out.append(tmpl.render(a=a))
    return "\n".join(out)


def _load(cfg: Config) -> list[dict]:
    db.init_db(cfg.db_path)
    rows = []
    with db.connect(cfg.db_path) as conn:
        for r in conn.execute("SELECT * FROM articles ORDER BY date DESC, article_id"):
            d = dict(r)
            for col in ("tags", "entities", "themes", "cross_cutting_topics", "related_article_ids"):
                try:
                    d[col] = json.loads(d.get(col) or "[]")
                except (TypeError, json.JSONDecodeError):
                    d[col] = []
            d["cross_cutting"] = d["cross_cutting_topics"]
            rows.append(d)
    return rows


def _write(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def run_build_site(cfg: Config) -> dict:
    cfg.ensure_dirs()
    site = cfg.site_dir
    articles = _load(cfg)
    canonical = [a for a in articles if a["dedupe_status"] != "duplicate"]
    pages = 0

    # --- snapshot (latest date) = index.html ---
    latest = canonical[0]["date"] if canonical else None
    snap = [a for a in canonical if a["date"] == latest]
    total_canon = len(canonical)
    total_dates = len({a["date"] for a in canonical if a["date"]})
    body = (
        f'<div class="grid">'
        f'<div class="card"><div class="count">{len(snap)}</div><div class="label">stories today</div></div>'
        f'<div class="card"><div class="count">{total_canon:,}</div><div class="label">total articles</div></div>'
        f'<div class="card"><div class="count">{total_dates}</div><div class="label">days covered</div></div>'
        f'</div>'
        + _cards(snap)
    )
    _write(site / "index.html",
           _render(f"Daily Brief \u2014 {latest or 'n/a'}", body,
                   active="index",
                   subtitle=f"Latest snapshot from {latest or 'n/a'} \u2014 {len(snap)} stories"))
    pages += 1

    # --- archive + per-date snapshots ---
    by_date: dict[str, list[dict]] = defaultdict(list)
    for a in canonical:
        by_date[a["date"] or "undated"].append(a)
    rows = '<div class="grid">' + "".join(
        f'<div class="card"><a class="t" href="snapshots/{d}.html">{d}</a>'
        f'<div class="count">{len(items)}</div><div class="label">stories</div></div>'
        for d, items in sorted(by_date.items(), reverse=True)
    ) + '</div>'
    _write(site / "archive.html",
           _render("Timeline", rows, active="archive",
                   subtitle=f"{len(by_date)} days \u00b7 {total_canon:,} articles"))
    pages += 1
    for d, items in by_date.items():
        _write(site / "snapshots" / f"{d}.html",
                _render(f"Snapshot \u2014 {d}", _cards(items), rel="../",
                        subtitle=f"{len(items)} stories"))
        pages += 1

    # --- topics ---
    by_topic: dict[str, list[dict]] = defaultdict(list)
    for a in canonical:
        for t in a["themes"] + a["cross_cutting"]:
            by_topic[t].append(a)
    topic_rows = '<div class="grid">' + "".join(
        f'<div class="card"><a class="t" href="topics/{t}.html">{_topic_label(t)}</a>'
        f'<div class="count">{len(items)}</div><div class="label">stories</div></div>'
        for t, items in sorted(by_topic.items(), key=lambda x: len(x[1]), reverse=True)
    ) + '</div>'
    _write(site / "topics.html",
           _render("Themes", topic_rows, active="topics",
                   subtitle="Browse AI news by theme"))
    pages += 1
    for t, items in by_topic.items():
        _write(site / "topics" / f"{t}.html",
               _render(_topic_label(t), _cards(items), rel="../",
                       subtitle=f"{len(items)} stories"))
        pages += 1

    # --- entities (alphabetical with letter nav) ---
    ent_counter: Counter = Counter()
    by_entity: dict[str, list[dict]] = defaultdict(list)
    for a in canonical:
        for e in a["entities"]:
            ent_counter[e] += 1
            by_entity[e].append(a)

    sorted_entities = sorted(ent_counter.keys(), key=str.upper)
    letters_with_entities = sorted({e[0].upper() for e in sorted_entities})
    all_letters = [chr(c) for c in range(65, 91)]
    letter_nav = '<div class="letter-nav">' + "".join(
        f'<a href="#letter-{L}">{L}</a>' if L in letters_with_entities
        else f'<a class="disabled">{L}</a>'
        for L in all_letters
    ) + '</div>'

    ent_body_parts = [letter_nav]
    current_letter = ""
    for e in sorted_entities:
        first = e[0].upper()
        if first != current_letter:
            current_letter = first
            ent_body_parts.append(f'<h2 id="letter-{first}">{first}</h2>')
        c = ent_counter[e]
        safe = e.replace("/", "-")
        ent_body_parts.append(
            f'<div class="card"><a class="t" href="entities/{safe}.html">{e}</a>'
            f'<div class="meta"><span>{c} {"story" if c == 1 else "stories"}</span></div></div>'
        )
    ent_rows = "\n".join(ent_body_parts)
    _write(site / "entities.html",
           _render("Players", ent_rows, active="entities",
                   subtitle=f"{len(sorted_entities)} companies & organizations tracked"))
    pages += 1
    for e, items in by_entity.items():
        safe = e.replace("/", "-")
        _write(site / "entities" / f"{safe}.html",
               _render(f"{e}", _cards(items), rel="../",
                       subtitle=f"{len(items)} stories mentioning {e}"))
        pages += 1

    # --- client-side search (inline data — works with file:// protocol) ---
    search_index = [
        {"title": a["title"], "summary": a["summary"], "source": a["source"],
         "date": a["date"], "url": a["url_canonical"], "themes": a["themes"],
         "entities": a["entities"]}
        for a in canonical
    ]
    _write(site / "articles.json", json.dumps(search_index, ensure_ascii=False))
    inline_json = json.dumps(search_index, ensure_ascii=False)
    search_body = f"""<div class="search-box"><input id="q" placeholder="Search stories by title, source, entity, or keyword\u2026" autofocus></div>
<div class="search-count" id="count"></div>
<div id="results"></div>
<script>
const data={inline_json};
const q=document.getElementById('q'),out=document.getElementById('results'),cnt=document.getElementById('count');
q.addEventListener('input',()=>{{const s=q.value.toLowerCase().trim();
 if(s.length<2){{out.innerHTML='';cnt.textContent='';return;}}
 const terms=s.split(/\\s+/);
 const hits=data.filter(a=>{{const blob=(a.title+' '+a.source+' '+a.summary+' '+(a.entities||[]).join(' ')+' '+(a.themes||[]).join(' ')).toLowerCase();
   return terms.every(t=>blob.includes(t));}}).slice(0,80);
 cnt.textContent=hits.length>=80?'Showing first 80 results':hits.length+' result'+(hits.length!==1?'s':'');
 out.innerHTML=hits.map(a=>`<div class="card"><a class="t" href="${{a.url||'#'}}">${{a.title}}</a>`
  +`<div class="meta"><span>${{a.date}}</span><span class="meta-dot">${{a.source}}</span></div>`
  +`<div class="summary">${{(a.summary||'').slice(0,200)}}</div>`
  +`<div class="tags">${{(a.entities||[]).map(e=>`<span class="tag tag-entity">${{e}}</span>`).join('')}}</div>`
  +`</div>`).join('');}});
</script>"""
    _write(site / "search.html",
           _render("Search", search_body, active="search",
                   subtitle=f"Search across {len(search_index):,} articles"))
    pages += 1

    return {"pages": pages, "articles": len(articles), "canonical": len(canonical), "site_dir": str(site)}
