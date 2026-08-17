# Handoff Generation Workflow

When requested (`/HQE handoff` or as part of a full audit), generate an implementation-ready handoff for another agent.

## 1. Objective

Generate an unambiguous, structured, and implementation-ready handoff ledger enabling another AI agent or engineer to seamlessly execute verified remediations without context degradation.

## 2. Prerequisites

Before generating a handoff, confirm the following:

- [ ] Findings have been verified and validated against `schemas/finding.schema.json`.
- [ ] `templates/handoff.md` and `schemas/handoff.schema.json` are available.
- [ ] The remediation scope and priority order are defined.
- [ ] No unredacted secrets appear in any finding or artifact.
- [ ] `references/remediation.md` and `references/verification.md` are available for reference.

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- User invokes `/HQE handoff`.
- A full audit explicitly requests a handoff for implementation.
- A remediation run is transitioning to another agent or session.
- A verified finding set is ready for execution and needs context preservation.

## 4. Stop-the-Line Conditions

Immediately halt and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found during handoff generation:

- Unredacted credentials, API keys, tokens, or private keys in the finding inventory.
- A finding references a malicious payload or backdoor that requires incident response before remediation.
- Critical findings lack verification steps or are purely hypothetical.

Flag the issue as `STOP-THE-LINE: [issue]` and resolve before emitting the handoff.

## 5. Execution Model

### Phase 1: Inventory Findings

**Goal**: Select the exact findings to include in the handoff.

1. **Filter to actionable findings**:
   - Exclude `INFO` items unless they are prerequisites for higher-severity fixes.
   - Exclude findings marked `[NEEDS_VERIFICATION]` unless the handoff explicitly scopes verification work.
2. **Preserve stable IDs** (`HQE-SEC-001`, `HQE-REL-003`, etc.) across the handoff and downstream artifacts.
3. **Summarize each finding** with:
   - ID, title, severity, category, confidence.
   - Affected component.
   - Evidence triad (`file:line` or anchor+grep + snippet).
   - Root cause.

**Evidence to collect**:
- List of included findings with IDs.
- Rationale for excluded findings.

**Exit criteria**:
- [ ] Handoff finding inventory is defined.
- [ ] Stable IDs are preserved.

### Phase 2: Determine Priority Order

**Goal**: Define the exact execution sequence for the receiving agent.

1. **Order by severity and dependency**:
   - CRITICAL first, then HIGH, then MEDIUM, then LOW.
   - Security → correctness → reliability → performance → maintainability → DX.
   - Respect blockers: if finding X blocks finding Y, X must come first.
2. **Break ties** by blast radius, effort (smaller first), and verification ease.
3. **Document dependencies** for each finding (`Blocked by: [X]` | `Blocks: [Y]`).

**Evidence to collect**:
- Prioritized execution list.
- Dependency map.

**Exit criteria**:
- [ ] Priority order is documented and dependency-aware.

### Phase 3: Define Required Changes

**Goal**: Specify minimal, safe fixes for each finding.

1. **For each finding, provide**:
   - Root cause in one or two sentences.
   - Minimal safe fix with concrete file path(s) and change description.
   - Refactor alternative only if minimal is insufficient, with justification.
2. **Respect the change budget**: ≤5 files per TODO-ID.
3. **Flag behavior changes** with `⚠️ BEHAVIOR CHANGE` and document old vs new behavior.
4. **Flag new dependencies** with `[NEW_DEPENDENCY]` and include justification.

**Evidence to collect**:
- Per-finding required changes.
- Change-budget compliance notes.

**Exit criteria**:
- [ ] Every finding has a concrete, minimal required change.
- [ ] Behavior changes and new dependencies are flagged.

### Phase 4: Specify Tests & Validation

**Goal**: Make success criteria unambiguous and reproducible.

1. **For each finding, specify**:
   - Tests to add or update.
   - Exact validation command(s) to run.
   - Expected result for each command.
   - Verification tier (Tier 1/2/3 per `protocol/hqe-engineer.yaml`).
2. **Prefer Tier 1** (existing repo command) when available.
3. **Provide Tier 2 stubs** (new test code) when no existing test covers the fix.
4. **Provide Tier 3 checklists** only when execution is unavailable.

**Evidence to collect**:
- Per-finding test and validation plan.
- Tier classification.

**Exit criteria**:
- [ ] Every finding has verifiable success criteria.
- [ ] Validation commands are exact and expected results are stated.

### Phase 5: Assess Regression Risks

**Goal**: Surface what else might break when fixes are applied.

