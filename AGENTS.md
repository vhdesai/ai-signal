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
