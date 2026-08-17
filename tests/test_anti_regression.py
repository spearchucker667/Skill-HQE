"""Tests for the anti-regression gate."""

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from anti_regression_check import check_artifact_determinism, check_artifact_regression_patterns


def test_artifact_determinism_passes():
    errors = check_artifact_determinism()
    assert errors == []


def test_artifact_regression_patterns_passes():
    errors = check_artifact_regression_patterns()
    assert errors == []


def test_forbidden_security_wording_detected():
    # Patch the artifact generator temporarily by injecting an artifact with old wording.
    from runtime import ArtifactPipeline, FindingRegistry

    class BadPipeline(ArtifactPipeline):
        def generate_security_posture(self) -> str:
            return "No active security vulnerabilities detected.\n"

    registry = FindingRegistry()
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = BadPipeline(registry, repo_name="bad")
        artifacts = pipeline.build_all_artifacts(output_dir=tmpdir)
        text = artifacts["SECURITY_POSTURE_SUMMARY.md"].read_text(encoding="utf-8")
        assert "No active security vulnerabilities detected" in text
