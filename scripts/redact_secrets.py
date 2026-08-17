#!/usr/bin/env python3
"""CLI wrapper around the canonical HQE secret redaction engine.

The canonical implementation lives in ``runtime.redaction_engine`` and is
shared by the runtime evidence store. This script provides a command-line
interface for ad-hoc redaction of files or stdin.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow script to be run before the package is installed.
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from runtime.redaction_engine import RedactionEngine, redact_text


def redact_findings_file(file_path: Path) -> dict:
    """Redact secrets in a findings JSON file and return summary."""
    engine = RedactionEngine()
    with file_path.open("r", encoding="utf-8") as fh:
        raw_text = fh.read()
    redacted_text = engine.redact(raw_text, file_path=str(file_path))
    with file_path.open("w", encoding="utf-8") as fh:
        fh.write(redacted_text)
    return engine.summary()


def main() -> int:
    parser = argparse.ArgumentParser(description="Redact secrets from a string or file.")
    parser.add_argument("input", nargs="?", help="File to redact, or '-' for stdin")
    args = parser.parse_args()

    engine = RedactionEngine()

    if not args.input or args.input == "-":
        content = sys.stdin.read()
        file_path = "<stdin>"
    else:
        file_path = args.input
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

    redacted = engine.redact(content, file_path=file_path)
    print(redacted, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
