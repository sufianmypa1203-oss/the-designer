"""
The Designer — Validator Tests

Tests the DesignValidator's deterministic checks against
real and mock spec files.
"""
import json
import pytest
from pathlib import Path
from designer.validator import DesignValidator, ValidationIssue


@pytest.fixture
def tmp_specs(tmp_path):
    """Create temp specs directory with minimal valid upstream files."""
    specs = tmp_path / "specs"
    specs.mkdir()

    # Brief
    (specs / "01-brief.md").write_text("# Brief\nBrand: TestBrand\nColors: #FF6B35, #0A0A12, #FFFFFF\n" * 3)

    # Script
    (specs / "02-script.md").write_text("# Script\n## Scene 1: Hook\nYour money disappears.\n## Scene 2: Problem\nEvery month.\n")

    # Scene map
    scene_map = {
        "projectId": "test-project",
        "compositionName": "TestComp",
        "scenes": [
            {"id": "scene-1", "name": "Hook", "role": "hook", "prototypeFile": "Scene1_Hook.html"},
            {"id": "scene-2", "name": "Problem", "role": "problem", "prototypeFile": "Scene2_Problem.html"},
        ]
    }
    (specs / "03-scene-map.json").write_text(json.dumps(scene_map, indent=2))

    return specs


@pytest.fixture
def tmp_protos(tmp_path):
    """Create temp prototypes directory."""
    protos = tmp_path / "prototypes"
    protos.mkdir()
    return protos


class TestUpstreamValidation:
    def test_all_present_passes(self, tmp_specs):
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_upstream_artifacts()
        assert len(issues) == 0

    def test_missing_brief_fails(self, tmp_specs):
        (tmp_specs / "01-brief.md").unlink()
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_upstream_artifacts()
        assert any("01-brief.md" in i.message for i in issues)

    def test_empty_script_fails(self, tmp_specs):
        (tmp_specs / "02-script.md").write_text("")
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_upstream_artifacts()
        assert any("empty" in i.message.lower() for i in issues)

    def test_missing_all_three_reports_three(self, tmp_path):
        empty_specs = tmp_path / "empty_specs"
        empty_specs.mkdir()
        v = DesignValidator(specs_dir=empty_specs)
        issues = v.validate_upstream_artifacts()
        assert len(issues) == 3


class TestSceneMapValidation:
    def test_valid_scene_map(self, tmp_specs):
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_scene_map_schema()
        assert len(issues) == 0

    def test_invalid_json(self, tmp_specs):
        (tmp_specs / "03-scene-map.json").write_text("{invalid json}")
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_scene_map_schema()
        assert any("Invalid JSON" in i.message for i in issues)

    def test_missing_scenes_key(self, tmp_specs):
        (tmp_specs / "03-scene-map.json").write_text(json.dumps({"projectId": "test"}))
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_scene_map_schema()
        assert any("scenes" in i.message for i in issues)


class TestValidationReport:
    def test_empty_report(self, tmp_specs):
        v = DesignValidator(specs_dir=tmp_specs)
        report = v.format_report([])
        assert "passed" in report.lower()

    def test_critical_report(self):
        v = DesignValidator()
        issues = [
            ValidationIssue("CRITICAL", "TEST", "Something broke", "Fix it"),
        ]
        report = v.format_report(issues)
        assert "CRITICAL" in report
        assert "must be fixed" in report

    def test_has_critical_true(self):
        v = DesignValidator()
        issues = [
            ValidationIssue("CRITICAL", "TEST", "Broken"),
            ValidationIssue("MEDIUM", "TEST", "Warning"),
        ]
        assert v.has_critical_issues(issues) is True

    def test_has_critical_false(self):
        v = DesignValidator()
        issues = [ValidationIssue("MEDIUM", "TEST", "Fine")]
        assert v.has_critical_issues(issues) is False
