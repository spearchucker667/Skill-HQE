#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
SCHEMAS_DIR = ROOT_DIR / "schemas"
FIXTURES_DIR = ROOT_DIR / "tests" / "fixtures"

try:
    from jsonschema import validate, ValidationError
    from referencing import Registry, Resource
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

class TestHQESkillSuite(unittest.TestCase):

    def test_required_structure(self):
        required_paths = [
            "SKILL.md",
            "README.md",
            "LICENSE",
            "TERMS_OF_SERVICE.md",
            "PRIVACY.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            "CONTRIBUTING.md",
            "docs/ARCHITECTURE.md",
            "docs/SECURITY_MODEL.md",
            "docs/THREAT_MODEL.md",
            "docs/USER_GUIDE.md",
            "docs/DEVELOPER_GUIDE.md",
            "docs/FINDING_SPECIFICATION.md",
            "development/migration-notes/CAPABILITY_MAPPING.md",
            "schemas/finding.schema.json",
            "schemas/findings.schema.json",
            "schemas/run-manifest.schema.json",
            "schemas/handoff.schema.json",
            "scripts/inventory_repo.py",
            "scripts/validate_findings.py",
            "scripts/check_skill.py",
            "scripts/detect_manifests.py",
            ".github/workflows/ci.yml",
            ".github/workflows/validate-skill.yml",
            ".github/workflows/security-scan.yml",
        ]
        for path_str in required_paths:
            p = ROOT_DIR / path_str
            self.assertTrue(p.exists(), f"Expected path does not exist: {path_str}")

    @unittest.skipUnless(HAS_JSONSCHEMA, "jsonschema package not installed")
    def test_finding_valid_fixture(self):
        with open(SCHEMAS_DIR / "findings.schema.json") as sf:
            findings_schema = json.load(sf)
        with open(SCHEMAS_DIR / "finding.schema.json") as sf:
            finding_schema = json.load(sf)
        with open(FIXTURES_DIR / "sample_finding_valid.json") as ff:
            sample_data = json.load(ff)

        registry = Registry().with_resource(
            "finding.schema.json", Resource.from_contents(finding_schema)
        )
        # Should not raise
        validate(instance=sample_data, schema=findings_schema, registry=registry)

    @unittest.skipUnless(HAS_JSONSCHEMA, "jsonschema package not installed")
    def test_finding_invalid_fixture_fails(self):
        with open(SCHEMAS_DIR / "findings.schema.json") as sf:
            findings_schema = json.load(sf)
        with open(SCHEMAS_DIR / "finding.schema.json") as sf:
            finding_schema = json.load(sf)
        with open(FIXTURES_DIR / "sample_finding_invalid.json") as ff:
            sample_data = json.load(ff)

        registry = Registry().with_resource(
            "finding.schema.json", Resource.from_contents(finding_schema)
        )
        with self.assertRaises(ValidationError):
            validate(instance=sample_data, schema=findings_schema, registry=registry)

    @unittest.skipUnless(HAS_JSONSCHEMA, "jsonschema package not installed")
    def test_run_manifest_fixture(self):
        with open(SCHEMAS_DIR / "run-manifest.schema.json") as sf:
            manifest_schema = json.load(sf)
        with open(FIXTURES_DIR / "sample_manifest.json") as ff:
            sample_data = json.load(ff)
        validate(instance=sample_data, schema=manifest_schema)

    @unittest.skipUnless(HAS_JSONSCHEMA, "jsonschema package not installed")
    def test_handoff_fixture(self):
        with open(SCHEMAS_DIR / "handoff.schema.json") as sf:
            handoff_schema = json.load(sf)
        with open(SCHEMAS_DIR / "finding.schema.json") as sf:
            finding_schema = json.load(sf)
        with open(FIXTURES_DIR / "sample_handoff.json") as ff:
            sample_data = json.load(ff)

        registry = Registry().with_resource(
            "finding.schema.json", Resource.from_contents(finding_schema)
        )
        validate(instance=sample_data, schema=handoff_schema, registry=registry)

if __name__ == "__main__":
    unittest.main()
