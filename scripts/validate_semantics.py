#!/usr/bin/env python3
"""Semantic and cross-field invariant validator for HQE artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"^HQE-(BOOT|SEC|BUG|REL|PERF|UX|DX|DOC|DEBT|DEPS)-[0-9]{3,}$")


def validate_finding_semantics(finding: dict, index: int) -> list[str]:
    """Validate cross-field semantic invariants for a single finding."""
    errors: list[str] = []
    prefix = f"Finding[{index}] (ID: {finding.get('id', '<unknown>')})"

    # 1. ID regex & category coherence
    finding_id = str(finding.get("id", ""))
    match = ID_RE.match(finding_id)
    if not match:
        errors.append(f"{prefix}: ID '{finding_id}' does not match canonical pattern ^HQE-(BOOT|SEC|BUG|REL|PERF|UX|DX|DOC|DEBT|DEPS)-[0-9]{{3,}}$")
    else:
        id_cat = match.group(1)
        cat_field = finding.get("category", "")
        if id_cat != cat_field:
            errors.append(f"{prefix}: ID category prefix '{id_cat}' does not match 'category' field '{cat_field}'")

    severity = finding.get("severity", "")
    category = finding.get("category", "")

    # 2. Severity Gate for CRITICAL and HIGH
    if severity in ("CRITICAL", "HIGH"):
        gate_fields = [
            "preconditions", "exploitability", "blast_radius",
            "likelihood", "likelihood_justification", "exposure_evidence"
        ]
        for field in gate_fields:
            val = finding.get(field)
            if not val:
                errors.append(f"{prefix}: Severity is {severity} but required severity-gate field '{field}' is missing or empty")
            elif isinstance(val, (list, dict)) and len(val) == 0:
                errors.append(f"{prefix}: Severity is {severity} but severity-gate field '{field}' is empty collection")

    # 3. Taint Chain for Security Findings
    if category == "SEC":
        taint = finding.get("taint_chain")
        if not isinstance(taint, dict):
            errors.append(f"{prefix}: Security finding must include structured 'taint_chain' object")
        else:
            for required_step in ("source", "transforms", "validation_boundary", "sink", "impact"):
                if not taint.get(required_step):
                    errors.append(f"{prefix}: 'taint_chain' missing required element '{required_step}'")

    # 4. Evidence Integrity
    evidence_list = finding.get("evidence", [])
    if not isinstance(evidence_list, list) or len(evidence_list) == 0:
        errors.append(f"{prefix}: Evidence must be a non-empty array")
    else:
        for ev_idx, ev in enumerate(evidence_list):
            ev_prefix = f"{prefix} Evidence[{ev_idx}]"
            if not isinstance(ev, dict):
                errors.append(f"{ev_prefix}: Must be an object")
                continue

            snippet = ev.get("snippet", "")
            if not snippet or not isinstance(snippet, str) or not snippet.strip():
                errors.append(f"{ev_prefix}: 'snippet' must be non-empty string")

            if "start_line" in ev or "end_line" in ev:
                start_l = ev.get("start_line")
                end_l = ev.get("end_line")
                if not isinstance(start_l, int) or start_l < 1:
                    errors.append(f"{ev_prefix}: 'start_line' must be integer >= 1 (got {start_l})")
                if not isinstance(end_l, int) or (isinstance(start_l, int) and end_l < start_l):
                    errors.append(f"{ev_prefix}: 'end_line' must be integer >= start_line (got end={end_l}, start={start_l})")
            elif "anchor" in ev or "grep_signature" in ev:
                if not ev.get("anchor") or not ev.get("grep_signature"):
                    errors.append(f"{ev_prefix}: Anchor-based evidence must include both 'anchor' and 'grep_signature'")

    return errors


def validate_findings_file(file_path: Path) -> list[str]:
    """Load findings JSON and validate semantic rules."""
    path = file_path.resolve()
    if not path.is_file():
        return [f"File not found: {path}"]

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        return [f"JSON parse error in {path.name}: {exc}"]

    if isinstance(data, dict):
        findings = [data]
    elif isinstance(data, list):
        findings = data
    else:
        return [f"Expected JSON array or object, got {type(data).__name__}"]

    errors: list[str] = []
    seen_ids: set[str] = set()

    for idx, f in enumerate(findings):
        if isinstance(f, dict):
            fid = f.get("id")
            if fid in seen_ids:
                errors.append(f"Duplicate finding ID '{fid}' at index {idx}")
            if fid:
                seen_ids.add(fid)
            errors.extend(validate_finding_semantics(f, idx))
        else:
            errors.append(f"Finding[{idx}] is not an object")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate semantic invariants on findings JSON.")
    parser.add_argument("findings_file", help="Path to findings JSON file")
    args = parser.parse_args()

    errors = validate_findings_file(Path(args.findings_file))
    if errors:
        print("Semantic validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("Semantic validation PASSED: all cross-field invariants satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
