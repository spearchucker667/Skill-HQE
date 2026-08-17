# HQE Protocol — Skill Runtime Contract

This directory contains the canonical HQE Engineer protocol embedded in the `/HQE` skill.

## Canonical files

- `hqe-engineer.yaml` — authoritative HQE Engineer protocol definition.
- `hqe-engineer-schema.json` — JSON Schema for the active protocol.
- `validate.py` — source-provided v4 semantic/schema validator.
- `SOURCE_CHECKSUMS.sha256` — source-integrity record for the files imported from HQE Workbench/protocol bundle.

## Authority

For HQE protocol semantics, use this precedence:

1. `protocol/hqe-engineer.yaml`
2. `protocol/hqe-engineer-schema.json`
3. `SKILL.md` operational projection
4. `references/*.md` and `workflows/*.md`
5. Historical/migration documentation

If `SKILL.md` or a reference conflicts with `hqe-engineer.yaml`, the protocol YAML is the source of truth unless the repository explicitly records a newer protocol migration.

## Runtime loading

Do **not** load the full 60KB+ YAML into every `/HQE` invocation.

`SKILL.md` should carry the compact control plane and route to focused references. Load or inspect the canonical YAML when:

- validating skill/protocol parity;
- resolving a semantic conflict;
- maintaining/upgrading HQE;
- generating exhaustive protocol-derived artifacts;
- verifying a control absent from the human-readable projection.

This preserves progressive disclosure without losing the canonical protocol.

## Validation

Preferred repository-level validation:

```bash
python3 scripts/validate_protocol_bundle.py
```

Direct source validator:

```bash
python3 protocol/validate.py protocol/hqe-engineer.yaml
python3 protocol/validate.py --schema
```

Full schema validation requires Python dependencies such as PyYAML and jsonschema. Validation must fail closed when those dependencies are unavailable in CI.

## Legacy files

The v3-era `hqe-schema.json` and `verify.py` are not active protocol files. If backward compatibility is required, keep them under `protocol/legacy/`, never alongside the active files without clear naming/routing.

## Historical archives

Do not copy the old `archive/` protocol versions into the runtime skill by default. Preserve lineage in `references/source-lineage.md` and `docs/MIGRATION_FROM_HQE_WORKBENCH.md`. Add historical protocol files only when there is a concrete regression/compatibility requirement.
