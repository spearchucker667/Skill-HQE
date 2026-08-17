"""Coverage-aware health scoring for HQE run manifests.

The protocol rubric maps numeric scores to qualitative bands:

- 9-10  → Exceptional / Production-ready
- 7-8   → Solid
- 5-6   → Adequate / Fragile
- 3-4   → Concerning / Unstable
- 1-2   → Critical Risk / Broken

A perfect score is only meaningful when coverage is known.  When no findings
exist and coverage has not been established, the score MUST be omitted rather
than reported as 10 to avoid a false-perfect claim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HealthScore:
    """Container for a coverage-aware HQE health score."""

    score: int | None
    omitted: bool = False
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "omitted": self.omitted,
            "reasons": list(self.reasons),
        }
        if self.score is not None:
            data["score"] = self.score
        return data


# Severity weights used to penalise a baseline of 100.
_SEVERITY_WEIGHTS = {
    "CRITICAL": -25,
    "HIGH": -15,
    "MEDIUM": -8,
    "LOW": -3,
    "INFO": 0,
}


def _count_by_severity(findings) -> dict[str, int]:
    counts = {sev: 0 for sev in _SEVERITY_WEIGHTS}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return counts


def score_from_findings(findings) -> int:
    """Return a 1-10 numeric health score from an iterable of findings.

    The calculation intentionally ignores coverage; callers that need coverage
    awareness should use :func:`compute_health_score` instead.
    """
    if not findings:
        return 10

    counts = _count_by_severity(findings)
    penalty = sum(_SEVERITY_WEIGHTS.get(sev, 0) * count for sev, count in counts.items())
    raw = 100 + penalty
    score = max(1, min(100, raw))

    # Map 0-100 to the 1-10 rubric.
    if score >= 90:
        return 10
    if score >= 75:
        return 8
    if score >= 55:
        return 6
    if score >= 30:
        return 4
    return 2


def score_to_band(score: int) -> str:
    """Map a 1-10 numeric score to a qualitative band."""
    if score >= 9:
        return "Exceptional"
    if score >= 7:
        return "Solid"
    if score >= 5:
        return "Adequate"
    if score >= 3:
        return "Concerning"
    return "Critical Risk"


def compute_health_score(
    findings,
    *,
    coverage_known: bool = False,
    coverage_depth: str = "unknown",
    unreviewed_surfaces: list[str] | None = None,
) -> HealthScore:
    """Compute a coverage-aware health score.

    If there are no findings and coverage is not known, the score is omitted
    instead of claiming a perfect 10.  When coverage is known, the numeric
    score is computed from findings and annotated with the appropriate band
    and explanatory reasons.
    """
    unreviewed_surfaces = unreviewed_surfaces or []

    if not findings and not coverage_known:
        return HealthScore(
            score=None,
            omitted=True,
            reasons=[
                "No findings recorded and coverage is unknown; score omitted to avoid a false-perfect claim"
            ],
        )

    score = score_from_findings(findings)
    reasons = [f"Evaluated against HQE v5 rubric (coverage depth: {coverage_depth})"]

    if unreviewed_surfaces:
        reasons.append(
            f"{len(unreviewed_surfaces)} unreviewed surface(s) may affect confidence"
        )

    if not coverage_known:
        reasons.append("Coverage not fully established; score reflects known findings only")

    return HealthScore(score=score, omitted=False, reasons=reasons)
