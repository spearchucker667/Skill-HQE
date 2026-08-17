#!/usr/bin/env python3
"""Clean packaging script for Skill-HQE release bundles.

Builds a deterministic ZIP archive of Skill-HQE containing only approved runtime
and documentation files, strictly excluding development directories (development/, archive/, tests/),
git metadata, cache debris (__pycache__, *.pyc), macOS metadata (.DS_Store, __MACOSX),
and temporary/generated files.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import sys
import zipfile
from pathlib import Path

# Directories excluded from release archives
EXCLUDED_DIRECTORIES = {
    ".git",
    ".github",
    "__MACOSX",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "development",
    "archive",
    "tests",  # Test fixtures and tests are development assets
    "audit-output",
    "generated",
}

# Specific files excluded from release archives
EXCLUDED_FILES = {
    ".gitignore",
    ".gitattributes",
}

# Forbidden file patterns excluded from release archives
FORBIDDEN_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.log",
    "*.zip",
    "*.tar.gz",
    "*.tgz",
    ".DS_Store",
    "Thumbs.db",
    ".env",
    "*.secret",
    "*.key",
    "*.pem",
    "*__pycache__*",
]


def should_exclude(rel_path: str) -> bool:
    """Check if relative path matches excluded directory or pattern."""
    normalized = rel_path.replace("\\", "/")
    parts = normalized.split("/")

    for part in parts:
        if part in EXCLUDED_DIRECTORIES:
            return True

    if normalized in EXCLUDED_FILES or os.path.basename(normalized) in EXCLUDED_FILES:
        return True

    for pat in FORBIDDEN_PATTERNS:
        if fnmatch.fnmatch(normalized, pat) or fnmatch.fnmatch(os.path.basename(normalized), pat):
            return True

    return False


def package_skill(source_dir: Path, output_zip: Path) -> dict:
    """Package skill directory into a clean release zip archive."""
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

            # Prune excluded directories early
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRECTORIES and not should_exclude(f"{rel_dir_str}{d}")]

            for f in sorted(files):
                rel_file = f"{rel_dir_str}{f}"
                if should_exclude(rel_file):
                    continue

                abs_file = Path(current_root) / f
                # Safety: ensure the absolute file is still within the source tree
                try:
                    abs_file.resolve().relative_to(src)
                except ValueError:
                    continue

                # Normalize zip archive entry name (always forward slashes)
                archive_name = f"Skill-HQE/{rel_file}"
                if archive_name.startswith("Skill-HQE/../") or "/../" in archive_name:
                    continue

                zf.write(abs_file, arcname=archive_name)
                packaged_files.append(archive_name)

    # Post-packaging validation check
    try:
        from scripts.check_release_contents import check_zip_archive
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from check_release_contents import check_zip_archive

    errors = check_zip_archive(out)
    if errors:
        out.unlink()
        raise RuntimeError(f"Release contents validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    return {
        "output_path": str(out),
        "total_files_packaged": len(packaged_files),
        "size_bytes": out.stat().st_size,
        "clean_verification": True
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Package Skill-HQE into a clean release ZIP.")
    parser.add_argument("--source", "-s", default=".", help="Source directory (default: current directory)")
    parser.add_argument("--output", "-o", required=True, help="Output ZIP file path")
    args = parser.parse_args()

    src_path = Path(args.source)
    out_path = Path(args.output)

    try:
        res = package_skill(src_path, out_path)
        print(f"Skill successfully packaged: {res['output_path']} ({res['total_files_packaged']} files, {res['size_bytes']} bytes)")
        return 0
    except Exception as exc:
        print(f"Packaging failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
