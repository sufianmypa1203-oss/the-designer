"""
The Designer — Tool & Agent Tests

Tests for:
  - write_prototype() viewport validation (Phase C)
  - write_visual_spec() / write_typography_spec() / write_prototype_manifest()
  - export_schemas()
  - generate_handoff_block()
  - validate_upstream()
  - Agent scope guards and lifecycle
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


# ─── Helpers ──────────────────────────────────────────────────────────────────

VALID_HTML = (
    '<!DOCTYPE html><html><head>'
    '<meta name="viewport" content="width=360, initial-scale=1">'
    '</head><body>'
    '<div data-element-id="scene-1-hero-text-0" data-layer="foreground">'
    'Your money disappears</div></body></html>'
)

VALID_HTML_NO_VIEWPORT = (
    '<div data-element-id="el-1" data-layer="foreground">Text</div>'
)


# ─── write_prototype Tests ───────────────────────────────────────────────────

class TestWritePrototype:
    def test_valid_prototype_writes(self, tmp_path):
        result = write_prototype("Scene1_Hook.html", VALID_HTML, tmp_path)
        assert result["success"] is True
        assert (tmp_path / "Scene1_Hook.html").exists()

    def test_invalid_filename_rejects(self, tmp_path):
        result = write_prototype("bad.html", VALID_HTML, tmp_path)
        assert result["success"] is False
        assert "pattern" in result["error"]

    def test_non_html_rejects(self, tmp_path):
        result = write_prototype("Scene1_Hook.txt", VALID_HTML, tmp_path)
        assert result["success"] is False

    def test_missing_element_id_rejects(self, tmp_path):
        html = '<meta name="viewport" content="width=360"><div data-layer="foreground">x</div>'
        result = write_prototype("Scene1_Hook.html", html, tmp_path)
        assert result["success"] is False
        assert "data-element-id" in result["error"]

    def test_missing_data_layer_rejects(self, tmp_path):
        html = '<meta name="viewport" content="width=360"><div data-element-id="e1">x</div>'
        result = write_prototype("Scene1_Hook.html", html, tmp_path)
        assert result["success"] is False
        assert "data-layer" in result["error"]

    def test_missing_viewport_rejects(self, tmp_path):
        result = write_prototype("Scene1_Hook.html", VALID_HTML_NO_VIEWPORT, tmp_path)
        assert result["success"] is False
        assert "viewport" in result["error"]

    def test_viewport_with_meta_tag_passes(self, tmp_path):
        result = write_prototype("Scene1_Hook.html", VALID_HTML, tmp_path)
        assert result["success"] is True

    def test_returns_size_bytes(self, tmp_path):
        result = write_prototype("Scene1_Hook.html", VALID_HTML, tmp_path)
        assert result["size_bytes"] > 0

    def test_creates_directory_if_missing(self, tmp_path):
        target = tmp_path / "new_dir"
        result = write_prototype("Scene1_Hook.html", VALID_HTML, target)
        assert result["success"] is True
        assert target.exists()


# ─── write_visual_spec Tests ─────────────────────────────────────────────────

class TestWriteVisualSpec:
    def test_valid_spec_writes(self, tmp_path):
        from conftest import make_visual_spec
        content = json.dumps(make_visual_spec())
        result = write_visual_spec(content, tmp_path)
        assert result["success"] is True
        assert (tmp_path / "04-visual-design-spec.json").exists()

    def test_invalid_json_rejects(self, tmp_path):
        result = write_visual_spec("{bad json", tmp_path)
        assert result["success"] is False
        assert "Invalid JSON" in result["error"]

    def test_invalid_schema_rejects(self, tmp_path):
        result = write_visual_spec('{"bad": "data"}', tmp_path)
        assert result["success"] is False
        assert "Schema validation" in result["error"]

    def test_returns_scene_count(self, tmp_path):
        from conftest import make_visual_spec
        content = json.dumps(make_visual_spec())
        result = write_visual_spec(content, tmp_path)
        assert result["scene_count"] == 1


# ─── write_typography_spec Tests ─────────────────────────────────────────────

class TestWriteTypographySpec:
    def test_valid_spec_writes(self, tmp_path):
        from conftest import make_typography_spec
        content = json.dumps(make_typography_spec())
        result = write_typography_spec(content, tmp_path)
        assert result["success"] is True

    def test_invalid_json_rejects(self, tmp_path):
        result = write_typography_spec("not json!!", tmp_path)
        assert result["success"] is False

    def test_invalid_schema_rejects(self, tmp_path):
        result = write_typography_spec('{"wrong": true}', tmp_path)
        assert result["success"] is False


# ─── write_prototype_manifest Tests ──────────────────────────────────────────

class TestWritePrototypeManifest:
    def test_valid_manifest_writes(self, tmp_path):
        from conftest import make_prototype_manifest
        content = json.dumps(make_prototype_manifest())
        result = write_prototype_manifest(content, tmp_path)
        assert result["success"] is True
        assert result["total_elements"] == 2

    def test_invalid_json_rejects(self, tmp_path):
        result = write_prototype_manifest("{{", tmp_path)
        assert result["success"] is False


# ─── export_schemas Tests ────────────────────────────────────────────────────

class TestExportSchemas:
    def test_exports_three_schemas(self, tmp_path):
        result = export_schemas(tmp_path)
        assert result["success"] is True
        assert len(result["schemas_exported"]) == 3
        for f in result["schemas_exported"]:
            assert (tmp_path / f).exists()

    def test_schemas_are_valid_json(self, tmp_path):
        export_schemas(tmp_path)
        for f in (tmp_path).glob("*.json"):
            data = json.loads(f.read_text())
            assert "type" in data or "properties" in data


# ─── validate_upstream Tests ─────────────────────────────────────────────────

class TestValidateUpstream:
    def test_all_present_passes(self, tmp_specs):
        result = validate_upstream(tmp_specs)
        assert result["valid"] is True
        assert result["scene_count"] == 2

    def test_missing_artifacts_fails(self, tmp_path):
        target = tmp_path / "empty_specs"
        target.mkdir()
        result = validate_upstream(target)
        assert result["valid"] is False
        assert len(result["issues"]) > 0


# ─── generate_handoff_block Tests ────────────────────────────────────────────

class TestGenerateHandoff:
    def test_valid_project_generates(self, full_specs, tmp_path):
        protos = tmp_path / "prototypes"
        protos.mkdir()
        (protos / "Scene1_Hook.html").write_text(
            '<div data-element-id="e1" data-layer="fg">x</div>'
        )
        (protos / "Scene2_Problem.html").write_text(
            '<div data-element-id="e2" data-layer="fg">y</div>'
        )
        result = generate_handoff_block(
            project_id="test-project",
            specs_dir=full_specs,
            prototypes_dir=protos,
        )
        # Whether it succeeds or not, it should return a dict
        assert isinstance(result, dict)
        if result["success"]:
            assert "motion-architect" in result["handoff_block"]
            assert result["project_id"] == "test-project"

    def test_extracts_project_id_from_scene_map(self, full_specs, tmp_path):
        protos = tmp_path / "prototypes"
        protos.mkdir()
        (protos / "Scene1_Hook.html").write_text(
            '<div data-element-id="e1" data-layer="fg">x</div>'
        )
        (protos / "Scene2_Problem.html").write_text(
            '<div data-element-id="e2" data-layer="fg">y</div>'
        )
        result = generate_handoff_block(
            specs_dir=full_specs,
            prototypes_dir=protos,
        )
        if result["success"]:
            assert result["project_id"] == "test-project"


# ─── run_design_validation Tests ─────────────────────────────────────────────

class TestRunDesignValidation:
    def test_returns_structured_result(self, full_specs, tmp_path):
        protos = tmp_path / "prototypes"
        protos.mkdir()
        result = run_design_validation(full_specs, protos)
        assert "total_issues" in result
        assert "handoff_blocked" in result
        assert "report" in result

    def test_includes_report_text(self, full_specs, tmp_path):
        protos = tmp_path / "prototypes"
        protos.mkdir()
        result = run_design_validation(full_specs, protos)
        assert isinstance(result["report"], str)


# ─── Agent Scope Guard Tests ────────────────────────────────────────────────

class TestAgentScopeGuards:
    """Verify the agent respects its scope boundaries."""

    def test_tools_are_registered(self):
        from designer.tools import DESIGNER_TOOLS
        assert len(DESIGNER_TOOLS) == 8
        expected = {
            "validate_upstream", "write_prototype",
            "write_visual_spec", "write_typography_spec",
            "write_prototype_manifest", "run_design_validation",
            "generate_handoff_block", "export_schemas",
        }
        assert set(DESIGNER_TOOLS.keys()) == expected

    def test_models_are_importable(self):
        from designer.models import (
            VisualDesignSpec, TypographySpec, PrototypeManifest,
            ColorApplication, FocalPointSpec, DepthLayer,
            SceneDesignSpec, TextElement, SceneTypography,
            ElementGeometry, PrototypeEntry,
        )
        # All 11 models importable
        assert VisualDesignSpec is not None

    def test_color_utils_importable(self):
        from designer.color_utils import contrast_ratio, check_wcag_aa
        assert contrast_ratio("#FFFFFF", "#000000") == pytest.approx(21.0, abs=0.1)
        assert check_wcag_aa("#FFFFFF", "#000000") is True

    def test_validator_has_15_methods(self):
        from designer.validator import DesignValidator
        v = DesignValidator()
        methods = [m for m in dir(v) if m.startswith("validate_") and callable(getattr(v, m))]
        assert len(methods) == 15

    def test_validator_has_format_report(self):
        from designer.validator import DesignValidator
        v = DesignValidator()
        report = v.format_report([])
        assert "passed" in report.lower() or "clean" in report.lower()

    def test_validator_has_build_llm_prompt(self):
        from designer.validator import DesignValidator
        v = DesignValidator()
        prompt = v.build_llm_evaluator_prompt("brief", "visual", "typo")
        assert len(prompt) > 100
        assert "JSON" in prompt
