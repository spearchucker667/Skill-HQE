"""HQE Deterministic Control-Plane & Execution Runtime.

Provides execution state management, finding lifecycle tracking, evidence verification,
run manifest generation, and deterministic artifact assembly for Skill-HQE.
"""

from __future__ import annotations

from .session_manager import SessionManager, SessionState
from .finding_registry import FindingRegistry, Finding
from .evidence_store import EvidenceStore, CodeEvidence
from .run_manifest import RunManifestGenerator
from .artifact_pipeline import ArtifactPipeline
from .redaction_engine import TypedRedactionEngine, classify_secret
from .health_scoring import HealthScore, compute_health_score, score_from_findings, score_to_band

__all__ = [
    "SessionManager",
    "SessionState",
    "FindingRegistry",
    "Finding",
    "EvidenceStore",
    "CodeEvidence",
    "RunManifestGenerator",
    "ArtifactPipeline",
    "TypedRedactionEngine",
    "classify_secret",
    "HealthScore",
    "compute_health_score",
    "score_from_findings",
    "score_to_band",
]
