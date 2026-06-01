# 📡 AI Signal — Daily Intelligence

A daily AI news trends aggregator that generates a static website from markdown news digests.
Powered by NLP, semantic search (ChromaDB), and automated URL validation.

**Live site:** Deployed on [Cloudflare Pages](https://ai-signal.pages.dev)

## Features

- 📰 **Daily Brief** — Today's top AI stories at a glance
- 📅 **Timeline** — Browse historical snapshots by date
- 🏷️ **Themes** — Stories grouped by topic (Infrastructure, Policy, Corporate Moves, etc.)
- 🏢 **Players** — Track companies & organizations across stories
- 🔍 **Search** — Full-text client-side search across all articles

## Quick Start

### 1. Setup

```bash
# Clone the repo
git clone https://github.com/vhdesai/ai-signal.git
cd ai-signal

# One-time setup (creates venv, installs deps, caches embedding model)
pwsh ./scripts/setup.ps1       # Windows
./scripts/setup.sh             # Linux / macOS
```

### 2. Add News Digests

Drop markdown digest files into the `news/` directory.

### 3. Run the Pipeline

```bash
pwsh ./scripts/run-pipeline.ps1    # Windows
./scripts/run-pipeline.sh          # Linux / macOS
```

This runs the full pipeline: `ingest → split → index → dedupe → build-graph → validate-urls → repair-urls → build-site`

### 4. View the Site

Open `site/index.html` in a browser, or push to `main` to auto-deploy to Cloudflare Pages.

## Data Sync

If you also run the internal Obsidian pipeline, you can sync processed data:

```bash
# Copy SQLite DB + ChromaDB from Obsidian → ext-host
pwsh ./scripts/sync-data.ps1

# Reverse (ext-host → Obsidian)
pwsh ./scripts/sync-data.ps1 -Reverse
```

## Deployment (Cloudflare Pages)

### Initial Setup

1. Create a free [Cloudflare](https://dash.cloudflare.com) account
2. Install Wrangler: `npm install -g wrangler`
3. Create a Pages project: `wrangler pages project create ai-signal`
4. Add GitHub repo secrets:
   - `CLOUDFLARE_API_TOKEN` — API token with Pages permissions
   - `CLOUDFLARE_ACCOUNT_ID` — Your Cloudflare account ID

### Auto-Deploy

Every push to `main` that changes `site/` triggers automatic deployment via GitHub Actions.

### Manual Deploy

```bash
npx wrangler pages deploy site --project-name=ai-signal
```

## Project Structure

```
├── .github/workflows/    # CI/CD (Cloudflare Pages deploy)
├── scripts/              # Setup, run, and sync scripts
├── source/               # Python pipeline package + config
│   ├── config/           # YAML configuration
│   └── news_trends/      # Pipeline stages (ingest, index, dedupe, etc.)
├── news/                 # Raw markdown digests (git-ignored)
├── articles/             # Generated article notes
├── indexes/              # SQLite DB + ChromaDB
├── hubs/                 # Entity/topic hub pages
└── site/                 # Generated static HTML (deployed)
```

## Tech Stack

- **Python 3.11+** — Pipeline
- **SQLite + FTS5** — Article indexing and full-text search
- **ChromaDB** — Semantic embeddings and deduplication
- **Jinja2** — HTML template rendering
- **Cloudflare Pages** — Hosting (free tier, unlimited bandwidth)
- **GitHub Actions** — CI/CD

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — System design, data flow, and pipeline stages
- [CHANGELOG.md](CHANGELOG.md) — Version history and notable changes
- [CONTRIBUTING.md](CONTRIBUTING.md) — How to contribute
- [SECURITY.md](SECURITY.md) — Security policy and vulnerability reporting

## License

[MIT](LICENSE.md) — See [LICENSE.md](LICENSE.md) for details.
