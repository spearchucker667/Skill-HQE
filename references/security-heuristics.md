# HQE Security Heuristics

This reference codifies heuristics for discovering complex security vulnerabilities during an HQE audit. These go beyond simple pattern matching to identify structural, architectural, and logical flaws.

---

## 1. Trust Boundary Violations
Examine data flows crossing trust boundaries (e.g., from user input to database, from external API to internal state):
- **Missing Validation:** Is data validated immediately upon crossing the boundary?
- **Improper Serialization:** Are complex objects deserialized safely without arbitrary code execution?
- **Implicit Trust:** Does a microservice implicitly trust another without verifying the origin or integrity of the payload?

## 2. Authorization Bypasses (IDOR & BOLA)
Focus on horizontal and vertical privilege escalation:
- **Object Reference Validation:** When an ID is passed (e.g., `?user_id=123`), does the system verify the current user owns or has access to that object?
- **State Manipulation:** Can a user modify their own role/permissions by tampering with client-side state (JWT, cookies, hidden form fields)?

## 3. Cryptographic Failures
Review encryption and hashing implementations:
- **Hardcoded Secrets:** Are keys or tokens embedded in the source code?
- **Weak Algorithms:** Is the system using outdated algorithms (e.g., MD5, SHA1)?
- **Improper Key Management:** Are keys generated securely and rotated periodically? Are they stored in a secure vault?

## 4. Concurrency & Race Conditions (TOCTOU)
Analyze operations that involve state checking followed by state modification:
- **Time-of-Check to Time-of-Use:** Is the state locked between the check and the use to prevent concurrent modification?
- **Resource Exhaustion:** Can an attacker trigger concurrent operations that deplete system resources (e.g., connection pools, memory)?

## 5. Injection Flaws
Beyond standard SQL injection, look for:
- **Command Injection:** Are shell commands constructed using unsanitized user input?
- **Server-Side Request Forgery (SSRF):** Can the application be forced to make requests to internal or unintended external URLs?
- **Template Injection:** Are user inputs evaluated as part of a server-side template?

## 6. Logic Flaws
These are highly application-specific and often missed by automated scanners:
- **Business Logic Bypass:** Can a user skip required steps in a workflow (e.g., checkout process)?
- **Resource Limits:** Is there a lack of rate limiting or quota enforcement, leading to abuse?
