#!/usr/bin/env python3
"""Release contents verifier for Skill-HQE.

Verifies that a release package (ZIP archive or directory) contains ONLY approved
runtime skill files, documentation, and metadata, strictly rejecting development artifacts,
audit outputs, historical archives, test debris, and cache files.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import sys
import tempfile
import zipfile
from pathlib import Path

# Allowlist of top-level files permitted in a release
ALLOWED_ROOT_FILES = {
    "SKILL.md",
    "README.md",
    "LICENSE",
    "NOTICE",
    "VERSION",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "PRIVACY.md",
    "TERMS_OF_SERVICE.md",
    "pyproject.toml",
    "requirements-dev.txt",
    "AGENTS.md",
    ".secretscanignore",
}

# Allowlist of top-level directories permitted in a release
ALLOWED_ROOT_DIRS = {
    "protocol",
    "references",
    "workflows",
    "templates",
    "schemas",
    "scripts",
    "runtime",
    "docs",
}

# Explicitly forbidden top-level directories or patterns
FORBIDDEN_ROOT_DIRS = {
    "development",
    "archive",
    ".git",
    ".github",
    "__MACOSX",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "tests",  # Test fixtures and tests are development-only
    "audit-output",
}

# Explicitly forbidden file suffixes or glob patterns anywhere in the release
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
    ".gitignore",
    ".gitattributes",
    ".actionlint.yaml",
    ".pre-commit-config.yaml",
]

# Essential files that MUST be present in any valid release
REQUIRED_RELEASE_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "NOTICE",
    "VERSION",
    "CHANGELOG.md",
    "protocol/hqe-engineer.yaml",
    "protocol/hqe-engineer-schema.json",
    "protocol/validate.py",
    "protocol/SOURCE_CHECKSUMS.sha256",
    "schemas/finding.schema.json",
    "templates/finding.md",
    "runtime/__init__.py",
    "runtime/session_manager.py",
    "runtime/finding_registry.py",
    "runtime/evidence_store.py",
    "runtime/run_manifest.py",
    "runtime/artifact_pipeline.py",
    "scripts/inventory_repo.py",
    "scripts/detect_manifests.py",
]


def verify_file_list(files: list[str]) -> list[str]:
    """Verify a normalized relative file list against release rules."""
    errors: list[str] = []
    seen_files = set(files)

    # 1. Check required release files
    for req in REQUIRED_RELEASE_FILES:
        if req not in seen_files:
            errors.append(f"Missing required release file: {req}")

    # 2. Inspect each file path
    for rel_path in files:
        parts = rel_path.split("/")
        top_level = parts[0]

        # Check forbidden directories
        if top_level in FORBIDDEN_ROOT_DIRS:
            errors.append(f"Forbidden directory in release: {rel_path}")

        # If it's a root file, check against allowed root files
        if len(parts) == 1:
            if top_level not in ALLOWED_ROOT_FILES:
                errors.append(f"Unapproved root file in release: {rel_path}")
        else:
            # Subdirectory path: check if top-level dir is allowed
            if top_level not in ALLOWED_ROOT_DIRS:
                errors.append(f"Unapproved top-level directory in release: {rel_path}")

        # Check forbidden patterns
        basename = parts[-1]
        for pat in FORBIDDEN_PATTERNS:
            if fnmatch.fnmatch(rel_path, pat) or fnmatch.fnmatch(basename, pat):
                errors.append(f"Forbidden file pattern matched '{pat}': {rel_path}")

    return errors


def check_zip_archive(zip_path: Path) -> list[str]:
    """Check contents of a release ZIP archive."""
    if not zip_path.is_file():
        return [f"ZIP archive not found: {zip_path}"]

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
    except Exception as exc:
        return [f"Failed to read ZIP archive: {exc}"]

    # Normalize archive paths (strip top-level prefix like 'Skill-HQE/' if present)
    normalized: list[str] = []
    for name in names:
        if name.endswith("/"):
            continue  # skip directory entries
        norm = name.replace("\\", "/")
        if norm.startswith("Skill-HQE/"):
            norm = norm[len("Skill-HQE/"):]
        normalized.append(norm)

    return verify_file_list(normalized)


def check_directory(dir_path: Path) -> list[str]:
    """Check contents of an unpacked release directory."""
    if not dir_path.is_dir():
        return [f"Target directory not found: {dir_path}"]

    # If the directory is a development workspace (e.g. contains development/ or tests/),
    # package it into a temporary zip and test the release package
    if (dir_path / "development").exists() or (dir_path / "tests").exists():
        try:
            from scripts.package_skill import package_skill
        except ImportError:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from package_skill import package_skill

        with tempfile.TemporaryDirectory() as tmpdir:
            test_zip = Path(tmpdir) / "test_release.zip"
            package_skill(dir_path, test_zip)
            return check_zip_archive(test_zip)

    files: list[str] = []
    for root, _, filenames in os.walk(dir_path):
        rel_root = Path(root).relative_to(dir_path)
        for fname in filenames:
            if str(rel_root) == ".":
                files.append(fname)
            else:
                files.append(f"{str(rel_root).replace(chr(92), '/')}/{fname}")

    return verify_file_list(files)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify that Skill-HQE release package conforms to allowlist rules.")
    parser.add_argument("target", nargs="?", default=".", help="Path to release ZIP archive, unpacked release directory, or repository root (default: .)")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()

    if target_path.is_file() and target_path.suffix.lower() == ".zip":
        errors = check_zip_archive(target_path)
    elif target_path.is_dir():
        errors = check_directory(target_path)
    else:
        print(f"Error: Target '{target_path}' is neither a directory nor a .zip file.", file=sys.stderr)
        return 1

    if errors:
        print("Release Contents Check FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"Release contents check PASSED for: {target_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
