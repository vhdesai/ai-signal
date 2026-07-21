# Architecture

## Overview

AI Signal is a Python-based pipeline that transforms daily AI news markdown digests into
a searchable, categorized static website. The pipeline runs as a sequence of idempotent
stages, each reading from and writing to shared artifacts (markdown files, SQLite database,
and ChromaDB vector store).

## System Diagram

```
news/*.md (input)
    │
    ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Ingest   │───▶│  Split   │───▶│  Index   │───▶│  Dedupe  │
│           │    │          │    │          │    │          │
│ scan news │    │ parse    │    │ SQLite   │    │ hash +   │
│ archive   │    │ articles │    │ FTS5     │    │ semantic │
│ raw copy  │    │ write md │    │ ChromaDB │    │ cluster  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
    ┌─────────────────────────────────────────────────┘
    ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Build   │───▶│ Validate │───▶│  Repair  │───▶│  Build   │
│  Graph   │    │  URLs    │    │  URLs    │    │  Site    │
│          │    │          │    │          │    │          │
│ wikilinks│    │ HTTP     │    │ DDG      │    │ Jinja2   │
│ hub pages│    │ HEAD/GET │    │ search   │    │ static   │
│ _Index   │    │ check    │    │ validate │    │ HTML     │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                                                      ▼
                                               site/ (output)
                                                      │
                                                      ▼
                                            Cloudflare Pages
```

## Pipeline Stages

### 1. Ingest (`ingest.py`)

- Scans `news/*.md` for new or changed markdown digest files
- Computes SHA-256 file hashes for change detection
- Archives raw digests to `digests/raw/` for reproducibility
- Records digest metadata in the `digests` SQLite table

### 2. Split (`split.py`)

- Parses each archived digest into individual article records
- Handles two observed digest formats (tag-line and acronym-code layouts)
- Extracts: title, source, date, summary, URL, tags
- Classifies articles by entity and topic using keyword matching against `config/entities.yaml` and `config/topics.yaml`
- Writes each article as a YAML-frontmatter markdown file in `articles/YYYY/MM/`
- Computes content hashes and normalized title hashes for deduplication

### 3. Index (`index.py`)

- Reads all article markdown files from `articles/`
- Populates the `articles` SQLite table and `articles_fts` FTS5 virtual table
- Builds ChromaDB embeddings using `sentence-transformers` (BAAI/bge-small-en-v1.5)
- Embeddings are cosine-similarity vectors combining title + source + summary

### 4. Dedupe (`dedupe.py`)

- **Exact deduplication:** Groups articles by (date, normalized_title_hash) — identical titles on the same day are marked as duplicates
- **Semantic deduplication:** Uses ChromaDB cosine similarity to find same-day articles above the duplicate threshold (default 0.90)
- **Related stories:** Articles above the near-duplicate threshold (default 0.70) are linked as related
- Updates both markdown frontmatter and SQLite with dedupe status

### 5. Build Graph (`graph.py`)

- Appends Obsidian-compatible `[[wikilinks]]` to each article note inside a delimited `<!-- graph:start/end -->` block
- Generates hub/MOC (Map of Content) pages under `hubs/entities/` and `hubs/topics/`
- Writes `_Index.md` as the vault-level entry point

### 6. Validate URLs (`urls.py`)

- Checks each article's canonical URL via HTTP HEAD/GET requests using `httpx`
- Marks URLs as `ok`, `broken`, or `missing`
- Queues broken URLs for review

### 7. Repair URLs (`urls.py`)

- For broken/missing URLs, searches the live web (ddgs) for the article title + source
- Validates candidates against a relevance gate (blocked domains, homepage detection, title token overlap)
- Self-heals: reverts previously-written low-quality repairs
- Deliberately conservative to avoid incorrect URL assignments
- **Parallel:** runs concurrent search/fetch workers (`--repair-workers`, default 10); all SQLite writes stay on a single main thread
- **Time-boxed:** the network phase is capped (`--repair-timeout`, default 3600 s / 60 min; `0` disables). On timeout it drains in-flight work and exits
- **Gracefully interruptible:** an operator can create the `indexes/repair.stop` sentinel (or `--repair-stop-file`) to stop early
- **Resumable:** progress is committed incrementally and a rolling snapshot is written to `indexes/repair-status.json`; deferred URLs are retried on the next run

