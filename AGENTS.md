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
pwsh ./scripts/run-pipeline.ps1 repair-urls    # a single stage
pwsh ./scripts/run-pipeline.ps1 clean-repairs  # revert low-quality URL repairs
```

```bash
./scripts/run-pipeline.sh                       # full daily refresh (run-all)
./scripts/run-pipeline.sh build-graph           # a single stage
```

Equivalent raw CLI (run from `source/`, UTF-8 console required for en-dashes):

```bash
python -X utf8 -m news_trends --root .. run-all
```

## Stages (run-all order)

`ingest → split → index → dedupe → build-graph → validate-urls → repair-urls → build-site → publish`

Additional maintenance stage: `clean-repairs` (offline revert of wrong URL repairs).

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

## Data sync

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
