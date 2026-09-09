# Agent orchestration guide

This repository is orchestrated by **GitHub Copilot CLI** or **Clawpilot** (multi-agent).
Deployment to Cloudflare Pages is automated via GitHub Actions on push to `main`.

## One-time setup

Run once to create a virtual environment, install the pipeline, pre-cache the embedding
model, and smoke-test the CLI:

```pwsh
# Windows / PowerShell
pwsh ./scripts/setup.ps1
```

```bash
# Linux / macOS
./scripts/setup.sh
```

## Running the pipeline

```pwsh
pwsh ./scripts/run-pipeline.ps1                # full daily refresh (run-all)
pwsh ./scripts/run-pipeline.ps1 run-daily      # fast incremental daily refresh
pwsh ./scripts/run-pipeline.ps1 repair-urls    # a single stage
pwsh ./scripts/run-pipeline.ps1 clean-repairs  # revert low-quality URL repairs
```

```bash
./scripts/run-pipeline.sh                       # full daily refresh (run-all)
./scripts/run-pipeline.sh run-daily             # fast incremental daily refresh
./scripts/run-pipeline.sh build-graph           # a single stage
```

Equivalent raw CLI (run from `source/`, UTF-8 console required for en-dashes):

```bash
python -X utf8 -m news_trends --root .. run-all       # full rebuild
python -X utf8 -m news_trends --root .. run-daily     # incremental daily
```

## Stages (run-all order)

`ingest → split → index → dedupe → build-graph → validate-urls → repair-urls → build-site → publish`

Additional maintenance stage: `clean-repairs` (offline revert of wrong URL repairs).

## Fast daily rebuild (`run-daily`)

`run-daily` runs the same stages as `run-all` but with two important
optimizations for a fast, low-cost daily refresh:

1. **URL repair scoped to today's articles.** `repair-urls` defaults to
   `--repair-since today` and a 10-minute time budget instead of 60 minutes
   (both overridable). Older broken URLs are left for the next full `run-all`.
2. **Incremental site build.** The last stage is `build-site-daily` instead
   of `build-site`. It compares the current corpus state against
   `site/.build-manifest.json` and only re-writes pages whose content
   actually changed:
   * Root-level pages (index, investments, topics, entities, archive,
     sitemap, chat, about) are always rebuilt.
   * Snapshot page for each date whose articles changed.
   * Entity page for each entity mentioned by a changed article.
   * Topic / theme page for each theme touched by a changed article.
   * All 9 Investments sub-pages if any deal-classified article changed.
   * Standalone Analysis-tag article pages if that article changed.

   It **automatically falls back to a full `build-site`** when:
   * The manifest is missing (first daily run).
   * The manifest is corrupt / unreadable.
   * `site.py`, `split.py`, or `graph.py` has changed since the manifest
     was written (SHA of these files is stored in the manifest).
   * Any article was removed from the canonical set.

   After every run (full or incremental) a fresh manifest is written.

**Typical daily-run time:** ~30 min (vs. ~90 min for `run-all`).

## URL repair (parallel, time-boxed, resumable)

`repair-urls` searches the live web for broken/missing article links. It runs
concurrent search/fetch workers and is capped by a time box so a rebuild always
finishes in bounded time. Whatever it doesn't reach is durably saved and picked
up on the next run (already-repaired links are skipped).

- **Default time box: 60 minutes.** Configure it (both as a standalone stage and
  inside `run-all`):

  ```pwsh
  pwsh ./scripts/run-pipeline.ps1 -RepairTimeout 7200   # 2-hour time box
  pwsh ./scripts/run-pipeline.ps1 -RepairTimeout 0      # disable the time box
  pwsh ./scripts/run-pipeline.ps1 -RepairWorkers 16     # 16 concurrent workers
  ```

  ```bash
  REPAIR_TIMEOUT=7200 ./scripts/run-pipeline.sh         # 2-hour time box
  REPAIR_TIMEOUT=0 ./scripts/run-pipeline.sh            # disable the time box
  REPAIR_WORKERS=16 ./scripts/run-pipeline.sh           # 16 concurrent workers
  ```

  Raw CLI: `--repair-timeout <seconds>` (0 disables), `--repair-workers <n>`,
  `--repair-stop-file <path>`.

- **Graceful early stop:** create the sentinel file `indexes/repair.stop` (or the
  path given to `--repair-stop-file`) to make the stage finish its in-flight work
  and exit before the time box elapses.
- **Live progress:** a rolling snapshot is written to `indexes/repair-status.json`
  (state, attempted, repaired, unresolved, deferred, elapsed). Both files are
  git-ignored.

## Content quality (substantial articles only)

Every published article must carry **substantial information**; fragments and
snippet-only stubs are excluded automatically during the `split` stage and never
reach the site:

- Articles below `_MIN_BODY_WORDS` (default **30 words ≈ 4–5 lines**) are dropped
  (`skipped_thin_articles`). This bar applies to **all** article paths —
  daily-digest, narrative, **and event-file** articles.
- Mis-parsed digest mastheads (`source` starting "Compiled"/"Prepared for") and
  `*_Publication-Sources.md` files are dropped.
- Source/URL citation lists are preserved; only pure editorial-process notes are
  stripped.

To tune the threshold, edit `_MIN_BODY_WORDS` in `source/news_trends/split.py`.
See `ARCHITECTURE.md` → "Split → Substantial-content requirement" for details.
After any rebuild, verify no thin fragments leaked (spot-check the newest
`site/snapshots/*.html`).

## Merging missing source markdowns before a rebuild

New daily digests are authored in the internal Obsidian pipeline first. Before a
full rebuild, copy any markdowns present in the Obsidian `news/` folder but
missing from this repo's `news/` folder, then re-ingest:

```pwsh
$eh = 'news'
$ob = '..\Obsidian\news'   # adjust to the Obsidian repo's news path
$have = (Get-ChildItem $eh -Filter *.md).Name
Get-ChildItem $ob -Filter *.md |
  Where-Object { $_.Name -notin $have } |
  ForEach-Object { Copy-Item $_.FullName (Join-Path $eh $_.Name) -Force }
```

`ingest` then picks up the newly copied files (hash-based, idempotent). Multiple
digests per day are fine — `dedupe` collapses them.



Copy pipeline data (SQLite DB + ChromaDB) from the internal Obsidian pipeline:

```pwsh
pwsh ./scripts/sync-data.ps1                    # Obsidian → ext-host
pwsh ./scripts/sync-data.ps1 -Reverse           # ext-host → Obsidian
```

```bash
./scripts/sync-data.sh                          # Obsidian → ext-host
./scripts/sync-data.sh --reverse                # ext-host → Obsidian
```

## Deployment

The site deploys automatically to Cloudflare Pages when `site/` contents are pushed
to `main`. Manual deployment:

```bash
npx wrangler pages deploy site --project-name=ai-signal
```

Required GitHub secrets:
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

## Daily schedule

Target a daily 10:00 AM Pacific run of `run-all`. Schedule it with the orchestrator's own
scheduler (e.g. a Copilot CLI scheduled prompt or a Clawpilot job), the OS scheduler
(Task Scheduler / `cron`).

## Notes

- Always run pipeline commands from `source/` with `python -X utf8` (the Windows cp1252
  console cannot print en-dashes otherwise).
- Raw news/digest markdown is intentionally git-ignored and never published.
