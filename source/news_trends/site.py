"""Static site generation (Jinja2) for the public-facing AI Signal site."""

from __future__ import annotations

import json
import re as _re
import urllib.parse
from collections import Counter, defaultdict
from datetime import date as _date, datetime as _datetime, timezone as _tz
from pathlib import Path

import yaml
from jinja2 import Template

from . import db
from .chat import CHAT_BUBBLE_HTML, CHAT_CSS, build_chat_page
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

# Items per page for client-side pagination on large listings
_PAGE_SIZE = 30

# ---------------------------------------------------------------------------
# Shared CSS (written once to style.css, linked from every page)
# ---------------------------------------------------------------------------
_CSS = """\
:root{--brand:#0d6b5e;--brand-light:#0f9983;--accent:#f59e0b;--accent2:#10b981;--bg:#f0f5f4;--card:#fff;--text:#1b1f24;--muted:#64748b;--border:#e2e8f0;--radius:12px;
      --gradient:linear-gradient(135deg,#0d6b5e 0%,#0f9983 40%,#2dd4a8 100%)}
*{box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,-apple-system,Roboto,sans-serif;margin:0;background:var(--bg);color:var(--text);line-height:1.6}

/* ---- header / nav ---- */
header{background:var(--gradient);color:#fff;padding:0 24px;display:flex;align-items:center;gap:0;box-shadow:0 4px 20px rgba(0,0,0,.15)}
.brand{font-size:22px;font-weight:800;letter-spacing:-.5px;padding:18px 0;margin-right:40px;white-space:nowrap;text-decoration:none;color:#fff}
.brand:hover{opacity:.85}
.brand-icon{font-size:24px;margin-right:6px;vertical-align:middle}
nav{display:flex;gap:2px;flex-wrap:wrap}
nav a{color:rgba(255,255,255,.75);text-decoration:none;font-size:13.5px;font-weight:600;padding:10px 16px;border-radius:8px;transition:all .2s;text-transform:uppercase;letter-spacing:.5px}
nav a:hover,nav a[aria-current]{background:rgba(255,255,255,.15);color:#fff}

/* ---- hero banner ---- */
.hero{background:var(--gradient);color:#fff;margin:-28px -24px 28px;padding:32px 32px 28px;border-radius:0 0 20px 20px;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-50%;right:-20%;width:60%;height:200%;background:radial-gradient(circle,rgba(255,255,255,.06) 0%,transparent 70%);pointer-events:none}
.hero h1{font-size:28px;font-weight:800;margin:0 0 8px;position:relative}
.hero .subtitle{color:rgba(255,255,255,.8);font-size:14px;margin:0;position:relative}
.hero .hero-stats{display:flex;gap:24px;margin-top:16px;position:relative}
.hero .hero-stat{text-align:center}
.hero .hero-stat .num{font-size:28px;font-weight:800}
.hero .hero-stat .lbl{font-size:11px;text-transform:uppercase;letter-spacing:1px;opacity:.75}

/* ---- main ---- */
main{max-width:1080px;margin:0 auto;padding:28px 24px 48px}
h1{font-size:24px;font-weight:700;margin:0 0 4px}
.subtitle{color:var(--muted);font-size:14px;margin:0 0 24px}
h2{font-size:18px;margin-top:32px;color:var(--brand);border-bottom:2px solid var(--border);padding-bottom:8px}

/* ---- cards ---- */
article.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:18px 22px;margin:14px 0;
     transition:box-shadow .2s,transform .15s;border-left:3px solid transparent}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:18px 22px;margin:14px 0;
     transition:box-shadow .2s,transform .15s}
.card:hover{box-shadow:0 8px 24px rgba(0,0,0,.08);transform:translateY(-2px);border-left-color:var(--brand-light)}
a.t{color:var(--brand);text-decoration:none;font-weight:700;font-size:15.5px;line-height:1.4}
a.t:hover{color:var(--brand-light);text-decoration:underline}
a.t::before{content:'\U0001f517 ';font-size:12px}
span.t{font-weight:700;font-size:15.5px;line-height:1.4;color:var(--text)}
span.t::before{content:'\U0001f4c4 ';font-size:12px}
.meta{color:var(--muted);font-size:12.5px;margin:6px 0 8px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.meta-dot::before{content:'\u00b7';margin:0 2px}
.url-display{font-size:12px;margin:2px 0 4px}
.url-link{color:var(--brand-light);text-decoration:none;opacity:0.8}
.url-link:hover{opacity:1;text-decoration:underline}
.url-link::before{content:'\U0001f517 ';font-size:11px}
.summary{font-size:14px;color:#475569;margin:8px 0;line-height:1.65}
.summary ul.bullet-summary{margin:6px 0;padding-left:20px}
.summary ul.bullet-summary li{margin:3px 0;line-height:1.5}
.expand-toggle{color:var(--brand-light);cursor:pointer;font-size:13px;font-weight:600;text-decoration:none;border:none;background:none;padding:0;font-family:inherit}
.expand-toggle:hover{text-decoration:underline}
.dupe{opacity:.5;border-left:3px solid #ccc}

/* ---- tags / badges ---- */
.tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px}
.tag{display:inline-block;border-radius:20px;padding:3px 12px;font-size:11.5px;font-weight:600;text-decoration:none;transition:all .15s}
.tag:hover{transform:scale(1.05);box-shadow:0 2px 6px rgba(0,0,0,.1)}
.tag-label{background:#eef3f8;color:#2c5282}
.tag-entity{background:linear-gradient(135deg,#fef3c7,#fde68a);color:#92400e;border:1px solid #fcd34d}
.tag-topic{background:linear-gradient(135deg,#e0e7ff,#c7d2fe);color:#3730a3;border:1px solid #a5b4fc}
.tag-hot{background:linear-gradient(135deg,#fee2e2,#fecaca);color:#991b1b;border:1px solid #fca5a5}

/* ---- grid cards for index pages ---- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-top:16px}
.grid .card{margin:0;text-align:center;border:1px solid var(--border);transition:all .2s}
.grid .card:hover{border-color:var(--brand-light);box-shadow:0 8px 24px rgba(0,0,0,.08)}
.card .count{font-size:28px;font-weight:800;color:var(--brand-light);background:linear-gradient(135deg,var(--brand),var(--brand-light));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.card .label{font-size:12px;color:var(--muted);margin-top:2px;text-transform:uppercase;letter-spacing:.5px}
a.entity-link{display:block;text-decoration:none;color:var(--text);padding:16px 20px}
a.entity-link:hover{border-color:var(--brand-light);box-shadow:0 8px 24px rgba(0,0,0,.08)}
a.entity-link strong{font-size:15px;display:block;margin-bottom:4px}
.entity-count{font-size:13px;color:var(--muted);display:block}
.ev-panel{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin-top:16px}
.ev-panel h2{grid-column:1/-1;margin-bottom:0}
.ev-panel .letter-nav{grid-column:1/-1}

/* ---- letter nav ---- */
.letter-nav{display:flex;flex-wrap:wrap;gap:4px;margin:16px 0;padding:14px 18px;background:var(--card);border-radius:var(--radius);border:1px solid var(--border);box-shadow:0 1px 4px rgba(0,0,0,.04)}
.letter-nav a{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:8px;font-weight:700;font-size:13px;
              color:var(--brand-light);text-decoration:none;transition:all .15s}
.letter-nav a:hover:not(.disabled){background:var(--brand-light);color:#fff;box-shadow:0 2px 8px rgba(26,115,232,.3)}
.letter-nav a.disabled{color:#cbd5e1;pointer-events:none;cursor:default}

/* ---- search ---- */
.search-box{position:relative;margin-bottom:20px}
.search-box input{width:100%;padding:16px 20px 16px 48px;font-size:16px;border:2px solid var(--border);border-radius:var(--radius);
                   transition:all .2s;outline:none;background:var(--card);box-shadow:0 2px 8px rgba(0,0,0,.04)}
.search-box input:focus{border-color:var(--brand-light);box-shadow:0 4px 16px rgba(26,115,232,.15)}
.search-icon{position:absolute;left:16px;top:50%;transform:translateY(-50%);font-size:20px;opacity:.4;pointer-events:none}
.search-clear{position:absolute;right:14px;top:50%;transform:translateY(-50%);font-size:20px;cursor:pointer;border:none;background:none;color:var(--muted);display:none}
.search-clear:hover{color:var(--text)}
.search-count{color:var(--muted);font-size:13px;margin-bottom:12px}
.search-help{color:var(--muted);font-size:13px;margin:8px 0 16px;line-height:1.6}
.search-help code{background:#e2e8f0;padding:1px 6px;border-radius:4px;font-size:12px}
mark{background:#fef08a;border-radius:3px;padding:0 2px}
.top-searches{margin:20px 0 28px}
.top-searches h2{font-size:16px;border:none;margin-top:8px;padding-bottom:0}
.top-searches .ts-grid{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.top-searches .ts-btn{padding:8px 16px;background:var(--card);border:1px solid var(--border);border-radius:20px;font-size:13px;font-weight:500;
                      color:var(--brand);cursor:pointer;transition:all .15s;text-decoration:none}
.top-searches .ts-btn:hover{background:var(--brand-light);color:#fff;border-color:var(--brand-light);box-shadow:0 2px 8px rgba(26,115,232,.2)}

/* ---- event cards ---- */
.event-card{background:linear-gradient(135deg,#f0f9ff,#e0f2fe);border:1px solid #bae6fd;border-radius:var(--radius);padding:20px 24px;margin:14px 0}
.event-card h3{margin:0 0 6px;font-size:17px;color:var(--brand)}
.event-card h3 a{color:var(--brand);text-decoration:none}
.event-card h3 a:hover{color:var(--brand-light);text-decoration:underline}
.event-card .event-meta{color:var(--muted);font-size:13px;margin-bottom:8px}
.event-card .event-summary{font-size:14px;color:#475569;line-height:1.6}
.event-card .event-links{margin-top:10px;display:flex;flex-wrap:wrap;gap:6px}
.event-card .event-links a{font-size:12px;color:var(--brand-light);text-decoration:none;padding:3px 10px;border:1px solid #bae6fd;border-radius:12px}
.event-card .event-links a:hover{background:var(--brand-light);color:#fff}
.event-group{margin:20px 0 28px}
.event-group h2{display:flex;align-items:center;gap:10px}
.event-count{font-size:12px;font-weight:500;color:var(--muted);background:#f1f5f9;padding:2px 10px;border-radius:12px}
.event-tabs{display:flex;gap:4px;margin-bottom:16px;border-bottom:2px solid var(--border);padding-bottom:0}
.event-tab{padding:10px 24px;font-size:14px;font-weight:600;border:none;background:none;cursor:pointer;color:var(--muted);
           border-bottom:3px solid transparent;margin-bottom:-2px;transition:all .15s}
.event-tab:hover{color:var(--brand)}
.event-tab.active{color:var(--brand-light);border-bottom-color:var(--brand-light)}
.upcoming-section{margin-bottom:28px;padding:24px;background:linear-gradient(135deg,#eff6ff,#dbeafe);border:1px solid #93c5fd;border-radius:var(--radius)}
.upcoming-section h2{margin:0 0 16px;font-size:18px;color:var(--brand);border:none;padding:0}
.upcoming-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.upcoming-card{background:#fff;border:1px solid #bfdbfe;border-radius:var(--radius);padding:16px 20px;transition:all .2s}
.upcoming-card:hover{box-shadow:0 4px 16px rgba(37,99,235,.12);border-color:var(--brand-light)}
.upcoming-card h3{margin:0 0 8px;font-size:15px}
.upcoming-card h3 a{color:var(--brand);text-decoration:none}
.upcoming-card h3 a:hover{color:var(--brand-light);text-decoration:underline}
.upcoming-date{font-size:12px;font-weight:600;color:var(--brand-light);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}
.event-reg-btn{display:inline-block;padding:6px 16px;font-size:13px;font-weight:600;color:#fff;background:var(--brand-light);
               border-radius:8px;text-decoration:none;transition:all .15s}
.event-reg-btn:hover{background:var(--brand);box-shadow:0 2px 8px rgba(26,115,232,.3)}
.upcoming-badge{display:inline-block;font-size:10px;font-weight:700;color:#fff;background:var(--accent2);padding:2px 8px;
                border-radius:10px;margin-left:8px;vertical-align:middle;text-transform:uppercase;letter-spacing:.5px}
.event-iframe{width:100%;min-height:600px;border:1px solid var(--border);border-radius:var(--radius);background:var(--card)}

/* ---- pagination ---- */
.pagination{display:flex;align-items:center;justify-content:center;gap:8px;margin:24px 0;flex-wrap:wrap}
.pagination button{padding:8px 18px;border:1px solid var(--border);border-radius:8px;background:var(--card);color:var(--brand-light);
                   cursor:pointer;font-size:13px;font-weight:600;transition:all .15s}
.pagination button:hover:not(:disabled){background:var(--brand-light);color:#fff;box-shadow:0 2px 8px rgba(26,115,232,.2)}
.pagination button:disabled{opacity:.4;cursor:default}
.pagination .page-info{font-size:13px;color:var(--muted)}

/* ---- snapshot nav ---- */
.snap-nav{display:flex;justify-content:space-between;margin:20px 0;gap:12px}
.snap-nav a{color:var(--brand-light);text-decoration:none;font-size:14px;font-weight:600;padding:10px 20px;border:1px solid var(--border);border-radius:8px;background:var(--card);transition:all .15s}
.snap-nav a:hover{background:var(--brand-light);color:#fff;box-shadow:0 2px 8px rgba(26,115,232,.2)}
.snap-nav .spacer{flex:1}

/* ---- back to top ---- */
.btt{position:fixed;bottom:24px;right:24px;width:44px;height:44px;border-radius:50%;background:var(--brand-light);color:#fff;border:none;
     font-size:18px;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,.2);opacity:0;transition:opacity .3s;pointer-events:none;z-index:99}
.btt.visible{opacity:1;pointer-events:auto}
.btt:hover{background:var(--brand);transform:scale(1.1)}

/* ---- footer ---- */
footer{color:var(--muted);font-size:12px;padding:32px 24px;text-align:center;border-top:1px solid var(--border);margin-top:40px}

/* ---- curated links ---- */
.curated-links-section{margin-bottom:28px;padding:20px 24px;background:linear-gradient(135deg,#f0f7ff,#e8f0fe);border-radius:var(--radius);border:1px solid var(--border)}
.curated-links-section h3{margin:0 0 14px;font-size:16px;color:var(--brand)}
.curated-links-grid{display:flex;flex-wrap:wrap;gap:10px}
a.curated-link{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:#fff;border:1px solid var(--border);
               border-radius:8px;color:var(--brand-light);font-size:13px;font-weight:600;text-decoration:none;transition:all .15s}
a.curated-link:hover{background:var(--brand-light);color:#fff;box-shadow:0 2px 8px rgba(26,115,232,.25)}
.submit-link-cta{display:flex;align-items:center;gap:12px;margin-top:24px;padding:14px 20px;background:var(--card);
                 border:1px dashed var(--border);border-radius:var(--radius);font-size:13px;color:var(--muted)}
.submit-link-cta .submit-btn{padding:6px 16px;background:var(--accent2);color:#fff;border-radius:8px;text-decoration:none;
                              font-weight:600;font-size:12px;transition:all .15s}
.submit-link-cta .submit-btn:hover{background:#2e7d32;box-shadow:0 2px 8px rgba(46,125,50,.3)}

/* ---- submit form ---- */
.submit-form{max-width:560px;margin:0 auto}
.submit-form .form-group{margin-bottom:18px}
.submit-form label{display:block;font-weight:600;font-size:13px;margin-bottom:6px;color:var(--fg)}
.submit-form input,.submit-form select,.submit-form textarea{width:100%;padding:10px 14px;border:1px solid var(--border);border-radius:8px;
  font-size:14px;background:var(--card);color:var(--fg);box-sizing:border-box}
.submit-form input:focus,.submit-form select:focus,.submit-form textarea:focus{outline:none;border-color:var(--brand-light);box-shadow:0 0 0 3px rgba(26,115,232,.1)}
.submit-form textarea{resize:vertical;min-height:60px}
.submit-form .form-actions{display:flex;gap:10px;margin-top:20px}
.submit-form .btn-submit{padding:10px 28px;background:var(--brand-light);color:#fff;border:none;border-radius:8px;font-size:14px;
  font-weight:600;cursor:pointer;transition:all .15s}
.submit-form .btn-submit:hover{background:var(--brand);box-shadow:0 2px 8px rgba(26,115,232,.3)}
.submit-form .btn-clear{padding:10px 28px;background:var(--card);color:var(--muted);border:1px solid var(--border);border-radius:8px;
  font-size:14px;cursor:pointer}
.submit-history{margin-top:32px;padding:20px;background:var(--card);border:1px solid var(--border);border-radius:var(--radius)}
.submit-history h3{margin:0 0 12px;font-size:15px}
.submit-history .empty{color:var(--muted);font-size:13px}
.submit-history .entry{padding:8px 0;border-bottom:1px solid var(--border);font-size:13px;display:flex;gap:12px;align-items:center}
.submit-history .entry:last-child{border-bottom:none}
.submit-history .entry .status{font-size:11px;padding:2px 8px;border-radius:6px;font-weight:600}
.submit-history .status.pending{background:#fff3e0;color:#e65100}
.submit-history .status.approved{background:#e8f5e9;color:#2e7d32}
.submit-history .status.rejected{background:#fbe9e7;color:#c62828}

/* ---- responsive ---- */
@media(max-width:640px){
  header{flex-direction:column;align-items:flex-start;gap:4px;padding:12px 16px}
  .brand{margin-right:0;padding:8px 0 4px}
  nav{gap:0}
  main{padding:16px}
  .grid{grid-template-columns:1fr}
  .snap-nav{flex-direction:column;align-items:stretch;text-align:center}
  .hero{margin:-16px -16px 20px;padding:24px 20px 20px}
  .hero .hero-stats{flex-wrap:wrap;gap:16px}
}
"""

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
_BASE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} \u00b7 AI Signal</title>
<link rel="stylesheet" href="{{ rel }}style.css">
</head><body class="page-{{ active or 'default' }}">
<header>
 <a class="brand" href="{{ rel }}index.html"><span class="brand-icon">\U0001f4e1</span>AI Signal</a>
 <nav>
  <a href="{{ rel }}index.html"{% if active=='index' %} aria-current="page"{% endif %}>Today\u2019s Pulse</a>
  <a href="{{ rel }}archive.html"{% if active=='archive' %} aria-current="page"{% endif %}>Timeline</a>
  <a href="{{ rel }}topics.html"{% if active=='topics' %} aria-current="page"{% endif %}>Themes</a>
  <a href="{{ rel }}events.html"{% if active=='events' %} aria-current="page"{% endif %}>Events</a>
  <a href="{{ rel }}entities.html"{% if active=='entities' %} aria-current="page"{% endif %}>Companies</a>
  <a href="{{ rel }}search.html"{% if active=='search' %} aria-current="page"{% endif %}>Search</a>
  <a href="{{ rel }}chat.html"{% if active=='chat' %} aria-current="page"{% endif %}>Chat</a>
 </nav>
