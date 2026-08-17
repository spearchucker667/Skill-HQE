"""Finding registry and lifecycle state machine for HQE."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

from .evidence_store import CodeEvidence
from .health_scoring import HealthScore, compute_health_score

ID_RE = re.compile(r"^HQE-(BOOT|SEC|BUG|REL|PERF|UX|DX|DOC|DEBT|DEPS)-[0-9]{3,}$")

VALID_CATEGORIES = {"BOOT", "SEC", "BUG", "REL", "PERF", "UX", "DX", "DOC", "DEBT", "DEPS"}
VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
VALID_CONFIDENCE = {"FACT", "INFERENCE", "HYPOTHESIS", "NEEDS_VERIFICATION"}
VALID_STATUSES = {
    "CONFIRMED", "STRONGLY_SUPPORTED", "SUSPECTED",
    "NOT_REPRODUCED", "FIXED", "REOPENED", "SUPERSEDED"
}
VALID_EFFORTS = {"S", "M", "L"}

# HQE v5 lifecycle transition graph. Terminal states have no outbound edges
# unless explicitly reopened/superseded through dedicated APIs.
TRANSITION_GRAPH: dict[str, set[str]] = {
    "SUSPECTED": {"STRONGLY_SUPPORTED", "CONFIRMED", "NOT_REPRODUCED"},
    "STRONGLY_SUPPORTED": {"CONFIRMED", "SUSPECTED", "NOT_REPRODUCED"},
    "NOT_REPRODUCED": {"SUSPECTED", "STRONGLY_SUPPORTED"},
    "CONFIRMED": {"FIXED", "SUPERSEDED"},
    "FIXED": {"REOPENED"},
    "REOPENED": {"CONFIRMED", "FIXED"},
    "SUPERSEDED": set(),
}


@dataclass
class Finding:
    id: str
    title: str
    category: str
    severity: str
    confidence: str
    status: str
    affected_component: str
    observed_behavior: str
    expected_behavior: str
    root_cause: str
    impact: str
    remediation: str
    effort: str
    regression_risk: str
    evidence: list[CodeEvidence] = field(default_factory=list)
    reproduction: str | None = None
    preconditions: list[str] = field(default_factory=list)
    exploitability: str | None = None
    blast_radius: str | None = None
    likelihood: str | None = None
    likelihood_justification: str | None = None
    exposure_evidence: str | None = None
    taint_chain: dict[str, Any] | None = None
    validation: list[str] = field(default_factory=list)
    related_findings: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Validate all semantic and schema invariants for this finding."""
        errors: list[str] = []

        # 1. ID check
        m = ID_RE.match(self.id)
        if not m:
            errors.append(f"Invalid finding ID pattern: '{self.id}'")
        else:
            cat_prefix = m.group(1)
            if cat_prefix != self.category:
                errors.append(f"ID prefix '{cat_prefix}' does not match category '{self.category}'")

        if self.category not in VALID_CATEGORIES:
            errors.append(f"Invalid category: '{self.category}'")
        if self.severity not in VALID_SEVERITIES:
            errors.append(f"Invalid severity: '{self.severity}'")
        if self.confidence not in VALID_CONFIDENCE:
            errors.append(f"Invalid confidence tag: '{self.confidence}'")
        if self.status not in VALID_STATUSES:
            errors.append(f"Invalid status: '{self.status}'")
        if self.effort not in VALID_EFFORTS:
            errors.append(f"Invalid effort tier: '{self.effort}'")

        if not self.evidence:
            errors.append(f"Finding '{self.id}' must have at least one evidence item")

        # Severity Gate check for CRITICAL / HIGH
        if self.severity in ("CRITICAL", "HIGH"):
            if not self.preconditions:
                errors.append(f"Severity is {self.severity} but 'preconditions' is empty")
            if not self.exploitability:
                errors.append(f"Severity is {self.severity} but 'exploitability' is missing")
            if not self.blast_radius:
                errors.append(f"Severity is {self.severity} but 'blast_radius' is missing")
            if not self.likelihood:
                errors.append(f"Severity is {self.severity} but 'likelihood' is missing")
            if not self.likelihood_justification:
                errors.append(f"Severity is {self.severity} but 'likelihood_justification' is missing")
            if not self.exposure_evidence:
                errors.append(f"Severity is {self.severity} but 'exposure_evidence' is missing")

        # Taint Chain for SEC
        if self.category == "SEC" and self.severity in ("CRITICAL", "HIGH"):
            if not self.taint_chain or not isinstance(self.taint_chain, dict):
                errors.append(f"Security finding with {self.severity} severity must include 'taint_chain'")
            else:
                for k in ("source", "transforms", "validation_boundary", "sink", "impact"):
                    if not self.taint_chain.get(k):
                        errors.append(f"taint_chain missing '{k}'")

        return errors

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "severity": self.severity,
            "confidence": self.confidence,
            "status": self.status,
            "affected_component": self.affected_component,
            "evidence": [ev.to_dict() if isinstance(ev, CodeEvidence) else ev for ev in self.evidence],
            "observed_behavior": self.observed_behavior,
            "expected_behavior": self.expected_behavior,
            "root_cause": self.root_cause,
            "impact": self.impact,
            "remediation": self.remediation,
            "effort": self.effort,
            "regression_risk": self.regression_risk
        }
        if self.reproduction:
            data["reproduction"] = self.reproduction
        if self.preconditions:
            data["preconditions"] = self.preconditions
        if self.exploitability:
            data["exploitability"] = self.exploitability
        if self.blast_radius:
            data["blast_radius"] = self.blast_radius
        if self.likelihood:
            data["likelihood"] = self.likelihood
        if self.likelihood_justification:
            data["likelihood_justification"] = self.likelihood_justification
        if self.exposure_evidence:
            data["exposure_evidence"] = self.exposure_evidence
        if self.taint_chain:
            data["taint_chain"] = self.taint_chain
        if self.validation:
            data["validation"] = self.validation
        if self.related_findings:
            data["related_findings"] = self.related_findings
        return data


