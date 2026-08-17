from pathlib import Path
import json
import yaml
from jsonschema import FormatChecker
from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocol" / "hqe-engineer.yaml"
SCHEMA = ROOT / "protocol" / "hqe-engineer-schema.json"


def _load():
    protocol = yaml.safe_load(PROTOCOL.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return protocol, schema


def test_protocol_files_exist():
    assert PROTOCOL.is_file()
    assert SCHEMA.is_file()


def test_protocol_and_schema_versions_match():
    protocol, _ = _load()
    assert protocol["protocol_version"] == protocol["schema_version"]


def test_protocol_is_v500():
    protocol, _ = _load()
    assert protocol["protocol_version"] == "5.0.0"


def test_protocol_schema_validation():
    protocol, schema = _load()
    validator_cls = validator_for(schema)
    validator_cls.check_schema(schema)
    errors = list(
        validator_cls(schema, format_checker=FormatChecker()).iter_errors(protocol)
    )
    assert not errors, "\n".join(str(err) for err in errors)


def test_core_hqe_controls_present():
    protocol, _ = _load()
    for key in (
        "hard_constraints",
        "constraints",
        "phases",
        "output_controls",
        "pre_delivery_checklist",
    ):
        assert key in protocol

    prefixes = protocol["definitions"]["id_prefixes"]
    for prefix in ("BOOT", "SEC", "BUG", "REL", "PERF", "UX", "DX", "DOC", "DEBT", "DEPS"):
        assert prefix in prefixes


def test_all_canonical_phases_present():
    protocol, _ = _load()
    phases = protocol["phases"]
    expected = {
        "phase_minus_one",
        "phase_zero",
        "phase_zero_five",
        "phase_one",
        "phase_two",
        "phase_three",
        "phase_four",
    }
    assert expected.issubset(phases)
