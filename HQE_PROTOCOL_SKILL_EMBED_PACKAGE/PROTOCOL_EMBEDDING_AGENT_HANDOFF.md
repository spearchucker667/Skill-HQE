# Agent Handoff — Embed the Canonical HQE Protocol into `/HQE`

## Mission

Integrate the canonical HQE Engineer protocol into the existing skill repository:

```text
/Users/super_user/Projects/Skill-HQE/
```

Use the actual HQE Workbench implementation as the broader source of truth:

```text
/Users/super_user/Projects/HQE-Workbench/
```

This package supplies the protocol files and integration scaffolding needed to begin.

The protocol should become a **first-class, versioned, validated asset of the skill**, while `SKILL.md` remains the compact agent-facing control plane.

Do not rebuild HQE Workbench.

---

# 1. Start Here

Read these package files in this order:

```text
START_AGENT_PROMPT.md
HQE_SKILL_PARITY_REPAIR_AGENT_HANDOFF.md
PROTOCOL_EMBEDDING_AGENT_HANDOFF.md
PACKAGE_README.md
```

The user-provided launch prompt in `START_AGENT_PROMPT.md` must be treated as part of the task context.

The exhaustive parity handoff remains authoritative for the broader repair.

This handoff governs the protocol-specific embedding work.

---

# 2. Should the Protocol Files Be in Skill-HQE?

Yes.

The current skill claims HQE Protocol v4.2.1 lineage and its README already links to:

```text
protocol/hqe-engineer.yaml
```

but the current skill archive does not contain that path.

That is both a documentation defect and a capability/parity defect.

The active protocol should be embedded so the skill has:

- a canonical machine-readable source of truth;
- deterministic protocol validation;
- explicit versioning;
- a basis for parity tests;
- a stable source for maintaining `SKILL.md`, references, workflows, schemas, and artifacts;
- evidence for claims that `/HQE` implements the HQE protocol.

Do not make every invocation load the entire YAML. Use progressive disclosure.

---

# 3. Active vs Legacy vs Historical Files

The uploaded protocol bundle contains three categories.

## 3.1 Active — embed these

Canonical active files:

```text
hqe-engineer.yaml
hqe-engineer-schema.json
validate.py
```

Place them at:

```text
/Users/super_user/Projects/Skill-HQE/protocol/
```

The package contains exact source copies under:

```text
canonical-protocol/
```

and convenience copies under:

```text
drop-in/protocol/
```

## 3.2 Legacy — optional only

The bundle also contains:

```text
hqe-schema.json
verify.py
```

These correspond to the older v3.x validation path.

Do not route `/HQE`, CI, or `SKILL.md` through them.

If backward-compatibility regression testing is desired, place them under:

```text
protocol/legacy/
```

Otherwise omit them.

They are supplied under:

```text
optional-legacy-protocol/
```

## 3.3 Historical archive — do not runtime-embed by default

The source archive contains older protocol versions and historical markdown.

Do not copy the full archive into the skill runtime by default.

Reasons:

- unnecessary context/repo weight;
- risk of an agent selecting an obsolete protocol;
- duplicate/conflicting instructions;
- no runtime benefit for ordinary `/HQE` use.

Preserve lineage instead in:

```text
references/source-lineage.md
docs/MIGRATION_FROM_HQE_WORKBENCH.md
docs/SOURCE_AUDIT.md
```

If regression testing against old protocol versions later becomes a real requirement, add explicitly named fixtures under tests rather than exposing the archive as runtime authority.

---

# 4. Important Source-Bundle Defect

The live protocol file reports:

```text
schema_version: 4.2.1
protocol_version: 4.2.1
```

and both supplied validators successfully validate it.

However, the active JSON Schema currently has stale metadata:

```text
$id:
https://hqe.dev/schemas/hqe-engineer-v4.0.0.json

title:
HQE Engineer Protocol v4.2.0 Schema
```

Do not blindly preserve this mismatch without review.

## Required action

Before changing the `$id`, search the real source repository for consumers:

```bash
cd "/Users/super_user/Projects/HQE-Workbench"

rg -n \
  'hqe-engineer-v4\.0\.0|HQE Engineer Protocol v4\.2\.0 Schema|hqe-engineer-schema\.json' \
  .
```

Then search the target:

```bash
cd "/Users/super_user/Projects/Skill-HQE"

rg -n \
  'hqe-engineer-v4\.0\.0|HQE Engineer Protocol v4\.2\.0 Schema|hqe-engineer-schema\.json' \
  .
```

If no external compatibility contract depends on the old `$id`, update the target copy to:

```text
$id:
https://hqe.dev/schemas/hqe-engineer-v4.2.1.json

title:
HQE Engineer Protocol v4.2.1 Schema
```

