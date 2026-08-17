# Runtime Initialization & Session State Workflow

This workflow guides the host AI agent through initializing the deterministic HQE execution state at the start of an audit or remediation run.

---

## 1. Objective
Establish reproducible session tracking, verify the execution environment, and initialize the `HQE_SESSION_LOG.json` state machine.

---

## 2. Execution Steps

### Step 1: Pre-Flight Environment Inspection
1. Verify working directory cleanliness:
   ```bash
   git status --short
   ```
2. Inventory repository files:
   ```bash
   python3 scripts/inventory_repo.py . --summary-only
   ```
3. Detect ecosystem manifests and verification commands:
   ```bash
   python3 scripts/detect_manifests.py .
   python3 scripts/detect_test_commands.py .
   ```

### Step 2: Initialize Session Manager
1. Instantiate session state:
   ```python
   from runtime import SessionManager, SessionState
   session = SessionManager(repo_path=".")
   session.transition_to(SessionState.ORIENTED, "Phase 0 orientation completed")
   ```
2. Log initial goals and save `HQE_SESSION_LOG.json`:
   ```python
   session.mark_in_progress("Phase 1: Deep Security & Code Audit")
   session.save_to_file("HQE_SESSION_LOG.json")
   ```

### Step 3: Triage Check (Repo > 50 Files)
- If `total_files > 50`, transition to `SessionState.TRIAGED` and prioritize core subsystems before secondary tooling.
