#!/usr/bin/env python3
"""Deterministic CLI tool for generating an HQE run manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add repo root to import runtime
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from runtime import FindingRegistry, Finding, CodeEvidence, RunManifestGenerator


def main() -> int:
    parser = argparse.ArgumentParser(description="Create HQE Run Manifest JSON.")
    parser.add_argument("--repo-path", default=".", help="Repository root path")
    parser.add_argument("--mode", default="audit", help="HQE execution mode")
    parser.add_argument("--findings-file", default=None, help="Optional findings JSON file")
    parser.add_argument("--health-score", type=int, default=8, help="Health score (1-10)")
    parser.add_argument("--output", default="HQE_RUN_MANIFEST.json", help="Output JSON path")
    args = parser.parse_args()

    registry = FindingRegistry()
    if args.findings_file:
        f_path = Path(args.findings_file).resolve()
        if f_path.is_file():
            try:
                with f_path.open("r", encoding="utf-8") as fh:
                    raw_data = json.load(fh)
                raw_list = raw_data if isinstance(raw_data, list) else [raw_data]
                for raw in raw_list:
                    evidence_list = []
                    for ev in raw.get("evidence", []):
                        if isinstance(ev, dict):
                            evidence_list.append(CodeEvidence(
                                path=ev.get("path", ""),
                                snippet=ev.get("snippet", ""),
                                start_line=ev.get("start_line"),
                                end_line=ev.get("end_line"),
                                symbol=ev.get("symbol"),
                                anchor=ev.get("anchor"),
                                grep_signature=ev.get("grep_signature")
                            ))
                    f = Finding(
                        id=raw.get("id", ""),
                        title=raw.get("title", ""),
                        category=raw.get("category", ""),
                        severity=raw.get("severity", ""),
                        confidence=raw.get("confidence", "FACT"),
                        status=raw.get("status", "CONFIRMED"),
                        affected_component=raw.get("affected_component", ""),
                        observed_behavior=raw.get("observed_behavior", ""),
                        expected_behavior=raw.get("expected_behavior", ""),
                        root_cause=raw.get("root_cause", ""),
                        impact=raw.get("impact", ""),
                        remediation=raw.get("remediation", ""),
                        effort=raw.get("effort", "S"),
                        regression_risk=raw.get("regression_risk", "Low"),
                        evidence=evidence_list,
                        reproduction=raw.get("reproduction"),
                        preconditions=raw.get("preconditions", []),
                        exploitability=raw.get("exploitability"),
                        blast_radius=raw.get("blast_radius"),
                        likelihood=raw.get("likelihood"),
                        likelihood_justification=raw.get("likelihood_justification"),
                        exposure_evidence=raw.get("exposure_evidence"),
                        taint_chain=raw.get("taint_chain"),
                        validation=raw.get("validation", []),
                        related_findings=raw.get("related_findings", [])
                    )
                    registry.register(f)
            except Exception as exc:
                print(f"Warning: Failed to load findings from {f_path}: {exc}", file=sys.stderr)

    gen = RunManifestGenerator(repo_path=args.repo_path, mode=args.mode)
    manifest = gen.build_manifest(
        registry=registry,
        health_score=args.health_score,
        health_reasons=["Verified via deterministic HQE runtime generator"]
    )
    out_file = gen.save_to_file(manifest, target_path=args.output)
    print(f"Successfully generated run manifest: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
