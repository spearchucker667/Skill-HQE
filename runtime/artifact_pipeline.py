"""Deterministic artifact assembly pipeline for HQE audit deliverables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .finding_registry import FindingRegistry, Finding
from .session_manager import SessionManager


class ArtifactPipeline:
    def __init__(self, registry: FindingRegistry, session: SessionManager | None = None, repo_name: str = "repository"):
        self.registry = registry
        self.session = session
        self.repo_name = repo_name

    def generate_risk_register(self) -> str:
        """Assemble canonical Risk Register deliverable."""
        lines = [
            f"# Risk Register: {self.repo_name}",
            "",
            "| ID | Title | Category | Severity | Status | Exposure / Likelihood | Blast Radius |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        sorted_findings = sorted(
            self.registry.findings.values(),
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
        for f in sorted(self.registry.findings.values(), key=lambda x: (x.effort != "S", x.severity != "CRITICAL")):
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
        for f in self.registry.findings.values():
            by_cat.setdefault(f.category, []).append(f)

        for cat, items in sorted(by_cat.items()):
            if len(items) >= 1:
                lines.append(f"### {cat} Pattern Group ({len(items)} findings)")
                for item in items:
                    lines.append(f"- **{item.id}** ({item.severity}): {item.title} (`{item.affected_component}`)")
                lines.append("")
        return "\n".join(lines) + "\n"

    def generate_quick_wins_vs_structural(self) -> str:
        """Assemble Quick Wins vs Structural Work deliverable."""
        lines = [
            f"# Quick Wins vs Structural Work: {self.repo_name}",
            "",
            "## 🚀 Quick Wins (Effort S: <=2 files, Localized)",
            ""
        ]
        quick = [f for f in self.registry.findings.values() if f.effort == "S"]
        structural = [f for f in self.registry.findings.values() if f.effort in ("M", "L")]

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
        sec_findings = [f for f in self.registry.findings.values() if f.category == "SEC"]
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
            lines.append("No active security vulnerabilities detected.")
        return "\n".join(lines) + "\n"

    def generate_reliability_summary(self) -> str:
        """Assemble Reliability Summary deliverable."""
        rel_findings = [f for f in self.registry.findings.values() if f.category in ("BOOT", "REL")]
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
        for f in self.registry.findings.values():
            if f.validation:
                lines.append(f"### {f.id}: {f.title}")
                for cmd in f.validation:
                    lines.append(f"- `{cmd}`")
                lines.append("")
        return "\n".join(lines) + "\n"

    def generate_unknowns_verification(self) -> str:
        """Assemble Unknowns & Verification Hypotheses deliverable."""
        unknowns = [f for f in self.registry.findings.values() if f.confidence in ("HYPOTHESIS", "NEEDS_VERIFICATION")]
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
            lines.append("*(All findings verified as FACT or INFERENCE; zero unverified hypotheses)*")
        return "\n".join(lines) + "\n"

    def generate_confidence_declaration(self) -> str:
        """Assemble Confidence Declaration deliverable."""
        conf_counts = {c: 0 for c in ("FACT", "INFERENCE", "HYPOTHESIS", "NEEDS_VERIFICATION")}
        for f in self.registry.findings.values():
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

    def build_all_artifacts(self, output_dir: Path | str = "artifacts") -> dict[str, Path]:
        """Compile and write all 9 canonical deliverables."""
        out = Path(output_dir).resolve()
        out.mkdir(parents=True, exist_ok=True)

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
        }

        paths: dict[str, Path] = {}
        for filename, content in artifact_map.items():
            dest = out / filename
            dest.write_text(content, encoding="utf-8")
            paths[filename] = dest

        return paths
