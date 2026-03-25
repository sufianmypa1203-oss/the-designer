"""
The Designer — New Validator Tests (Checks 10-15)

Tests for the 6 newly added deterministic validation checks:
  10. Live WCAG contrast recalculation
  11. Canvas scaling ×3 spot-check
  12. Depth layers ≥2 per scene
  13. Weight contrast ≥300 cross-check
  14. Element IDs globally unique
  15. Text-to-script matching
Also: color_count duplicate detection fix (Check 9).
"""
import json
import pytest
from pathlib import Path
from designer.validator import DesignValidator, ValidationIssue


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _write_full_specs(specs_dir: Path, visual=None, typo=None, manifest=None):
    """Write visual/typo/manifest specs as JSON files."""
    from conftest import make_visual_spec, make_typography_spec, make_prototype_manifest
    if visual is not None:
        (specs_dir / "04-visual-design-spec.json").write_text(json.dumps(visual, indent=2))
    if typo is not None:
        (specs_dir / "05-typography-spec.json").write_text(json.dumps(typo, indent=2))
    if manifest is not None:
        (specs_dir / "06-prototype-manifest.json").write_text(json.dumps(manifest, indent=2))


# ─── Check 9: Color Count (Fixed) ────────────────────────────────────────────

class TestColorCountFixed:
    """The old validate_color_count was a no-op. Now it detects duplicate colors."""

    def test_distinct_colors_passes(self, full_specs):
        v = DesignValidator(specs_dir=full_specs)
        issues = v.validate_color_count()
        assert len(issues) == 0

    def test_duplicate_60_30_detected(self, tmp_specs):
        from conftest import make_visual_spec, make_scene_design, make_color_app
        visual = make_visual_spec(scenes=[
            make_scene_design(colors=make_color_app(
                dominant_60="#FFFFFF",
                secondary_30="#FFFFFF",  # same as dominant!
                accent_10="#FF6B35",
            ))
        ])
        _write_full_specs(tmp_specs, visual=visual)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_color_count()
        assert len(issues) == 1
        assert "Duplicate" in issues[0].message
        assert "#FFFFFF" in issues[0].message

    def test_all_three_same_detected(self, tmp_specs):
        from conftest import make_visual_spec, make_scene_design, make_color_app
        visual = make_visual_spec(scenes=[
            make_scene_design(colors=make_color_app(
                dominant_60="#000000",
                secondary_30="#000000",
                accent_10="#000000",
            ))
        ])
        _write_full_specs(tmp_specs, visual=visual)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_color_count()
        assert len(issues) == 1

    def test_missing_spec_skips(self, tmp_specs):
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_color_count()
        assert len(issues) == 0


# ─── Check 10: Live Contrast Recalculation ────────────────────────────────────

class TestContrastRecalc:
    """Re-calculates WCAG contrast from raw hex values in visual + typo specs."""

    def test_high_contrast_passes(self, tmp_specs):
        from conftest import make_visual_spec, make_typography_spec
        _write_full_specs(tmp_specs,
                          visual=make_visual_spec(),
                          typo=make_typography_spec())
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_contrast_recalc()
        # White (#FFFFFF) on dark (#0A0A12) = ~18:1, passes easily
        assert len(issues) == 0

    def test_low_contrast_fails(self, tmp_specs):
        from conftest import (make_visual_spec, make_typography_spec,
                              make_scene_typography, make_text_element,
                              make_sub_text_element)
        # Light gray text on white background = low contrast
        from conftest import make_scene_design, make_color_app
        visual = make_visual_spec(scenes=[
            make_scene_design(colors=make_color_app(
                dominant_60="#FFFFFF",  # white bg
            ))
        ])
        typo = make_typography_spec(scenes=[
            make_scene_typography(elements=[
                make_text_element(color="#CCCCCC"),  # light gray on white
                make_sub_text_element(color="#CCCCCC"),
            ])
        ])
        _write_full_specs(tmp_specs, visual=visual, typo=typo)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_contrast_recalc()
        assert len(issues) == 2
        assert all(i.severity == "CRITICAL" for i in issues)
        assert all("WCAG AA" in i.message for i in issues)

    def test_missing_visual_spec_skips(self, tmp_specs):
        from conftest import make_typography_spec
        _write_full_specs(tmp_specs, typo=make_typography_spec())
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_contrast_recalc()
        assert len(issues) == 0


# ─── Check 11: Canvas Scaling ×3 Spot-Check ──────────────────────────────────