> **Network-blocked domains:** Yandex and Softonic are unreachable behind some
> corporate networks (Microsoft IT controls). They are skipped during validation
> (kept as-is, not marked broken) and never accepted as repaired canonical URLs.

### 8. Build Site (`site.py`)

Generates the static HTML website in `site/` with these pages:

| Page | Description |
|------|-------------|
| `index.html` | Daily Brief — latest snapshot with story cards |
| `archive.html` | Timeline — grid of date-linked snapshots |
| `snapshots/{date}.html` | Per-date story lists |
| `topics.html` | Theme index (grid cards) |
| `topics/{slug}.html` | Per-theme story lists |
| `entities.html` | Player index (A–Z letter nav) |
| `entities/{name}.html` | Per-entity story lists |
| `search.html` | Client-side full-text search (inline JSON) |
| `chat.html` | Conversational assistant grounded in article summaries |
| `articles.json` | Search index data |

The chat page (`chat.html`, generated from the template in `chat.py`) is a
client-side retrieval-augmented assistant. On each question it ranks the loaded
`articles.json` by keyword/date relevance and injects only the **top few** article
summaries plus a short slice of recent conversation into the request sent to a
free hosted model (via a Cloudflare Worker proxy). To keep the models responsive,
the request payload is deliberately bounded by tunable constants in `chat.py`:

| Constant | Purpose |
|----------|---------|
| `MAX_CONTEXT_ARTICLES` | Number of most-relevant articles injected as context |
| `MAX_SUMMARY_CHARS` | Max characters of each article summary sent |
| `MAX_HISTORY_MESSAGES` | Trailing user/assistant messages replayed per turn |

## Data Stores

### SQLite Database (`indexes/news_trends.db`)

| Table | Purpose |
|-------|---------|
| `digests` | Tracks ingested digest files and their hashes |
| `articles` | Full article metadata (title, date, source, URLs, dedupe status, etc.) |
| `articles_fts` | FTS5 full-text search index (title, summary, source, entities, themes) |
| `url_status` | URL validation and repair history |
| `review_queue` | Items flagged for manual review |
| `run_history` | Pipeline run logs |

### ChromaDB (`indexes/chroma/`)

- Collection: `articles`
- Embedding model: `BAAI/bge-small-en-v1.5` (384-dim, cosine similarity)
- Used for semantic deduplication and related-story linking

### Article Markdown Files (`articles/YYYY/MM/*.md`)

- YAML frontmatter with full metadata
- Markdown body with article summary
- Optional `<!-- graph:start/end -->` block with wikilinks

## Configuration (`source/config/`)

| File | Purpose |
|------|---------|
| `sources.yaml` | Directory paths (news, articles, site, indexes) |
| `topics.yaml` | Topic taxonomy and labels |
| `entities.yaml` | Tracked companies/organizations with keywords |
| `dedupe-thresholds.yaml` | Duplicate and near-duplicate similarity thresholds |
| `embeddings.yaml` | Embedding model selection |
| `publishing.yaml` | Repository URL, audience, schedule |
| `retention.yaml` | Snapshot retention policy |

## Deployment

```
git push origin main
        │
        ▼
GitHub Actions (.github/workflows/deploy.yml)
        │
        ▼
Cloudflare Pages (site/ directory)
        │
        ▼
https://ai-signal.pages.dev
```

- Triggered on push to `main` when `site/**` files change
- Also supports `workflow_dispatch` for manual deploys
- Uses `cloudflare/wrangler-action@v3`

## Data Portability

The SQLite database and ChromaDB directory use identical schemas across pipeline
instances. The `sync-data` scripts enable bidirectional copying between environments:

```
Obsidian (internal)  ◄──sync-data──►  ext-host (public)
```

## Key Design Decisions

1. **Static-only site:** No server-side rendering. Search uses inline JSON for `file://` protocol compatibility.
2. **Idempotent stages:** Every stage can be re-run safely; state is reconciled, not appended.
3. **Conservative URL repair:** Candidates must pass domain, homepage, and title-overlap relevance gates to prevent incorrect links.
4. **Graceful degradation:** If ChromaDB/embeddings fail, the pipeline continues with keyword-only indexing.
5. **Portable data:** SQLite + ChromaDB files can be copied between pipeline instances.
6. **Bounded chat context:** The chat assistant retrieves only the top-ranked article summaries and a short conversation window (see `chat.py` constants), keeping request payloads small so hosted models stay responsive rather than stalling on oversized context.
