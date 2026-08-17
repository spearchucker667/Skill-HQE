# HQE Protocol → Skill-HQE Integration Package

## Answer

Yes: the active HQE protocol belongs in the `/HQE` repository.

The recommended canonical runtime set is:

```text
protocol/hqe-engineer.yaml
protocol/hqe-engineer-schema.json
protocol/validate.py
protocol/README.md
protocol/VALIDATORS.md
protocol/SOURCE_CHECKSUMS.sha256
```

Also integrate:

```text
scripts/validate_protocol_bundle.py
tests/test_protocol_contract.py
```

The old v3 `hqe-schema.json` and `verify.py` are optional compatibility assets only. The historical `archive/` should not be runtime-embedded by default.

## Package contents

```text
START_AGENT_PROMPT.md
    User-provided launch prompt, preserved verbatim.

HQE_SKILL_PARITY_REPAIR_AGENT_HANDOFF.md
    Exhaustive broader parity-repair specification.

PROTOCOL_EMBEDDING_AGENT_HANDOFF.md
    Protocol-specific placement, wiring, validation, and acceptance handoff.

canonical-protocol/
    Byte-for-byte active protocol source files from the uploaded bundle.

drop-in/
    Recommended files to place into Skill-HQE.

optional-legacy-protocol/
    Older v3 validation assets. Do not install by default.

source-reference/
    Original Workbench-oriented protocol documentation for provenance.

support/
    Dependency hint and repo .gitignore support file.

SOURCE_PROTOCOL_SHA256SUMS.txt
    Integrity hashes for source protocol files.
```

## Important finding

The active protocol YAML is v4.2.1 and validates with both supplied validators.

The active `hqe-engineer-schema.json` is structurally usable but its metadata is stale:

```text
$id   references v4.0.0
title references v4.2.0
```

The embedding handoff requires the agent to determine whether this can be safely corrected to v4.2.1 in the target copy.

## Start

Give the entire unpacked package to the implementation agent and tell it:

```text
Read START_AGENT_PROMPT.md first, then execute
HQE_SKILL_PARITY_REPAIR_AGENT_HANDOFF.md and
PROTOCOL_EMBEDDING_AGENT_HANDOFF.md against
/Users/super_user/Projects/Skill-HQE/.
```
