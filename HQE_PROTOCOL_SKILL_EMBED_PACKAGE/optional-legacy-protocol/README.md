# Optional Legacy Protocol Compatibility

These files come from the uploaded HQE protocol bundle:

- `hqe-schema.json` — legacy v3.1.0 JSON Schema.
- `verify.py` — legacy validator for `hqe-schema.json`.

They are **not** the canonical runtime definition for `/HQE` v4.2.1.

Default recommendation: do not copy these into the active `protocol/` directory. Keep them only if the maintainer explicitly wants backward-compatibility/regression tests for older protocol generations. If retained in the repo, place them under `protocol/legacy/` and ensure `SKILL.md`, CI, and runtime validation point to the v4.2.1 files instead.
