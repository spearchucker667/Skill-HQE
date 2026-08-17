"""Tests for truthful run manifest defaults and protocol derivation."""

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import (
    FindingRegistry,
    EvidenceStore,
    RunManifestGenerator,
    HealthScore,
)


def test_default_coverage_is_not_claimed_full():
    registry = FindingRegistry()
    gen = RunManifestGenerator(repo_path=ROOT, mode="audit")
    manifest = gen.build_manifest(registry=registry, total_files=0)

    assert len(manifest["coverage"]) == 1
    coverage = manifest["coverage"][0]
    assert coverage["reviewed"] is False
    assert coverage["depth"] == "unknown"
    assert manifest["unreviewed_surfaces"]


def test_default_health_score_omitted_when_coverage_unknown():
    registry = FindingRegistry()
    gen = RunManifestGenerator(repo_path=ROOT, mode="audit")
    manifest = gen.build_manifest(registry=registry, total_files=0)

    assert manifest["health_score"]["omitted"] is True
    assert "score" not in manifest["health_score"]
    assert "false-perfect" in " ".join(manifest["health_score"]["reasons"]).lower()


def test_health_score_included_when_coverage_known():
    registry = FindingRegistry()
    gen = RunManifestGenerator(repo_path=ROOT, mode="audit")
    manifest = gen.build_manifest(
        registry=registry,
        total_files=1,
        subsystems_coverage=[
            {"subsystem": "src", "files": 1, "reviewed": True, "depth": "full", "findings_count": 0}
        ],
        unreviewed_surfaces=[],
    )

    assert manifest["health_score"]["omitted"] is False
    assert manifest["health_score"]["score"] == 10


def test_protocol_version_derived_from_yaml():
    import yaml

    protocol_path = ROOT / "protocol" / "hqe-engineer.yaml"
    raw = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    expected = raw.get("protocol_version") or raw.get("schema_version")

    registry = FindingRegistry()
    gen = RunManifestGenerator(repo_path=ROOT, mode="audit")
    manifest = gen.build_manifest(registry=registry, total_files=0)

    assert manifest["protocol_details"]["version"] == str(expected)
    assert manifest["protocol_details"]["name"] == raw["meta"]["name"]


def test_command_records_preserve_structure():
    registry = FindingRegistry()
    store = EvidenceStore(repo_root=ROOT)
    store.record_tool_execution(
        tool_name="pytest",
        command="pytest tests/",
        exit_code=0,
        stdout="ok",
        stderr="",
    )
    store.record_tool_execution(
        tool_name="ruff",
        command="ruff check .",
        exit_code=1,
        stdout="",
        stderr="error",
    )

    gen = RunManifestGenerator(repo_path=ROOT, mode="audit")
    manifest = gen.build_manifest(registry=registry, total_files=0, evidence_store=store)

    assert manifest["commands"] == ["pytest tests/", "ruff check ."]
    assert len(manifest["command_records"]) == 2
    assert manifest["command_records"][0] == {
        "tool": "pytest",
        "command": "pytest tests/",
        "exit_code": 0,
        "result": "success",
    }
    assert manifest["command_records"][1]["result"] == "failure"


def test_int_health_score_backward_compatible():
    registry = FindingRegistry()
    gen = RunManifestGenerator(repo_path=ROOT, mode="audit")
    manifest = gen.build_manifest(registry=registry, total_files=0, health_score=8)

    assert manifest["health_score"]["score"] == 8
    assert manifest["health_score"]["band"] == "Solid"
    assert manifest["health_score"]["omitted"] is False


def test_health_score_object_accepted():
    registry = FindingRegistry()
    gen = RunManifestGenerator(repo_path=ROOT, mode="audit")
    hs = HealthScore(score=5, omitted=False, reasons=["custom reason"])
    manifest = gen.build_manifest(registry=registry, total_files=0, health_score=hs)

    assert manifest["health_score"]["score"] == 5
    assert manifest["health_score"]["reasons"] == ["custom reason"]


def test_manifest_validates_against_schema():
    import json
    from jsonschema import validate

    registry = FindingRegistry()
    store = EvidenceStore(repo_root=ROOT)
    store.record_tool_execution(tool_name="pytest", command="pytest", exit_code=0)
    gen = RunManifestGenerator(repo_path=ROOT, mode="audit")
    manifest = gen.build_manifest(registry=registry, total_files=3, evidence_store=store)

    schema = json.loads((ROOT / "schemas" / "run-manifest.schema.json").read_text(encoding="utf-8"))
    validate(instance=manifest, schema=schema)
