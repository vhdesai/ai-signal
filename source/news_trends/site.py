"""Static site generation (Jinja2) for the public-facing AI Signal site."""

from __future__ import annotations

import html as _html
import json
import re as _re
import urllib.parse
from collections import Counter, defaultdict
from datetime import date as _date, datetime as _datetime, timezone as _tz
from pathlib import Path

import yaml
from jinja2 import Template

from . import db
from .chat import CHAT_BUBBLE_HTML, CHAT_CSS, _chat_shell, build_chat_page
from .config import Config

# ---------------------------------------------------------------------------
# Display-name mappings
# ---------------------------------------------------------------------------
TOPIC_LABELS: dict[str, str] = {
    "model-capabilities": "\U0001f9e0 Model Breakthroughs",
    "datacenter-infrastructure": "\u26a1 Infrastructure & Compute",
    "policy-regulation": "\U0001f4dc Policy & Regulation",
    "company-storylines": "\U0001f3e2 Corporate Moves",
    "ma-activity": "\U0001f91d M&A Activity",
    "company-investments": "\U0001f4b0 Company Investments",
    "infrastructure-investments": "\U0001f3d7\ufe0f Infrastructure Investments",
    "what-changed": "\U0001f504 What Changed",
    "related-stories": "\U0001f517 Related Stories",
    "china-compete": "\U0001f30f Global AI Race",
}