1. **For each finding, identify**:
   - Callers or consumers of the changed code.
   - Shared state, schemas, or APIs affected.
   - Configuration or environment assumptions that might change.
2. **Rate regression risk** as Low, Medium, or High.
3. **Suggest safe-rollout steps** for high-risk changes (feature flags, staged deploys, rollback command).

**Evidence to collect**:
- Regression risk list per finding.
- Rollout recommendations for high-risk items.

**Exit criteria**:
- [ ] Regression risks are documented for each finding.

### Phase 6: Draft Handoff

**Goal**: Produce the human-readable handoff artifact.

1. **Use `templates/handoff.md`** as the structural guide.
2. **Populate every required section**:
   - Mission
   - Repository/path
   - Current verified state
   - Do-not-assume rules
   - Finding inventory
   - Priority order
   - Files/components involved
   - Root cause per finding
   - Required changes
   - Tests to add/update
   - Validation commands
   - Regression risks
   - Completion criteria
   - Do-not rules
   - Final reporting format
3. **Use concrete, unambiguous language**. Avoid phrases like "improve error handling" or "clean up code". Specify where, why, and how success is proven.

**Evidence to collect**:
- Draft `HQE_HANDOFF.md`.

**Exit criteria**:
- [ ] `HQE_HANDOFF.md` is complete and follows the template.

### Phase 7: Validate Against Schema

**Goal**: Confirm the handoff is machine-parseable and complete.

1. **If producing a JSON handoff**, validate against `schemas/handoff.schema.json`:
   ```bash
   python3 scripts/validate_handoff.py HQE_HANDOFF.json
   ```
2. **Verify all required fields** from `schemas/handoff.schema.json` are present:
   - `mission`
   - `repository_path`
   - `current_state`
   - `do_not_assume`
   - `finding_inventory`
   - `priority_order`
   - `required_changes`
   - `tests_to_update`
   - `validation_commands`
   - `regression_risks`
   - `completion_criteria`
   - `do_not_rules`
3. **Cross-check** the handoff finding inventory against `HQE_FINDINGS.json`.

**Evidence to collect**:
- Schema-validation result.
- Cross-check result.

**Exit criteria**:
- [ ] Handoff passes schema validation (if JSON) or template completeness check (if Markdown only).
- [ ] Finding inventory matches `HQE_FINDINGS.json`.

## 6. Required Controls / Checks

- The handoff must be structured and unambiguous. Avoid vague language.
- Every finding must include a concrete root cause, required change, and verification path.
- Validation commands must be exact, with expected results and verification tier.
- Required changes must respect the change budget (≤5 files per TODO-ID).
- Behavior changes must be flagged with `⚠️ BEHAVIOR CHANGE`.
- New dependencies must be flagged with `[NEW_DEPENDENCY]`.
- Do-not-assume rules and do-not rules must be explicit.
- Regression risks must be rated and high-risk changes must include rollout/rollback guidance.
- Stable finding IDs must be preserved across the handoff and source findings.
- No raw secrets may appear in the handoff.

## 7. Artifact Outputs

- `HQE_HANDOFF.md` — human-readable implementation-ready handoff.
- `HQE_HANDOFF.json` (optional) — machine-readable handoff ledger.
- Updated `HQE_SESSION_LOG.json` with handoff generation recorded.

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

If a JSON handoff is produced, validate it against `schemas/handoff.schema.json`.

## 8. Exit Criteria

Handoff generation is complete when:

- [ ] The finding inventory is defined and stable IDs are preserved.
- [ ] Priority order and dependencies are documented.
- [ ] Every finding has a concrete required change and verification plan.
- [ ] Regression risks are rated and high-risk items have rollout guidance.
- [ ] `HQE_HANDOFF.md` follows `templates/handoff.md` and is complete.
- [ ] JSON handoff (if produced) passes schema validation.
- [ ] No unredacted secrets appear in the handoff.
- [ ] Stop-the-line conditions have been checked and handled if triggered.
- [ ] The session log is updated with handoff completion.

## 9. Confidence Model Reminders

Tag handoff content:

- `[FACT]` — Verified finding details, exact file paths, and known test commands.
- `[INFERENCE]` — Likely regression risks or rollout steps derived from code structure.
- `[HYPOTHESIS]` — A suspected interaction or failure mode that should be validated by the receiving agent.
- `[NEEDS_VERIFICATION]` — Items the receiving agent must confirm before implementing.

Never present hypotheses as facts. The handoff should make the receiving agent's job unambiguous, including what is known and what still needs to be verified.
