"""Command-line entry point for the News Trends pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import db
from .config import Config
from .ingest import ingest
from .split import run_split
from .index import run_index
from .dedupe import run_dedupe
from .graph import run_build_graph
from .urls import run_validate_urls, run_repair_urls, run_clean_repairs
from .site import run_build_site, run_review_submissions
from .runlog import write_run

DEFAULT_OBSIDIAN_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="news-trends",
        description="Run the News Trends knowledge-base and static publishing pipeline.",
    )
    parser.add_argument(
        "--root", type=Path, default=DEFAULT_OBSIDIAN_ROOT,
        help="Obsidian root containing news, source, indexes, and site directories.",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Cap the number of URLs processed by validate-urls/repair-urls.",
    )
    parser.add_argument(
        "--no-embeddings", action="store_true",
        help="Skip Chroma/semantic embedding work in the index stage.",
    )

    subcommands = parser.add_subparsers(dest="command", required=True)
    for command in (
        "ingest", "normalize", "split", "index", "dedupe", "build-graph",
        "validate-urls", "repair-urls", "clean-repairs", "build-site",
        "review-submissions", "publish", "run-all",
    ):
        subcommands.add_parser(command)
    return parser


def run_stage(command: str, cfg: Config, args: argparse.Namespace) -> dict:
    if command == "ingest":
        return ingest(cfg)
    if command in ("normalize", "split"):
        # normalization is applied inline during split (digest -> article notes)
        return run_split(cfg)
    if command == "index":
        return run_index(cfg, with_embeddings=not args.no_embeddings)
    if command == "dedupe":
        return run_dedupe(cfg)
    if command == "build-graph":
        return run_build_graph(cfg)
    if command == "validate-urls":
        return run_validate_urls(cfg, limit=args.limit)
    if command == "repair-urls":
        return run_repair_urls(cfg, limit=args.limit)
    if command == "clean-repairs":
        return run_clean_repairs(cfg)
    if command == "build-site":
        return run_build_site(cfg)
    if command == "review-submissions":
        return run_review_submissions(cfg)
    if command == "publish":
        # local-only build; publishing is an intentional no-op / dry-run
        return {"status": "dry-run", "note": "site/ generated locally; no remote publish configured"}
    return {"status": "unknown-command", "command": command}


def main() -> None:
    args = build_parser().parse_args()
    cfg = Config.load(args.root)
    started = db.now_iso()

    if args.command == "run-all":
        sequence = [
            "ingest", "split", "index", "dedupe", "build-graph",
            "validate-urls", "repair-urls", "build-site", "publish",
        ]
        stages = {stage: run_stage(stage, cfg, args) for stage in sequence}
        result = {"command": "run-all", "stages": stages}
        result["run_log"] = write_run(cfg, started, result)
    else:
        result = {"command": args.command, "result": run_stage(args.command, cfg, args)}
        result["run_log"] = write_run(cfg, started, result)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