# Sub-taxonomy grouped under the M&A & Investments hub page. Order controls
# how the hub renders each sub-section.
_DEALS_SUBCATEGORIES: tuple[str, ...] = (
    "ma-activity",
    "company-investments",
    "infrastructure-investments",
)

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
.search-chat-section{margin:36px 0 16px;padding:22px 24px;background:linear-gradient(135deg,rgba(13,107,94,.06),rgba(16,185,129,.1));border:1px solid rgba(13,107,94,.16);border-radius:18px}
.search-chat-section h2{margin:0 0 8px;border:none;padding:0;color:var(--brand)}
.search-chat-desc{margin:0;color:#475569;font-size:14px}

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
.entity-date{display:block;font-size:12px;color:var(--muted);margin-top:4px}
.compare-section{margin-bottom:28px;padding:24px;background:linear-gradient(135deg,rgba(13,107,94,.06),rgba(245,158,11,.06));border:1px solid rgba(13,107,94,.16);border-radius:var(--radius)}
.compare-section h2{margin:0 0 6px;font-size:18px;color:var(--brand);border:none;padding:0}
.compare-subtitle{margin:0 0 16px;font-size:13px;color:var(--muted)}
.compare-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.compare-card{background:#fff;border:1px solid rgba(13,107,94,.14);border-radius:var(--radius);padding:18px 20px;transition:all .2s}
.compare-card:hover{box-shadow:0 4px 16px rgba(13,107,94,.12);border-color:var(--brand-light)}
.compare-card h3{margin:0 0 10px;font-size:16px}
.compare-card h3 a{color:var(--brand);text-decoration:none}
.compare-card h3 a:hover{text-decoration:underline}
.compare-stat{font-size:13px;color:var(--muted);margin-bottom:4px}
.compare-num{font-weight:700;color:var(--brand);font-size:15px}
.compare-themes{font-size:12px;color:var(--muted);margin-top:8px;font-style:italic}
.compare-link-row{margin:18px 0 0}
.compare-link{display:inline-flex;align-items:center;gap:8px;color:var(--brand);font-size:14px;font-weight:700;text-decoration:none}
.compare-link:hover{color:var(--brand-light);text-decoration:underline}
.compare-page-intro{margin-bottom:24px;padding:24px;background:linear-gradient(135deg,rgba(13,107,94,.07),rgba(245,158,11,.08));border:1px solid rgba(13,107,94,.16);border-radius:var(--radius)}
.compare-page-intro h2{margin:0 0 8px;border:none;padding:0}
.compare-page-intro p{margin:0;color:#475569;max-width:78ch}
.compare-page-layout{display:grid;grid-template-columns:minmax(220px,280px) minmax(0,1fr);gap:20px;align-items:start}
.compare-tabs{display:grid;gap:10px;position:sticky;top:20px}
.compare-tab-btn{width:100%;text-align:left;padding:14px 16px;border:1px solid var(--border);border-radius:14px;background:var(--card);color:var(--text);font-size:13px;font-weight:700;cursor:pointer;transition:all .2s}
.compare-tab-btn:hover{border-color:var(--brand-light);box-shadow:0 4px 16px rgba(13,107,94,.08)}
.compare-tab-btn.active{background:linear-gradient(135deg,var(--brand),var(--brand-light));border-color:transparent;color:#fff}
.compare-content{min-width:0}
.compare-doc{display:none;background:var(--card);border:1px solid var(--border);border-radius:18px;padding:24px 26px;box-shadow:0 10px 28px rgba(15,23,42,.05)}
.compare-doc.active{display:block}
.compare-doc-header{margin-bottom:20px}
.compare-doc-header h2{margin:0 0 6px;border:none;padding:0}
.compare-doc-source{margin:0;color:var(--muted);font-size:12px}
.compare-doc h1,.compare-doc h2,.compare-doc h3,.compare-doc h4{border:none;padding:0;color:var(--brand)}
.compare-doc h1{font-size:28px;margin:0 0 14px}
.compare-doc h2{font-size:22px;margin:26px 0 12px}
.compare-doc h3{font-size:18px;margin:22px 0 10px}
.compare-doc h4{font-size:15px;margin:18px 0 8px}
.compare-doc p{margin:0 0 14px}
.compare-doc ul,.compare-doc ol{margin:0 0 16px 22px;padding:0}
.compare-doc li{margin:6px 0}
.compare-doc hr{border:none;border-top:1px solid var(--border);margin:22px 0}
.compare-doc pre{margin:0 0 16px;padding:14px 16px;border-radius:14px;background:#0f172a;color:#e2e8f0;overflow:auto}
.compare-doc code{font-family:Consolas,'Courier New',monospace}
.compare-doc table{width:100%;border-collapse:collapse;margin:0 0 18px;display:block;overflow-x:auto}
.compare-doc th,.compare-doc td{padding:10px 12px;border:1px solid var(--border);text-align:left;vertical-align:top}
.compare-doc th{background:#f8fafc;color:var(--brand)}
.digest-events-section{margin-top:20px}
.digest-toggle{cursor:pointer;font-size:14px;font-weight:600;color:var(--muted);padding:12px 16px;border:1px dashed var(--border);border-radius:var(--radius);list-style:none}
.digest-toggle:hover{color:var(--brand);border-color:var(--brand-light)}
.chat-highlight{margin:20px 0 24px;padding:18px 24px;background:linear-gradient(135deg,rgba(13,107,94,.08),rgba(16,185,129,.12));border:1px solid rgba(13,107,94,.2);border-radius:16px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.chat-highlight-icon{font-size:28px}
.chat-highlight-text{flex:1;min-width:200px}
.chat-highlight-text strong{display:block;color:var(--brand);font-size:15px;margin-bottom:4px}
.chat-highlight-text span{font-size:13px;color:#475569}
.chat-highlight-btn{padding:10px 20px;border-radius:12px;background:linear-gradient(135deg,var(--brand),var(--brand-light));color:#fff;text-decoration:none;font-size:13px;font-weight:700;transition:all .2s;white-space:nowrap}
.chat-highlight-btn:hover{transform:translateY(-1px);box-shadow:0 6px 16px rgba(13,107,94,.25)}
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

/* ---- analysis-page CTA on article cards ---- */
.analysis-cta{margin:10px 0 4px}
a.analysis-link{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:var(--brand-light);color:#fff;
                border-radius:6px;font-size:12.5px;font-weight:600;text-decoration:none;transition:all .15s}
a.analysis-link:hover{background:var(--brand);box-shadow:0 2px 8px rgba(13,107,94,.35)}

/* ---- standalone curated-analysis page ---- */
.analysis-page{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:32px 40px;
               margin-bottom:32px;line-height:1.7}
.analysis-page h1{font-size:26px;margin:0 0 8px;color:var(--brand)}
.analysis-page h2{font-size:20px;margin-top:32px;color:var(--brand);border-bottom:2px solid var(--border);padding-bottom:6px}
.analysis-page h3{font-size:16px;margin-top:24px;color:var(--brand-light)}
.analysis-page table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px}
.analysis-page th,.analysis-page td{border:1px solid var(--border);padding:8px 12px;text-align:left;vertical-align:top}
.analysis-page th{background:#f0f7f5;color:var(--brand);font-weight:700}
.analysis-page tr:nth-child(even) td{background:#fafcfb}
.analysis-page blockquote{border-left:4px solid var(--brand-light);padding:4px 16px;color:var(--muted);margin:14px 0}
.analysis-page code{background:#f3f5f7;padding:1px 6px;border-radius:4px;font-size:.9em}
.analysis-meta{margin:0 0 20px;color:var(--muted);font-size:13px}
.analysis-source-link{display:inline-block;margin-top:8px;color:var(--brand);text-decoration:none;font-weight:600}
.analysis-source-link:hover{text-decoration:underline}

/* ---- M&A & Investments hub ---- */
a.deals-hub-card{display:block;margin:16px 0 24px;padding:20px 24px;background:linear-gradient(135deg,#fff8e6,#fff2d1);
                 border:1px solid #f3d17a;border-left:4px solid var(--accent);border-radius:var(--radius);
                 text-decoration:none;color:var(--text);transition:box-shadow .15s,transform .15s}
a.deals-hub-card:hover{box-shadow:0 4px 14px rgba(245,158,11,.20);transform:translateY(-1px)}
.deals-hub-title{font-size:18px;font-weight:700;color:var(--brand);margin-bottom:4px}
.deals-hub-sub{font-size:13px;color:var(--muted);margin-bottom:12px}
.deals-hub-pills{display:flex;flex-wrap:wrap;gap:8px}
a.deals-pill{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#fff;border:1px solid var(--border);
             border-radius:999px;text-decoration:none;color:var(--brand);font-size:13px;transition:background .15s}
a.deals-pill:hover{background:var(--accent);color:#fff;border-color:var(--accent)}
.deals-pill-label{font-weight:600}
.deals-pill-count{color:var(--muted);font-weight:500}
a.deals-pill:hover .deals-pill-count{color:#fff}
.deals-intro{margin-bottom:24px;padding:20px 24px;background:var(--card);border:1px solid var(--border);
             border-radius:var(--radius)}
.deals-intro h2{margin:0 0 10px;color:var(--brand);font-size:22px}
.deals-intro p{margin:0;color:var(--muted);font-size:14px;line-height:1.55}
.deals-section{margin:32px 0}
.deals-section-head{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:14px;
                    padding-bottom:6px;border-bottom:2px solid var(--border)}
.deals-section-head h3{margin:0;font-size:18px}
.deals-section-head h3 a{color:var(--brand);text-decoration:none}
.deals-section-head h3 a:hover{text-decoration:underline}
.deals-section-count{color:var(--muted);font-size:13px}
.deals-more{margin-top:14px;text-align:right}
a.deals-more-link{color:var(--brand-light);font-weight:600;font-size:13px;text-decoration:none}
a.deals-more-link:hover{text-decoration:underline}

/* ---- Investments sub-nav tabs ---- */
.deals-hub-static{cursor:default;pointer-events:none}
.deals-hub-static .deals-pill{pointer-events:auto}
.investments-tabs-row{margin:12px 0 8px}
a.deals-pill-active{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:700}
a.deals-pill-active .deals-pill-count{color:#fff}
a.deals-pill-active:hover{background:var(--accent);color:#fff}
.view-tabs{display:flex;gap:2px;margin:0 0 24px;padding:4px;background:var(--card);border:1px solid var(--border);
           border-radius:10px;width:fit-content}
a.view-tab{display:inline-flex;align-items:center;padding:8px 18px;border-radius:8px;text-decoration:none;
           color:var(--muted);font-size:13px;font-weight:600;transition:all .15s}
a.view-tab:hover{background:var(--bg);color:var(--brand)}
a.view-tab-active{background:var(--brand);color:#fff}
a.view-tab-active:hover{background:var(--brand);color:#fff}

/* ---- Alphabetical view: per-entity card w/ recent stories ---- */
.alpha-entity-card ul.alpha-recent{list-style:none;padding:0;margin:10px 0 0;font-size:13px}
.alpha-entity-card ul.alpha-recent li{padding:4px 0;color:var(--muted);border-top:1px dashed var(--border)}
.alpha-entity-card ul.alpha-recent li:first-child{border-top:none}
.alpha-entity-card ul.alpha-recent a{color:var(--brand-light);text-decoration:none;font-weight:600}
.alpha-entity-card ul.alpha-recent a:hover{text-decoration:underline}
.alpha-title{color:var(--text)}
.alpha-more{margin-top:8px;font-size:12px}
.alpha-more a{color:var(--brand);text-decoration:none;font-weight:600}
.alpha-more a:hover{text-decoration:underline}

/* ---- Timeline view: date-grid + articles-by-date sections ---- */
.timeline-days{margin-top:32px}
.timeline-day{margin:24px 0 40px;padding-top:12px;border-top:2px solid var(--border)}
.timeline-day h3{margin:0 0 14px;font-size:18px;color:var(--brand)}
.timeline-day h3 a{color:inherit;text-decoration:none}
.timeline-day h3 a:hover{text-decoration:underline}
.timeline-day-count{color:var(--muted);font-size:13px;font-weight:500;margin-left:10px}

/* ---- Investments landing page (article-free hub) ---- */
.invest-tagline{font-size:16px;color:var(--muted);margin:8px 0 20px;line-height:1.5}
.invest-hero-grid{display:flex;flex-direction:column;gap:22px;margin:24px 0 40px}
.invest-hero-card{display:grid;grid-template-columns:minmax(280px,1.15fr) minmax(280px,1fr);
                  gap:24px;padding:24px 26px;background:linear-gradient(135deg,#fff8e1 0%,#fff 60%);
                  border:1px solid var(--border);border-radius:14px;
                  box-shadow:0 2px 8px rgba(0,0,0,0.04);transition:box-shadow .18s}
.invest-hero-card:hover{box-shadow:0 6px 20px rgba(0,0,0,0.10)}
@media (max-width:720px){.invest-hero-card{grid-template-columns:1fr}}
.invest-hero-left{display:flex;flex-direction:column}
.invest-hero-head{display:flex;justify-content:space-between;align-items:baseline;
                  margin-bottom:10px;gap:10px;flex-wrap:wrap}
.invest-hero-title{font-size:22px;font-weight:700;color:var(--brand)}
.invest-hero-count{font-size:13px;color:var(--muted);font-weight:600;white-space:nowrap}
.invest-hero-desc{font-size:14.5px;line-height:1.55;color:var(--text);margin:0 0 22px}
a.invest-hero-cta-btn{display:inline-block;align-self:flex-start;margin-top:auto;
                      padding:12px 22px;font-size:17px;font-weight:700;color:#fff;
                      background:var(--accent);border-radius:8px;text-decoration:none;
                      transition:background .18s,transform .18s,box-shadow .18s;
                      box-shadow:0 1px 2px rgba(0,0,0,0.08)}
a.invest-hero-cta-btn:hover{background:var(--brand);transform:translateY(-1px);
                            box-shadow:0 4px 10px rgba(0,0,0,0.12)}
.invest-hero-right{background:rgba(255,255,255,0.55);border:1px dashed var(--border);
                   border-radius:10px;padding:14px 16px 12px;min-width:0}
.invest-hero-right-label{display:block;color:var(--muted);margin-bottom:8px;
                         font-size:11.5px;font-weight:700;letter-spacing:0.5px;
                         text-transform:uppercase}
.invest-hero-examples-list{list-style:none;padding:0;margin:0;
                           display:flex;flex-direction:column;gap:7px;font-size:13.5px;line-height:1.5}
.invest-hero-examples-list li{padding-left:14px;position:relative;
                              overflow-wrap:break-word;word-break:break-word}
.invest-hero-examples-list li::before{content:"\25CF";position:absolute;left:0;top:0;
                                      color:var(--accent);font-size:9px;line-height:1.9}
.invest-hero-examples-list a{color:var(--brand);text-decoration:none;
                             border-bottom:1px dotted var(--brand)}
.invest-hero-examples-list a:hover{color:var(--accent);border-bottom-color:var(--accent)}
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
@media(max-width:900px){
  .compare-page-layout{grid-template-columns:1fr}
  .compare-tabs{grid-template-columns:repeat(auto-fit,minmax(180px,1fr));position:static}
}
@media(max-width:640px){
  header{flex-direction:column;align-items:flex-start;gap:4px;padding:12px 16px}
  .brand{margin-right:0;padding:8px 0 4px}
  nav{gap:0}
  main{padding:16px}
  .grid{grid-template-columns:1fr}
  .snap-nav{flex-direction:column;align-items:stretch;text-align:center}
  .hero{margin:-16px -16px 20px;padding:24px 20px 20px}
  .hero .hero-stats{flex-wrap:wrap;gap:16px}
  .chat-highlight{padding:16px 18px}
  .compare-doc{padding:18px}
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
  <a href="{{ rel }}investments.html"{% if active=='investments' %} aria-current="page"{% endif %}>Investments</a>
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
  {% if a.analysis_page %}<div class="analysis-cta"><a href="{{ a.rel }}analysis/{{ a.analysis_page }}" class="analysis-link">\U0001f4d6 Read full analysis on site &rarr;</a></div>{% endif %}
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
        # If this article is a curated long-form analysis (tag "Analysis"), the
        # article_id doubles as the standalone page slug written by
        # _build_curated_analysis_pages().
        if "Analysis" in a.get("tags", []):
            a["analysis_page"] = f"{a['article_id']}.html"
        else:
            a["analysis_page"] = ""
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


def _chat_highlight(title: str, description: str, rel: str = "") -> str:
    return (
        '<div class="chat-highlight">'
        '<div class="chat-highlight-icon">💬</div>'
        '<div class="chat-highlight-text">'
        f'<strong>{_html.escape(title)}</strong>'
        f'<span>{_html.escape(description)}</span>'
        '</div>'
        f'<a href="{rel}chat.html" class="chat-highlight-btn">Open AI Chat →</a>'
        '</div>'
    )


def _md_inline(text: str) -> str:
    text = _html.escape(text.strip())
    text = _re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = _re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    return text


def _md_to_html(text: str) -> str:
    html_parts: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    list_kind: str | None = None
    table_rows: list[list[str]] = []
    code_lines: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            html_parts.append(f'<p>{_md_inline(" ".join(paragraph_lines))}</p>')
            paragraph_lines = []

    def flush_list() -> None:
        nonlocal list_items, list_kind
        if list_items and list_kind:
            html_parts.append(f'<{list_kind}>{"".join(list_items)}</{list_kind}>')
            list_items = []
            list_kind = None

    def flush_table() -> None:
        nonlocal table_rows
        if not table_rows:
            return

        def is_sep(row: list[str]) -> bool:
            return bool(row) and all(cell and set(cell) <= {':', '-'} for cell in row)

        header = table_rows[0]
        body_rows = table_rows[1:]
        if len(table_rows) > 1 and is_sep(table_rows[1]):
            body_rows = table_rows[2:]
        table_html = ['<table>']
        if header:
            table_html.append('<thead><tr>' + ''.join(f'<th>{_md_inline(cell)}</th>' for cell in header) + '</tr></thead>')
        if body_rows:
            table_html.append('<tbody>' + ''.join(
                '<tr>' + ''.join(f'<td>{_md_inline(cell)}</td>' for cell in row) + '</tr>'
                for row in body_rows
            ) + '</tbody>')
        table_html.append('</table>')
        html_parts.append(''.join(table_html))
        table_rows = []

    def flush_code() -> None:
        nonlocal code_lines
        if code_lines:
            html_parts.append('<pre><code>' + _html.escape('\n'.join(code_lines)) + '</code></pre>')
            code_lines = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if in_code:
            if stripped.startswith('```'):
                flush_code()
                in_code = False
            else:
                code_lines.append(raw_line)
            continue

        if stripped.startswith('```'):
            flush_paragraph()
            flush_list()
            flush_table()
            in_code = True
            code_lines = []
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            flush_table()
            continue

        if stripped == '---':
            flush_paragraph()
            flush_list()
            flush_table()
            html_parts.append('<hr>')
            continue

        if stripped.startswith('|') and stripped.endswith('|'):
            flush_paragraph()
            flush_list()
            table_rows.append([cell.strip() for cell in stripped.strip('|').split('|')])
            continue
        flush_table()

        heading = _re.match(r'^(#{1,4})\s+(.*)$', stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            html_parts.append(f'<h{level}>{_md_inline(heading.group(2))}</h{level}>')
            continue

        ul_item = _re.match(r'^[-*]\s+(.*)$', stripped)
        if ul_item:
            flush_paragraph()
            if list_kind != 'ul':
                flush_list()
                list_kind = 'ul'
            list_items.append(f'<li>{_md_inline(ul_item.group(1))}</li>')
            continue

        ol_item = _re.match(r'^\d+\.\s+(.*)$', stripped)
        if ol_item:
            flush_paragraph()
            if list_kind != 'ol':
                flush_list()
                list_kind = 'ol'
            list_items.append(f'<li>{_md_inline(ol_item.group(1))}</li>')
            continue

        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_list()
    flush_table()
    if in_code:
        flush_code()
    return ''.join(html_parts)


def _build_build_io_compare_page(cfg: Config, site: Path) -> int:
    compare_specs = [
        ('01_Build_vs_IO_Executive_Summary.md', 'Executive Summary'),
        ('02_Google_Microsoft_AI_Models_Comparison.md', 'Models'),
        ('03_Microsoft_Google_Agent_Platforms_Comparison.md', 'Agent Platforms'),
        ('04_Microsoft_Google_Infrastructure_Developer_Tools.md', 'Infrastructure & Tools'),
        ('05_Microsoft_Google_Market_Positioning_Strategy.md', 'Strategy'),
        ('07_Microsoft_Google_Quick_Reference_Guide.md', 'Quick Reference'),
    ]
    docs: list[dict[str, str]] = []
    for idx, (filename, tab_label) in enumerate(compare_specs):
        path = cfg.news_dir / filename
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        title = tab_label
        for line in text.splitlines():
            if line.startswith('#'):
                title = line.lstrip('#').strip() or tab_label
                break
        docs.append({
            'id': f'compare-doc-{idx}',
            'tab': tab_label,
            'title': title,
            'source': filename,
            'content': _md_to_html(text),
        })

    if not docs:
        body = '<p>No Build vs I/O comparison files were found.</p>'
    else:
        tabs_html = ''.join(
            f'<button class="compare-tab-btn{" active" if i == 0 else ""}" onclick="showCompareDoc(this, \'{doc["id"]}\')">{_html.escape(doc["tab"])}</button>'
            for i, doc in enumerate(docs)
        )
        docs_html = ''.join(
            f'<section id="{doc["id"]}" class="compare-doc{" active" if i == 0 else ""}">'
            f'<div class="compare-doc-header"><h2>{_html.escape(doc["title"])}</h2>'
            f'<p class="compare-doc-source">Source: news/{_html.escape(doc["source"])}</p></div>'
            f'{doc["content"]}'
            '</section>'
            for i, doc in enumerate(docs)
        )
        body = (
            '<div class="compare-page-intro">'
            '<h2>⚡ Microsoft Build vs Google I/O</h2>'
            '<p>Explore the full side-by-side comparison across strategy, models, agent platforms, infrastructure, and quick-reference takeaways.</p>'
            '</div>'
            '<div class="compare-page-layout">'
            f'<div class="compare-tabs">{tabs_html}</div>'
            f'<div class="compare-content">{docs_html}</div>'
            '</div>'
            '<script>'
            'function showCompareDoc(btn,id){'
            'document.querySelectorAll(".compare-doc").forEach(el=>el.classList.remove("active"));'
            'document.querySelectorAll(".compare-tab-btn").forEach(el=>el.classList.remove("active"));'
            'document.getElementById(id).classList.add("active");'
            'btn.classList.add("active");}'
            '</script>'
        )

    _write(site / 'compare-build-io.html',
           _render('Build vs I/O Comparison', body, active='events',
                   subtitle='Tabbed comparison of Microsoft Build and Google I/O coverage'))
    return 1


def _build_wwdc_analysis_page(cfg: Config, site: Path) -> int:
    """Build a multi-day tabbed analysis page for Apple WWDC 2026."""
    # Organise specs by day
    day_specs = [
        ('Day 1 — Keynote & Platform', [
            ('01_Apple_WWDC26_Executive_Summary.md', 'Executive Summary'),
            ('02_Apple_WWDC26_Siri_AI_and_Apple_Intelligence.md', 'Siri & Apple Intelligence'),
            ('03_Apple_WWDC26_OS27_Platform_Updates.md', 'OS 27 Platforms'),
            ('04_Apple_WWDC26_Developer_Tools_and_Xcode.md', 'Developer Tools'),
            ('05_Apple_WWDC26_App_Store_Developer_Business.md', 'App Store & Business'),
            ('06_Apple_WWDC26_Child_Safety_Privacy_Regulatory.md', 'Privacy & Safety'),
            ('07_Apple_WWDC26_Quick_Reference_Guide.md', 'Quick Reference'),
        ]),
        ('Day 2 — Services & Intelligence', [
            ('08_Apple_WWDC26_Day2_Executive_Summary.md', 'Day 2 Executive Summary'),
            ('09_Apple_WWDC26_Day2_Services_Intelligence_Deep_Dive.md', 'Services & Intelligence Deep Dive'),
            ('10_Apple_WWDC26_Day2_Wallet_Maps_FindMy_iCloud.md', 'Wallet, Maps, Find My & iCloud'),
            ('11_Apple_WWDC26_Day2_Media_Fitness_Sports_Developer_Releases.md', 'Media, Fitness & Sports'),
            ('12_Apple_WWDC26_Day2_Quick_Reference_Guide.md', 'Day 2 Quick Reference'),
        ]),
    ]

    # Build docs per day
    all_days: list[tuple[str, list[dict]]] = []
    total_docs = 0
    global_idx = 0
    for day_label, specs in day_specs:
        docs: list[dict[str, str]] = []
        for filename, tab_label in specs:
            path = cfg.news_dir / filename
            if not path.exists():
                continue
            text = path.read_text(encoding='utf-8', errors='replace')
            title = tab_label
            for line in text.splitlines():
                if line.startswith('#'):
                    title = line.lstrip('#').strip() or tab_label
                    break
            docs.append({
                'id': f'wwdc-doc-{global_idx}',
                'tab': tab_label,
                'title': title,
                'source': filename,
                'content': _md_to_html(text),
            })
            global_idx += 1
        if docs:
            all_days.append((day_label, docs))
            total_docs += len(docs)

    if not total_docs:
        return 0

    # Build day-level tabs and content
    day_tabs_html = ''.join(
        f'<button class="day-tab-btn{" active" if i == 0 else ""}" '
        f'onclick="showDay(this, \'day-panel-{i}\')">{_html.escape(day_label)}</button>'
        for i, (day_label, _) in enumerate(all_days)
    )

    day_panels: list[str] = []
    first_global = True
    for day_i, (day_label, docs) in enumerate(all_days):
        tabs_html = ''.join(
            f'<button class="compare-tab-btn{" active" if j == 0 else ""}" '
            f'onclick="showCompareDoc(this, \'{doc["id"]}\')">{_html.escape(doc["tab"])}</button>'
            for j, doc in enumerate(docs)
        )
        docs_html = ''.join(
            f'<section id="{doc["id"]}" class="compare-doc{" active" if j == 0 else ""}">'
            f'<div class="compare-doc-header"><h2>{_html.escape(doc["title"])}</h2>'
            f'<p class="compare-doc-source">Source: news/{_html.escape(doc["source"])}</p></div>'
            f'{doc["content"]}'
            '</section>'
            for j, doc in enumerate(docs)
        )
        panel = (
            f'<div id="day-panel-{day_i}" class="day-panel{" active" if day_i == 0 else ""}">'
            f'<div class="compare-page-layout">'
            f'<div class="compare-tabs">{tabs_html}</div>'
            f'<div class="compare-content">{docs_html}</div>'
            f'</div></div>'
        )
        day_panels.append(panel)

    day_panels_html = ''.join(day_panels)

    day_css = (
        '<style>'
        '.day-tabs{display:flex;gap:6px;margin-bottom:18px;flex-wrap:wrap;}'
        '.day-tab-btn{padding:10px 22px;border:2px solid #00d4aa;background:transparent;'
        'color:#e0e0e0;border-radius:8px;cursor:pointer;font-size:1rem;font-weight:600;'
        'transition:all .2s;}'
        '.day-tab-btn:hover{background:rgba(0,212,170,.15);}'
        '.day-tab-btn.active{background:#00d4aa;color:#0a0a0a;}'
        '.day-panel{display:none;}'
        '.day-panel.active{display:block;}'
        '</style>'
    )

    body = (
        day_css
        + '<div class="compare-page-intro">'
        '<h2>\U0001f34e Apple WWDC 2026 — Full Analysis</h2>'
        '<p>Comprehensive multi-day coverage of WWDC26: Day 1 keynote &amp; platform announcements and '
        'Day 2 services &amp; intelligence deep-dive.</p>'
        f'<p style="color:#aaa;font-size:.9rem;">{total_docs} analysis documents across {len(all_days)} days</p>'
        '</div>'
        f'<div class="day-tabs">{day_tabs_html}</div>'
        f'{day_panels_html}'
        '<script>'
        'function showDay(btn,id){'
        'document.querySelectorAll(".day-panel").forEach(el=>el.classList.remove("active"));'
        'document.querySelectorAll(".day-tab-btn").forEach(el=>el.classList.remove("active"));'
        'document.getElementById(id).classList.add("active");'
        'btn.classList.add("active");}'
        'function showCompareDoc(btn,id){'
        'document.querySelectorAll(".compare-doc").forEach(el=>el.classList.remove("active"));'
        'var panel=btn.closest(".day-panel");'
        'panel.querySelectorAll(".compare-tab-btn").forEach(el=>el.classList.remove("active"));'
        'document.getElementById(id).classList.add("active");'
        'btn.classList.add("active");}'
        '</script>'
    )

    _write(site / 'wwdc-2026.html',
           _render('Apple WWDC 2026 Analysis', body, active='events',
                   subtitle='Comprehensive multi-day analysis of Apple WWDC 2026'))
    return 1


# --- Microsoft FY27 strategy & comparison analysis (curated, July 2026) ------
# These files are rich narrative analysis docs (headings + tables) that are
# rendered directly from news/ as curated pages, mirroring the Build vs I/O and
# WWDC analysis pages. They are intentionally NOT parsed as digest articles
# (see _is_curated_analysis_file in split.py). Files are auto-discovered so new
# per-company briefings are picked up on the next build without code changes.
_FY27_DATE = "2026-07-21"


# --- Standalone curated analysis pages ---------------------------------------
# Any `YYYY-MM-DD_*_Strategy.md` file that is NOT part of the FY27 date series
# is a standalone long-form analysis (e.g. the Aug 2026 Nvidia startup-
# investment strategy write-up). split.py emits ONE indexable Article record
# per file (tag "Analysis"); this builder renders the full markdown body to
# `site/analysis/<article_id>.html` and cross-links it from the article card
# via the `analysis_page` field populated in `_cards()`.
_CURATED_ANALYSIS_FILE_RE = _re.compile(
    r"^(\d{4}-\d{2}-\d{2})_.+_(?:Strategy|Strategy_Signals|Comparison)\.md$"
)


def _curated_analysis_files(cfg: Config) -> list[Path]:
    """Enumerate standalone curated-analysis markdowns (excluding the FY27
    series which is rendered by its own bespoke builder)."""
    out: list[Path] = []
    for path in sorted(cfg.news_dir.glob("*.md")):
        m = _CURATED_ANALYSIS_FILE_RE.match(path.name)
        if not m or m.group(1) == _FY27_DATE:
            continue
        # Skip the FY27 head-to-head comparison files as well.
        if "_vs_" in path.name and path.name.endswith("_Comparison.md"):
            continue
        out.append(path)
    return out


def _investments_tab_strip(active_slug: str, active_view: str,
                           deals_by_slug: dict[str, list[dict]], rel: str) -> str:
    """Two-row tab strip shown at the top of every /investments/* page.

    Row 1 (category switcher): pills for the three sub-categories with the
    active one highlighted. Row 2 (view switcher): Latest / Alphabetical /
    Timeline tabs for the current sub-category. Both link to real static URLs
    so navigation is directly bookmarkable and works with no JS.
    """
    view_labels = (
        ("latest", "Latest", ""),
        ("by-company", "Alphabetical", "-by-company"),
        ("timeline", "Timeline", "-timeline"),
    )

    # Category pills
    pills: list[str] = []
    for slug in _DEALS_SUBCATEGORIES:
        count = len(deals_by_slug.get(slug, []))
        # When switching category, land on the SAME view the user was on
        view_suffix = next((s for k, _l, s in view_labels if k == active_view), "")
        href = f"{rel}investments/{slug}{view_suffix}.html"
        classes = "deals-pill"
        if slug == active_slug:
            classes += " deals-pill-active"
        pills.append(
            f'<a class="{classes}" href="{href}">'
            f'<span class="deals-pill-label">{_topic_label(slug)}</span>'
            f'<span class="deals-pill-count">{count}</span></a>'
        )
    category_row = f'<div class="deals-hub-pills investments-tabs-row">{"".join(pills)}</div>'

    # View tabs (Latest / Alphabetical / Timeline)
    view_tabs: list[str] = []
    for key, label, suffix in view_labels:
        href = f"{rel}investments/{active_slug}{suffix}.html"
        classes = "view-tab"
        if key == active_view:
            classes += " view-tab-active"
        view_tabs.append(f'<a class="{classes}" href="{href}">{label}</a>')
    view_row = f'<div class="view-tabs">{"".join(view_tabs)}</div>'

    return category_row + view_row


# --- Strong-signal patterns used to pick "truly relevant" example stories
# for the /investments landing hub. These are applied to the article TITLE
# (case-insensitive) so we only surface examples whose headline itself
# unambiguously describes a deal in that sub-category. Broader classifier
# patterns can legitimately match body text (e.g. an entity page mention),
# but on the hub we want the reader to see three clean, canonical examples.
_HUB_EXAMPLE_STRONG = {
    "ma-activity": _re.compile(
        r"\b(acqui(?:re[ds]?|res|ring|sition)|merge[ds]?|merger|"
        r"buy(?:s|out|ing)|bought|takeover|take[- ]private|"
        r"spin[- ]off|divest|carve[- ]out|acqui[- ]?hire)\b",
        _re.IGNORECASE,
    ),
    "company-investments": _re.compile(
        r"\b(raise[ds]?|raising|funding round|series\s+[a-h]\b|"
        r"seed round|pre[- ]seed|valuation|valued at|"
        r"ipo\b|s-1\b|files? to go public|secondary sale|"
        r"tender offer|pre[- ]money|post[- ]money)\b",
        _re.IGNORECASE,
    ),
    "infrastructure-investments": _re.compile(
        r"\b(data ?center|hyperscaler|gigawatt|megawatt|"
        r"gpu (?:cluster|order|supply)|chip supply|foundry|"
        r"capex|build[- ]?out|power purchase|nuclear|"
        r"substation|fab\b|wafer)\b",
        _re.IGNORECASE,
    ),
}

# Any $-amount or "billion/million/bn/mn" is a strong hint that the story
# describes a concrete deal (rather than an opinion piece / analysis).
_HUB_EXAMPLE_MONEY = _re.compile(
    r"(\$\s?\d|\b\d+(?:\.\d+)?\s*(?:billion|million|trillion|bn|mn)\b)",
    _re.IGNORECASE,
)


def _pick_hub_examples(items: list[dict], slug: str, n: int = 3) -> list[dict]:
    """Choose up to `n` recent, truly-relevant example articles for the hub.

    Selection strategy (in priority order):
      1. Recent (title matches the sub-category's strong pattern AND mentions
         a money amount, AND has a working canonical URL).
      2. Recent (title matches strong pattern OR mentions money; URL working).
      3. Fallback to the most-recent items regardless of title strictness.
    Deduplicates on a normalized-title signature so the same deal reported
    by three feeds does not appear three times.
    """
    if not items:
        return []
    strong_re = _HUB_EXAMPLE_STRONG.get(slug)
    money_re = _HUB_EXAMPLE_MONEY
    ok_status = {"ok", "repaired", "found"}

    def _url_ok(a: dict) -> bool:
        return bool(a.get("url_canonical")) and a.get("url_status") in ok_status

    def _title(a: dict) -> str:
        return (a.get("title") or "").strip()

    sorted_items = sorted(items, key=lambda a: (a.get("date") or ""), reverse=True)

    tier1: list[dict] = []
    tier2: list[dict] = []
    tier3: list[dict] = []
    for a in sorted_items:
        title = _title(a)
        if not title:
            continue
        has_strong = bool(strong_re and strong_re.search(title))
        has_money = bool(money_re.search(title))
        url_ok = _url_ok(a)
        if url_ok and has_strong and has_money:
            tier1.append(a)
        elif url_ok and (has_strong or has_money):
            tier2.append(a)
        else:
            tier3.append(a)

    picked: list[dict] = []
    seen_signatures: set[str] = set()
    for pool in (tier1, tier2, tier3):
        for a in pool:
            sig = _re.sub(r"\W+", "", _title(a).lower())[:40]
            if sig in seen_signatures:
                continue
            seen_signatures.add(sig)
            picked.append(a)
            if len(picked) >= n:
                return picked
    return picked


def _format_hub_example(a: dict) -> str:
    """Render one example article as a compact clickable snippet.

    Uses the external canonical URL when working; otherwise renders as plain
    text. Truncates the title to ~55 chars so three examples fit on one line
    on typical desktop widths.
    """
    title = (a.get("title") or "").strip()
    if not title:
        return ""
    display = title
    if len(display) > 58:
        display = display[:55].rstrip() + "\u2026"
    display = _html.escape(display)
    url = a.get("url_canonical") or ""
    status = a.get("url_status") or ""
    if url and status in ("ok", "repaired", "found"):
        return (f'<a href="{_html.escape(url)}" target="_blank" '
                f'rel="noopener">{display}</a>')
    return display


def _build_investments_pages(site: Path, deals_by_slug: dict[str, list[dict]],
                             entity_files: dict[str, str],
                             paginate_js: str) -> int:
    """Generate the /investments.html landing + nine sub-category view pages.

    Structure:
      /investments.html                                (landing hub)
      /investments/<slug>.html                         (Latest view)
      /investments/<slug>-by-company.html              (Alphabetical A-Z)
      /investments/<slug>-timeline.html                (Timeline w/ date-boxes)

    where <slug> is one of ma-activity, company-investments,
    infrastructure-investments. The Latest view mirrors the old
    /topics/<slug>.html card list; the two additional views scope the existing
    site-wide patterns (letter-nav for entities, date-grid for archive) to a
    single sub-category.
    """
    pages_written = 0
    total = sum(len(v) for v in deals_by_slug.values())
    if not total:
        return 0

    # ----- Landing hub: /investments.html -----
    # A clean, article-free landing: heading + intro paragraph + three large
    # category cards (each with a description + example story types) so the
    # reader picks the right sub-category before diving into content.
    intro = (
        '<div class="deals-intro">'
        '<p>Where the money is moving in AI. This hub groups deal-flow stories '
        'into three sub-categories: full-company transactions, equity going '
        '<em>into</em> companies, and capital going <em>into</em> physical '
        'infrastructure. Articles can appear in more than one sub-category '
        '(e.g. an equity stake tied to a chip supply deal).</p>'
        '</div>'
    )

    # Human-facing description + typical examples per sub-category. The
    # `examples_fallback` string is used only when there are no articles
    # (empty pipeline) — normally we render three recent-and-relevant
    # example articles picked by `_pick_hub_examples()`.
    subcat_meta = {
        "ma-activity": {
            "desc": ("Full-company transactions: acquisitions, mergers, "
                     "acqui-hires, take-privates, spin-offs and divestitures. "
                     "Who bought whom, and for how much."),
            "examples_fallback": ("Meta acquires ARI \u2022 Anthropic\u2013Blackstone JV "
                                  "buys Fractional AI \u2022 AMD acquires Taalas"),
        },
        "company-investments": {
            "desc": ("Money going <em>into</em> companies: funding rounds, "
                     "venture capital, IPOs, S-1 filings, secondary sales, "
                     "strategic equity stakes and valuations."),
            "examples_fallback": ("Anthropic\u2019s $30B round at $900B valuation \u2022 "
                                  "Cerebras IPO \u2022 DeepSeek $50B pre-money"),
        },
        "infrastructure-investments": {
            "desc": ("Capital going <em>into</em> physical AI infrastructure: "
                     "datacenter build-outs, GPU / chip orders, foundry "
                     "capacity, power purchase agreements, and hyperscaler "
                     "capex."),
            "examples_fallback": ("Anthropic \u2013 SpaceX $40B compute deal \u2022 "
                                  "Huawei $11.7B autonomy build-out \u2022 nuclear PPAs"),
        },
    }

    hero_cards = []
    for slug in _DEALS_SUBCATEGORIES:
        items = deals_by_slug.get(slug, [])
        n = len(items)
        meta = subcat_meta.get(slug, {"desc": "", "examples_fallback": ""})
        label = _topic_label(slug)
        # Dynamic examples: pick up to 3 recent, truly-relevant example
        # stories from THIS sub-category and render them as clickable links.
        picked = _pick_hub_examples(items, slug, n=3)
        rendered = [s for s in (_format_hub_example(a) for a in picked) if s]
        if rendered:
            examples_html = "".join(f"<li>{item}</li>" for item in rendered)
        else:
            examples_html = f"<li>{meta['examples_fallback']}</li>"
        # Outer wrapper is a <div> (not <a>) because we want nested <a> tags
        # for each example link. The big CTA button is the primary click
        # target for reaching the sub-category page.
        hero_cards.append(
            f'<div class="invest-hero-card">'
            f'<div class="invest-hero-left">'
            f'<div class="invest-hero-head">'
            f'<span class="invest-hero-title">{label}</span>'
            f'<span class="invest-hero-count">{n} stories</span>'
            f'</div>'
            f'<p class="invest-hero-desc">{meta["desc"]}</p>'
            f'<a class="invest-hero-cta-btn" href="investments/{slug}.html">'
            f'Browse {label} \u2192</a>'
            f'</div>'
            f'<div class="invest-hero-right">'
            f'<span class="invest-hero-right-label">Recent examples</span>'
            f'<ul class="invest-hero-examples-list">{examples_html}</ul>'
            f'</div>'
            f'</div>'
        )
    hero_grid = '<div class="invest-hero-grid">' + "".join(hero_cards) + '</div>'

    # Big title + tagline live in the page subtitle / body header so we can
    # keep the standard site layout wrapper.
    body = (
        '<div class="invest-tagline">'
        'Follow the money: Acquisitions, Company Investments &amp; Funding '
        'Rounds, and Infrastructure Investments.'
        '</div>'
        + intro
        + hero_grid
    )
    _write(site / "investments.html",
           _render("\U0001f4b0 M&A and Investments", body,
                   active="investments",
                   subtitle=f"{total} deal-flow stories across three sub-categories"))
    pages_written += 1

    # ----- Sub-category pages: 3 slugs \u00d7 3 views = 9 pages -----
    for slug in _DEALS_SUBCATEGORIES:
        items = deals_by_slug.get(slug, [])
        if not items:
            continue
        label = _topic_label(slug)

        # Latest view (default). Cards list, newest first, matches old /topics/ page.
        latest_items = sorted(items, key=lambda a: (a.get("date") or ""), reverse=True)
        tabs = _investments_tab_strip(slug, "latest", deals_by_slug, rel="../")
        body = tabs + _cards(latest_items, rel="../", entity_files=entity_files)
        if len(latest_items) > _PAGE_SIZE:
            body += paginate_js
        _write(site / "investments" / f"{slug}.html",
               _render(label, body, rel="../", active="investments",
                       subtitle=f"{len(items)} stories \u00b7 Latest first"))
        pages_written += 1

        # Alphabetical view: A-Z letter nav then per-letter sections listing
        # each company with its article count in THIS sub-category. Each
        # company entry expands to show up to 5 most-recent article titles
        # (with dates) so the "and also by date" ordering is visible.
        ent_counter: Counter = Counter()
        by_entity: dict[str, list[dict]] = defaultdict(list)
        for a in items:
            for e in a.get("entities", []):
                ent_counter[e] += 1
                by_entity[e].append(a)
        sorted_ents = sorted(ent_counter.keys(), key=str.upper)
        letters_present = sorted({e[0].upper() for e in sorted_ents if e})
        all_letters = [chr(c) for c in range(65, 91)]
        letter_nav = '<div class="letter-nav">' + "".join(
            f'<a href="#letter-{L}">{L}</a>' if L in letters_present
            else f'<a class="disabled">{L}</a>'
            for L in all_letters
        ) + '</div>'

        parts: list[str] = [letter_nav]
        current_letter = ""
        for e in sorted_ents:
            first = e[0].upper()
            if first != current_letter:
                current_letter = first
                parts.append(f'<h2 id="letter-{first}">{first}</h2>')
            c = ent_counter[e]
            safe = _safe_filename(e)
            # Show up to 5 most-recent article titles+dates under each company.
            recent = sorted(by_entity[e], key=lambda a: (a.get("date") or ""), reverse=True)[:5]
            recent_html = "".join(
                f'<li><a href="../snapshots/{a["date"]}.html">{_format_date(a["date"]) or a.get("date") or ""}</a>'
                f' \u2014 <span class="alpha-title">{_html.escape(a.get("title") or "")[:120]}</span></li>'
                for a in recent if a.get("date")
            )
            more_link = ""
            if len(by_entity[e]) > len(recent):
                more_link = (f'<div class="alpha-more">'
                             f'<a href="../entities/{safe}.html">View all {c} stories for {_html.escape(e)} \u2192</a></div>')
            parts.append(
                f'<div class="card alpha-entity-card">'
                f'<a class="t" href="../entities/{safe}.html">{_html.escape(e)}</a>'
                f'<div class="meta"><span>{c} {"story" if c == 1 else "stories"}</span></div>'
                f'<ul class="alpha-recent">{recent_html}</ul>'
                f'{more_link}'
                f'</div>'
            )
        tabs = _investments_tab_strip(slug, "by-company", deals_by_slug, rel="../")
        body = tabs + "\n".join(parts)
        _write(site / "investments" / f"{slug}-by-company.html",
               _render(f"{label} \u2014 Alphabetical", body, rel="../",
                       active="investments",
                       subtitle=f"{len(sorted_ents)} companies \u00b7 {len(items)} stories"))
        pages_written += 1

        # Timeline view: date-box grid (like /archive.html) + articles grouped
        # by date below, so users can browse chronologically without leaving
        # the sub-category scope.
        by_date: dict[str, list[dict]] = defaultdict(list)
        for a in items:
            d = a.get("date")
            if d:
                by_date[d].append(a)
        sorted_dates = sorted(by_date.keys(), reverse=True)
        date_grid = '<div class="grid">' + "".join(
            f'<div class="card"><a class="t" href="#date-{d}">{_format_date(d)}</a>'
            f'<div class="count">{len(by_date[d])}</div><div class="label">'
            f'{"story" if len(by_date[d]) == 1 else "stories"}</div></div>'
            for d in sorted_dates
        ) + '</div>'
        date_sections: list[str] = []
        for d in sorted_dates:
            day_articles = sorted(by_date[d], key=lambda a: (a.get("title") or ""))
            date_sections.append(
                f'<section class="timeline-day" id="date-{d}">'
                f'<h3><a href="../snapshots/{d}.html">{_format_date(d)}</a> '
                f'<span class="timeline-day-count">'
                f'{len(day_articles)} {"story" if len(day_articles) == 1 else "stories"}</span></h3>'
                f'{_cards(day_articles, rel="../", entity_files=entity_files)}'
                f'</section>'
            )
        tabs = _investments_tab_strip(slug, "timeline", deals_by_slug, rel="../")
        body = tabs + date_grid + '<div class="timeline-days">' + "".join(date_sections) + '</div>'
        _write(site / "investments" / f"{slug}-timeline.html",
               _render(f"{label} \u2014 Timeline", body, rel="../",
                       active="investments",
                       subtitle=f"{len(sorted_dates)} days \u00b7 {len(items)} stories"))
        pages_written += 1

    return pages_written


def _build_curated_analysis_pages(cfg: Config, site: Path,
                                  canonical: list[dict]) -> int:
    """Render each standalone curated-analysis markdown to its own site page.

    The output filename is `analysis/<article_id>.html`, matching the slug that
    `_cards()` computes for the article's "Read full analysis" CTA link.
    """
    files = _curated_analysis_files(cfg)
    if not files:
        return 0

    # Map file date+slug -> article record so we can surface the article's
    # source URL and canonical page anchor. `parse_curated_analysis` uses the
    # file's H1 as the title and `util.slugify` on that for the article_id.
    from . import util as _util
    article_by_slug: dict[str, dict] = {}
    for art in canonical:
        if "Analysis" in (art.get("tags") or []):
            article_by_slug[art["article_id"]] = art

    pages = 0
    for path in files:
        text = path.read_text(encoding='utf-8', errors='replace')
        # Derive the H1 title (same rule as parse_curated_analysis).
        title = path.stem
        body_start = 0
        for i, line in enumerate(text.splitlines()):
            stripped = line.strip()
            if stripped.startswith("# ") and not stripped.startswith("## "):
                title = stripped.lstrip("# ").strip() or title
                body_start = i + 1
                break
        body_md = "\n".join(text.splitlines()[body_start:]).strip()
        m = _re.match(r"^(\d{4}-\d{2}-\d{2})", path.name)
        iso_date = m.group(1) if m else ""
        slug = f"{iso_date}-{_util.slugify(title)}" if iso_date else _util.slugify(title)

        art = article_by_slug.get(slug)
        source_url = (art or {}).get("url_canonical") or ""
        date_display = _format_date(iso_date) if iso_date else ""

        source_link_html = ""
        if source_url:
            try:
                domain = urllib.parse.urlparse(source_url).netloc.removeprefix("www.")
            except Exception:
                domain = source_url[:60]
            source_link_html = (
                f'<a class="analysis-source-link" href="{_html.escape(source_url)}" '
                f'target="_blank" rel="noopener">\U0001f517 Primary source: '
                f'{_html.escape(domain)} &rarr;</a>'
            )

        body_html = _md_to_html(body_md)
        page_body = (
            '<article class="analysis-page">'
            f'<h1>{_html.escape(title)}</h1>'
            f'<p class="analysis-meta">{_html.escape(date_display)} '
            f'\u00b7 Executive Analysis \u00b7 Source: news/{_html.escape(path.name)}</p>'
            f'{source_link_html}'
            f'{body_html}'
            '</article>'
        )
        _write(site / 'analysis' / f'{slug}.html',
               _render(title, page_body, rel='../', active='',
                       subtitle='Long-form analysis'))
        pages += 1
    return pages


def _read_curated_doc(path: Path, fallback_title: str) -> tuple[str, str]:
    """Return (raw_markdown, first-heading title) for a curated analysis file."""
    text = path.read_text(encoding='utf-8', errors='replace')
    title = fallback_title
    for line in text.splitlines():
        if line.startswith('#'):
            title = line.lstrip('#').strip() or fallback_title
            break
    return text, title


def _fy27_strategy_files(cfg: Config) -> list[tuple[Path, str, str]]:
    """Discover FY27 strategy-signal files -> [(path, label, page-slug)].

    Microsoft (the baseline) is listed first; the rest are alphabetical.
    """
    out: list[tuple[Path, str, str]] = []
    for path in cfg.news_dir.glob(f"{_FY27_DATE}_*_Strategy*.md"):
        if "_vs_" in path.name or path.name.endswith("_Comparison.md"):
            continue
        token = path.name[len(_FY27_DATE) + 1:-3]
        token = _re.sub(r"_Strategy(?:_Signals)?$", "", token)
        if token.startswith("Microsoft_FY27"):
            label, slug = "Microsoft FY27", "fy27-microsoft"
        else:
            label = token.replace("_", " ")
            slug = "fy27-" + _safe_filename(label).lower()
        out.append((path, label, slug))
    out.sort(key=lambda t: (t[1] != "Microsoft FY27", t[1].lower()))
    return out


def _fy27_compare_files(cfg: Config) -> list[tuple[Path, str]]:
    """Discover Microsoft FY27 head-to-head comparison files -> [(path, tab)]."""
    out: list[tuple[Path, str]] = []
    for path in cfg.news_dir.glob(f"{_FY27_DATE}_Microsoft_FY27_vs_*_Comparison.md"):
        token = path.name.split("_vs_", 1)[1][:-3]
        token = _re.sub(r"_Comparison$", "", token)
        out.append((path, "vs " + token.replace("_", " ")))
    out.sort(key=lambda t: t[1].lower())
    return out



def _build_fy27_compare_page(cfg: Config, site: Path) -> int:
    """Tabbed page comparing Microsoft FY27 against each big-tech competitor."""
    docs: list[dict[str, str]] = []
    for idx, (path, tab_label) in enumerate(_fy27_compare_files(cfg)):
        text, title = _read_curated_doc(path, tab_label)
        docs.append({
            'id': f'fy27-compare-doc-{idx}',
            'tab': tab_label,
            'title': title,
            'source': path.name,
            'content': _md_to_html(text),
        })
    if not docs:
        return 0

    tabs_html = ''.join(
        f'<button class="compare-tab-btn{" active" if i == 0 else ""}" '
        f'onclick="showCompareDoc(this, \'{doc["id"]}\')">{_html.escape(doc["tab"])}</button>'
        for i, doc in enumerate(docs)
    )
    docs_html = ''.join(
        f'<section id="{doc["id"]}" class="compare-doc{" active" if i == 0 else ""}">'
        f'<div class="compare-doc-header"><h2>{_html.escape(doc["title"])}</h2>'
        f'<p class="compare-doc-source">Source: news/{_html.escape(doc["source"])}</p></div>'
        f'{doc["content"]}'
        '</section>'
        for i, doc in enumerate(docs)
    )
    body = (
        '<div class="compare-page-intro">'
        '<h2>\u2694\ufe0f Microsoft FY27 vs Big Tech</h2>'
        f'<p>Side-by-side comparison of Microsoft\u2019s FY27 kickoff strategy against '
        f'{len(docs)} competitors across strategy, models, infrastructure, and '
        'market positioning.</p>'
        '<p class="compare-link-row"><a href="fy27-strategy.html" class="compare-link">'
        'View the per-company strategy signals \u2192</a></p>'
        '</div>'
        '<div class="compare-page-layout">'
        f'<div class="compare-tabs">{tabs_html}</div>'
        f'<div class="compare-content">{docs_html}</div>'
        '</div>'
        '<script>'
        'function showCompareDoc(btn,id){'
        'document.querySelectorAll(".compare-doc").forEach(el=>el.classList.remove("active"));'
        'document.querySelectorAll(".compare-tab-btn").forEach(el=>el.classList.remove("active"));'
        'document.getElementById(id).classList.add("active");'
        'btn.classList.add("active");}'
        '</script>'
    )
    _write(site / 'compare-fy27.html',
           _render('Microsoft FY27 vs Big Tech', body, active='events',
                   subtitle='Tabbed comparison of Microsoft FY27 strategy vs big-tech competitors'))
    return 1


def _build_fy27_strategy_pages(cfg: Config, site: Path) -> int:
    """Build a combined tabbed FY27 strategy page plus one page per company."""
    docs: list[dict[str, str]] = []
    for idx, (path, label, slug) in enumerate(_fy27_strategy_files(cfg)):
        text, title = _read_curated_doc(path, label)
        docs.append({
            'id': f'fy27-strat-doc-{idx}',
            'tab': label,
            'title': title,
            'slug': slug,
            'source': path.name,
            'content': _md_to_html(text),
        })
    if not docs:
        return 0

    pages = 0

    # --- individual per-company event pages (events/<slug>.html) ---
    for doc in docs:
        detail_body = (
            '<div class="compare-page-intro">'
            f'<h2>{_html.escape(doc["title"])}</h2>'
            '<p>Strategy signals extracted from the July 2026 briefings. '
            'Part of the <a href="../compare-fy27.html">Microsoft FY27 vs Big Tech</a> series '
            'and the <a href="../fy27-strategy.html">combined strategy view</a>.</p>'
            '</div>'
            '<section class="compare-doc active">'
            f'<div class="compare-doc-header"><p class="compare-doc-source">Source: news/{_html.escape(doc["source"])}</p></div>'
            f'{doc["content"]}'
            '</section>'
        )
        _write(site / 'events' / f'{doc["slug"]}.html',
               _render(doc['title'], detail_body, rel='../', active='events',
                       subtitle='FY27 strategy signals'))
        pages += 1

    # --- combined tabbed page (fy27-strategy.html) ---
    tabs_html = ''.join(
        f'<button class="compare-tab-btn{" active" if i == 0 else ""}" '
        f'onclick="showCompareDoc(this, \'{doc["id"]}\')">{_html.escape(doc["tab"])}</button>'
        for i, doc in enumerate(docs)
    )
    docs_html = ''.join(
        f'<section id="{doc["id"]}" class="compare-doc{" active" if i == 0 else ""}">'
        f'<div class="compare-doc-header"><h2>{_html.escape(doc["title"])}</h2>'
        f'<p class="compare-doc-source">Source: news/{_html.escape(doc["source"])} \u00b7 '
        f'<a href="events/{doc["slug"]}.html">open standalone page \u2192</a></p></div>'
        f'{doc["content"]}'
        '</section>'
        for i, doc in enumerate(docs)
    )
    body = (
        '<div class="compare-page-intro">'
        '<h2>\U0001f4c8 FY27 Strategy Signals</h2>'
        f'<p>Per-company AI strategy signals from the July 2026 briefings: Microsoft\u2019s '
        f'FY27 kickoff and the competitive posture of {len(docs) - 1} other companies '
        'across models, agents, infrastructure, and go-to-market.</p>'
        '<p class="compare-link-row"><a href="compare-fy27.html" class="compare-link">'
        'See Microsoft FY27 head-to-head comparisons \u2192</a></p>'
        '</div>'
        '<div class="compare-page-layout">'
        f'<div class="compare-tabs">{tabs_html}</div>'
        f'<div class="compare-content">{docs_html}</div>'
        '</div>'
        '<script>'
        'function showCompareDoc(btn,id){'
        'document.querySelectorAll(".compare-doc").forEach(el=>el.classList.remove("active"));'
        'document.querySelectorAll(".compare-tab-btn").forEach(el=>el.classList.remove("active"));'
        'document.getElementById(id).classList.add("active");'
        'btn.classList.add("active");}'
        '</script>'
    )
    _write(site / 'fy27-strategy.html',
           _render('FY27 Strategy Signals', body, active='events',
                   subtitle='Per-company AI strategy signals \u00b7 July 2026'))
    pages += 1
    return pages


def _fy27_events_section(cfg: Config) -> str:
    """Card section for events.html linking the FY27 strategy & comparison pages."""
    strat = _fy27_strategy_files(cfg)
    compare = _fy27_compare_files(cfg)
    if not strat and not compare:
        return ""

    company_cards = "".join(
        '<div class="compare-card">'
        f'<h3><a href="events/{slug}.html">{_html.escape(label)}</a></h3>'
        '<div class="compare-stat">Strategy signals \u00b7 July 2026</div>'
        '</div>'
        for _f, label, slug in strat
    )
    combined_stat = (
        f'<div class="compare-stat"><span class="compare-num">{len(strat)}</span> company briefings</div>'
        if strat else ''
    )
    compare_stat = (
        f'<div class="compare-stat"><span class="compare-num">{len(compare)}</span> head-to-head comparisons</div>'
        if compare else ''
    )
    hub_cards = ""
    if strat:
        theme_names = ", ".join(label for _f, label, _s in strat[:6])
        if len(strat) > 6:
            theme_names += f", +{len(strat) - 6} more"
        hub_cards += (
            '<div class="compare-card">'
            '<h3><a href="fy27-strategy.html">FY27 Strategy Signals</a></h3>'
            f'{combined_stat}'
            f'<div class="compare-themes">{_html.escape(theme_names)}</div>'
            '</div>'
        )
    if compare:
        hub_cards += (
            '<div class="compare-card">'
            '<h3><a href="compare-fy27.html">Microsoft FY27 vs Big Tech</a></h3>'
            f'{compare_stat}'
            '<div class="compare-themes">Strategy, models, infrastructure, positioning</div>'
            '</div>'
        )

    link_row = ""
    if compare:
        link_row = ('<p class="compare-link-row"><a href="compare-fy27.html" class="compare-link">'
                    'View full FY27 comparison \u2192</a></p>')
    elif strat:
        link_row = ('<p class="compare-link-row"><a href="fy27-strategy.html" class="compare-link">'
                    'View FY27 strategy signals \u2192</a></p>')

    return (
        '<div class="compare-section">'
        '<h2>\U0001f4c8 Microsoft FY27 &amp; Big Tech Strategy</h2>'
        '<p class="compare-subtitle">Per-company strategy signals and Microsoft head-to-head comparisons \u00b7 July 2026</p>'
        '<div class="compare-grid">' + hub_cards + company_cards + '</div>'
        + link_row +
        '</div>'
    )


def _build_event_pages(cfg: Config, site: Path, canonical: list[dict],
                       entity_files: dict[str, str]) -> int:
    """Build event pages using DB-indexed event articles.

    Generates:
      - events.html: main page with upcoming banner + two inline tab views
      - events/<event-slug>.html: individual event detail pages
    """
    event_articles = [a for a in canonical if a.get("event_name")]
    if not event_articles:
        empty_body = _chat_highlight(
            "The best way to explore event coverage is AI Chat",
            "Ask about events — 'Summarize Microsoft Build' or 'What was announced at Google I/O?'",
        ) + "<p>No event coverage found. Run the pipeline to ingest event files.</p>"
        _write(site / "events.html",
               _render("Events", empty_body, active="events"))
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
    # If only preview variants exist (no base), create the base from previews.
    event_names = list(by_event.keys())
    # First pass: group previews by their base name
    preview_groups: dict[str, list[str]] = defaultdict(list)
    for ev in event_names:
        base = _re.sub(r"\s+Preview\b.*", "", ev).strip()
        if base != ev:
            preview_groups[base].append(ev)
    # Second pass: merge
    for base, previews in preview_groups.items():
        if base in by_event:
            # Base exists — fold previews into it
            for pv in previews:
                if pv in by_event:
                    by_event[base].extend(by_event.pop(pv))
        else:
            # No base event — create it from all preview variants
            merged: list[dict] = []
            for pv in previews:
                if pv in by_event:
                    merged.extend(by_event.pop(pv))
            if merged:
                by_event[base] = merged
        # Also fix by_company references
        for comp in list(by_company.keys()):
            by_company[comp] = [a for a in by_company[comp] if a.get("event_name") not in previews]
            if base in by_event:
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

    # Determine upcoming events (date strictly > today — events starting today show coverage)
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

    # --- Build "By Event" tab content: clickable card list, sorted by latest date (newest first) ---
    def _event_max_date(ev_name: str) -> str:
        items = by_event[ev_name]
        dates = [a["date"] for a in items if a.get("date")]
        return max(dates) if dates else "0000-00-00"

    ev_cards = []
    # Separate major conference events from digest/daily roundups
    _digest_patterns = _re.compile(r"(News Digest|Last 24 Hours|Daily.*News|Weekly.*Roundup)", _re.IGNORECASE)
    major_events = [ev for ev in by_event.keys() if not _digest_patterns.search(ev)]
    digest_events = [ev for ev in by_event.keys() if _digest_patterns.search(ev)]

    # Sort both groups by date (newest first)
    major_events.sort(key=_event_max_date, reverse=True)
    digest_events.sort(key=_event_max_date, reverse=True)

    # --- Build comparison section for major conferences ---
    comparison_events = ["Microsoft Build 2026", "Google I/O 2026"]
    comparison_cards_html = ""
    found_comparisons = [ev for ev in comparison_events if ev in by_event]
    if len(found_comparisons) >= 2:
        comp_items = []
        for ev_name in found_comparisons:
            items = by_event[ev_name]
            slug = _safe_filename(ev_name)
            dates = [a["date"] for a in items if a.get("date")]
            ev_date = _format_date(max(dates)) if dates else ""
            themes = set()
            for a in items:
                themes.update(a.get("themes") or [])
            top_themes = sorted(themes)[:5]
            comp_items.append(
                f'<div class="compare-card">'
                f'<h3><a href="events/{slug}.html">{ev_name}</a></h3>'
                f'<div class="compare-stat"><span class="compare-num">{len(items)}</span> articles</div>'
                f'<div class="compare-stat">Latest: {ev_date}</div>'
                f'<div class="compare-themes">{", ".join(top_themes[:4])}</div>'
                f'</div>'
            )
        comparison_cards_html = (
            '<div class="compare-section">'
            '<h2>⚡ Major Conference Showdown</h2>'
            '<p class="compare-subtitle">Side-by-side coverage of the biggest AI conferences</p>'
            '<div class="compare-grid">' + "".join(comp_items) + '</div>'
            '<p class="compare-link-row"><a href="compare-build-io.html" class="compare-link">View full comparison →</a></p>'
            '</div>'
        )

    # --- WWDC analysis section (if analysis files exist) ---
    wwdc_analysis_html = ""
    wwdc_file = cfg.news_dir / "01_Apple_WWDC26_Executive_Summary.md"
    if wwdc_file.exists():
        wwdc_count = "Apple WWDC 2026" in by_event and len(by_event["Apple WWDC 2026"]) or 0
        # Count analysis docs
        wwdc_doc_count = sum(1 for f in [
            "01_Apple_WWDC26_Executive_Summary.md", "02_Apple_WWDC26_Siri_AI_and_Apple_Intelligence.md",
            "03_Apple_WWDC26_OS27_Platform_Updates.md", "04_Apple_WWDC26_Developer_Tools_and_Xcode.md",
            "05_Apple_WWDC26_App_Store_Developer_Business.md", "06_Apple_WWDC26_Child_Safety_Privacy_Regulatory.md",
            "07_Apple_WWDC26_Quick_Reference_Guide.md", "08_Apple_WWDC26_Day2_Executive_Summary.md",
            "09_Apple_WWDC26_Day2_Services_Intelligence_Deep_Dive.md", "10_Apple_WWDC26_Day2_Wallet_Maps_FindMy_iCloud.md",
            "11_Apple_WWDC26_Day2_Media_Fitness_Sports_Developer_Releases.md", "12_Apple_WWDC26_Day2_Quick_Reference_Guide.md",
        ] if (cfg.news_dir / f).exists())
        day_count = 1 + int((cfg.news_dir / "08_Apple_WWDC26_Day2_Executive_Summary.md").exists())
        wwdc_analysis_html = (
            '<div class="compare-section">'
            '<h2>🍎 Apple WWDC 2026 — Full Analysis</h2>'
            f'<p class="compare-subtitle">Multi-day deep-dive: Day 1 keynote &amp; platforms, Day 2 services &amp; intelligence</p>'
            '<div class="compare-grid">'
            '<div class="compare-card">'
            '<h3><a href="events/Apple-WWDC-2026.html">Apple WWDC 2026</a></h3>'
            f'<div class="compare-stat"><span class="compare-num">{wwdc_count}</span> news articles</div>'
            '<div class="compare-stat">Siri AI · Apple Intelligence · OS 27</div>'
            '<div class="compare-themes">Xcode 27, Privacy, App Store, Services</div>'
            '</div>'
            '<div class="compare-card">'
            '<h3><a href="wwdc-2026.html">Full WWDC Analysis</a></h3>'
            f'<div class="compare-stat"><span class="compare-num">{wwdc_doc_count}</span> deep-dive sections across <span class="compare-num">{day_count}</span> days</div>'
            '<div class="compare-stat">Day 1: Keynote · Day 2: Services</div>'
            '<div class="compare-themes">Models, platforms, tools, strategy, privacy, services</div>'
            '</div>'
            '</div>'
            '<p class="compare-link-row"><a href="wwdc-2026.html" class="compare-link">Read full WWDC 2026 analysis →</a></p>'
            '</div>'
        )

    for ev_name in major_events:
        items = by_event[ev_name]
        slug = _safe_filename(ev_name)
        # Mark upcoming with a badge (strictly future — not today)
        dates = [a["date"] for a in items if a.get("date")]
        is_upcoming = any(d > today for d in dates) if dates else False
        badge = '<span class="upcoming-badge">Upcoming</span>' if is_upcoming else ''
        ev_date = max(dates) if dates else ""
        date_label = f'<span class="entity-date">{_format_date(ev_date)}</span>' if ev_date else ''
        ev_cards.append(
            f'<a href="events/{slug}.html" class="card entity-link">'
            f'<strong>{ev_name}</strong>{badge}'
            f'{date_label}'
            f'<span class="entity-count">{len(items)} articles</span></a>'
        )

    # Add digest events in a collapsible section
    if digest_events:
        ev_cards.append('<details class="digest-events-section"><summary class="digest-toggle">📋 Daily Digests & Roundups ({} entries)</summary>'.format(len(digest_events)))
        for ev_name in digest_events:
            items = by_event[ev_name]
            slug = _safe_filename(ev_name)
            dates = [a["date"] for a in items if a.get("date")]
            ev_date = max(dates) if dates else ""
            date_label = f'<span class="entity-date">{_format_date(ev_date)}</span>' if ev_date else ''
            ev_cards.append(
                f'<a href="events/{slug}.html" class="card entity-link">'
                f'<strong>{ev_name}</strong>'
                f'{date_label}'
                f'<span class="entity-count">{len(items)} articles</span></a>'
            )
        ev_cards.append('</details>')

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
        + comparison_cards_html
        + wwdc_analysis_html
        + _fy27_events_section(cfg)
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

    events_body = _chat_highlight(
        "The best way to explore event coverage is AI Chat",
        "Ask about events — 'Summarize Microsoft Build' or 'What was announced at Google I/O?'",
    ) + tab_html
    _write(site / "events.html",
           _render("Events", events_body, active="events",
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
               _render(ev_name, body, rel="../", active="events",
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
    chat_highlight = _chat_highlight(
        "Try AI Chat — the fastest way to explore the news",
        'Ask questions in natural language and get answers grounded in the latest articles. "What happened with OpenAI this week?" or "Summarize Google I/O announcements"',
    )
    body = chat_highlight + _cards(snap, entity_files=entity_files)
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
    archive_body = _chat_highlight(
        "The best way to explore news across the timeline is AI Chat",
        "Ask about any date — 'What happened on May 30?' or 'Summarize last week's news'",
    ) + rows
    _write(site / "archive.html",
           _render("Timeline", archive_body, active="archive",
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
                        active="archive", subtitle=f"{len(items)} stories"))
        pages += 1

    # --- topics (exclude future-dated articles) ---
    by_topic: dict[str, list[dict]] = defaultdict(list)
    for a in canonical:
        if a["date"] and a["date"] > today_iso:
            continue
        for t in a["themes"] + a["cross_cutting"]:
            by_topic[t].append(a)

    # M&A & Investments hub: lives at top-level /investments.html (built by
    # _build_investments_pages below). The three sub-category slugs
    # (ma-activity, company-investments, infrastructure-investments) are NOT
    # rendered as /topics/*.html pages — their canonical home is under
    # /investments/. They are also filtered OUT of the /topics.html grid so
    # the Themes page shows only pure editorial themes.
    deals_by_slug = {slug: by_topic.get(slug, []) for slug in _DEALS_SUBCATEGORIES}
    deals_total = sum(len(v) for v in deals_by_slug.values())

    # Grid cards for /topics.html EXCLUDING the deals sub-slugs.
    topic_rows = '<div class="grid">' + "".join(
        f'<div class="card"><a class="t" href="topics/{t}.html">{_topic_label(t)}</a>'
        f'<div class="count">{len(items)}</div><div class="label">stories</div></div>'
        for t, items in sorted(by_topic.items(), key=lambda x: len(x[1]), reverse=True)
        if t not in _DEALS_SUBCATEGORIES
    ) + '</div>'
    topics_body = _chat_highlight(
        "The best way to explore news by theme is AI Chat",
        "Ask about topics — 'Latest model breakthroughs?' or 'Policy news this week?'",
    ) + topic_rows
    _write(site / "topics.html",
           _render("Themes", topics_body, active="topics",
                   subtitle="Browse AI news by theme"))
    pages += 1
    # Auto-generate one /topics/<slug>.html per remaining theme (deals slugs
    # go under /investments/ instead).
    for t, items in by_topic.items():
        if t in _DEALS_SUBCATEGORIES:
            continue
        body = _cards(items, rel="../", entity_files=entity_files)
        if len(items) > _PAGE_SIZE:
            body += paginate_js
        _write(site / "topics" / f"{t}.html",
               _render(_topic_label(t), body, rel="../", active="topics",
                       subtitle=f"{len(items)} stories"))
        pages += 1

    # /investments.html landing + /investments/<slug>[-by-company|-timeline].html
    if deals_total:
        pages += _build_investments_pages(site, deals_by_slug, entity_files, paginate_js)

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
    entities_body = _chat_highlight(
        "The best way to explore company news is AI Chat",
        "Ask about companies — 'What\'s new with NVIDIA?' or 'Latest OpenAI funding news'",
    ) + ent_rows
    _write(site / "entities.html",
           _render("Companies", entities_body, active="entities",
                   subtitle=f"{len(sorted_entities)} companies & organizations tracked"))
    pages += 1
    for e, items in by_entity.items():
        safe = _safe_filename(e)
        body = _cards(items, rel="../", entity_files=entity_files)
        if len(items) > _PAGE_SIZE:
            body += paginate_js
        _write(site / "entities" / f"{safe}.html",
               _render(f"{e}", body, rel="../", active="entities",
                       subtitle=f"{len(items)} stories mentioning {e}"))
        pages += 1

    # --- event pages (from DB-indexed event articles) ---
    events = _build_event_pages(cfg, site, canonical, entity_files)
    pages += events
    pages += _build_build_io_compare_page(cfg, site)
    pages += _build_wwdc_analysis_page(cfg, site)
    pages += _build_fy27_compare_page(cfg, site)
    pages += _build_fy27_strategy_pages(cfg, site)
    pages += _build_curated_analysis_pages(cfg, site, canonical)

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
    search_chat = (
        '<div class="search-chat-section">'
        "<h2>💬 Can't find what you're looking for? Ask AI</h2>"
        '<p class="search-chat-desc">The AI assistant searches through all articles and answers your question.</p>'
        '</div>'
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
</script>""" + search_chat + _chat_shell(
       "page",
       "AI Search Assistant",
       "Ask a question — the assistant searches all articles for relevant context.",
       compact=False,
   )
    _write(site / "search.html",
           _render("Search", search_body, active="search",
                   subtitle=f"Search across {len(search_index):,} articles"))
    pages += 1

    # --- AI chat page ---
    pages += build_chat_page(cfg, site, canonical, entity_files)

    # --- admin / provenance removed for public site ---

    return {"pages": pages, "articles": len(articles), "canonical": len(canonical), "site_dir": str(site)}
