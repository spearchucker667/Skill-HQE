#!/usr/bin/env python3
"""Regex-based secret redactor for HQE findings, logs, and artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PATTERNS = [
    ("AWS_ACCESS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS_SECRET_KEY", re.compile(r"\b[0-9a-zA-Z/+]{40}\b")),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("SSH_KEY", re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]*?-----END OPENSSH PRIVATE KEY-----")),
    ("SLACK_TOKEN", re.compile(r"xox[baprs]-[0-9a-zA-Z-]+")),
    ("GITHUB_TOKEN", re.compile(r"gh[pousr]_[0-9a-zA-Z_]{36,}")),
    ("GITHUB_PAT", re.compile(r"github_pat_[0-9a-zA-Z_]+")),
    ("GOOGLE_API_KEY", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("SECRET", re.compile(r'(?i)(secret|api[_-]?key|token)\s*=\s*["\']?[a-zA-Z0-9_-]{16,64}["\']?')),
    ("PASSWORD", re.compile(r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{8,128}["\']')),
    ("API_KEY", re.compile(r'(?i)api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9_-]{16,64}["\']')),
    ("BEARER_TOKEN", re.compile(r'(?i)bearer\s+[a-zA-Z0-9_\-\.=]{20,}')),
]


class RedactionEngine:
    def __init__(self):
        self.counters: dict[str, int] = {}
        self.log_entries: list[dict] = []

    def redact(self, content: str, file_path: str = "<stdin>") -> str:
        result = content
        for secret_type, pattern in PATTERNS:
            def repl(m: re.Match, stype: str = secret_type) -> str:
                count = self.counters.get(stype, 0) + 1
                self.counters[stype] = count
                replacement = f"REDACTED_{stype}_{count}"
                self.log_entries.append({
                    "file": file_path,
                    "secret_type": stype,
                    "replacement": replacement
                })
                return replacement

            result = pattern.sub(repl, result)
        return result

    def summary(self) -> dict:
        total = sum(self.counters.values())
        return {
            "total_redactions": total,
            "by_type": dict(self.counters),
            "entries": list(self.log_entries)
        }

    def reset(self) -> None:
        self.counters.clear()
        self.log_entries.clear()


def redact_text(content: str) -> tuple[str, int]:
    """Convenience helper to redact a string and return (redacted_str, total_count)."""
    engine = RedactionEngine()
    redacted = engine.redact(content)
    return redacted, engine.summary()["total_redactions"]


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
