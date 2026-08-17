#!/usr/bin/env python3
"""Deterministic CLI tool for assembling all canonical HQE deliverables from findings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add repo root to import runtime
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from runtime import FindingRegistry, ArtifactPipeline, SessionManager


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble canonical HQE audit deliverables.")
    parser.add_argument("findings_file", help="Path to findings JSON file")
    parser.add_argument("--output-dir", default="artifacts", help="Target directory for deliverables")
    parser.add_argument("--session-file", default=None, help="Optional session log JSON file")
    parser.add_argument("--repo-name", default="repository", help="Repository name for headers")
    args = parser.parse_args()

    findings_path = Path(args.findings_file).resolve()
    if not findings_path.is_file():
        print(f"Error: findings file not found: {findings_path}", file=sys.stderr)
        return 1

    try:
        with findings_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        print(f"Error reading findings JSON: {exc}", file=sys.stderr)
        return 1

    raw_findings = data if isinstance(data, list) else [data]

    registry = FindingRegistry()
    registry.load_many(raw_findings)

    session = None
    if args.session_file:
        s_path = Path(args.session_file).resolve()
        if not s_path.is_file():
            print(f"Error: session file not found: {s_path}", file=sys.stderr)
            return 1
        try:
            session = SessionManager.load_from_file(s_path)
        except Exception as exc:
            print(f"Error: Failed to load session file {s_path}: {exc}", file=sys.stderr)
            return 1

    pipeline = ArtifactPipeline(registry, session=session, repo_name=args.repo_name)
    generated = pipeline.build_all_artifacts(output_dir=args.output_dir)

    print(f"Successfully assembled {len(generated)} canonical deliverables in '{args.output_dir}':")
    for name, path in generated.items():
        print(f"  - {name} -> {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
