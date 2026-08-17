#!/usr/bin/env python3
"""Clean packaging script for Skill-HQE release bundles.

Builds a deterministic ZIP archive of Skill-HQE, strictly excluding git metadata,
cache debris (__pycache__, *.pyc), macOS metadata (.DS_Store, __MACOSX), and temporary files.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import sys
import zipfile
from pathlib import Path

FORBIDDEN_PATTERNS = [
    ".git", ".git/*",
    "__MACOSX", "__MACOSX/*", "*/__MACOSX/*",
    "__pycache__", "*__pycache__*", "*/__pycache__/*",
    "*.pyc", "*.pyo", "*.pyd",
    ".DS_Store", "*/.DS_Store",
    ".pytest_cache", ".pytest_cache/*",
    "*.zip", "*.tar.gz", "*.tgz",
    "HQE_PROTOCOL_SKILL_EMBED_PACKAGE", "HQE_PROTOCOL_SKILL_EMBED_PACKAGE/*",
    "protocolupdate", "protocolupdate/*"
]


def should_exclude(rel_path: str) -> bool:
    """Check if relative path matches forbidden archive patterns."""
    normalized = rel_path.replace("\\", "/")
    parts = normalized.split("/")

    for part in parts:
        if part in {".git", "__MACOSX", "__pycache__", ".pytest_cache", ".DS_Store", "HQE_PROTOCOL_SKILL_EMBED_PACKAGE", "protocolupdate"}:
            return True

    for pat in FORBIDDEN_PATTERNS:
        if fnmatch.fnmatch(normalized, pat) or fnmatch.fnmatch(os.path.basename(normalized), pat):
            return True

    return False


def package_skill(source_dir: Path, output_zip: Path) -> dict:
    """Package skill directory into a clean zip archive."""
    src = source_dir.resolve()
    out = output_zip.resolve()

    if not src.is_dir():
        raise ValueError(f"Source directory does not exist: {src}")

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    packaged_files: list[str] = []

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for current_root, dirs, files in os.walk(src):
            rel_dir = Path(current_root).relative_to(src)
            rel_dir_str = "" if str(rel_dir) == "." else str(rel_dir).replace("\\", "/") + "/"

            # Prune forbidden directories early
            dirs[:] = [d for d in dirs if not should_exclude(f"{rel_dir_str}{d}")]

            for f in sorted(files):
                rel_file = f"{rel_dir_str}{f}"
                if should_exclude(rel_file):
                    continue

                abs_file = Path(current_root) / f
                # Normalize zip archive entry name (always forward slashes)
                archive_name = f"Skill-HQE/{rel_file}"
                zf.write(abs_file, arcname=archive_name)
                packaged_files.append(archive_name)

    # Verification pass over generated archive
    with zipfile.ZipFile(out, "r") as zf:
        for name in zf.namelist():
            parts = name.split("/")
            for part in parts:
                if part in {".git", "__MACOSX", "__pycache__", ".DS_Store"}:
                    out.unlink()
                    raise RuntimeError(f"Archive verification failed: forbidden directory '{part}' found in '{name}'")
            if name.endswith(".pyc") or name.endswith(".pyo"):
                out.unlink()
                raise RuntimeError(f"Archive verification failed: compiled python file found in '{name}'")

    return {
        "output_path": str(out),
        "total_files_packaged": len(packaged_files),
        "size_bytes": out.stat().st_size,
        "clean_verification": True
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Package Skill-HQE into a clean release ZIP.")
    parser.add_argument("--source", default=".", help="Skill-HQE root path (default: .)")
    parser.add_argument("--output", default="Skill-HQE-v5.0.0.zip", help="Output ZIP path")
    args = parser.parse_args()

    try:
        res = package_skill(Path(args.source), Path(args.output))
        print(f"Skill successfully packaged: {res['output_path']} ({res['total_files_packaged']} files, {res['size_bytes']} bytes)")
        return 0
    except Exception as exc:
        print(f"Packaging ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
