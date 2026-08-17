# Security Policy & Vulnerability Reporting

The HQE Skill project team takes security vulnerabilities and unintended agent behavior seriously. We are committed to maintaining a safe, robust, and reliable framework for AI-assisted engineering and auditing.

---

## 1. Supported Versions

Only the current main branch and latest released tagged versions receive active security patches.

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 1.0.x   | :white_check_mark: | Active |
| < 1.0.0 | :x:                | Legacy |

---

## 2. Threat Vector Scope

We specifically welcome security reports concerning:
- **Prompt Injection Bypasses**: Scenarios where untrusted repository content causes an agent executing the HQE skill to bypass safety rules.
- **Unsafe Script Execution**: Flaws in `scripts/inventory_repo.py`, `scripts/validate_findings.py`, or `scripts/check_skill.py`.
- **Schema Validation Gaps**: Weaknesses in JSON schemas that allow malicious or malformed finding payloads to bypass validation.

---

## 3. Reporting a Vulnerability

**Please DO NOT open public GitHub issues or discussions for security vulnerabilities.**

To report a vulnerability:
1. **Email / Security Advisory**: Submit a private advisory via GitHub Security Advisories or contact the maintainers directly at `security@hqe.local` (or via encrypted security channels).
2. **Include in Report**:
   - Detailed description of the vulnerability.
   - Proof of Concept (PoC) prompt, malicious test fixture, or payload.
   - Host agent runtime and model used during reproduction (e.g., Antigravity CLI with Gemini 3.1 Pro, Kimi Code, Claude 3.7 Sonnet).
   - Potential impact and suggested remediation if known.

---

## 4. Response Timeline & Triage

- **Initial Acknowledgment**: Within 48 hours of receipt.
- **Triage & Reproduction**: Within 5 business days.
- **Remediation & Patch Release**: Dependent on complexity, typically within 14 business days.
- **Public Disclosure**: Coordinated disclosure after fix availability and verification.

---

## 5. Security Architecture References
For deep dives into our defense-in-depth model:
- [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) — Threat boundaries, secret management, and isolation.
- [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) — STRIDE analysis and adversary simulation.
- [references/prompt-injection-defense.md](references/prompt-injection-defense.md) — AI prompt isolation rules.
