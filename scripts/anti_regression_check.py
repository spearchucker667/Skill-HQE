#!/usr/bin/env python3
"""Anti-regression gate for Skill-HQE artifacts and repository state."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

# Allow running from repository root or scripts/ directory.
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent))

from runtime import FindingRegistry, ArtifactPipeline, CodeEvidence, Finding

FORBIDDEN_ARTIFACT_PATTERNS = {
    "No active security vulnerabilities detected": "softened security no-findings wording required",
    "All findings verified as FACT or INFERENCE": "softened unknowns wording required",
}


def _make_sample_registry() -> FindingRegistry:
    """Build a small registry that exercises all artifact generators."""
    registry = FindingRegistry()
    ev = CodeEvidence(path="src/x.py", start_line=1, end_line=1, snippet="x")

    # A representative bug finding.
    registry.register(Finding(
        id="HQE-BUG-001",
        title="Missing null check",
        category="BUG",
        severity="MEDIUM",
        confidence="FACT",
        status="CONFIRMED",
        affected_component="src/x.py",
        observed_behavior="Crash on null input",
        expected_behavior="Graceful handling",
        root_cause="Missing check",
        impact="Process termination",
        remediation="Add null check",
        effort="S",
        regression_risk="Low",
        evidence=[ev],
        validation=["pytest tests/test_x.py"],
    ))

    # Two findings in the same category to exercise pattern grouping.
    registry.register(Finding(
        id="HQE-SEC-001",
        title="Hardcoded key",
        category="SEC",
        severity="HIGH",
        confidence="FACT",
        status="CONFIRMED",
        affected_component="src/auth.py",
        observed_behavior="Static key in source",
        expected_behavior="Read from env",
        root_cause="Hardcoding",
        impact="Token forgery",
        remediation="Use env var",
        effort="S",
        regression_risk="Low",
        evidence=[ev],
        preconditions=["dev mode"],
        exploitability="High",
        blast_radius="System wide",
        likelihood="High",
        likelihood_justification="Default config",
        exposure_evidence="src/auth.py:1",
        taint_chain={
            "source": "auth.py",
            "transforms": ["parser"],
            "validation_boundary": "validator",
            "sink": "verify",
            "impact": "forgery",
        },
    ))
    registry.register(Finding(
        id="HQE-SEC-002",
        title="Insecure comparison",
        category="SEC",
        severity="MEDIUM",
        confidence="INFERENCE",
        status="CONFIRMED",
        affected_component="src/auth.py",
        observed_behavior="Timing-unsafe comparison",
        expected_behavior="Constant-time comparison",
        root_cause="Using == on secrets",
        impact="Side-channel leak",
        remediation="Use hmac.compare_digest",
        effort="S",
        regression_risk="Low",
        evidence=[ev],
        preconditions=["network proximity"],
        exploitability="Medium",
        blast_radius="Auth subsystem",
        likelihood="Medium",
        likelihood_justification="Observed pattern",
        exposure_evidence="src/auth.py:2",
        taint_chain={
            "source": "src/auth.py#L2",
            "transforms": ["comparator"],
            "validation_boundary": "auth module",
            "sink": "equality check",
            "impact": "side-channel leakage",
        },
    ))

    return registry


def check_artifact_determinism(repo_name: str = "regression-test") -> list[str]:
    """Generate artifacts twice and verify byte-for-byte determinism."""
    errors: list[str] = []
    registry = _make_sample_registry()

    with tempfile.TemporaryDirectory() as tmpdir:
        out1 = Path(tmpdir) / "run1"
        out2 = Path(tmpdir) / "run2"
        pipeline1 = ArtifactPipeline(registry, repo_name=repo_name)
        pipeline2 = ArtifactPipeline(registry, repo_name=repo_name)
        artifacts1 = pipeline1.build_all_artifacts(output_dir=out1)
        artifacts2 = pipeline2.build_all_artifacts(output_dir=out2)

        if set(artifacts1.keys()) != set(artifacts2.keys()):
            errors.append("Artifact set differs between runs")
            return errors

        for name in artifacts1:
            text1 = artifacts1[name].read_text(encoding="utf-8")
            text2 = artifacts2[name].read_text(encoding="utf-8")
            if text1 != text2:
                errors.append(f"Non-deterministic output in {name}")

    return errors


def check_artifact_regression_patterns(repo_name: str = "regression-test") -> list[str]:
    """Check generated artifacts for known overclaim/anti-patterns."""
    errors: list[str] = []
    registry = _make_sample_registry()

    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = ArtifactPipeline(registry, repo_name=repo_name)
        artifacts = pipeline.build_all_artifacts(output_dir=tmpdir)

        for name, path in artifacts.items():
            text = path.read_text(encoding="utf-8")
            for pattern, reason in FORBIDDEN_ARTIFACT_PATTERNS.items():
                if pattern in text:
                    errors.append(f"{name}: {reason} (found '{pattern}')")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Skill-HQE anti-regression checks.")
    parser.add_argument("repo_path", nargs="?", type=Path, default=Path("."), help="Repository root to check")
    args = parser.parse_args(argv)

    repo_path = args.repo_path.resolve()
    errors: list[str] = []

    # 1. Run high-level validators.
    validators = [
        ("check_skill.py", [sys.executable, str(_SCRIPT_DIR / "check_skill.py"), str(repo_path)]),
        ("scan_secrets.py", [sys.executable, str(_SCRIPT_DIR / "scan_secrets.py"), str(repo_path), "--allowlist", str(repo_path / ".secretscanignore")]),
    ]
    for name, cmd in validators:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            errors.append(f"{name} failed:\n{result.stderr or result.stdout}")

    # 2. Artifact determinism and regression-pattern checks.
    errors.extend(check_artifact_determinism())
    errors.extend(check_artifact_regression_patterns())

    if errors:
        print("Anti-regression check FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("Anti-regression check PASSED: no deterministic drift or known anti-patterns detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