</header><main>
{% if hero %}{{ hero }}{% else %}<h1>{{ title }}</h1>
{% if subtitle %}<p class="subtitle">{{ subtitle }}</p>{% endif %}{% endif %}
{{ body }}
</main>
""" + CHAT_BUBBLE_HTML + """
<button class="btt" onclick="scrollTo({top:0,behavior:'smooth'})" aria-label="Back to top">↑</button>
<script>addEventListener('scroll',()=>document.querySelector('.btt').classList.toggle('visible',scrollY>400))</script>
<footer>\u00a9 """ + str(_datetime.now(_tz.utc).year) + """ AI Signal \u00b7 Public \u00b7 ai-signal \u00b7 {{ build_ts }}</footer>
</body></html>"""

_CARD = """<article class="card {{ 'dupe' if a.dedupe_status=='duplicate' else '' }}">
  {% if a.has_url %}<a class="t" href="{{ a.url_canonical }}">{{ a.title }}</a>{% else %}<span class="t">{{ a.title }}</span>{% endif %}
  {% if a.has_url %}<div class="url-display"><a href="{{ a.url_canonical }}" class="url-link" target="_blank" rel="noopener">{{ a.url_domain }}</a></div>{% endif %}
  <div class="meta">
    <span>{{ a.date_display }}</span>
    {% if a.theme_label %}<span class="meta-dot">{{ a.theme_label }}</span>{% endif %}
  </div>
  <div class="summary">{{ a.summary_html }}</div>
  <div class="tags">
  {%- for t in a.tags %}<span class="tag tag-hot">{{ t }}</span>{% endfor -%}
  {%- for e in a.entities %}<a class="tag tag-entity" href="{{ a.rel }}entities/{{ a.entity_files[e] }}">{{ e }}</a>{% endfor -%}
  {%- for c in a.cross_cutting %}<a class="tag tag-topic" href="{{ a.rel }}topics/{{ c }}.html">{{ a.cross_cutting_labels[c] }}</a>{% endfor -%}
  </div>