class TestCanvasScalingSpotcheck:
    """Re-verifies canvas = prototype × 3 across both typo and manifest specs."""

    def test_correct_scaling_passes(self, tmp_specs):
        from conftest import make_typography_spec, make_prototype_manifest
        _write_full_specs(tmp_specs,
                          typo=make_typography_spec(),
                          manifest=make_prototype_manifest())
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_canvas_scaling_spotcheck()
        assert len(issues) == 0

    def test_wrong_font_scaling_fails(self, tmp_specs):
        from conftest import (make_typography_spec, make_scene_typography,
                              make_text_element, make_sub_text_element)
        # font_size_canvas should be 96 (32×3) but we set 90
        typo = make_typography_spec(scenes=[
            make_scene_typography(elements=[
                make_text_element(font_size_prototype=32, font_size_canvas=90),
                make_sub_text_element(),
            ])
        ])
        _write_full_specs(tmp_specs, typo=typo)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_canvas_scaling_spotcheck()
        assert len(issues) == 1
        assert "font_size_canvas=90" in issues[0].message
        assert "96" in issues[0].message

    def test_wrong_manifest_scaling_fails(self, tmp_specs):
        from conftest import make_prototype_manifest, make_element_geometry
        el = make_element_geometry(
            element_id="scene-1-hero-text-0",
            scene_id="scene-1",
            x=30, canvas_x=100,  # should be 90
        )
        manifest = make_prototype_manifest(prototypes=[
            {"scene_id": "scene-1", "file_path": "p1.html",
             "element_count": 1, "elements": [el]},
        ], total_elements=1)
        _write_full_specs(tmp_specs, manifest=manifest)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_canvas_scaling_spotcheck()
        assert any("canvas_x=100" in i.message for i in issues)


# ─── Check 12: Depth Layers ≥2 Per Scene ─────────────────────────────────────

class TestDepthLayers:
    """Every scene must have ≥2 depth layers with distinct z-indices."""

    def test_two_layers_passes(self, tmp_specs):
        from conftest import make_visual_spec
        _write_full_specs(tmp_specs, visual=make_visual_spec())
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_depth_layers()
        assert len(issues) == 0

    def test_one_layer_fails(self, tmp_specs):
        from conftest import make_visual_spec, make_scene_design
        visual = make_visual_spec(scenes=[
            make_scene_design(depth_layers=[
                {"element_id": "bg", "layer": "background", "z_index": 0},
            ])
        ])
        _write_full_specs(tmp_specs, visual=visual)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_depth_layers()
        assert len(issues) == 1
        assert "minimum 2" in issues[0].message

    def test_same_z_index_warns(self, tmp_specs):
        from conftest import make_visual_spec, make_scene_design
        visual = make_visual_spec(scenes=[
            make_scene_design(depth_layers=[
                {"element_id": "bg", "layer": "background", "z_index": 5},
                {"element_id": "fg", "layer": "foreground", "z_index": 5},
            ])
        ])
        _write_full_specs(tmp_specs, visual=visual)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_depth_layers()
        assert len(issues) == 1
        assert issues[0].severity == "HIGH"
        assert "same" in issues[0].message.lower()

    def test_zero_layers_fails(self, tmp_specs):
        from conftest import make_visual_spec, make_scene_design
        visual = make_visual_spec(scenes=[
            make_scene_design(depth_layers=[])
        ])
        _write_full_specs(tmp_specs, visual=visual)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_depth_layers()
        assert len(issues) == 1


# ─── Check 13: Weight Contrast ≥300 ──────────────────────────────────────────

class TestWeightContrastValidator:
    """Re-verifies weight contrast from raw typography spec JSON."""

    def test_strong_contrast_passes(self, tmp_specs):
        from conftest import make_typography_spec
        _write_full_specs(tmp_specs, typo=make_typography_spec())
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_weight_contrast()
        # 900 vs 400 = diff 500 ≥ 300 ✓
        assert len(issues) == 0

    def test_weak_contrast_fails(self, tmp_specs):
        from conftest import (make_typography_spec, make_scene_typography,
                              make_text_element)
        typo = make_typography_spec(scenes=[
            make_scene_typography(elements=[
                make_text_element(font_weight=500),
                make_text_element(
                    element_id="scene-1-sub-text-0",
                    role="sub",
                    text_content="Every month",
                    font_weight=400,
                    font_size_prototype=24,
                    font_size_canvas=72,
                ),
            ])
        ])
        _write_full_specs(tmp_specs, typo=typo)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_weight_contrast()
        assert len(issues) == 1
        assert "100" in issues[0].message  # diff = 500-400=100

    def test_single_element_skips(self, tmp_specs):
        from conftest import (make_typography_spec, make_scene_typography,
                              make_text_element)
        typo = make_typography_spec(scenes=[
            make_scene_typography(elements=[make_text_element()])
        ])
        _write_full_specs(tmp_specs, typo=typo)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_weight_contrast()
        assert len(issues) == 0


# ─── Check 14: Element IDs Globally Unique ────────────────────────────────────

class TestElementIdsUnique:
    """Element IDs must be unique across ALL prototypes."""

    def test_unique_ids_passes(self, tmp_specs):
        from conftest import make_prototype_manifest
        _write_full_specs(tmp_specs, manifest=make_prototype_manifest())
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_element_ids_unique()
        assert len(issues) == 0

    def test_duplicate_ids_fails(self, tmp_specs):
        from conftest import make_element_geometry
        el1 = make_element_geometry(element_id="same-id", scene_id="scene-1")
        el2 = make_element_geometry(element_id="same-id", scene_id="scene-2")
        manifest = {
            "project_id": "test",
            "composition_name": "TestComp",
            "canvas": {"width": 1080, "height": 1920, "scale_factor": 3},
            "prototypes": [
                {"scene_id": "scene-1", "file_path": "p1.html",
                 "element_count": 1, "elements": [el1]},
                {"scene_id": "scene-2", "file_path": "p2.html",
                 "element_count": 1, "elements": [el2]},
            ],
            "total_elements": 2,
        }
        _write_full_specs(tmp_specs, manifest=manifest)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_element_ids_unique()
        assert len(issues) == 1
        assert "same-id" in issues[0].message

    def test_missing_manifest_skips(self, tmp_specs):
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_element_ids_unique()
        assert len(issues) == 0


