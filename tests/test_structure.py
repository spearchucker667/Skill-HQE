from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_core_root_files_exist():
    for f in ("SKILL.md", "README.md", "LICENSE", "NOTICE", "VERSION", "CHANGELOG.md", "pyproject.toml", "requirements-dev.txt"):
        p = ROOT / f
        assert p.is_file(), f"Missing root file: {f}"


def test_protocol_files_exist():
    for f in ("hqe-engineer.yaml", "hqe-engineer-schema.json", "validate.py", "README.md", "VALIDATORS.md", "SOURCE_CHECKSUMS.sha256"):
        p = ROOT / "protocol" / f
        assert p.is_file(), f"Missing protocol file: protocol/{f}"


def test_all_canonical_schemas_exist():
    for f in ("finding.schema.json", "findings.schema.json", "run-manifest.schema.json", "handoff.schema.json", "session-log.schema.json", "redaction-log.schema.json", "report.schema.json"):
        p = ROOT / "schemas" / f
        assert p.is_file(), f"Missing schema: schemas/{f}"


def test_all_canonical_templates_exist():
    for f in (
        "finding.md", "report.md", "handoff.md", "run-manifest.md",
        "risk-register.md", "master-todo-backlog.md", "pattern-findings.md",
        "quick-wins-vs-structural.md", "security-posture-summary.md",
        "reliability-summary.md", "testing-gaps.md", "unknowns-verification.md",
        "confidence-declaration.md", "session-log.md", "redaction-log.md",
        "patch-action.md", "remediation-plan.md", "validation-report.md", "incident-mini-report.md"
    ):
        p = ROOT / "templates" / f
        assert p.is_file(), f"Missing template: templates/{f}"


def test_all_canonical_scripts_exist():
    for f in (
        "inventory_repo.py", "detect_manifests.py", "detect_test_commands.py",
        "local_risk_scan.py", "redact_secrets.py", "summarize_tree.py",
        "validate_findings.py", "validate_manifest.py", "validate_session_log.py",
        "validate_semantics.py", "validate_protocol_bundle.py",
        "build_artifacts.py", "create_run_manifest.py", "check_protocol_sync.py",
        "package_skill.py", "check_skill.py", "check_release_contents.py",
        "verify_invariants.sh"
    ):
        p = ROOT / "scripts" / f
        assert p.is_file(), f"Missing script: scripts/{f}"


def test_runtime_layer_files_exist():
    for f in (
        "__init__.py", "session_manager.py", "finding_registry.py",
        "evidence_store.py", "run_manifest.py", "artifact_pipeline.py"
    ):
        p = ROOT / "runtime" / f
        assert p.is_file(), f"Missing runtime file: runtime/{f}"