</article>"""

# Pagination JS injected into pages with many cards
_PAGINATE_JS = """<script>
(function(){{
  const cards=document.querySelectorAll('article.card');
  if(cards.length<={ps})return;
  const sz={ps};let pg=0;const total=Math.ceil(cards.length/sz);
  const nav=document.createElement('div');nav.className='pagination';
  nav.innerHTML='<button id="pprev">&larr; Prev</button><span class="page-info" id="pinfo"></span><button id="pnext">Next &rarr;</button>';
  cards[0].parentNode.insertBefore(nav,cards[0]);
  const nav2=nav.cloneNode(true);cards[cards.length-1].after(nav2);
  function show(){{
    cards.forEach((c,i)=>c.style.display=(i>=pg*sz&&i<(pg+1)*sz)?'':'none');
    document.querySelectorAll('#pinfo').forEach(el=>el.textContent='Page '+(pg+1)+' of '+total+' ('+cards.length+' stories)');
    document.querySelectorAll('#pprev').forEach(b=>b.disabled=pg===0);
    document.querySelectorAll('#pnext').forEach(b=>b.disabled=pg>=total-1);
    scrollTo({{top:0,behavior:'smooth'}});
  }}
  document.querySelectorAll('#pprev').forEach(b=>b.onclick=()=>{{pg--;show();}});
  document.querySelectorAll('#pnext').forEach(b=>b.onclick=()=>{{pg++;show();}});
  show();
}})();
</script>"""


def _render(title: str, body: str, rel: str = "", active: str = "",
            subtitle: str = "", hero: str = "") -> str:
    build_ts = f"Last built {_datetime.now(_tz.utc).strftime('%B %d, %Y at %H:%M UTC')}"
    return Template(_BASE).render(title=title, body=body, rel=rel,
                                  active=active, subtitle=subtitle,
                                  hero=hero, build_ts=build_ts)


def _topic_label(slug: str) -> str:
    """Return a human-friendly display name for a topic slug."""
    return TOPIC_LABELS.get(slug, slug.replace("-", " ").title())


def _safe_filename(name: str) -> str:
    """Create a safe filename from an entity/topic/event name.
    
    Uses hyphens instead of spaces, strips special chars. No percent-encoding.
    """
    s = name.replace("/", "-").replace("\\", "-")
    # Remove characters unsafe for filenames
    s = _re.sub(r"[<>:\"\'|?*,;]", "", s)
    # Collapse whitespace to hyphens
    s = _re.sub(r"\s+", "-", s.strip())
    # Collapse multiple hyphens
    s = _re.sub(r"-{2,}", "-", s).strip("-")
    return s


def _format_date(iso_str: str | None) -> str:
    """Convert ISO date '2026-05-29' to 'May 29, 2026'."""
    if not iso_str:
        return ""
    try:
        d = _date.fromisoformat(iso_str)
        return d.strftime("%B %d, %Y").replace(" 0", " ")
    except (ValueError, TypeError):
        return iso_str

# Sentences shorter than this won't be bullet-ized even in a long block.
_BULLET_THRESHOLD = 200
_MAX_PREVIEW = 300


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    parts = _re.split(r'(?<=[.!?;])\s+(?=[A-Z\u201c\u2018$\d])', text)
    return [s.strip() for s in parts if s.strip()]


_expand_id = 0

def _format_summary(text: str) -> str:
    """Format a dense summary into readable HTML with bullets + truncation."""
    global _expand_id
    if not text:
        return ""
    text = text.strip()
    sentences = _split_sentences(text)

    if len(text) <= _BULLET_THRESHOLD or len(sentences) <= 2:
        if len(text) > _MAX_PREVIEW * 2:
            _expand_id += 1
            eid = f"exp{_expand_id}"
            preview = text[:_MAX_PREVIEW].rsplit(" ", 1)[0]
            return (
                f'{preview}\u2026 '
                f'<button class="expand-toggle" onclick="var el=document.getElementById(\'{eid}\');'
                f'el.style.display=el.style.display===\'none\'?\'inline\':\'none\';'
                f'this.textContent=el.style.display===\'none\'?\'Show more\':\'Show less\'">'
                f'Show more</button>'
                f'<span id="{eid}" style="display:none">{text[len(preview):]}</span>'
            )
        return text

    visible = []
    hidden = []
    char_count = 0
    for s in sentences:
        if char_count <= _MAX_PREVIEW:
            visible.append(s)
        else:
            hidden.append(s)
        char_count += len(s)

    bullets_vis = "".join(f"<li>{s}</li>" for s in visible)
    if not hidden:
        return f'<ul class="bullet-summary">{bullets_vis}</ul>'

    _expand_id += 1
    eid = f"exp{_expand_id}"
    bullets_hid = "".join(f"<li>{s}</li>" for s in hidden)
    return (
        f'<ul class="bullet-summary">{bullets_vis}'
        f'<span id="{eid}" style="display:none">{bullets_hid}</span></ul>'
        f'<button class="expand-toggle" onclick="var el=document.getElementById(\'{eid}\');'
        f'el.style.display=el.style.display===\'none\'?\'inline\':\'none\';'
        f'this.textContent=el.style.display===\'none\'?\'Show {len(hidden)} more\u2026\':\'Show less\'">'
        f'Show {len(hidden)} more\u2026</button>'
    )


def _cards(articles: list[dict], rel: str = "", entity_files: dict | None = None) -> str:
    tmpl = Template(_CARD)
    if entity_files is None:
        entity_files = {}
    out = []
    for a in articles:
        a = dict(a)
        a["theme_label"] = _topic_label(a.get("theme", "")) if a.get("theme") else ""
        a["summary_html"] = _format_summary(a.get("summary", ""))
        a["date_display"] = _format_date(a.get("date"))
        url = a.get("url_canonical") or ""
        status = a.get("url_status", "")
        a["has_url"] = bool(url) and status in ("ok", "repaired", "found")
        # Extract display domain from URL (e.g. "techcrunch.com")
        if a["has_url"]:
            try:
                a["url_domain"] = urllib.parse.urlparse(url).netloc.removeprefix("www.")
            except Exception:
                a["url_domain"] = url[:60]
        else:
            a["url_domain"] = ""
        a["rel"] = rel
        a["entity_files"] = entity_files
        a["cross_cutting_labels"] = {slug: _topic_label(slug) for slug in a.get("cross_cutting", [])}
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
            # Strip markdown heading prefixes from titles
            if d.get("title"):
                d["title"] = d["title"].lstrip("# ").strip()
            rows.append(d)
    return rows


def _write(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def _build_event_pages(cfg: Config, site: Path, canonical: list[dict],
                       entity_files: dict[str, str]) -> int:
    """Build event pages using DB-indexed event articles.

    Generates:
      - events.html: main page with upcoming banner + two inline tab views
      - events/<event-slug>.html: individual event detail pages
    """
    event_articles = [a for a in canonical if a.get("event_name")]
    if not event_articles:
        _write(site / "events.html",
               _render("Events", "<p>No event coverage found. Run the pipeline to ingest event files.</p>",
                       active="events"))
        return 1

    pages = 0
    today = _date.today().isoformat()

    # Load curated event links from YAML
    curated_links: dict[str, list[dict]] = {}
    links_path = cfg.root / "source" / "config" / "event-links.yaml"
    if links_path.exists():
        raw = yaml.safe_load(links_path.read_text(encoding="utf-8")) or {}
        curated_links = {k: v for k, v in raw.items() if isinstance(v, list)}

    # Group by event name
    by_event: dict[str, list[dict]] = defaultdict(list)
    for a in event_articles:
        by_event[a["event_name"]].append(a)

    # Group by company (entity)
    by_company: dict[str, list[dict]] = defaultdict(list)
    for a in event_articles:
        for ent in (a.get("entities") or []):
            by_company[ent].append(a)

    # --- Merge preview / variant events into the main event ---
    # If "X" and "X Preview" (or "X Preview: subtitle") both exist,
    # fold the preview articles into the main event and drop the preview.
    event_names = list(by_event.keys())
    for ev in list(event_names):
        # Check if this event is a preview/variant of another
        base = _re.sub(r"\s+Preview\b.*", "", ev).strip()
        if base != ev and base in by_event:
            by_event[base].extend(by_event.pop(ev))
            # Also merge in by_company
            for comp in list(by_company.keys()):
                orig_len = len(by_company[comp])
                by_company[comp] = [a for a in by_company[comp] if a.get("event_name") != ev]
                if len(by_company[comp]) < orig_len:
                    for a in by_event[base]:
                        if comp in (a.get("entities") or []) and a not in by_company[comp]:
                            by_company[comp].append(a)

    # Extract registration URLs from event source markdown files
    event_urls: dict[str, list[tuple[str, str]]] = {}
    news_dir = cfg.news_dir
    for path in sorted(news_dir.glob("*.md")):
        if _re.match(r"^\d{4}-\d{2}-\d{2}", path.name):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        title = lines[0].lstrip("# ").strip() if lines else ""
        if not title:
            continue
        urls: list[tuple[str, str]] = []
        in_ext = False
        for line in lines:
            if "external sources" in line.lower() or "corroborating url" in line.lower():
                in_ext = True
                continue
            if in_ext:
                if line.startswith("## ") or line.startswith("### Source corpus"):
                    break
                m = _re.search(r"(https?://[^\s)]+)", line)
                if m:
                    label = line.split("http")[0].strip("- :").strip()
                    urls.append((label, m.group(1).rstrip(".,;")))
        if urls:
            event_urls[title] = urls

    # Determine upcoming events (date strictly > today — past/today events show coverage)
    upcoming: list[tuple[str, str, str, list[tuple[str, str]]]] = []  # (name, date, slug, urls)
    for ev_name, items in sorted(by_event.items()):
        dates = [a["date"] for a in items if a.get("date")]
        ev_date = max(dates) if dates else None
        if ev_date and ev_date > today:
            slug = _safe_filename(ev_name)
            # Find matching URLs from source files
            urls = event_urls.get(ev_name, [])
            if not urls:
                # Try partial match on event name
                for src_title, src_urls in event_urls.items():
                    if ev_name.split(":")[0].strip() in src_title or src_title.split(":")[0].strip() in ev_name:
                        urls = src_urls
                        break
            upcoming.append((ev_name, ev_date, slug, urls))
    upcoming.sort(key=lambda x: x[1])

    # --- Upcoming events banner ---
    upcoming_html = ""
    if upcoming:
        cards = []
        for ev_name, ev_date, slug, urls in upcoming:
            reg_link = ""
            if urls:
                # Pick the most likely official/registration URL
                best = urls[0][1]
                for label, u in urls:
                    ll = label.lower()
                    if any(k in ll for k in ("official", "register", "site", "event")):
                        best = u
                        break
                    if any(k in u for k in ("developer.apple.com", "build.microsoft.com",
                                            "io.google", "nvidia.com/gtc", "nvidia.com/events")):
                        best = u
                        break
                reg_link = f'<a href="{best}" target="_blank" rel="noopener" class="event-reg-btn">Register \u2192</a>'
            cards.append(
                f'<div class="upcoming-card">'
                f'<div class="upcoming-date">{_format_date(ev_date)}</div>'
                f'<h3><a href="events/{slug}.html">{ev_name}</a></h3>'
                f'{reg_link}'
                f'</div>'
            )
        upcoming_html = (
            '<div class="upcoming-section">'
            '<h2>\U0001f4c5 Upcoming Events</h2>'
            '<div class="upcoming-grid">' + "".join(cards) + '</div>'
            '</div>'
        )

    # --- Build "By Event" tab content: clickable card list ---
    ev_cards = []
    for ev_name in sorted(by_event.keys()):
        items = by_event[ev_name]
        slug = _safe_filename(ev_name)
        # Mark upcoming with a badge (strictly future — not today)
        dates = [a["date"] for a in items if a.get("date")]
        is_upcoming = any(d > today for d in dates) if dates else False
        badge = '<span class="upcoming-badge">Upcoming</span>' if is_upcoming else ''
        ev_cards.append(
            f'<a href="events/{slug}.html" class="card entity-link">'
            f'<strong>{ev_name}</strong>{badge}'
            f'<span class="entity-count">{len(items)} articles</span></a>'
        )

    # --- Build "By Company" tab content: A-Z clickable card list ---
    sorted_companies = sorted(by_company.keys(), key=str.upper)
    letters_with = sorted({c[0].upper() for c in sorted_companies})
    all_letters = [chr(c) for c in range(65, 91)]
    co_letter_nav = '<div class="letter-nav">' + "".join(
        f'<a href="#ev-letter-{L}">{L}</a>' if L in letters_with
        else f'<a class="disabled">{L}</a>'
        for L in all_letters
    ) + '</div>'

    co_cards = [co_letter_nav]
    current_letter = ""
    for co_name in sorted_companies:
        letter = co_name[0].upper()
        if letter != current_letter:
            current_letter = letter
            co_cards.append(f'<h2 id="ev-letter-{letter}">{letter}</h2>')
        items = by_company[co_name]
        safe = entity_files.get(co_name, _safe_filename(co_name) + ".html")
        # Link to the entity's own page
        co_cards.append(
            f'<a href="entities/{safe}" class="card entity-link">'
            f'<strong>{co_name}</strong>'
            f'<span class="entity-count">{len(items)} event mentions</span></a>'
        )

    # --- Combine into tabbed layout (inline, no iframes) ---
    tab_html = (
        upcoming_html
        + '<div class="event-tabs">'
        '<button class="event-tab active" onclick="evTab(this,0)">By Event</button>'
        '<button class="event-tab" onclick="evTab(this,1)">By Company</button>'
        '</div>'
        f'<div class="ev-panel" id="ev-panel-0">\n{"".join(ev_cards)}\n</div>'
        f'<div class="ev-panel" id="ev-panel-1" style="display:none">\n{"".join(co_cards)}\n</div>'
        '<script>'
        'function evTab(btn,idx){'
        'document.querySelectorAll(".ev-panel").forEach((p,i)=>p.style.display=i===idx?"":"none");'
        'document.querySelectorAll(".event-tab").forEach(b=>b.classList.remove("active"));'
        'btn.classList.add("active");}'
        '</script>'
    )

    _write(site / "events.html",
           _render("Events", tab_html, active="events",
                   subtitle=f"{len(event_articles)} articles across {len(by_event)} events \u00b7 {len(by_company)} companies"))
    pages += 1

    # --- individual event detail pages ---
    paginate_js = _PAGINATE_JS.replace("PAGE_SIZE", str(_PAGE_SIZE))
    for ev_name, items in by_event.items():
        slug = _safe_filename(ev_name)
        # Curated links section
        links_html = ""
        ev_links = curated_links.get(ev_name, [])
        if ev_links:
            link_items = "\n".join(
                f'<a href="{lk["url"]}" target="_blank" class="curated-link">'
                f'🔗 {lk["label"]}</a>'
                for lk in ev_links if lk.get("url")
            )
            links_html = (
                '<div class="curated-links-section">'
                '<h3>📌 Official & Curated Links</h3>'
                f'<div class="curated-links-grid">{link_items}</div>'
                '</div>'
            )
        # Submit link CTA
        submit_cta = (
            '<div class="submit-link-cta">'
            '<span>Have a useful link for this event?</span> '
            f'<a href="../submit.html?event={urllib.parse.quote(ev_name)}" class="submit-btn">📥 Submit Link</a>'
            '</div>'
        )
        body = links_html + _cards(items, rel="../", entity_files=entity_files) + submit_cta
        if len(items) > _PAGE_SIZE:
            body += paginate_js
        _write(site / "events" / f"{slug}.html",
               _render(ev_name, body, rel="../",
                       subtitle=f"{len(items)} articles from this event"))
        pages += 1

    return pages


def _build_submit_page(site: Path, cfg: Config, canonical: list[dict]) -> int:
    """Generate submit.html — a form for users to submit links for events."""
    event_names = sorted({a["event_name"] for a in canonical if a.get("event_name")})
    options_html = "\n".join(f'<option value="{e}">{e}</option>' for e in event_names)

    form_html = f"""
    <div class="submit-form">
      <p style="color:var(--muted);font-size:14px;margin-bottom:24px">
        Submit useful links for event coverage. Links are saved locally and
        reviewed daily by the site owner before publishing.
      </p>
      <div class="form-group">
        <label for="sf-event">Event</label>
        <select id="sf-event">
          <option value="">— Select an event —</option>
          {options_html}
        </select>
      </div>
      <div class="form-group">
        <label for="sf-url">URL</label>
        <input id="sf-url" type="url" placeholder="https://…">
      </div>
      <div class="form-group">
        <label for="sf-label">Label / Description</label>
        <input id="sf-label" type="text" placeholder="Official schedule, session videos, etc.">
      </div>
      <div class="form-group">
        <label for="sf-name">Your Name (optional)</label>
        <input id="sf-name" type="text" placeholder="Jane Doe">
      </div>
      <div class="form-actions">
        <button class="btn-submit" onclick="submitLink()">📥 Submit</button>
        <button class="btn-clear" onclick="clearForm()">Clear</button>
      </div>
      <div id="sf-msg" style="margin-top:14px;font-size:13px"></div>
    </div>
    <div class="submit-history">
      <h3>📋 Your Submissions</h3>
      <div id="sf-list"><p class="empty">No submissions yet.</p></div>
    </div>
    <script>
    const STORAGE_KEY = 'ai_signal_link_submissions';
    function getSubmissions() {{ try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }} catch {{ return []; }} }}
    function saveSubmissions(s) {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(s)); }}
    function renderList() {{
      const s = getSubmissions();
      const el = document.getElementById('sf-list');
      if (!s.length) {{ el.innerHTML = '<p class="empty">No submissions yet.</p>'; return; }}
      el.innerHTML = s.slice().reverse().map(x =>
        '<div class="entry">' +
        '<span class="status ' + x.status + '">' + x.status + '</span>' +
        '<span><strong>' + x.event + '</strong>: <a href="' + x.url + '" target="_blank">' + (x.label || x.url) + '</a></span>' +
        '<span style="margin-left:auto;color:var(--muted);font-size:11px">' + x.date + '</span>' +
        '</div>'
      ).join('');
    }}
    function submitLink() {{
      const ev = document.getElementById('sf-event').value;
      const url = document.getElementById('sf-url').value.trim();
      const label = document.getElementById('sf-label').value.trim();
      const name = document.getElementById('sf-name').value.trim();
      const msg = document.getElementById('sf-msg');
      if (!ev) {{ msg.innerHTML = '<span style="color:#c62828">⚠ Please select an event.</span>'; return; }}
      if (!url) {{ msg.innerHTML = '<span style="color:#c62828">⚠ Please enter a URL.</span>'; return; }}
      const entry = {{ event: ev, url, label: label || url, submitter: name || 'Anonymous',
                       date: new Date().toISOString().slice(0,10), status: 'pending' }};
      const s = getSubmissions();
      s.push(entry);
      saveSubmissions(s);
      // Also store in downloadable format for the site owner
      const blob = new Blob([JSON.stringify(s, null, 2)], {{type:'application/json'}});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      // Auto-download only on first submission
      if (s.length === 1) {{ a.download = 'link-submissions-' + entry.date + '.json'; a.click(); }}
      msg.innerHTML = '<span style="color:#2e7d32">✅ Link submitted! It will appear on the event page after review.</span>';
      clearForm();
      renderList();
    }}
    function clearForm() {{
      document.getElementById('sf-event').value = '';
      document.getElementById('sf-url').value = '';
      document.getElementById('sf-label').value = '';
      document.getElementById('sf-name').value = '';
    }}
    // Pre-select event from URL param
    (function() {{
      const p = new URLSearchParams(window.location.search);
      const ev = p.get('event');
      if (ev) document.getElementById('sf-event').value = decodeURIComponent(ev);
      renderList();
    }})();
    // Export button
    document.querySelector('.submit-history h3').insertAdjacentHTML('afterend',
      '<button style="float:right;margin-top:-30px;font-size:12px;padding:4px 12px;border:1px solid var(--border);' +
      'border-radius:6px;background:var(--card);cursor:pointer;color:var(--muted)" onclick="exportAll()">⬇ Export JSON</button>');
    function exportAll() {{
      const s = getSubmissions();
      if (!s.length) return;
      const blob = new Blob([JSON.stringify(s, null, 2)], {{type:'application/json'}});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'link-submissions-' + new Date().toISOString().slice(0,10) + '.json';
      a.click();
    }}
    </script>
    """

    _write(site / "submit.html",
           _render("📥 Submit Link", form_html, active="events",
                   subtitle="Suggest useful links for event coverage"))
    return 1


def run_review_submissions(cfg: Config) -> dict:
    """CLI command: review link submissions from JSON files in submissions/ directory.

    Reads all .json files, shows pending links, writes approved ones
    into event-links.yaml for the next build-site run.
    """
    subs_dir = cfg.root / "submissions"
    links_path = cfg.root / "source" / "config" / "event-links.yaml"

    # Load existing curated links
    curated: dict = {}
    if links_path.exists():
        curated = yaml.safe_load(links_path.read_text(encoding="utf-8")) or {}

    # Scan submission files
    pending: list[dict] = []
    json_files = sorted(subs_dir.glob("*.json")) if subs_dir.exists() else []
    for jf in json_files:
        try:
            entries = json.loads(jf.read_text(encoding="utf-8"))
            for e in entries:
                if e.get("status", "pending") == "pending":
                    e["_file"] = str(jf)
                    pending.append(e)
        except (json.JSONDecodeError, TypeError):
            continue

    if not pending:
        print("No pending submissions found.")
        return {"reviewed": 0, "approved": 0}

    approved = 0
    for i, p in enumerate(pending, 1):
        print(f"\n--- Submission {i}/{len(pending)} ---")
        print(f"  Event:     {p.get('event', '?')}")
        print(f"  URL:       {p.get('url', '?')}")
        print(f"  Label:     {p.get('label', '?')}")
        print(f"  Submitter: {p.get('submitter', '?')}")
        print(f"  Date:      {p.get('date', '?')}")
        choice = input("  [a]pprove / [r]eject / [s]kip? ").strip().lower()
        if choice == "a":
            ev = p["event"]
            if ev not in curated:
                curated[ev] = []
            # Avoid duplicates
            existing_urls = {lk["url"] for lk in curated[ev]}
            if p["url"] not in existing_urls:
                curated[ev].append({"label": p.get("label", p["url"]), "url": p["url"]})
            p["status"] = "approved"
            approved += 1
        elif choice == "r":
            p["status"] = "rejected"
        # else skip — leave as pending

    # Write back curated links
    if approved:
        links_path.write_text(yaml.dump(curated, default_flow_style=False, allow_unicode=True),
                              encoding="utf-8")
        print(f"\n✅ {approved} links approved and written to {links_path}")

    # Update submission files with new statuses
    by_file: dict[str, list] = defaultdict(list)
    for p in pending:
        by_file[p["_file"]].append(p)
    for fpath, entries in by_file.items():
        all_entries = json.loads(Path(fpath).read_text(encoding="utf-8"))
        for ae in all_entries:
            for e in entries:
                if ae.get("url") == e.get("url") and ae.get("event") == e.get("event"):
                    ae["status"] = e["status"]
        Path(fpath).write_text(json.dumps(all_entries, indent=2), encoding="utf-8")

    return {"reviewed": len(pending), "approved": approved}


def run_build_site(cfg: Config) -> dict:
    cfg.ensure_dirs()
    site = cfg.site_dir
    articles = _load(cfg)
    canonical = [a for a in articles if a["dedupe_status"] != "duplicate"]
    pages = 0

    # Write shared CSS
    _write(site / "style.css", _CSS + "\n" + CHAT_CSS)

    # Build entity filename lookup (used for clickable tags)
    entity_files: dict[str, str] = {}
    for a in canonical:
        for e in a["entities"]:
            if e not in entity_files:
                entity_files[e] = _safe_filename(e) + ".html"

    paginate_js = _PAGINATE_JS.format(ps=_PAGE_SIZE)

    # --- snapshot (latest date) = index.html ---
    today_iso = _date.today().isoformat()
    # Only show articles up to today (exclude future-dated event previews)
    past_canonical = [a for a in canonical if a["date"] and a["date"] <= today_iso]
    latest = past_canonical[0]["date"] if past_canonical else None
    snap = [a for a in past_canonical if a["date"] == latest]
    total_canon = len(canonical)
    total_dates = len({a["date"] for a in canonical if a["date"] and a["date"] <= today_iso})
    urls_count = sum(1 for a in canonical if a.get("url_status") == "found")
    hero_html = (
        f'<div class="hero"><h1>\U0001f4e1 AI Signal</h1>'
        f'<p class="subtitle">AI industry intelligence \u2014 curated daily from {total_dates} days of coverage across frontier models, infrastructure, policy, and corporate strategy.</p>'
        f'<div class="hero-stats">'
        f'<div class="hero-stat"><div class="num">{total_canon:,}</div><div class="lbl">Articles</div></div>'
        f'<div class="hero-stat"><div class="num">{total_dates}</div><div class="lbl">Days</div></div>'
        f'<div class="hero-stat"><div class="num">{len(snap)}</div><div class="lbl">Today</div></div>'
        f'<div class="hero-stat"><div class="num">{urls_count}</div><div class="lbl">Linked</div></div>'
        f'</div></div>'
    )
    body = _cards(snap, entity_files=entity_files)
    _write(site / "index.html",
           _render(f"Today\u2019s Pulse \u2014 {_format_date(latest) or 'n/a'}", body,
                   active="index", hero=hero_html))
    pages += 1

    # --- archive + per-date snapshots with prev/next ---
    by_date: dict[str, list[dict]] = defaultdict(list)
    for a in canonical:
        d = a["date"]
        # Exclude undated and future-dated articles from the timeline
        if d and d <= today_iso:
            by_date[d].append(a)
    sorted_dates = sorted(by_date.keys(), reverse=True)
    rows = '<div class="grid">' + "".join(
        f'<div class="card"><a class="t" href="snapshots/{d}.html">{_format_date(d)}</a>'
        f'<div class="count">{len(by_date[d])}</div><div class="label">stories</div></div>'
        for d in sorted_dates
    ) + '</div>'
    _write(site / "archive.html",
           _render("Timeline", rows, active="archive",
                   subtitle=f"{len(by_date)} days \u00b7 {total_canon:,} articles"))
    pages += 1
    for i, d in enumerate(sorted_dates):
        items = by_date[d]
        prev_d = sorted_dates[i - 1] if i > 0 else None
        next_d = sorted_dates[i + 1] if i < len(sorted_dates) - 1 else None
        snap_nav = '<div class="snap-nav">'
        if next_d:
            snap_nav += f'<a href="{next_d}.html">\u2190 {_format_date(next_d)}</a>'
        else:
            snap_nav += '<span class="spacer"></span>'
        snap_nav += '<span class="spacer"></span>'
        if prev_d:
            snap_nav += f'<a href="{prev_d}.html">{_format_date(prev_d)} \u2192</a>'
        snap_nav += '</div>'
        card_html = _cards(items, rel="../", entity_files=entity_files)
        body = snap_nav + card_html + snap_nav
        if len(items) > _PAGE_SIZE:
            body += paginate_js
        _write(site / "snapshots" / f"{d}.html",
                _render(f"Snapshot \u2014 {_format_date(d)}", body, rel="../",
                        subtitle=f"{len(items)} stories"))
        pages += 1

    # --- topics (exclude future-dated articles) ---
    by_topic: dict[str, list[dict]] = defaultdict(list)
    for a in canonical:
        if a["date"] and a["date"] > today_iso:
            continue
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
        body = _cards(items, rel="../", entity_files=entity_files)
        if len(items) > _PAGE_SIZE:
            body += paginate_js
        _write(site / "topics" / f"{t}.html",
               _render(_topic_label(t), body, rel="../",
                       subtitle=f"{len(items)} stories"))
        pages += 1

    # --- entities (alphabetical with letter nav, exclude future-dated) ---
    ent_counter: Counter = Counter()
    by_entity: dict[str, list[dict]] = defaultdict(list)
    for a in canonical:
        if a["date"] and a["date"] > today_iso:
            continue
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
        safe = _safe_filename(e)
        ent_body_parts.append(
            f'<div class="card"><a class="t" href="entities/{safe}.html">{e}</a>'
            f'<div class="meta"><span>{c} {"story" if c == 1 else "stories"}</span></div></div>'
        )
    ent_rows = "\n".join(ent_body_parts)
    _write(site / "entities.html",
           _render("Companies", ent_rows, active="entities",
                   subtitle=f"{len(sorted_entities)} companies & organizations tracked"))
    pages += 1
    for e, items in by_entity.items():
        safe = _safe_filename(e)
        body = _cards(items, rel="../", entity_files=entity_files)
        if len(items) > _PAGE_SIZE:
            body += paginate_js
        _write(site / "entities" / f"{safe}.html",
               _render(f"{e}", body, rel="../",
                       subtitle=f"{len(items)} stories mentioning {e}"))
        pages += 1

    # --- event pages (from DB-indexed event articles) ---
    events = _build_event_pages(cfg, site, canonical, entity_files)
    pages += events

    # --- submit link page ---
    pages += _build_submit_page(site, cfg, canonical)

    # --- client-side search (inline data — works with file:// protocol) ---
    search_index = [
        {"title": a["title"], "summary": a["summary"], "source": a["source"],
         "date": a["date"], "url": a["url_canonical"], "url_status": a["url_status"],
         "themes": a["themes"], "entities": a["entities"],
         "event": a.get("event_name", "")}
        for a in canonical
    ]
    _write(site / "articles.json", json.dumps(search_index, ensure_ascii=False))
    inline_json = json.dumps(search_index, ensure_ascii=False)

    # Build top-search terms from entity and topic frequency
    top_entities = [e for e, _ in ent_counter.most_common(10)]
    top_topic_names = [_topic_label(t) for t, _ in sorted(by_topic.items(), key=lambda x: len(x[1]), reverse=True)[:5]]
    suggested = ["NVIDIA chips", "OpenAI funding", "Anthropic Claude", "AI regulation",
                 "Google Gemini", "Microsoft Copilot", "China AI", "robotics",
                 "datacenter", "cybersecurity"]
    top_search_html = (
        '<div class="top-searches"><h2>\U0001f525 Popular Searches</h2><div class="ts-grid">'
        + "".join(f'<a class="ts-btn" href="#" onclick="document.getElementById(\'q\').value=\'{s}\';document.getElementById(\'q\').dispatchEvent(new Event(\'input\'));return false">{s}</a>'
                  for s in suggested)
        + '</div></div>'
    )

    search_body = f"""<div class="search-box">
