#!/usr/bin/env python3
"""Deterministic CLI tool for assembling all canonical HQE deliverables from findings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add repo root to import runtime
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from runtime import FindingRegistry, Finding, CodeEvidence, ArtifactPipeline, SessionManager


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble canonical HQE audit deliverables.")
    parser.add_argument("findings_file", help="Path to findings JSON file")
    parser.add_argument("--output-dir", default="artifacts", help="Target directory for deliverables")
    parser.add_argument("--session-file", default=None, help="Optional session log JSON file")
    parser.add_argument("--repo-name", default="repository", help="Repository name for headers")
    args = parser.parse_args()

    findings_path = Path(args.findings_file).resolve()
    if not findings_path.is_file():
        print(f"Error: findings file not found: {findings_path}", file=sys.stderr)
        return 1

    try:
        with findings_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        print(f"Error reading findings JSON: {exc}", file=sys.stderr)
        return 1

    raw_findings = data if isinstance(data, list) else [data]

    registry = FindingRegistry()
    for raw in raw_findings:
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

    session = None
    if args.session_file:
        s_path = Path(args.session_file).resolve()
        if s_path.is_file():
            session = SessionManager(repo_path=str(ROOT_DIR))

    pipeline = ArtifactPipeline(registry, session=session, repo_name=args.repo_name)
    generated = pipeline.build_all_artifacts(output_dir=args.output_dir)

    print(f"Successfully assembled {len(generated)} canonical deliverables in '{args.output_dir}':")
    for name, path in generated.items():
        print(f"  - {name} -> {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