class FindingRegistry:
    def __init__(self):
        self.findings: dict[str, Finding] = {}
        self._history: dict[str, list[dict[str, Any]]] = {}

    def _record_transition(
        self,
        finding_id: str,
        from_status: str,
        to_status: str,
        reason: str | None = None,
        verification_evidence: list[str] | None = None
    ) -> None:
        import datetime
        self._history.setdefault(finding_id, []).append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "from_status": from_status,
            "to_status": to_status,
            "reason": reason,
            "verification_evidence": verification_evidence or []
        })

    def register(self, finding: Finding) -> None:
        """Register a finding and validate semantic rules."""
        if finding.id in self.findings:
            raise ValueError(f"Finding '{finding.id}' is already registered")
        errors = finding.validate()
        if errors:
            raise ValueError(f"Finding validation failed for {finding.id}:\n" + "\n".join(f" - {e}" for e in errors))
        self.findings[finding.id] = finding

    def get(self, finding_id: str) -> Finding | None:
        return self.findings.get(finding_id)

    def get_history(self, finding_id: str) -> list[dict[str, Any]]:
        return list(self._history.get(finding_id, []))

    def update(self, finding_id: str, **kwargs: Any) -> Finding:
        """Explicitly update mutable fields of a registered finding."""
        finding = self.findings.get(finding_id)
        if not finding:
            raise KeyError(f"Finding '{finding_id}' not found in registry")
        for key, value in kwargs.items():
            if not hasattr(finding, key):
                raise ValueError(f"Finding has no attribute '{key}'")
            setattr(finding, key, value)
        return finding

    def merge(self, target_id: str, source_id: str) -> Finding:
        """Merge source finding evidence into target and supersede source."""
        target = self.findings.get(target_id)
        source = self.findings.get(source_id)
        if not target or not source:
            raise KeyError("Both target and source findings must exist")
        target.evidence.extend(source.evidence)
        target.validation = list(set(target.validation + source.validation))
        target.related_findings = list(set(target.related_findings + [source_id] + source.related_findings))
        self.supersede(source_id, target_id, reason=f"merged into {target_id}")
        return target

    def supersede(self, finding_id: str, successor_id: str, reason: str | None = None) -> Finding:
        """Mark a finding as superseded by another finding."""
        finding = self.findings.get(finding_id)
        successor = self.findings.get(successor_id)
        if not finding:
            raise KeyError(f"Finding '{finding_id}' not found in registry")
        if not successor:
            raise KeyError(f"Successor finding '{successor_id}' not found in registry")
        old_status = finding.status
        finding.status = "SUPERSEDED"
        finding.related_findings.append(successor_id)
        self._record_transition(finding_id, old_status, "SUPERSEDED", reason=reason)
        return finding

    def transition_status(
        self,
        finding_id: str,
        new_status: str,
        *,
        reason: str | None = None,
        verification_evidence: list[str] | None = None
    ) -> Finding:
        """Update finding status with a valid lifecycle transition.

        FIXED requires verification evidence. REOPENED requires a reason.
        """
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid finding status '{new_status}'")
        finding = self.findings.get(finding_id)
        if not finding:
            raise KeyError(f"Finding '{finding_id}' not found in registry")

        current = finding.status
        allowed = TRANSITION_GRAPH.get(current, set())
        if new_status not in allowed:
            raise ValueError(
                f"invalid transition from '{current}' to '{new_status}'"
            )

        if new_status == "FIXED" and not verification_evidence:
            raise ValueError("FIXED transition requires verification evidence")

        if new_status == "REOPENED" and not reason:
            raise ValueError("REOPENED transition requires a reason")

        finding.status = new_status
        self._record_transition(
            finding_id,
            current,
            new_status,
            reason=reason,
            verification_evidence=verification_evidence
        )
        return finding

    def by_category(self, category: str) -> list[Finding]:
        return [f for f in self.findings.values() if f.category == category]

    def by_severity(self, severity: str) -> list[Finding]:
        return [f for f in self.findings.values() if f.severity == severity]

    def count_by_severity(self) -> dict[str, int]:
        counts = {s: 0 for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")}
        for f in self.findings.values():
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def health_score(
        self,
        *,
        coverage_known: bool = False,
        coverage_depth: str = "unknown",
        unreviewed_surfaces: list[str] | None = None,
    ) -> HealthScore:
        """Return a coverage-aware 1-10 health score.

        Delegates to :mod:`runtime.health_scoring` so the scoring algorithm is
        defined in one place.  When no findings exist and coverage is unknown,
        the score is omitted rather than reported as a false-perfect 10.
        """
        return compute_health_score(
            self.findings.values(),
            coverage_known=coverage_known,
            coverage_depth=coverage_depth,
            unreviewed_surfaces=unreviewed_surfaces,
        )

    def to_list(self) -> list[dict[str, Any]]:
        return [f.to_dict() for f in self.findings.values()]
