#!/usr/bin/env python3
"""Repository inventory and file classification utility for HQE.

Inventories ALL files in a repository without dropping binary or media files
from overall counts, classifying every file by category and determining
eligibility for deep code review while respecting gitignore semantics.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from pathlib import Path

# File classification extensions
EXT_SOURCE = {
    ".rs", ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".c", ".cpp", ".cc", ".cxx",
    ".h", ".hpp", ".hxx", ".java", ".kt", ".kts", ".cs", ".fs", ".swift", ".rb",
    ".php", ".dart", ".sh", ".bash", ".zsh", ".pl", ".pm", ".lua", ".ex", ".exs",
    ".erl", ".hrl", ".clj", ".scala", ".m", ".mm", ".r", ".zig", ".nim", ".v",
    ".proto", ".graphql", ".gql", ".sql", ".html", ".htm", ".css", ".scss", ".sass",
    ".less", ".vue", ".svelte"
}

EXT_CONFIG = {
    ".json", ".yaml", ".yml", ".toml", ".xml", ".ini", ".cfg", ".conf", ".properties",
    ".env", ".env.example", ".env.sample", ".env.template", ".editorconfig",
    ".gitattributes", ".dockerignore", ".npmrc", ".yarnrc", ".pypirc"
}

EXT_DOCS = {
    ".md", ".markdown", ".rst", ".adoc", ".txt", ".pdf", ".docx", ".rtf", ".tex"
}

EXT_BINARY = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".o", ".obj", ".a", ".lib", ".class",
    ".jar", ".war", ".ear", ".pyc", ".pyo", ".pyd", ".wasm", ".node"
}

EXT_MEDIA = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".bmp", ".tiff",
    ".mp3", ".mp4", ".wav", ".ogg", ".avi", ".mov", ".flv", ".webm", ".ttf",
    ".otf", ".woff", ".woff2", ".eot"
}

EXT_ARCHIVE = {
    ".zip", ".tar", ".gz", ".tgz", ".bz2", ".tbz2", ".xz", ".txz", ".7z", ".rar",
    ".dmg", ".pkg", ".deb", ".rpm", ".apk", ".ipa"
}


def load_ignore_patterns(root: Path) -> list[str]:
    """Load ignore patterns from standard ignore files and defaults."""
    patterns = [
        ".git", ".git/*", ".hg", ".svn",
        "__pycache__", "*.py[cod]", ".pytest_cache",
        "node_modules", "node_modules/*",
        "target", "target/*",
        "dist", "dist/*", "build", "build/*",
        ".DS_Store", "__MACOSX"
    ]
    for ignore_filename in [".gitignore", ".ignore", ".hqeignore"]:
        ignore_file = root / ignore_filename
        if ignore_file.is_file():
            try:
                with ignore_file.open("r", encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
            except OSError:
                pass
    return patterns


def is_path_ignored(rel_path: str, patterns: list[str]) -> bool:
    """Check if relative path matches any ignore pattern."""
    normalized = rel_path.replace("\\", "/")
    parts = normalized.split("/")

    for pattern in patterns:
        pat = pattern.strip()
        if not pat:
            continue

        # Directory-only match
        if pat.endswith("/"):
            clean_pat = pat.rstrip("/")
            if clean_pat in parts:
                return True
            if fnmatch.fnmatch(normalized, f"*{clean_pat}/*") or normalized.startswith(f"{clean_pat}/"):
                return True
            continue

        # Exact component or glob match
        if pat in parts:
            return True
        if fnmatch.fnmatch(normalized, pat) or fnmatch.fnmatch(normalized, f"*/{pat}"):
            return True
        if fnmatch.fnmatch(normalized, f"**/{pat}"):
            return True

    return False


def classify_file(path_input: str | Path, ext: str | None = None) -> str:
    """Classify file into category based on path and extension."""
    if isinstance(path_input, Path):
        path_str = str(path_input)
        if ext is None:
            ext = path_input.suffix.lower()
    else:
        path_str = str(path_input)
        if ext is None:
            ext = Path(path_str).suffix.lower()

    lower_path = path_str.lower()

    if "/test/" in lower_path or "/tests/" in lower_path or "/spec/" in lower_path or \
       lower_path.startswith("test/") or lower_path.startswith("tests/") or \
       "test_" in lower_path or "_test." in lower_path or ".spec." in lower_path or ".test." in lower_path:
        return "test"

    if "/vendor/" in lower_path or "/third_party/" in lower_path or "/external/" in lower_path or \
       lower_path.startswith("vendor/") or lower_path.startswith("third_party/"):
        return "vendored"

    if "/generated/" in lower_path or "/gen/" in lower_path or lower_path.endswith(".generated.ts") or \
       lower_path.endswith(".pb.go") or lower_path.endswith("_pb2.py"):
        return "generated"

    if "/build/" in lower_path or lower_path.startswith("build/") or \
       "/dist/" in lower_path or lower_path.startswith("dist/") or \
       "/out/" in lower_path or lower_path.startswith("out/"):
        return "build"

    if ext in EXT_BINARY:
        return "binary"
    if ext in EXT_MEDIA:
        return "media"
    if ext in EXT_ARCHIVE:
        return "archive"
    if ext in EXT_DOCS or lower_path.endswith("readme") or lower_path.endswith("license") or lower_path.endswith("notice"):
        return "docs"
    if ext in EXT_CONFIG or lower_path.startswith(".env") or "config" in lower_path or "manifest" in lower_path or lower_path.endswith(".toml") or lower_path.endswith(".json") or lower_path.endswith(".yaml") or lower_path.endswith(".yml"):
        return "config"
    if ext in EXT_SOURCE:
        return "source"

    return "unknown"


def inventory_repository(root_path: Path, max_files: int | None = None) -> dict:
    """Perform comprehensive inventory of all repository files."""
    root = root_path.resolve()
    if not root.is_dir():
        raise ValueError(f"Target path does not exist or is not a directory: {root}")

    ignore_patterns = load_ignore_patterns(root)

    total_files = 0
    reviewable_files = 0
    excluded_files = 0
    binary_files = 0
    generated_files = 0
    vendored_files = 0

    category_counts: dict[str, int] = {}
    extension_counts: dict[str, int] = {}
    files_list: list[dict] = []

    for current_root, dirs, files in os.walk(root):
        rel_dir = Path(current_root).relative_to(root)
        rel_dir_str = "" if str(rel_dir) == "." else str(rel_dir).replace("\\", "/") + "/"

        # Filter out ignored directories early for performance
        pruned_dirs = []
        for d in dirs:
            dir_rel = f"{rel_dir_str}{d}"
            if is_path_ignored(dir_rel, ignore_patterns) or d == ".git":
                continue
            pruned_dirs.append(d)
        dirs[:] = pruned_dirs

        for f in files:
            rel_file = f"{rel_dir_str}{f}".replace("\\", "/")
            total_files += 1

            path_obj = Path(current_root) / f
            ext = path_obj.suffix.lower()
            extension_counts[ext] = extension_counts.get(ext, 0) + 1

            try:
                size_bytes = path_obj.stat().st_size
            except OSError:
                size_bytes = 0

            category = classify_file(rel_file, ext)
            category_counts[category] = category_counts.get(category, 0) + 1

            is_ignored = is_path_ignored(rel_file, ignore_patterns)
            is_non_text = category in {"binary", "media", "archive"}
            is_noise = category in {"generated", "vendored", "build"}

            if is_non_text:
                binary_files += 1
            if category == "generated":
                generated_files += 1
            if category == "vendored":
                vendored_files += 1

            if is_ignored or is_non_text or is_noise:
                excluded_files += 1
                included_for_deep_review = False
                if is_ignored:
                    excluded_reason = "matches_ignore_rule"
                elif is_non_text:
                    excluded_reason = f"non_text_{category}"
                else:
                    excluded_reason = f"noise_{category}"
            else:
                reviewable_files += 1
                included_for_deep_review = True
                excluded_reason = None

            if max_files is None or len(files_list) < max_files:
                files_list.append({
                    "path": rel_file,
                    "category": category,
                    "extension": ext,
                    "size_bytes": size_bytes,
                    "included_for_deep_review": included_for_deep_review,
                    "excluded_reason": excluded_reason
                })

    summary_data = {
        "total_files": total_files,
        "reviewable_files": reviewable_files,
        "excluded_files": excluded_files,
        "binary_files": binary_files,
        "generated_files": generated_files,
        "vendored_files": vendored_files,
        "categories": category_counts,
        "extensions": extension_counts
    }

    return {
        "root": str(root),
        "total_files": total_files,
        "reviewable_files": reviewable_files,
        "excluded_files": excluded_files,
        "binary_files": binary_files,
        "generated_files": generated_files,
        "vendored_files": vendored_files,
        "categories": category_counts,
        "extensions": extension_counts,
        "summary": summary_data,
        "files": files_list
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory repository files with full classification.")
    parser.add_argument("path", nargs="?", default=".", help="Repository root path")
    parser.add_argument("--max-files", type=int, default=None, help="Max file items to include in detailed output")
    parser.add_argument("--summary-only", action="store_true", help="Print summary without file list")
    args = parser.parse_args()

    try:
        inv = inventory_repository(Path(args.path), max_files=args.max_files)
        if args.summary_only:
            print(json.dumps(inv["summary"], indent=2))
        else:
            print(json.dumps(inv, indent=2))
        return 0
    except Exception as exc:
        print(f"Error during repository inventory: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
