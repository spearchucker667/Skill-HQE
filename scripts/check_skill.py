#!/usr/bin/env python3
"""Comprehensive Skill-HQE repository structure, links, schema, and syntax checker."""

from __future__ import annotations

import json
import os
import py_compile
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "NOTICE",
    "VERSION",
    "CHANGELOG.md",
    "pyproject.toml",
    "requirements-dev.txt",
    # Protocol
    "protocol/hqe-engineer.yaml",
    "protocol/hqe-engineer-schema.json",
    "protocol/hqe-schema.json",
    "protocol/validate.py",
    "protocol/verify.py",
    "protocol/README.md",
    "protocol/VALIDATORS.md",
    "protocol/HQE_v5_MIGRATION_NOTES.md",
    "protocol/SOURCE_CHECKSUMS.sha256",
    # References
    "references/hqe-protocol.md",
    "references/audit-methodology.md",
    "references/evidence-standard.md",
    "references/severity-confidence-effort.md",
    "references/health-scoring.md",
    "references/change-control.md",
    "references/blockers-and-unknowns.md",
    "references/pre-delivery-gates.md",
    "references/output-controls.md",
    "references/patch-packaging.md",
    "references/quality-gates.md",
    "references/reasoning-methodologies.md",
    "references/repository-orientation.md",
    "references/security-review.md",
    "references/reliability-review.md",
    "references/observability-review.md",
    "references/performance-review.md",
    "references/architecture-review.md",
    "references/testing-review.md",
    "references/dependency-review.md",
    "references/ci-cd-review.md",
    "references/documentation-review.md",
    "references/ux-dx-review.md",
    "references/boot-startup-review.md",
    "references/technical-debt-review.md",
    "references/remediation.md",
    "references/verification.md",
    "references/large-repo-strategy.md",
    "references/prompt-injection-defense.md",
    "references/source-lineage.md",
    # Workflows
    "workflows/full-audit.md",
    "workflows/targeted-bug-hunt.md",
    "workflows/security-audit.md",
    "workflows/architecture-audit.md",
    "workflows/performance-audit.md",
    "workflows/dependency-audit.md",
    "workflows/ci-audit.md",
    "workflows/testing-audit.md",
    "workflows/documentation-audit.md",
    "workflows/remediation-run.md",
    "workflows/verification-run.md",
    "workflows/regression-analysis.md",
    "workflows/pr-review.md",
    "workflows/incident-response.md",
    "workflows/debug-error.md",
    "workflows/trace-regression.md",
    "workflows/handoff-generation.md",
    # Templates
    "templates/finding.md",
    "templates/report.md",
    "templates/handoff.md",
    "templates/run-manifest.md",
    "templates/remediation-plan.md",
    "templates/validation-report.md",
    "templates/incident-mini-report.md",
    "templates/risk-register.md",
    "templates/master-todo-backlog.md",
    "templates/pattern-findings.md",
    "templates/quick-wins-vs-structural.md",
    "templates/security-posture-summary.md",
    "templates/reliability-summary.md",
    "templates/testing-gaps.md",
    "templates/unknowns-verification.md",
    "templates/confidence-declaration.md",
    "templates/session-log.md",
    "templates/redaction-log.md",
    "templates/patch-action.md",
    # Schemas
    "schemas/finding.schema.json",
    "schemas/findings.schema.json",
    "schemas/run-manifest.schema.json",
    "schemas/handoff.schema.json",
    "schemas/session-log.schema.json",
    "schemas/redaction-log.schema.json",
    "schemas/report.schema.json",
    # Scripts
    "scripts/inventory_repo.py",
    "scripts/detect_manifests.py",
    "scripts/detect_test_commands.py",
    "scripts/local_risk_scan.py",
    "scripts/redact_secrets.py",
    "scripts/summarize_tree.py",
    "scripts/validate_findings.py",
    "scripts/validate_manifest.py",
    "scripts/validate_session_log.py",
    "scripts/validate_semantics.py",
    "scripts/validate_protocol_bundle.py",
    "scripts/package_skill.py",
    "scripts/check_skill.py",
    # Docs
    "docs/ARCHITECTURE.md",
    "docs/SECURITY_MODEL.md",
    "docs/THREAT_MODEL.md",
    "docs/FINDING_SPECIFICATION.md",
    "docs/USER_GUIDE.md",
    "docs/DEVELOPER_GUIDE.md",
    "docs/CAPABILITY_MAPPING.md",
    "docs/MIGRATION_FROM_HQE_WORKBENCH.md",
    "docs/DESIGN_DECISIONS.md",
    "docs/SOURCE_AUDIT.md",
]

