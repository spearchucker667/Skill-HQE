#!/usr/bin/env python3
"""Check protocol synchronization and SHA-256 integrity across Skill-HQE.

The canonical protocol lives in ``protocol/`` and ``protocol/SOURCE_CHECKSUMS.sha256``
is the recorded set of canonical hashes.  This check establishes synchronization
by requiring every required protocol file to exist, have a recorded hash, and
match that hash exactly.  A missing checksum file is a hard failure rather than
a vacuously passing check.
"""

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
    """Verify protocol/ matches the canonical hashes recorded in SOURCE_CHECKSUMS.sha256."""
    root = root_path.resolve()
    errors: list[str] = []

    protocol_dir = root / "protocol"
    if not protocol_dir.is_dir():
        return [f"protocol/ directory missing at {protocol_dir}"]

    # Check integrity against protocol/SOURCE_CHECKSUMS.sha256
    checksum_file = protocol_dir / "SOURCE_CHECKSUMS.sha256"
    if not checksum_file.is_file():
        return [f"Missing canonical checksum file: protocol/SOURCE_CHECKSUMS.sha256"]

    expected_hashes: dict[str, str] = {}
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split()
            if len(parts) >= 2:
                expected_hashes[parts[1].strip()] = parts[0].strip()

    for filename in REQUIRED_PROTOCOL_FILES:
        target_file = protocol_dir / filename
        if not target_file.is_file():
            errors.append(f"Missing protocol file: protocol/{filename}")
            continue
        actual_hash = compute_sha256(target_file)
        if filename in expected_hashes:
            if actual_hash != expected_hashes[filename]:
                errors.append(f"Checksum mismatch for protocol/{filename}: expected {expected_hashes[filename]}, got {actual_hash}")
        else:
            errors.append(f"Missing expected hash in SOURCE_CHECKSUMS.sha256 for protocol/{filename}")

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

    print("Protocol sync check PASSED: protocol/ files match the canonical SOURCE_CHECKSUMS.sha256 hashes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
