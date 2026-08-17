# Severity, Confidence, and Effort

HQE utilizes a strict taxonomy for classifying findings. You must use these exact classifications when producing findings.

## Confidence Tags
Every finding must be explicitly tagged to indicate the strength of its evidence.

- **[FACT]**: The issue is undeniable. You have a file, exact line numbers, and a code snippet showing a clear defect.
- **[INFERENCE]**: The issue is strongly supported by surrounding code, but requires reasoning. You must explain your reasoning chain.
- **[HYPOTHESIS]**: You suspect an issue based on patterns or missing information, but cannot prove it statically. You must include steps to confirm or refute the hypothesis.
- **[NEEDS_VERIFICATION]**: A finding that requires runtime testing or external context to validate.

## Severity Levels
- **CRITICAL**: Remote code execution, privilege escalation, data destruction, or complete service outage. Fix immediately.
- **HIGH**: Data leakage, serious business logic bypass, or major reliability issue affecting many users. Fix in current sprint.
- **MEDIUM**: Moderate impact bugs, DoS vulnerabilities, or reliability issues requiring edge cases to trigger.
- **LOW**: Minor bugs, UI glitches, or defense-in-depth gaps.
- **INFO**: Best practice deviations, technical debt, or refactoring suggestions.

## Effort Tiers
- **S**: 1-2 files changed, localized impact, very low regression risk. Can be implemented and verified quickly.
- **M**: 2-5 files changed, requires updating tests or configuration. Needs moderate verification.
- **L**: Cross-cutting changes, architecture modifications, or significant migration/rollout considerations. High regression risk.

## Status Tracking
As findings progress through the lifecycle, update their status:
- `CONFIRMED`: Verified as a real issue.
- `STRONGLY_SUPPORTED`: High confidence but not yet 100% verified.
- `INFERRED`: Based on strong reasoning.
- `SUSPECTED`: A hypothesis.
- `NOT_REPRODUCED`: Attempted verification failed to reproduce the issue.
- `FIXED`: Remediation applied and verification succeeded.
