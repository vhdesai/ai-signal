# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] — 2026-06-09

### Added

- **Publication email merger** — New `merge_publications.py` script that extracts articles from 10 publication email export files (Berkeley RDI, Business Insider, CIO Dive, DealBook, PitchBook, The Information, The Tactical Allocation Letter, Wall Street Journal, WSJ Pro CyberSecurity, WSJ Wealth Advisor) and merges them into date-based digest files
- 53 existing digests enriched with publication newsletter sources
- 27 new date-based digest files created from publication-only dates (Mar 8–May 30)
- Total digest coverage expanded from 190 to 217 files (80 unique dates across publications)
- Pipeline rebuilt: 217 digests → 2302 articles → 1944 canonical → 141 pages

### Preserved

- `compare-build-io.html` URL unchanged at `https://ai-signal-72f.pages.dev/compare-build-io`
- `wwdc-2026.html` WWDC 2026 analysis page
- All chat features, banners, and event pages

## [0.3.0] — 2026-06-08

### Added

- **Apple WWDC 2026 analysis page** — 7-section tabbed analysis (Executive Summary, Siri AI, OS 27, etc.)
- WWDC analysis section on Events page with cards linking to news and analysis
- Pipeline rebuilt with 227 digests

## [0.2.0] — 2026-06-07

### Added

- **AI Chat** — RAG-enhanced chat with Cloudflare Worker proxy to OpenRouter API
- Chat bubble on all pages with page-specific starter prompts
- Dedicated chat page and embedded chat on search page
- Chat promotion banners on all main pages
- **Build vs IO comparison page** — Tabbed view of 6 comparison markdown files
- **Events overhaul** — Events sorted by date, preview merging, digest collapsing
- Date-based RAG search with `normalizeDate()` for natural language date queries
- 4-model fallback chain on 429 rate limit errors

## [0.1.0] — 2026-06-01

### Added

- Full pipeline: `ingest → split → index → dedupe → build-graph → validate-urls → repair-urls → build-site`
- Static site generation with Daily Brief, Timeline, Themes, Players, and Search pages
- SQLite + FTS5 article indexing
- ChromaDB semantic embeddings for deduplication and related-story linking
- URL validation (HTTP HEAD/GET) and repair (DuckDuckGo web search)
- Obsidian-compatible knowledge graph with wikilinks and hub pages
- Client-side full-text search with inline JSON data
- GitHub Actions workflow for automatic Cloudflare Pages deployment
- Data sync scripts (`sync-data.ps1` / `sync-data.sh`) for bidirectional data portability
- Cross-platform setup and run scripts (PowerShell + Bash)
- YAML-based configuration for topics, entities, thresholds, and publishing

### Infrastructure

- Hosting: Cloudflare Pages (free tier, unlimited bandwidth)
- CI/CD: GitHub Actions on push to `main`
- Package: Python 3.11+, installable via `pip install -e ./source`
