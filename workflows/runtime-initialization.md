# Runtime Initialization & Session State Workflow

This workflow guides the host AI agent through initializing the deterministic HQE execution state at the start of any audit or remediation run.

## 1. Objective

Establish reproducible session tracking, verify the execution environment, detect the repository's technology stack and verification commands, and initialize the `HQE_SESSION_LOG.json` state machine.

## 2. Prerequisites

Before initializing the runtime, confirm the following:

- [ ] The working directory is accessible and contains a repository or a defined audit scope.
- [ ] Python 3 is available and the `runtime` package is importable.
- [ ] `scripts/inventory_repo.py`, `scripts/detect_manifests.py`, and `scripts/detect_test_commands.py` are present.
- [ ] `protocol/hqe-engineer.yaml` and `references/repository-orientation.md` are available for reference.
- [ ] Write access is available for `HQE_SESSION_LOG.json` and supporting run metadata.

## 3. Entry Criteria

Begin this workflow when any of the following are true:

- Start of any HQE audit or remediation run.
- Resuming a session after interruption or context compaction.
- Switching from one workflow to another that requires a fresh session state.
- The user explicitly invokes `/HQE init` or equivalent.

## 4. Stop-the-Line Conditions

Immediately halt and invoke [`workflows/incident-response.md`](incident-response.md) if any of the following are found during initialization:

- Missing required protocol files (`protocol/hqe-engineer.yaml`, critical schemas, validators).
- Evidence of a compromised environment (unexpected files, unauthorized modifications to HQE tooling).
- Active credentials or secrets exposed in the working directory root.
- The working directory is not a git repository and no explicit audit scope has been provided.

Flag the issue as `STOP-THE-LINE: [issue]` in any interim log and do not proceed until resolved.

## 5. Execution Model

### Phase 0: Pre-Flight Environment Inspection

**Goal**: Record the state of the environment before analysis begins.

1. **Verify working directory cleanliness**:
   ```bash
   git status --short
   ```
2. **Inventory repository files**:
   ```bash
   python3 scripts/inventory_repo.py . --summary-only
   ```
3. **Detect ecosystem manifests**:
   ```bash
   python3 scripts/detect_manifests.py .
   ```
4. **Detect available verification commands**:
   ```bash
   python3 scripts/detect_test_commands.py .
   ```
5. **Record environment constraints**: tooling present, tooling missing, chunking mode, session start timestamp.

**Evidence to collect**:
- `git status` output.
- Repository inventory summary.
- Manifest list (package manager, build system, test framework).
- Detected test/build/lint commands.
- Environment limitations or blockers.

**Exit criteria**:
- [ ] Working directory state is documented.
- [ ] Repository stack and verification commands are detected.
- [ ] Missing tooling is recorded as a blocker or limitation.

### Phase 1: Initialize Session Manager

**Goal**: Create the canonical session state object and transition it through the initial phases.

1. **Instantiate session state**:
   ```python
   from runtime import SessionManager, SessionState
   session = SessionManager(repo_path=".")
   session.transition_to(SessionState.ORIENTED, "Phase 0 orientation completed")
   ```
2. **Log initial goals**:
   ```python
   session.mark_in_progress("Phase 1: Deep analysis")
   ```
3. **Record repository identity** in the session:
   - Repository name and path.
   - Current commit/branch (if available).
   - Protocol version (`5.0.0`).
   - Audit mode (`full`, `security`, `remediation`, etc.).
4. **Save `HQE_SESSION_LOG.json`**:
   ```python
   session.save_to_file("HQE_SESSION_LOG.json")
   ```

**Evidence to collect**:
- Session object contents.
- Saved `HQE_SESSION_LOG.json` path and checksum.

**Exit criteria**:
- [ ] `SessionManager` is instantiated and persisted.
- [ ] `HQE_SESSION_LOG.json` exists and is schema-valid.

### Phase 2: Triage Check (Repo > 50 Files)

**Goal**: Activate large-repository triage when appropriate.

1. **Retrieve file count** from the inventory produced in Phase 0.
2. If `total_files > 50`:
   - Transition to `SessionState.TRIAGED`.
   - Prioritize core subsystems before secondary tooling.
   - Document triage buckets (`T1_Deep`, `T2_Standard`, `T3_Skim`, `T4_Skip`) per `protocol/hqe-engineer.yaml`.
3. If `total_files <= 50`:
   - Note that triage is skipped and all files are in scope for deep review unless explicitly excluded.

**Evidence to collect**:
- Total file count and triage decision.
- Scope declaration for large repositories.

**Exit criteria**:
- [ ] Triage state is recorded in the session log.
- [ ] For large repos, a coverage strategy is documented.

### Phase 3: State Logging & Handoff to Analysis

**Goal**: Finalize initialization records and hand control to the active workflow.

1. **Update session log** with:
   - Completed initialization steps.
   - In-progress analysis phase.
   - Discovered blockers or unknowns.
   - Environment limitations.
2. **Emit a reproducibility manifest stub** noting what commands were run, what succeeded, and what failed.
3. **Transition to the first analysis state** (`SessionState.ANALYZING` or workflow-specific state).

**Evidence to collect**:
- Updated `HQE_SESSION_LOG.json`.
- Reproducibility manifest stub.

**Exit criteria**:
- [ ] Session log reflects initialization completion.
- [ ] The next workflow phase is marked in progress.

## 6. Required Controls / Checks

- Do not proceed without verifying the working directory and repository identity.
- Record all detected verification commands exactly as discovered.
- Persist session state after each major transition.
- If tooling is missing, record it as a limitation rather than silently skipping.
- For large repositories, activate triage and document scope honestly.
- Never invent repository metadata (commit hash, branch, file counts); use observed values or mark `[NEEDS_VERIFICATION]`.

## 7. Artifact Outputs

- `HQE_SESSION_LOG.json` — canonical session state machine.
- `HQE_RUN_MANIFEST.json` (stub, finalized later by [`workflows/artifact-generation.md`](artifact-generation.md)).
- Reproducibility manifest notes (may be incorporated into `HQE_UNKNOWNS.md` or `HQE_CONFIDENCE.md`).

Validate machine-readable artifacts with:

```bash
python3 scripts/validate_session_log.py HQE_SESSION_LOG.json
```

## 8. Exit Criteria

Runtime initialization is complete when:

- [ ] Environment inspection is complete and recorded.
- [ ] Session manager is initialized and persisted.
- [ ] Repository stack and verification commands are detected.
- [ ] Triage decision is recorded (skipped or active).
- [ ] `HQE_SESSION_LOG.json` exists and is schema-valid.
- [ ] No stop-the-line conditions remain unaddressed.
- [ ] The session log marks the next analysis phase as in progress.

## 9. Confidence Model Reminders

Tag environment and repository claims:

- `[FACT]` — Values observed directly from commands (`git status`, `inventory_repo.py`, etc.).
- `[INFERENCE]` — Stack classification derived from detected manifests.
- `[HYPOTHESIS]` — Suspected behavior or capability not yet verified.
- `[NEEDS_VERIFICATION]` — Missing tooling or context that prevents confirmation.

Never upgrade confidence without evidence. If the repository cannot be inspected, record the limitation and proceed with the available scope rather than stalling.
