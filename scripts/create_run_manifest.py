#!/usr/bin/env python3
"""Deterministic CLI tool for generating an HQE run manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add repo root to import runtime
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from runtime import FindingRegistry, RunManifestGenerator


def main() -> int:
    parser = argparse.ArgumentParser(description="Create HQE Run Manifest JSON.")
    parser.add_argument("--repo-path", default=".", help="Repository root path")
    parser.add_argument("--mode", default="audit", help="HQE execution mode")
    parser.add_argument("--findings-file", default=None, help="Optional findings JSON file")
    parser.add_argument(
        "--health-score",
        type=int,
        default=None,
        help="Health score (1-10). Defaults to coverage-aware calculation from the registry.",
    )
    parser.add_argument(
        "--best-effort",
        action="store_true",
        help="Continue with a warning when findings cannot be loaded/validated instead of failing.",
    )
    parser.add_argument("--output", default="HQE_RUN_MANIFEST.json", help="Output JSON path")
    args = parser.parse_args()

    registry = FindingRegistry(repo_root=args.repo_path)
    if args.findings_file:
        f_path = Path(args.findings_file).resolve()
        if not f_path.is_file():
            print(f"Error: findings file not found: {f_path}", file=sys.stderr)
            return 1
        try:
            with f_path.open("r", encoding="utf-8") as fh:
                raw_data = json.load(fh)
            raw_list = raw_data if isinstance(raw_data, list) else [raw_data]
            registry.load_many(raw_list)
        except Exception as exc:
            if args.best_effort:
                print(f"Warning: Failed to load findings from {f_path}: {exc}", file=sys.stderr)
            else:
                print(f"Error: Failed to load findings from {f_path}: {exc}", file=sys.stderr)
                return 1

    gen = RunManifestGenerator(repo_path=args.repo_path, mode=args.mode)
    if args.health_score is None:
        # Let the generator compute a truthful, coverage-aware score.
        manifest = gen.build_manifest(registry=registry)
    else:
        manifest = gen.build_manifest(
            registry=registry,
            health_score=args.health_score,
            health_reasons=[f"User-supplied health score ({args.health_score}/10)"],
        )
    out_file = gen.save_to_file(manifest, target_path=args.output)
    print(f"Successfully generated run manifest: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
