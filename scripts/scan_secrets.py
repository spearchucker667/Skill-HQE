#!/usr/bin/env python3
"""Repository secret scanner for CI and local validation.

Reports potential secrets as ``path:line:TYPE`` without printing the secret
itself, so CI logs do not leak credentials.  Supports path-based allowlists for
test fixtures and documentation examples.
"""

from __future__ import annotations

import argparse
import mimetypes
import re
import sys
from pathlib import Path

# Allow the script to be invoked from the repository root or scripts/ directory.
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent))

# Conservative, high-confidence patterns for CI secret scanning.
# Broad generic patterns (e.g. "password = ...") are intentionally omitted
# because they produce excessive false positives in documentation and tests.
PATTERNS = [
    ("AWS_ACCESS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("OPENSSH_PRIVATE_KEY", re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]*?-----END OPENSSH PRIVATE KEY-----")),
    ("SLACK_TOKEN", re.compile(r"xox[baprs]-[0-9a-zA-Z-]+")),
    ("GITHUB_TOKEN", re.compile(r"gh[pousr]_[0-9a-zA-Z_]{36,}")),
    ("GITHUB_PAT", re.compile(r"github_pat_[0-9a-zA-Z_]+")),
    ("GOOGLE_API_KEY", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("OPENAI_API_KEY", re.compile(r"sk-[a-zA-Z0-9]{32,}")),
]

DEFAULT_SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    ".tox",
    "dist",
    "build",
}

DEFAULT_SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf", ".zip", ".tar",
    ".gz", ".bz2", ".7z", ".mp4", ".mp3", ".mov", ".woff", ".woff2", ".ttf",
    ".otf", ".eot", ".exe", ".dll", ".so", ".dylib", ".bin",
}


def _looks_binary(file_path: Path) -> bool:
    """Return True if the file is likely binary based on extension or MIME type."""
    suffix = file_path.suffix.lower()
    if suffix in DEFAULT_SKIP_EXTENSIONS:
        return True
    mime, _ = mimetypes.guess_type(str(file_path))
    if mime and not mime.startswith(("text/", "application/json", "application/xml")):
        return True
    return False


def _has_binary_content(file_path: Path, sample_size: int = 8192) -> bool:
    """Check the file head for NUL bytes as a binary-content heuristic."""
    try:
        with file_path.open("rb") as fh:
            chunk = fh.read(sample_size)
            return b"\x00" in chunk
    except OSError:
        return True


def _load_allowlist(allowlist_path: Path | None) -> list[str]:
    """Load newline-separated allowlist glob/path fragments."""
    if allowlist_path is None or not allowlist_path.is_file():
        return []
    text = allowlist_path.read_text(encoding="utf-8", errors="replace")
    return [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]


def _is_allowed(path: Path, repo_root: Path, allowlist: list[str]) -> bool:
    """Return True if a path matches an allowlist entry."""
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        rel = path
    rel_str = str(rel).replace("\\", "/")
    for entry in allowlist:
        # Exact suffix match or substring match for simple allowlisting.
        entry = entry.replace("\\", "/")
        if rel_str == entry or rel_str.endswith(entry) or entry in rel_str:
            return True
    return False


def scan_file(file_path: Path) -> list[tuple[int, str]]:
    """Scan a single text file and return list of (line_number, secret_type)."""
    matches: list[tuple[int, str]] = []
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return matches

    for line_no, line in enumerate(text.splitlines(), start=1):
        for secret_type, pattern in PATTERNS:
            if pattern.search(line):
                matches.append((line_no, secret_type))
                break  # one type per line is enough for reporting
    return matches


def scan_directory(
    repo_root: Path,
    *,
    allowlist: list[str] | None = None,
    skip_dirs: set[str] | None = None,
) -> list[tuple[Path, int, str]]:
    """Scan repository and return findings as (path, line, type) tuples."""
    skip_dirs = skip_dirs or DEFAULT_SKIP_DIRS
    allowlist = allowlist or []
    findings: list[tuple[Path, int, str]] = []

    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if _looks_binary(path) or _has_binary_content(path):
            continue
        if _is_allowed(path, repo_root, allowlist):
            continue
        for line_no, secret_type in scan_file(path):
            findings.append((path, line_no, secret_type))

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan a repository for potential secrets.")
    parser.add_argument("path", type=Path, help="Repository root to scan")
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=None,
        help="File containing path fragments to exclude (one per line)",
    )
    parser.add_argument(
        "--skip-dirs",
        default=",".join(DEFAULT_SKIP_DIRS),
        help="Comma-separated directory names to skip",
    )
    args = parser.parse_args(argv)

    repo_root = args.path.resolve()
    allowlist = _load_allowlist(args.allowlist)
    skip_dirs = set(args.skip_dirs.split(",")) if args.skip_dirs else DEFAULT_SKIP_DIRS

    findings = scan_directory(repo_root, allowlist=allowlist, skip_dirs=skip_dirs)

    if not findings:
        print("No potential secrets detected.")
        return 0

    print("Potential secret(s) detected (path:line:TYPE):")
    for path, line_no, secret_type in findings:
        try:
            rel = path.relative_to(repo_root)
        except ValueError:
            rel = path
        print(f"{rel}:{line_no}:{secret_type}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