<span class="search-icon">\U0001f50d</span>
<input id="q" type="search" aria-label="Search articles" placeholder="Search \u2014 use quotes for phrases, OR between terms\u2026" autofocus>
<button class="search-clear" id="clear" aria-label="Clear search">\u2715</button>
</div>
<p class="search-help">Tips: <code>chips</code> \u2014 single keyword &nbsp;\u00b7&nbsp; <code>Huawei chips</code> \u2014 both words &nbsp;\u00b7&nbsp; <code>"Huawei chips" OR "Alibaba chips"</code> \u2014 either phrase &nbsp;\u00b7&nbsp; <code>NVIDIA OR AMD</code> \u2014 either word</p>
<div class="search-count" id="count"></div>
{top_search_html}
<div id="results"></div>
<script>
const data={inline_json};
const months=['January','February','March','April','May','June','July','August','September','October','November','December'];
function fmtDate(d){{if(!d)return'';const p=d.split('-');if(p.length!==3)return d;return months[parseInt(p[1],10)-1]+' '+parseInt(p[2],10)+', '+p[0];}}
function hasUrl(a){{return a.url&&a.url_status&&['ok','repaired','found'].includes(a.url_status);}}
function hl(text,terms){{if(!text||!terms.length)return text||'';let r=text;terms.forEach(t=>{{const re=new RegExp('('+t.replace(/[.*+?^${{}}()|[\\]\\\\]/g,'\\\\$&')+')','gi');r=r.replace(re,'<mark>$1</mark>');}});return r;}}
function parseQuery(raw){{
  const s=raw.trim().toLowerCase();if(!s)return null;
  // Split on OR (case-insensitive)
  const orGroups=s.split(/\\bor\\b/i).map(g=>g.trim()).filter(Boolean);
  return orGroups.map(g=>{{
    // Extract quoted phrases and bare words
    const parts=[];const re=/"([^"]+)"/g;let m;let rest=g;
    while((m=re.exec(g))!==null)parts.push(m[1].toLowerCase());
    rest=g.replace(/"[^"]*"/g,' ').trim();
    if(rest)rest.split(/\\s+/).forEach(w=>parts.push(w));
    return parts;
  }});
}}
const q=document.getElementById('q'),out=document.getElementById('results'),cnt=document.getElementById('count'),clr=document.getElementById('clear');
clr.onclick=()=>{{q.value='';out.innerHTML='';cnt.textContent='';clr.style.display='none';q.focus();}};
q.addEventListener('input',()=>{{const raw=q.value;const parsed=parseQuery(raw);
 clr.style.display=raw.trim()?'block':'none';
 if(!parsed||parsed.every(g=>g.every(t=>t.length<2))){{out.innerHTML='';cnt.textContent='';return;}}
 const allTerms=[...new Set(parsed.flat())];
 const hits=data.filter(a=>{{const blob=(a.title+' '+a.source+' '+a.summary+' '+(a.entities||[]).join(' ')+' '+(a.themes||[]).join(' ')+' '+(a.event||'')).toLowerCase();
   // OR between groups, AND within each group
   return parsed.some(group=>group.every(t=>blob.includes(t)));
 }}).slice(0,100);
 cnt.textContent=hits.length>=100?'Showing first 100 of many results':hits.length+' result'+(hits.length!==1?'s':'')+' found';
 out.innerHTML=hits.length?hits.map(a=>{{const dom=hasUrl(a)?(()=>{{try{{return new URL(a.url).hostname.replace('www.','')}}catch{{return''}}}})():'';return`<article class="card">${{hasUrl(a)?`<a class="t" href="${{a.url}}">${{hl(a.title,allTerms)}}</a>`:`<span class="t">${{hl(a.title,allTerms)}}</span>`}}`
  +(dom?`<div class="url-display"><a href="${{a.url}}" class="url-link" target="_blank" rel="noopener">${{dom}}</a></div>`:'')
  +`<div class="meta"><span>${{fmtDate(a.date)}}</span></div>`
  +`<div class="summary">${{hl((a.summary||'').slice(0,300),allTerms)}}</div>`
  +`<div class="tags">${{(a.entities||[]).map(e=>`<span class="tag tag-entity">${{e}}</span>`).join('')}}</div>`
  +`</article>`}}).join(''):'<p style="color:var(--muted);text-align:center;margin-top:40px">No results found. Try different keywords or use OR between terms.</p>';}});
</script>"""
    _write(site / "search.html",
           _render("Search", search_body, active="search",
                   subtitle=f"Search across {len(search_index):,} articles"))
    pages += 1

    # --- AI chat page ---
    pages += build_chat_page(cfg, site, canonical, entity_files)

    # --- admin / provenance removed for public site ---

    return {"pages": pages, "articles": len(articles), "canonical": len(canonical), "site_dir": str(site)}