Do not alter structural validation semantics merely to change metadata.

Record the adjustment in:

```text
docs/SOURCE_AUDIT.md
CHANGELOG.md
```

Preserve source checksums so the difference is transparent.

If a consumer depends on the old `$id`, retain it and document the compatibility reason.

---

# 5. Target Layout

The target should contain at least:

```text
Skill-HQE/
├── SKILL.md
├── protocol/
│   ├── hqe-engineer.yaml
│   ├── hqe-engineer-schema.json
│   ├── validate.py
│   ├── README.md
│   ├── VALIDATORS.md
│   └── SOURCE_CHECKSUMS.sha256
├── scripts/
│   └── validate_protocol_bundle.py
├── tests/
│   └── test_protocol_contract.py
├── references/
│   ├── hqe-protocol.md
│   └── source-lineage.md
└── docs/
    ├── CAPABILITY_MAPPING.md
    ├── MIGRATION_FROM_HQE_WORKBENCH.md
    └── SOURCE_AUDIT.md
```

If legacy support is explicitly retained:

```text
protocol/legacy/
├── hqe-schema.json
├── verify.py
└── README.md
```

Do not mix legacy files into the active protocol directory without the `legacy/` boundary.

---

# 6. Copy the Supplied Files

From the unpacked package:

```bash
cd "/Users/super_user/Projects/Skill-HQE"

mkdir -p protocol scripts tests

cp "/path/to/package/drop-in/protocol/hqe-engineer.yaml" \
  protocol/hqe-engineer.yaml

cp "/path/to/package/drop-in/protocol/hqe-engineer-schema.json" \
  protocol/hqe-engineer-schema.json

cp "/path/to/package/drop-in/protocol/validate.py" \
  protocol/validate.py

cp "/path/to/package/drop-in/protocol/README.md" \
  protocol/README.md

cp "/path/to/package/drop-in/protocol/VALIDATORS.md" \
  protocol/VALIDATORS.md

cp "/path/to/package/drop-in/scripts/validate_protocol_bundle.py" \
  scripts/validate_protocol_bundle.py

cp "/path/to/package/drop-in/tests/test_protocol_contract.py" \
  tests/test_protocol_contract.py

chmod +x protocol/validate.py scripts/validate_protocol_bundle.py
```

Do not copy the package's `optional-legacy-protocol/` unless the compatibility decision is explicitly YES.

---

# 7. Preserve Source Integrity

Before editing the canonical copies, compute:

```bash
cd "/Users/super_user/Projects/Skill-HQE/protocol"

shasum -a 256 \
  hqe-engineer.yaml \
  hqe-engineer-schema.json \
  validate.py \
  > SOURCE_CHECKSUMS.sha256
```

Important:

If you intentionally update schema metadata after this baseline, do one of:

1. retain a `SOURCE_CHECKSUMS.sha256` that records the imported source hash and add a separate `TARGET_CHECKSUMS.sha256`; or
2. use a manifest documenting source hash and target hash.

Do not pretend an altered schema is byte-identical to source.

The uploaded source hashes observed during package preparation were:

```text
hqe-engineer.yaml:
f8703feee7b2915c6874f89fe299a467f9e79527a7e4b0e8b75785743dd0cc71

hqe-engineer-schema.json:
6b5e1a685e3cd3d2bc308be5d3147bf4dccef20ca75490971f51a162bdfbe314

validate.py:
0b907bb2ac5994f8dae0030f7a20690c8ab745e872a78f452cdd5c8ed8fe788f
```

Recompute them locally rather than trusting this text alone.

---

# 8. `SKILL.md` Integration

Do not paste the full YAML into `SKILL.md`.

Instead, `SKILL.md` must state the authority relationship clearly.

Required semantics:

```text
protocol/hqe-engineer.yaml is the canonical HQE protocol.
SKILL.md is the compact operational projection for agent runtime use.
If they conflict, the canonical protocol wins unless a documented migration
explicitly supersedes it.
```

Progressive disclosure should route as follows:

```text
routine invocation
-> SKILL.md + relevant focused references/workflow

protocol parity question
-> protocol/hqe-engineer.yaml

skill maintenance/version upgrade
-> protocol YAML + schema + validator + source-lineage docs

exhaustive audit requiring protocol artifact semantics
-> load only relevant protocol sections/references, not necessarily the whole file
```

Also fix the known current conflict:

Current skill:

```text
Always begin with Phase 0 — Orientation
```

Correct semantics:

```text
PR/change-set task:
Phase -1 first, then Phase 0.

Non-PR repository task:
Phase 0 first.

Phase 0 is mandatory before repository-wide substantive conclusions.
```

