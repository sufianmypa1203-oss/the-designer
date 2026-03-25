"""
The Designer — Cross-Validation Tests

Tests that validate the handoff pipeline:
upstream artifacts → tools → specs → validator → handoff.
"""
import json
import pytest
from pathlib import Path
from designer.tools import (
    validate_upstream,
    write_prototype,
    write_visual_spec,
    write_typography_spec,
    write_prototype_manifest,
    run_design_validation,
    generate_handoff_block,
    export_schemas,
)


@pytest.fixture
def mock_project(tmp_path):
    """Create a complete mock project directory."""
    specs = tmp_path / "specs"
    specs.mkdir()
    protos = tmp_path / "prototypes"
    protos.mkdir()

    # Upstream artifacts
    (specs / "01-brief.md").write_text("# Brief\nBrand: TestBrand\nColors: #FF6B35\n" * 3)
    (specs / "02-script.md").write_text("# Script\n## Scene 1\nYour money disappears.\n" * 3)
    scene_map = {
        "projectId": "test-project",
        "compositionName": "TestComp",
        "scenes": [
            {"id": "scene-1", "name": "Hook", "role": "hook", "prototypeFile": "Scene1_Hook.html"},
        ]
    }
    (specs / "03-scene-map.json").write_text(json.dumps(scene_map, indent=2))

    return tmp_path, specs, protos


class TestValidateUpstream:
    def test_valid_upstream(self, mock_project):
        _, specs, _ = mock_project
        result = validate_upstream(specs_dir=specs)
        assert result["valid"] is True
        assert result["scene_count"] == 1

    def test_missing_upstream(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = validate_upstream(specs_dir=empty)
        assert result["valid"] is False
        assert len(result["issues"]) == 3


class TestWritePrototype:
    def test_valid_prototype(self, mock_project):
        _, _, protos = mock_project
        html = ('<meta name="viewport" content="width=360, initial-scale=1">'
                '<div data-element-id="el-1" data-layer="foreground">Hello</div>')
        result = write_prototype("Scene1_Hook.html", html, prototypes_dir=protos)
        assert result["success"] is True

    def test_invalid_filename(self, mock_project):
        _, _, protos = mock_project
        result = write_prototype("bad.html", "<div></div>", prototypes_dir=protos)
        assert result["success"] is False

    def test_missing_element_id(self, mock_project):
        _, _, protos = mock_project
        result = write_prototype("Scene1_Hook.html", "<div>no ids</div>", prototypes_dir=protos)
        assert result["success"] is False
        assert "data-element-id" in result["error"]

    def test_missing_data_layer(self, mock_project):
        _, _, protos = mock_project
        html = '<div data-element-id="el-1">no layer</div>'
        result = write_prototype("Scene1_Hook.html", html, prototypes_dir=protos)
        assert result["success"] is False
        assert "data-layer" in result["error"]


class TestExportSchemas:
    def test_exports_3_schemas(self, tmp_path):
        out = tmp_path / "schemas"
        result = export_schemas(output_dir=out)
        assert result["success"] is True
        assert len(result["schemas_exported"]) == 3
        for f in result["schemas_exported"]:
            assert (out / f).exists()

    def test_schema_is_valid_json(self, tmp_path):
        out = tmp_path / "schemas"
        export_schemas(output_dir=out)
        for f in out.iterdir():
            data = json.loads(f.read_text())
            assert "properties" in data or "$defs" in data


class TestHandoffBlock:
    def test_handoff_blocked_without_specs(self, mock_project):
        _, specs, protos = mock_project
        result = generate_handoff_block(
            project_id="test",
            specs_dir=specs,
            prototypes_dir=protos,
        )
        # Should fail because Designer specs don't exist
        assert result["success"] is False

    def test_validation_no_specs(self, mock_project):
        _, specs, protos = mock_project
        result = run_design_validation(specs_dir=specs, prototypes_dir=protos)
        # Missing designer specs = critical
        assert result["handoff_blocked"] is True
        assert result["critical_count"] > 0