REQUIRED_SKILL_TERMS = [
    "Phase -1",
    "Phase 0",
    "protocol/hqe-engineer.yaml",
    "5.0.0",
    "NEEDS_VERIFICATION",
    "Zero Hallucination",
    "Mandatory Evidence",
    "No Secret Leakage",
    "Minimal Change",
    "Health Scoring",
    "Severity Gates",
    "Taint Chains",
    "Change Budget",
    "Stop-the-Line",
    "Pre-Delivery",
]

MD_LINK_RE = re.compile(r'\[([^\]]+)\]\((?!https?://|mailto:|#|conversation://)([^)]+)\)')


def check_skill(root_path: Path) -> list[str]:
    """Execute complete integrity checks on Skill-HQE repository."""
    root = root_path.resolve()
    errors: list[str] = []

    # 1. Required Files Presence
    for req in REQUIRED_FILES:
        p = root / req
        if not p.is_file():
            errors.append(f"Missing required file: {req}")

    # 2. SKILL.md Control Plane Invariants
    skill_file = root / "SKILL.md"
    if skill_file.is_file():
        skill_text = skill_file.read_text(encoding="utf-8", errors="replace")
        for term in REQUIRED_SKILL_TERMS:
            if term.lower() not in skill_text.lower():
                errors.append(f"SKILL.md missing required control plane concept: '{term}'")

    # 3. JSON Schemas Self-Validation (Draft-7)
    try:
        from jsonschema import Draft7Validator
        has_jsonschema = True
    except ImportError:
        has_jsonschema = False
        errors.append("jsonschema package not installed for schema self-validation")

    schema_dir = root / "schemas"
    if schema_dir.is_dir():
        for s_file in schema_dir.glob("*.schema.json"):
            try:
                with s_file.open("r", encoding="utf-8") as fh:
                    s_data = json.load(fh)
                if has_jsonschema:
                    Draft7Validator.check_schema(s_data)
            except Exception as exc:
                errors.append(f"Schema validation error in {s_file.name}: {exc}")

    # 4. Markdown Relative Link Verification
    for md_file in root.rglob("*.md"):
        # Skip package subfolder or git
        rel_str = str(md_file.relative_to(root))
        if "HQE_PROTOCOL_SKILL_EMBED_PACKAGE" in rel_str or ".git" in rel_str:
            continue

        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
            for match in MD_LINK_RE.finditer(content):
                target_str = match.group(2).split("#")[0].strip()
                if not target_str:
                    continue
                # Resolve relative to current md file
                target_path = (md_file.parent / target_str).resolve()
                if not target_path.exists():
                    errors.append(f"Broken relative link in {rel_str} -> '{target_str}'")
        except Exception as exc:
            errors.append(f"Error reading {rel_str}: {exc}")

    # 5. Python Syntax Compilation
    for py_file in root.rglob("*.py"):
        rel_str = str(py_file.relative_to(root))
        if "HQE_PROTOCOL_SKILL_EMBED_PACKAGE" in rel_str or ".git" in rel_str:
            continue
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"Python syntax error in {rel_str}: {exc}")

    # 6. Check for Forbidden Source Path Leaks (outside migration/lineage docs)
    source_path_str = "/Users/super_user/Projects/HQE-Workbench"
    allowed_leak_files = {
        "docs/MIGRATION_FROM_HQE_WORKBENCH.md",
        "references/source-lineage.md",
        "docs/SOURCE_AUDIT.md",
        "docs/CAPABILITY_MAPPING.md",
        "docs/DESIGN_DECISIONS.md",
        "HQE_SKILL_PARITY_REPAIR_AGENT_HANDOFF.md",
        "HQE_SKILL_AGENT_HANDOFF.md",
        "HQE_SKILL_CONVERSION_PROMPT.md",
        "START_AGENT_PROMPT.md",
        "PROTOCOL_EMBEDDING_AGENT_HANDOFF.md",
        "scripts/check_skill.py"
    }

    for text_file in root.rglob("*"):
        if not text_file.is_file():
            continue
        rel_str = str(text_file.relative_to(root))
        if any(skip in rel_str for skip in ("HQE_PROTOCOL_SKILL_EMBED_PACKAGE", ".git", ".pytest_cache", "tests/fixtures", "__pycache__")):
            continue
        if rel_str in allowed_leak_files:
            continue

        try:
            content = text_file.read_text(encoding="utf-8", errors="replace")
            if source_path_str in content:
                errors.append(f"Unsanitized source path '{source_path_str}' in {rel_str}")
        except Exception:
            pass

    return errors


def main() -> int:
    path_arg = sys.argv[1] if len(sys.argv) > 1 else "."
    errors = check_skill(Path(path_arg))

    if errors:
        print(f"Skill validation FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("Skill check PASSED: All structure, schema, markdown link, and syntax checks succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
