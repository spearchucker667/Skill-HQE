"""Deterministic artifact assembly pipeline for HQE audit deliverables."""

from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from .finding_registry import FindingRegistry, Finding
from .redaction_engine import TypedRedactionEngine
from .session_manager import SessionManager

_PROTOCOL_YAML = Path(__file__).resolve().parents[1] / "protocol" / "hqe-engineer.yaml"
_SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "schemas"


def _derive_protocol_version() -> str:
    """Read the canonical protocol version from the HQE protocol YAML."""
    try:
        data = yaml.safe_load(_PROTOCOL_YAML.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            version = data.get("protocol_version") or data.get("schema_version")
            if version:
                return str(version)
    except Exception:
        pass
    return "unknown"


def _derive_output_controls() -> dict[str, Any]:
    """Read output controls from the canonical HQE protocol YAML."""
    try:
        data = yaml.safe_load(_PROTOCOL_YAML.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data.get("output_controls", {}) or {}
    except Exception:
        pass
    return {}


def _apply_output_caps(findings, size_limits: dict[str, Any] | None) -> list:
    """Apply per-category output caps from the protocol.

    CRITICAL/HIGH findings are uncapped by default. MEDIUM findings are capped
    per category. LOW/INFO findings are capped per category. Findings are
    prioritized by severity and then by stable ID.
    """
    if size_limits is None:
        size_limits = {}

    medium_max = size_limits.get("medium_max_per_category")
    low_info_max = size_limits.get("low_and_info_max_per_category")
    critical_high_max = size_limits.get("critical_and_high_max_total")

    by_cat: dict[str, list] = {}
    for finding in findings:
        by_cat.setdefault(finding.category, []).append(finding)

    severity_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    result = []
    for cat, items in by_cat.items():
        items = sorted(
            items,
            key=lambda f: (severity_rank.get(f.severity, 5), f.id)
        )
        critical_high = [f for f in items if f.severity in ("CRITICAL", "HIGH")]
        medium = [f for f in items if f.severity == "MEDIUM"]
        low_info = [f for f in items if f.severity in ("LOW", "INFO")]

        if critical_high_max is not None:
            critical_high = critical_high[:critical_high_max]
        if medium_max is not None:
            medium = medium[:medium_max]
        if low_info_max is not None:
            low_info = low_info[:low_info_max]

        result.extend(critical_high + medium + low_info)

    return sorted(result, key=lambda f: f.id)


def _score_to_report_band(score: int | None) -> str:
    """Map internal health score band to report.schema.json enum values."""
    if score is None:
        return "Unknown"
    if score >= 9:
        return "Production-ready"
    if score >= 7:
        return "Solid"
    if score >= 5:
        return "Fragile"
    if score >= 3:
        return "Unstable"
    return "Broken"


def _validate_json_artifact(data: dict[str, Any], schema_name: str) -> None:
    """Validate artifact payload against canonical schemas in schemas/ directory."""
    try:
        from jsonschema import validate as jsonschema_validate
        from referencing import Registry, Resource
    except ImportError:
        return

    schema_path = _SCHEMAS_DIR / schema_name
    if not schema_path.is_file():
        return

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    reg = Registry()
    for ref_schema_file in _SCHEMAS_DIR.glob("*.schema.json"):
        try:
            ref_data = json.loads(ref_schema_file.read_text(encoding="utf-8"))
            reg = reg.with_resource(ref_schema_file.name, Resource.from_contents(ref_data))
        except Exception:
            pass

    jsonschema_validate(instance=data, schema=schema, registry=reg)


class ArtifactPipeline:
    def __init__(
        self,
        registry: FindingRegistry,
        session: SessionManager | None = None,
        repo_name: str = "repository",
        redaction_engine: TypedRedactionEngine | None = None,
    ):
        self.registry = registry
        self.session = session
        self.repo_name = repo_name
        self.redaction_engine = redaction_engine
        self._output_limits = _derive_output_controls().get("size_limits")

    def _capped_findings(self):
        """Return registry findings after applying protocol output caps."""
        return _apply_output_caps(self.registry.findings.values(), self._output_limits)

    def generate_risk_register(self) -> str:
        """Assemble canonical Risk Register deliverable."""
        lines = [
            f"# Risk Register: {self.repo_name}",
            "",
            "| ID | Title | Category | Severity | Status | Exposure / Likelihood | Blast Radius |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        sorted_findings = sorted(
            self._capped_findings(),
            key=lambda f: ({"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}.get(f.severity, 5), f.id)
        )
        for f in sorted_findings:
            exp = f.likelihood or "N/A"
            blast = f.blast_radius or "N/A"
            lines.append(f"| {f.id} | {f.title} | {f.category} | {f.severity} | {f.status} | {exp} | {blast} |")
        return "\n".join(lines) + "\n"

    def generate_master_todo(self) -> str:
        """Assemble canonical Master TODO Backlog deliverable."""
        lines = [
            f"# Master TODO Backlog: {self.repo_name}",
            "",
            "| Priority | Finding ID | Title | Effort | Regression Risk | Remediation Target |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        priority = 1
        # Priority: severity > confidence > effort.  Higher-severity, more-certain,
        # smaller-effort items are addressed first.
        severity_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        confidence_rank = {"FACT": 0, "INFERENCE": 1, "HYPOTHESIS": 2, "NEEDS_VERIFICATION": 3}
        effort_rank = {"S": 0, "M": 1, "L": 2}
        for f in sorted(
            self._capped_findings(),
            key=lambda x: (
                severity_rank.get(x.severity, 5),
                confidence_rank.get(x.confidence, 4),
                effort_rank.get(x.effort, 3),
            ),
        ):
            lines.append(f"| P{priority} | {f.id} | {f.title} | {f.effort} | {f.regression_risk} | `{f.affected_component}` |")
            priority += 1
        return "\n".join(lines) + "\n"

    def generate_pattern_findings(self) -> str:
        """Assemble Cross-Cutting Pattern Findings deliverable."""
        lines = [
            f"# Pattern & Architectural Findings: {self.repo_name}",
            "",
            "## Identified Systematic Patterns",
            ""
        ]
        by_cat: dict[str, list[Finding]] = {}
        for f in self._capped_findings():
            by_cat.setdefault(f.category, []).append(f)

        for cat, items in sorted(by_cat.items()):
            # A pattern group requires at least two related occurrences; a single
            # finding is an isolated issue, not a systematic pattern.
            if len(items) >= 2:
                lines.append(f"### {cat} Pattern Group ({len(items)} findings)")
                for item in items:
                    lines.append(f"- **{item.id}** ({item.severity}): {item.title} (`{item.affected_component}`)")
                lines.append("")
        if len(lines) == 4:
            lines.append("*(No systematic patterns with two or more occurrences identified)*")
        return "\n".join(lines) + "\n"

    def generate_quick_wins_vs_structural(self) -> str:
        """Assemble Quick Wins vs Structural Work deliverable."""
        lines = [
            f"# Quick Wins vs Structural Work: {self.repo_name}",
            "",
            "## 🚀 Quick Wins (Effort S: <=2 files, Localized)",
            ""
        ]
        quick = [f for f in self._capped_findings() if f.effort == "S"]
        structural = [f for f in self._capped_findings() if f.effort in ("M", "L")]

        for q in quick:
            lines.append(f"- [ ] **{q.id}**: {q.title} — `{q.affected_component}`")
        if not quick:
            lines.append("*(No single-file quick wins identified)*")

        lines.extend([
            "",
            "## 🏗️ Structural & Architectural Work (Effort M/L: >2 files, Cross-cutting)",
            ""
        ])
        for s in structural:
            lines.append(f"- [ ] **{s.id}** (Effort {s.effort}): {s.title} — `{s.affected_component}`")
        if not structural:
            lines.append("*(No structural refactorings required)*")

        return "\n".join(lines) + "\n"

    def generate_security_posture(self) -> str:
        """Assemble Security Posture Summary deliverable."""
        sec_findings = [f for f in self._capped_findings() if f.category == "SEC"]
        lines = [
            f"# Security Posture Summary: {self.repo_name}",
            "",
            f"**Total Security Findings:** {len(sec_findings)}",
            ""
        ]
        for f in sec_findings:
            lines.append(f"### {f.id} — {f.title} ({f.severity})")
            lines.append(f"- **Component:** `{f.affected_component}`")
            lines.append(f"- **Observed:** {f.observed_behavior}")
            lines.append(f"- **Expected:** {f.expected_behavior}")
            if f.taint_chain:
                lines.append(f"- **Taint Chain:** Source `{f.taint_chain.get('source')}` -> Sink `{f.taint_chain.get('sink')}`")
            lines.append(f"- **Remediation:** {f.remediation}")
            lines.append("")
        if not sec_findings:
            lines.append("No active security findings recorded in this audit.")
            lines.append("This is not a guarantee of complete security coverage.")
        return "\n".join(lines) + "\n"

    def generate_reliability_summary(self) -> str:
        """Assemble Reliability Summary deliverable."""
        rel_findings = [f for f in self._capped_findings() if f.category in ("BOOT", "REL")]
        lines = [
            f"# Reliability & Startup Posture: {self.repo_name}",
            "",
            f"**Reliability / Boot Findings:** {len(rel_findings)}",
            ""
        ]
        for f in rel_findings:
            lines.append(f"- **{f.id}** ({f.severity}): {f.title} (`{f.affected_component}`)")
            lines.append(f"  - Impact: {f.impact}")
            lines.append(f"  - Root Cause: {f.root_cause}")
        return "\n".join(lines) + "\n"

    def generate_testing_gaps(self) -> str:
        """Assemble Testing Gaps deliverable."""
        lines = [
            f"# Testing Gaps & Verification Debt: {self.repo_name}",
            "",
            "## Required Verification Suites"
        ]
        for f in self._capped_findings():
            if f.validation:
                lines.append(f"### {f.id}: {f.title}")
                for cmd in f.validation:
                    lines.append(f"- `{cmd}`")
                lines.append("")
        return "\n".join(lines) + "\n"

    def generate_unknowns_verification(self) -> str:
        """Assemble Unknowns & Verification Hypotheses deliverable."""
        unknowns = [f for f in self._capped_findings() if f.confidence in ("HYPOTHESIS", "NEEDS_VERIFICATION")]
        lines = [
            f"# Unknowns, Assumptions & Verification Plan: {self.repo_name}",
            "",
            "## Hypotheses Requiring Live Verification",
            ""
        ]
        for u in unknowns:
            lines.append(f"- **{u.id}** `[{u.confidence}]`: {u.title}")
            lines.append(f"  - Component: `{u.affected_component}`")
            lines.append(f"  - Verification Need: {u.reproduction or 'Requires sandbox run'}")
        if not unknowns:
            lines.append("*(No unverified hypotheses recorded in this audit.)*")
            lines.append("Absence of recorded unknowns does not imply complete certainty.")
        return "\n".join(lines) + "\n"

    def generate_confidence_declaration(self) -> str:
        """Assemble Confidence Declaration deliverable."""
        conf_counts = {c: 0 for c in ("FACT", "INFERENCE", "HYPOTHESIS", "NEEDS_VERIFICATION")}
        for f in self._capped_findings():
            conf_counts[f.confidence] = conf_counts.get(f.confidence, 0) + 1

        lines = [
            f"# Audit Confidence Declaration: {self.repo_name}",
            "",
            "| Confidence Level | Count | Definition |",
            "| :--- | :--- | :--- |",
            f"| **FACT** | {conf_counts['FACT']} | Directly verified in code / executed tests |",
            f"| **INFERENCE** | {conf_counts['INFERENCE']} | Logically derived from call graph / configs |",
            f"| **HYPOTHESIS** | {conf_counts['HYPOTHESIS']} | Suspected behavior requiring validation |",
            f"| **NEEDS_VERIFICATION** | {conf_counts['NEEDS_VERIFICATION']} | Blocked by missing runtime / environment |",
            ""
        ]
        return "\n".join(lines) + "\n"

    def generate_incident_mini_report(self) -> str:
        """Assemble Incident Mini-Report for active security incidents."""
        sec_incidents = [
            f for f in self._capped_findings()
            if f.category == "SEC" and f.severity in ("CRITICAL", "HIGH") and f.status not in ("VERIFIED", "REJECTED", "DEFERRED")
        ]
        lines = [
            f"# Incident Mini-Report: {self.repo_name}",
            "",
            f"**Active Security Incidents:** {len(sec_incidents)}",
            ""
        ]
        if not sec_incidents:
            lines.append("No active CRITICAL/HIGH security incidents.")
        for f in sec_incidents:
            lines.append(f"## {f.id} — {f.title}")
            lines.append(f"- **Impacted paths:** `{f.affected_component}`")
            lines.append(f"- **Evidence:** {f.observed_behavior}")
            if f.taint_chain:
                lines.append(
                    f"- **Indicators:** Source `{f.taint_chain.get('source')}` -> "
                    f"Sink `{f.taint_chain.get('sink')}`"
                )
            lines.append(f"- **Containment:** {f.remediation}")
            lines.append(f"- **Safe verification:** {f.validation or 'See remediation plan'}")
            lines.append(f"- **Blockers:** {f.reproduction or 'None documented'}")
            lines.append(f"- **Resume criteria:** Verification commands pass and findings transition to VERIFIED")
            lines.append("")
        return "\n".join(lines) + "\n"

    def generate_patch_actions(self) -> str:
        """Assemble Patch Actions deliverable for all open findings."""
        open_findings = [f for f in self._capped_findings() if f.status not in ("VERIFIED", "REJECTED", "DEFERRED")]
        lines = [
            f"# Patch Actions: {self.repo_name}",
            "",
            "One patch per finding with exact intended change, diff, validation, and rollback.",
            ""
        ]
        for f in sorted(open_findings, key=lambda x: x.id):
            lines.append(f"## {f.id} — {f.title}")
            lines.append(f"**Files:** `{f.affected_component}`")
            lines.append(f"**Exact Intended Change:** {f.remediation}")
            lines.append("**Patch:**")
            lines.append("```diff")
            lines.append("# TODO: append minimal diff once change is implemented")
            lines.append("```")
            lines.append(f"**Validation:** {f.validation or 'N/A'}")
            lines.append("**Expected Result:** Finding transitions to VERIFIED; no regressions.")
            lines.append("**Rollback:** Revert the diff and re-run validation.")
            lines.append("")
        return "\n".join(lines) + "\n"

    def generate_remediation_plan(self) -> str:
        """Assemble Remediation Plan deliverable."""
        open_findings = [f for f in self._capped_findings() if f.status not in ("VERIFIED", "REJECTED", "DEFERRED")]
        lines = [
            f"# Remediation Plan: {self.repo_name}",
            "",
            f"**Total findings addressed:** {len(open_findings)}",
            "",
            "## Findings",
            "",
            "| ID | Title | Severity | Effort | Status |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]
        severity_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        for f in sorted(open_findings, key=lambda x: (severity_rank.get(x.severity, 5), x.id)):
            lines.append(f"| {f.id} | {f.title} | {f.severity} | {f.effort} | {f.status} |")

        lines.extend([
            "",
            "## Phases",
            "",
            "### Phase 1: Containment / Safety",
            "",
            "**Objective:** Stop exploitation paths and prevent regression.",
            "",
            "**Actions:**",
            "- [ ] Address all CRITICAL findings",
            "- [ ] Add regression tests for HIGH findings",
            "",
            "**Exit criteria:**",
            "- [ ] No CRITICAL findings remain OPEN",
            "- [ ] CI passes",
            "",
            "### Phase 2: Minimal Fixes",
            "",
            "**Objective:** Resolve HIGH/MEDIUM findings with smallest safe change.",
            "",
            "**Actions:**",
            "- [ ] Apply patch actions",
            "**Exit criteria:**",
            "- [ ] All HIGH findings transition to VERIFIED or DEFERRED",
            "",
            "### Phase 3: Verification",
            "",
            "**Objective:** Prove fixes work and no regressions introduced.",
            "",
            "**Actions:**",
            "- [ ] Run validation commands from each finding",
            "",
            "**Exit criteria:**",
            "- [ ] All validation commands pass",
            "",
            "## Patch Actions",
            "",
            "See `PATCH_ACTIONS.md`.",
            "",
            "## Verification Commands",
            ""
        ])
        for f in open_findings:
            if f.validation:
                lines.append(f"### {f.id}")
                for cmd in f.validation:
                    lines.append(f"- `{cmd}`")
                lines.append("")
        return "\n".join(lines) + "\n"

    def generate_validation_report(self) -> str:
        """Assemble Validation Report deliverable."""
        lines = [
            f"# Validation Report: {self.repo_name}",
            "",
            "## Summary",
            "",
            "Validation results for findings with explicit verification commands.",
            "",
            "## Findings Validated",
            "",
            "| Finding ID | Status | Commands | Expected | Actual | Notes |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for f in self._capped_findings():
            if f.validation:
                cmds = "; ".join(f.validation)
                lines.append(
                    f"| {f.id} | NOT_VERIFIED | `{cmds}` | Fix verified | (run commands) | {f.confidence} |"
                )
        return "\n".join(lines) + "\n"

    def generate_redaction_log(self) -> str:
        """Assemble Redaction Log deliverable."""
        data = self._build_redaction_log_data()
        lines = [
            f"# Redaction Log: {self.repo_name}",
            "",
            f"**Run ID:** {data['run_id']}",
            f"**Timestamp:** {data['timestamp']}",
            f"**Total Redactions:** {data['total_redactions']}",
            f"**Files Scanned:** {data.get('files_scanned', 0)}",
            "",
            "## Redactions by Type",
            ""
        ]
        if data["by_type"]:
            for secret_type, count in sorted(data["by_type"].items()):
                lines.append(f"- **{secret_type}**: {count}")
        else:
            lines.append("*(No secrets redacted during this audit)*")

        lines.extend(["", "## Detailed Redactions", ""])
        redactions = data.get("redactions", [])
        if redactions:
            lines.append("| File | Line | Secret Type | Replacement |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for r in redactions:
                line = r.get("line", "N/A")
                lines.append(f"| {r['file']} | {line} | {r['secret_type']} | {r['replacement']} |")
        else:
            lines.append("*(No detailed redaction records)*")

        return "\n".join(lines) + "\n"

    def _build_redaction_log_data(self) -> dict[str, Any]:
        """Build redaction log payload matching redaction-log.schema.json.

        The timestamp is derived from the session when available so that repeated
        artifact generation with the same session is deterministic. Without a
        session a stable placeholder is used.
        """
        run_id = self.session.session_id if self.session else "hqe-redaction-run"
        timestamp = self.session.started_at if self.session else "1970-01-01T00:00:00Z"
        if self.redaction_engine:
            summary = self.redaction_engine.typed_summary()
            redactions: list[dict[str, Any]] = []
            for entry in summary.get("typed_entries", []):
                redactions.append({
                    "file": entry["file"],
                    "secret_type": entry["secret_type"],
                    "replacement": entry["replacement"]
                })
            return {
                "run_id": run_id,
                "timestamp": timestamp,
                "total_redactions": summary["total_redactions"],
                "by_type": summary["by_type"],
                "files_scanned": 0,
                "redactions": redactions
            }
        return {
            "run_id": run_id,
            "timestamp": timestamp,
            "total_redactions": 0,
            "by_type": {},
            "files_scanned": 0,
            "redactions": []
        }

    def generate_patch_actions_json(self) -> dict[str, Any]:
        """Return JSON Patch Actions payload matching patch-actions.schema.json.

        Only open findings receive remediation instructions; findings already
        VERIFIED, REJECTED, or DEFERRED must not produce patch actions.
        """
        open_findings = [f for f in self._capped_findings() if f.status not in ("VERIFIED", "REJECTED", "DEFERRED")]
        actions = []
        for f in sorted(open_findings, key=lambda x: x.id):
            actions.append({
                "finding_id": f.id,
                "files": [f.affected_component],
                "exact_intended_change": f.remediation,
                "patch": "",
                "validation": list(f.validation),
                "expected_result": "Finding transitions to VERIFIED; no regressions.",
                "rollback": [f"Revert changes for {f.id} and re-run validation."]
            })
        return {"patch_actions": actions}

    def generate_remediation_plan_json(self) -> dict[str, Any]:
        """Return JSON Remediation Plan payload matching remediation-plan.schema.json."""
        open_findings = [f for f in self._capped_findings() if f.status not in ("VERIFIED", "REJECTED", "DEFERRED")]
        phases = [
            {
                "phase": "Containment / Safety",
                "objective": "Stop exploitation paths and prevent regression.",
                "actions": ["Address all CRITICAL findings", "Add regression tests for HIGH findings"],
                "exit_criteria": ["No CRITICAL findings remain OPEN", "CI passes"]
            },
            {
                "phase": "Minimal Fixes",
                "objective": "Resolve HIGH/MEDIUM findings with smallest safe change.",
                "actions": ["Apply patch actions"],
                "exit_criteria": ["All HIGH findings transition to VERIFIED or DEFERRED"]
            },
            {
                "phase": "Verification",
                "objective": "Prove fixes work and no regressions introduced.",
                "actions": ["Run validation commands from each finding"],
                "exit_criteria": ["All validation commands pass"]
            }
        ]
        verification: list[str] = []
        for f in open_findings:
            verification.extend(f.validation)
        severity_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        return {
            "title": f"Remediation Plan: {self.repo_name}",
            "findings": [f.id for f in sorted(open_findings, key=lambda x: (severity_rank.get(x.severity, 5), x.id))],
            "phases": phases,
            "patches": self.generate_patch_actions_json()["patch_actions"],
            "verification": verification
        }

    def generate_validation_report_json(self) -> dict[str, Any]:
        """Return JSON Validation Report payload matching validation-report.schema.json."""
        findings_validated = []
        for f in self._capped_findings():
            if f.validation:
                findings_validated.append({
                    "finding_id": f.id,
                    "status": "NOT_VERIFIED",
                    "validation_commands": list(f.validation),
                    "expected_results": ["Fix verified"],
                    "actual_results": [],
                    "notes": f.confidence
                })
        return {
            "title": f"Validation Report: {self.repo_name}",
            "findings_validated": findings_validated,
            "summary": "Validation results for findings with explicit verification commands."
        }

    def generate_redaction_log_json(self) -> dict[str, Any]:
        """Return JSON Redaction Log payload matching redaction-log.schema.json."""
        return self._build_redaction_log_data()

    def _repo_root(self) -> str:
        """Derive normalized repository root path."""
        if self.session and self.session.repository_path:
            return self.session.repository_path
        return str(Path.cwd())

    def _get_git_commit(self) -> str:
        """Return the current git HEAD commit hash or 'unknown'."""
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self._repo_root(),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def _get_git_branch(self) -> str:
        """Return the current git branch or 'unknown'."""
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self._repo_root(),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def generate_report_json(self) -> dict[str, Any]:
        """Return JSON Report payload matching report.schema.json.

        The report aligns with the Workbench ``HqeReport`` model by providing
        run identity, repository context, a coverage-aware health score, an
        executive summary with severity counts, and the full findings list.
        """
        run_id = self.session.session_id if self.session else "hqe-report-run"
        timestamp = (
            self.session.started_at
            if self.session
            else "1970-01-01T00:00:00Z"
        )
        repo_path = self._repo_root()
        protocol_version = _derive_protocol_version()

        health = self.registry.health_score()
        score = health.score
        band = _score_to_report_band(health.score)
        reasons = list(health.reasons) if health.reasons else [f"Evaluated against HQE v{protocol_version} rubric"]

        counts = self.registry.count_by_severity()
        open_findings = [f for f in self._capped_findings() if f.status not in ("VERIFIED", "REJECTED", "DEFERRED")]
        critical_high = [f for f in open_findings if f.severity in ("CRITICAL", "HIGH")]
        severity_rank = {"CRITICAL": 0, "HIGH": 1}
        sorted_critical_high = sorted(
            critical_high,
            key=lambda f: (severity_rank.get(f.severity, 2), f.id),
        )

        top_priorities = [f"{f.id}: {f.title}" for f in sorted_critical_high]
        blockers = [
            f"{f.id} ({f.severity}) — {f.affected_component}: {f.title}"
            for f in sorted_critical_high
        ]

        return {
            "run_id": run_id,
            "protocol_version": protocol_version,
            "timestamp": timestamp,
            "repository": {
                "name": self.repo_name,
                "path": repo_path,
                "commit": self._get_git_commit(),
                "branch": self._get_git_branch(),
            },
            "health_score": {
                "score": score,
                "band": band,
                "omitted": health.omitted,
                "reasons": reasons,
            },
            "executive_summary": {
                "top_priorities": top_priorities,
                "critical_count": counts.get("CRITICAL", 0),
                "high_count": counts.get("HIGH", 0),
                "medium_count": counts.get("MEDIUM", 0),
                "low_count": counts.get("LOW", 0),
                "blockers": blockers,
            },
            "findings": self.registry.to_list(),
        }

    def build_all_artifacts(self, output_dir: Path | str = "artifacts") -> dict[str, Path]:
        """Compile, validate against schemas, and write all canonical deliverables."""
        out = Path(output_dir).resolve()
        out.mkdir(parents=True, exist_ok=True)

        patch_actions_json = self.generate_patch_actions_json()
        remediation_plan_json = self.generate_remediation_plan_json()
        validation_report_json = self.generate_validation_report_json()
        redaction_log_json = self.generate_redaction_log_json()
        report_json = self.generate_report_json()

        # Enforce canonical schema contracts before emitting machine deliverables
        _validate_json_artifact(patch_actions_json, "patch-actions.schema.json")
        _validate_json_artifact(remediation_plan_json, "remediation-plan.schema.json")
        _validate_json_artifact(validation_report_json, "validation-report.schema.json")
        _validate_json_artifact(redaction_log_json, "redaction-log.schema.json")
        _validate_json_artifact(report_json, "report.schema.json")

        artifact_map = {
            "RISK_REGISTER.md": self.generate_risk_register(),
            "MASTER_TODO_BACKLOG.md": self.generate_master_todo(),
            "PATTERN_FINDINGS.md": self.generate_pattern_findings(),
            "QUICK_WINS_VS_STRUCTURAL.md": self.generate_quick_wins_vs_structural(),
            "SECURITY_POSTURE_SUMMARY.md": self.generate_security_posture(),
            "RELIABILITY_SUMMARY.md": self.generate_reliability_summary(),
            "TESTING_GAPS.md": self.generate_testing_gaps(),
            "UNKNOWNS_VERIFICATION.md": self.generate_unknowns_verification(),
            "CONFIDENCE_DECLARATION.md": self.generate_confidence_declaration(),
            "INCIDENT_MINI_REPORT.md": self.generate_incident_mini_report(),
            "PATCH_ACTIONS.md": self.generate_patch_actions(),
            "REMEDIATION_PLAN.md": self.generate_remediation_plan(),
            "VALIDATION_REPORT.md": self.generate_validation_report(),
            "REDACTION_LOG.md": self.generate_redaction_log(),
            "PATCH_ACTIONS.json": json.dumps(patch_actions_json, indent=2),
            "REMEDIATION_PLAN.json": json.dumps(remediation_plan_json, indent=2),
            "VALIDATION_REPORT.json": json.dumps(validation_report_json, indent=2),
            "REDACTION_LOG.json": json.dumps(redaction_log_json, indent=2),
            "REPORT.json": json.dumps(report_json, indent=2),
        }

        paths: dict[str, Path] = {}
        for filename, content in artifact_map.items():
            dest = out / filename
            dest.write_text(content, encoding="utf-8")
            paths[filename] = dest

        return paths
