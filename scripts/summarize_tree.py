#!/usr/bin/env python3
"""Tree and subsystem summarization utility for HQE."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

IGNORED_DIRS = {
    ".git", "node_modules", "target", "dist", "build", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".idea", ".vscode", "__MACOSX"
}


def build_tree_summary(root_path: Path, max_depth: int = 3) -> dict:
    """Build structured subsystem and directory summary."""
    root = root_path.resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")

    subsystems: dict[str, dict] = {}
    total_files = 0
    total_dirs = 0

    for current_root, dirs, files in os.walk(root):
        rel_path = Path(current_root).relative_to(root)
        depth = len(rel_path.parts)

        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        if depth == 0:
            subsystems["."] = {
                "path": ".",
                "subdirectories": list(dirs),
                "direct_files": len(files),
                "key_files": [f for f in files if f in ("README.md", "Cargo.toml", "package.json", "pyproject.toml", "go.mod", "Makefile", "SKILL.md")]
            }
        elif depth <= max_depth:
            subsystem_name = str(rel_path).replace("\\", "/")
            total_dirs += 1
            total_files += len(files)
            exts: dict[str, int] = {}
            for f in files:
                ext = Path(f).suffix.lower() or "<no_ext>"
                exts[ext] = exts.get(ext, 0) + 1

            subsystems[subsystem_name] = {
                "path": subsystem_name,
                "depth": depth,
                "subdirectories": list(dirs),
                "file_count": len(files),
                "extensions": exts
            }

        if depth >= max_depth:
            dirs[:] = []

    return {
        "root": str(root),
        "max_depth": max_depth,
        "total_subsystems": len(subsystems),
        "subsystems": subsystems
    }


def render_ascii_tree(root_path: Path, max_depth: int = 3, prefix: str = "") -> None:
    """Render compact ASCII tree up to max_depth."""
    root = root_path.resolve()

    def _walk(current: Path, current_depth: int, pfx: str):
        if current_depth > max_depth:
            return
        try:
            entries = sorted(list(current.iterdir()), key=lambda e: (e.is_file(), e.name.lower()))
        except OSError:
            return

        entries = [e for e in entries if e.name not in IGNORED_DIRS]
        for idx, entry in enumerate(entries):
            is_last = (idx == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            print(f"{pfx}{connector}{entry.name}")
            if entry.is_dir() and current_depth < max_depth:
                next_pfx = pfx + ("    " if is_last else "│   ")
                _walk(entry, current_depth + 1, next_pfx)

    print(root.name or ".")
    _walk(root, 1, prefix)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize codebase subsystem tree.")
    parser.add_argument("path", nargs="?", default=".", help="Repository root path")
    parser.add_argument("--depth", type=int, default=3, help="Maximum tree depth (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output JSON structure")
    args = parser.parse_args()

    root = Path(args.path)
    if args.json:
        try:
            data = build_tree_summary(root, max_depth=args.depth)
            print(json.dumps(data, indent=2))
            return 0
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    else:
        render_ascii_tree(root, max_depth=args.depth)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