Restore `NEEDS_VERIFICATION` to the confidence vocabulary.

---

# 9. `references/hqe-protocol.md`

Create or update this as a human-readable projection of the active protocol.

Do not duplicate the entire YAML.

It should summarize and link to canonical sections for:

```text
identity/version
execution order
severity
confidence
effort
finding prefixes
health score
hard constraints
evidence standard
severity gate
likelihood model
taint chain
change budget
anti-regression
stop-the-line
no-stall
output controls
artifact contract
session log
quality gates
pre-delivery checklist
```

At the top:

```text
Canonical source:
../protocol/hqe-engineer.yaml

Protocol:
4.2.1
```

State that the YAML wins on conflict.

---

# 10. README Integration

The current README already links its protocol badge to:

```text
protocol/hqe-engineer.yaml
```

Once the file is embedded, that link becomes valid.

Do not stop there.

Correct claims so they are evidence-backed.

If parity repair is still incomplete, avoid:

```text
complete HQE Protocol v4.2.1
```

until tests prove that the skill's operational projection preserves required controls.

Prefer:

```text
built from and validated against HQE Engineer Protocol v4.2.1
```

until full parity is established.

Add protocol validation instructions.

---

# 11. Capability Mapping Integration

Expand:

```text
docs/CAPABILITY_MAPPING.md
```

Add separate entries for:

```text
canonical protocol YAML
active v4 schema
protocol validator
health scoring
hard constraints
severity gate
likelihood rubric
taint-chain requirement
change budget
anti-regression
stop-the-line
no-stall
output controls
finding IDs
artifact contract
session log
quality gates
pre-delivery checklist
```

Do not map the entire protocol to one generic row.

For each:

```text
Source file/section
Disposition
Target file(s)
Validation
```

---

# 12. CI Integration

Merge protocol dependencies into the repository's development dependency source of truth.

Package reference:

```text
support/requirements-protocol.txt
```

Do not create redundant dependency lists if the target already uses `pyproject.toml` or `requirements-dev.txt`.

CI must run:

```bash
python3 protocol/validate.py protocol/hqe-engineer.yaml
python3 protocol/validate.py --schema
python3 scripts/validate_protocol_bundle.py
python3 -m pytest -q tests/test_protocol_contract.py
```

After reconciling schema metadata, also run:

```bash
python3 scripts/validate_protocol_bundle.py --strict-schema-metadata
```

No "basic syntax validation" fallback in CI.

If PyYAML/jsonschema are missing, CI must fail.

---

# 13. Validator Integration

The package supplies:

```text
scripts/validate_protocol_bundle.py
```

Use this as a repository-level integrity wrapper.

It checks:

- required files;
- YAML parsing;
- JSON schema parsing;
- Draft 7 schema validity;
- full schema validation;
- format checks;
- semver coherence;
- core HQE sections;
- canonical finding prefixes;
- canonical phases;
- stale schema metadata.

The source `protocol/validate.py` remains useful because it carries source-specific semantic linting.

Use both.

Do not replace one with the other unless the functionality is explicitly merged and tested.

---

# 14. Tests

The package supplies:

```text
tests/test_protocol_contract.py
```

Keep and expand it.

Add tests proving the operational skill projection preserves protocol controls.

Recommended additional test:

```text
tests/test_protocol_skill_parity.py
```

It should assert that `SKILL.md` or mapped references expose required runtime controls such as:

```text
Phase -1
Phase 0
NEEDS_VERIFICATION
No Secret Leakage
Mandatory Evidence
Minimal Change
stop-the-line
behavior change
severity gate
pre-delivery
```

Do not make the test a brittle full-text snapshot.

Test meaningful control presence/routing.

---

# 15. Workbench Source Docs vs Skill Docs

The source protocol README references:

```text
./scripts/validate_protocol.sh
cargo build --release -p hqe
./target/release/hqe validate-protocol
```

Those are Workbench-specific.

Do not copy that README directly as the target `protocol/README.md`.

The package provides a skill-specific replacement.

The original source docs are preserved under:

```text
source-reference/
```

for provenance and comparison.

---

# 16. Legacy Validator Decision

Default:

```text
DO NOT INSTALL
```

for:

```text
optional-legacy-protocol/hqe-schema.json
optional-legacy-protocol/verify.py
```

If the maintainer wants legacy regression tests, install as:

```text
protocol/legacy/hqe-schema-v3.1.0.json
protocol/legacy/verify_v3.py
```

or equivalently clear names.

Do not leave generic names that could be mistaken for active v4 files.

Add tests ensuring active validation never imports the legacy schema.

---

# 17. Historical Archive Decision

Do not copy:

