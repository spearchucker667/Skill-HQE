import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_protocol_sync import check_sync, compute_sha256


def test_protocol_sync_integrity():
    errors = check_sync(ROOT)
    assert not errors, f"Protocol sync failures: {errors}"


def test_protocol_hash_stability():
    protocol_yaml = ROOT / "protocol" / "hqe-engineer.yaml"
    assert protocol_yaml.is_file()
    actual_hash = compute_sha256(protocol_yaml)
    assert len(actual_hash) == 64
