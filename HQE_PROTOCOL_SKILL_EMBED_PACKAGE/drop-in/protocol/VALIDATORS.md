# HQE Protocol Validation in Skill-HQE

## Active validator

The active protocol is:

```text
protocol/hqe-engineer.yaml
```

validated against:

```text
protocol/hqe-engineer-schema.json
```

The source-provided validator is:

```text
protocol/validate.py
```

The skill-level integration validator is:

```text
scripts/validate_protocol_bundle.py
```

## Required behavior

Protocol validation must:

1. parse YAML safely;
2. parse the JSON Schema;
3. validate the JSON Schema itself;
4. validate protocol data against the schema;
5. enforce semantic invariants not expressible cleanly in schema;
6. fail closed if full validation dependencies are unavailable in CI;
7. verify `schema_version == protocol_version`;
8. surface stale schema metadata;
9. never rewrite the protocol as a side effect.

## Known source-bundle issue to reconcile

The uploaded live protocol is v4.2.1 and validates successfully, but the active schema metadata currently contains stale identifiers:

```text
$id   -> ...hqe-engineer-v4.0.0.json
title -> HQE Engineer Protocol v4.2.0 Schema
```

Do not silently ignore this.

During integration, determine whether external consumers depend on the old `$id`. If not, update the target skill copy to v4.2.1 metadata and document the change in `docs/SOURCE_AUDIT.md` / changelog. Preserve the original source checksum separately so provenance remains clear.

## Legacy validator

`hqe-schema.json` + `verify.py` are v3.x compatibility assets. They should not be part of default runtime validation for v4.2.1.