# ─── Check 15: Text Matches Script ───────────────────────────────────────────

class TestTextMatchesScript:
    """Cross-references typography text_content against 02-script.md."""

    def test_matching_text_passes(self, tmp_specs):
        from conftest import make_typography_spec
        _write_full_specs(tmp_specs, typo=make_typography_spec())
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_text_matches_script()
        # "Your money disappears" IS in the script
        assert len(issues) == 0

    def test_invented_text_warns(self, tmp_specs):
        from conftest import (make_typography_spec, make_scene_typography,
                              make_text_element)
        typo = make_typography_spec(scenes=[
            make_scene_typography(elements=[
                make_text_element(text_content="This was never in the script at all"),
                make_text_element(
                    element_id="scene-1-sub-text-0",
                    role="sub",
                    text_content="Also completely made up content",
                    font_weight=400,
                    font_size_prototype=24,
                    font_size_canvas=72,
                ),
            ])
        ])
        _write_full_specs(tmp_specs, typo=typo)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_text_matches_script()
        assert len(issues) == 2
        assert all(i.severity == "MEDIUM" for i in issues)
        assert all("not found" in i.message for i in issues)

    def test_short_text_skipped(self, tmp_specs):
        from conftest import (make_typography_spec, make_scene_typography,
                              make_text_element)
        typo = make_typography_spec(scenes=[
            make_scene_typography(elements=[
                make_text_element(text_content="Yes", role="label"),  # too short
            ])
        ])
        _write_full_specs(tmp_specs, typo=typo)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_text_matches_script()
        assert len(issues) == 0

    def test_counter_role_skipped(self, tmp_specs):
        from conftest import (make_typography_spec, make_scene_typography,
                              make_text_element)
        typo = make_typography_spec(scenes=[
            make_scene_typography(elements=[
                make_text_element(
                    text_content="$1,234,567",
                    role="counter",
                    font_size_prototype=50,
                    font_size_canvas=150,
                ),
            ])
        ])
        _write_full_specs(tmp_specs, typo=typo)
        v = DesignValidator(specs_dir=tmp_specs)
        issues = v.validate_text_matches_script()
        assert len(issues) == 0


# ─── Master Validation ───────────────────────────────────────────────────────

class TestRunAllDeterministic:
    def test_full_valid_project(self, full_specs, tmp_path):
        protos = tmp_path / "prototypes"
        protos.mkdir(exist_ok=True)
        (protos / "Scene1_Hook.html").write_text(
            '<div data-element-id="el-1" data-layer="foreground">Hook</div>'
        )
        (protos / "Scene2_Problem.html").write_text(
            '<div data-element-id="el-2" data-layer="foreground">Problem</div>'
        )
        v = DesignValidator(specs_dir=full_specs, prototypes_dir=protos)
        issues = v.run_all_deterministic()
        # Should run without errors — verify it returns a list
        assert isinstance(issues, list)
        # All issues should have a severity and message
        for i in issues:
            assert i.severity in ("CRITICAL", "HIGH", "MEDIUM")
            assert len(i.message) > 0

    def test_count_is_15_methods(self):
        """Ensure run_all_deterministic calls exactly 15 checks."""
        v = DesignValidator()
        import inspect
        validate_methods = [
            m for m in dir(v)
            if m.startswith("validate_") and callable(getattr(v, m))
        ]
        assert len(validate_methods) == 15


# ─── LLM Evaluator Prompt ────────────────────────────────────────────────────

class TestLLMEvaluatorPrompt:
    def test_prompt_contains_6_dimensions(self):
        v = DesignValidator()
        prompt = v.build_llm_evaluator_prompt("brief", "visual", "typo")
        for dim in ["color", "typography", "focal", "depth", "emotion", "craft"]:
            assert dim in prompt.lower()

    def test_prompt_contains_scoring_guide(self):
        v = DesignValidator()
        prompt = v.build_llm_evaluator_prompt("brief", "visual", "typo")
        assert "0-10" in prompt
        assert "below 7 blocks" in prompt.lower()

    def test_prompt_truncates_inputs(self):
        v = DesignValidator()
        long_brief = "x" * 5000
        prompt = v.build_llm_evaluator_prompt(long_brief, "visual", "typo")
        # Input should be truncated
        assert len(prompt) < len(long_brief)

    def test_prompt_requests_json(self):
        v = DesignValidator()
        prompt = v.build_llm_evaluator_prompt("brief", "visual", "typo")
        assert "JSON" in prompt
        assert "violations" in prompt
