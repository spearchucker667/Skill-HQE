#!/usr/bin/env python3
"""Check protocol synchronization and SHA-256 integrity across Skill-HQE."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REQUIRED_PROTOCOL_FILES = [
    "hqe-engineer.yaml",
    "hqe-engineer-schema.json",
    "validate.py",
    "verify.py",
    "hqe-schema.json"
]


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hex digest of file."""
    h = hashlib.sha256()
    with file_path.open("rb") as fh:
        while chunk := fh.read(65536):
            h.update(chunk)
    return h.hexdigest()


def check_sync(root_path: Path) -> list[str]:
    """Verify synchronization between protocol/ and package canonical-protocol/."""
    root = root_path.resolve()
    errors: list[str] = []

    protocol_dir = root / "protocol"
    pkg_canonical = root / "HQE_PROTOCOL_SKILL_EMBED_PACKAGE" / "canonical-protocol"

    if not protocol_dir.is_dir():
        return [f"protocol/ directory missing at {protocol_dir}"]

    # 1. Check integrity against protocol/SOURCE_CHECKSUMS.sha256
    checksum_file = protocol_dir / "SOURCE_CHECKSUMS.sha256"
    if checksum_file.is_file():
        expected_hashes: dict[str, str] = {}
        for line in checksum_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    expected_hashes[parts[1].strip()] = parts[0].strip()

        for filename in ("hqe-engineer.yaml", "hqe-engineer-schema.json", "validate.py"):
            target_file = protocol_dir / filename
            if not target_file.is_file():
                errors.append(f"Missing protocol file: protocol/{filename}")
                continue
            actual_hash = compute_sha256(target_file)
            if filename in expected_hashes:
                if actual_hash != expected_hashes[filename]:
                    errors.append(f"Checksum mismatch for protocol/{filename}: expected {expected_hashes[filename]}, got {actual_hash}")

    # 2. Check synchronization with package canonical-protocol if present
    if pkg_canonical.is_dir():
        for filename in ("hqe-engineer.yaml", "hqe-engineer-schema.json", "validate.py"):
            f_main = protocol_dir / filename
            f_pkg = pkg_canonical / filename
            if f_main.is_file() and f_pkg.is_file():
                h_main = compute_sha256(f_main)
                h_pkg = compute_sha256(f_pkg)
                if h_main != h_pkg:
                    errors.append(f"Protocol drift: protocol/{filename} ({h_main}) != package/{filename} ({h_pkg})")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check protocol synchronization and integrity.")
    parser.add_argument("path", nargs="?", default=".", help="Skill-HQE root path")
    args = parser.parse_args()

    errors = check_sync(Path(args.path))
    if errors:
        print(f"Protocol sync check FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("Protocol sync check PASSED: protocol/ matches canonical source checksums.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