```text
archive/hqe-engineer-v3.0.0.yaml
archive/hqe-engineer-v3.1.0.yaml
archive/hqe-engineer-v4.2.0.yaml
archive/hqe-engineer-v4.2.1.yaml
historical HQE markdown docs
verify.hs
```

into runtime skill directories.

Notably, the uploaded archived file named:

```text
hqe-engineer-v4.2.1.yaml
```

is not byte-identical to the live `hqe-engineer.yaml`, and its banner still identifies v4.2.0 before later live changes. That is exactly why the archive should not compete with the active source.

Use the live file.

---

# 18. Licensing / Source Lineage

The active protocol YAML declares:

```text
license: MIT
```

while the broader HQE Workbench root has separate repository licensing signals.

Do not infer that all Workbench material is governed by the protocol's metadata.

In:

```text
docs/SOURCE_AUDIT.md
references/source-lineage.md
```

record:

- exact protocol source files imported;
- protocol-declared license;
- Workbench root license separately;
- any MCP/third-party source used elsewhere in the parity repair;
- modifications made to the target copy;
- source and target checksums where applicable.

---

# 19. Gitignore / Packaging

Do not package:

```text
.git/
__MACOSX/
__pycache__/
.DS_Store
*.pyc
```

The package includes a proposed complete Skill-HQE gitignore under:

```text
support/Skill-HQE.gitignore
```

Review it against the target repo and merge/replace `.gitignore` as appropriate.

Do not blindly overwrite if the target gained project-specific exceptions since this package was created.

---

# 20. Validation Sequence

After embedding but before semantic edits:

```bash
cd "/Users/super_user/Projects/Skill-HQE"

python3 protocol/validate.py protocol/hqe-engineer.yaml
python3 protocol/validate.py --schema
python3 scripts/validate_protocol_bundle.py
python3 -m pytest -q tests/test_protocol_contract.py
```

The wrapper may warn about stale schema metadata.

After deciding/fixing metadata:

```bash
python3 scripts/validate_protocol_bundle.py --strict-schema-metadata
```

Then run the entire skill suite:

```bash
python3 -m compileall -q scripts tests
python3 -m pytest -q
python3 scripts/check_skill.py .
```

Run all expanded parity-repair validations from:

```text
HQE_SKILL_PARITY_REPAIR_AGENT_HANDOFF.md
```

---

# 21. Verify Source Equality

For files intended to remain exact source imports:

```bash
cmp \
  "/Users/super_user/Projects/HQE-Workbench/protocol/hqe-engineer.yaml" \
  "/Users/super_user/Projects/Skill-HQE/protocol/hqe-engineer.yaml"
```

Repeat for any exact-import files.

If the target intentionally differs, document the diff.

Never silently fork the canonical protocol.

---

# 22. Definition of Done

Protocol embedding is complete only when:

1. `protocol/hqe-engineer.yaml` exists in Skill-HQE.
2. It is the active v4.2.1 source of truth.
3. The active schema exists beside it.
4. Full validation succeeds.
5. Stale schema metadata has been explicitly resolved/documented.
6. `SKILL.md` declares protocol authority and progressive disclosure.
7. PR Phase -1 ordering is correct.
8. `NEEDS_VERIFICATION` is represented.
9. README protocol links work.
10. `references/hqe-protocol.md` accurately projects the protocol.
11. capability mapping has granular protocol entries.
12. CI validates the protocol.
13. tests enforce protocol integrity.
14. legacy validators cannot become active accidentally.
15. old archive files are not runtime authorities.
16. source lineage/licensing is documented.
17. packaging excludes `.git`, `__MACOSX`, caches, and generated debris.
18. the broader parity-repair handoff remains satisfied.

---

# 23. Required Final Agent Report

Return:

```text
Protocol source path
Target protocol path
Protocol version
Schema version
Imported source hashes
Target hashes
Schema metadata decision
Files created
Files modified
SKILL.md integration changes
README integration changes
Capability mapping changes
CI changes
Tests added
Validation commands
Exact results
Legacy protocol decision
Archive decision
Licensing/source-lineage notes
Remaining limitations
```

Include:

```bash
find "/Users/super_user/Projects/Skill-HQE/protocol" -type f | sort
```

and:

```bash
python3 scripts/validate_protocol_bundle.py --strict-schema-metadata
python3 -m pytest -q
```

final outputs.

---

# 24. Final Directive

Embed the protocol as **canonical data**, not as another giant prompt.

The correct model is:

```text
canonical protocol YAML
        ↓
validated schema/semantic contract
        ↓
compact SKILL.md control plane
        ↓
focused references/workflows/templates
        ↓
tests proving parity
```

This gives `/HQE` a stable source of truth without making every invocation ingest the entire Workbench or protocol corpus.
