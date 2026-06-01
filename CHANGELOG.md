# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
