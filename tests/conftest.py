"""
The Designer — Shared Test Fixtures (conftest.py)

Factory functions and pytest fixtures used across all test files.
Everything builds from minimal valid data → inject one defect at a time.
"""
import json
import pytest
from pathlib import Path


# ─── Minimal Valid Spec Factories ─────────────────────────────────────────────


def make_color_app(**overrides) -> dict:
    base = {
        "scene_id": "scene-1",
        "dominant_60": "#0A0A12",
        "secondary_30": "#FFFFFF",
        "accent_10": "#FF6B35",
        "color_temperature": "warm",
        "background_treatment": "solid #0A0A12",
        "contrast_ratios": {"hero-on-bg": 15.0, "sub-on-bg": 12.0},
    }
    base.update(overrides)
    return base


def make_focal(**overrides) -> dict:
    base = {
        "scene_id": "scene-1",
        "focal_element_id": "scene-1-hero-text-0",
        "isolation_technique": "scale-contrast",
        "eye_entry_point": "50%, 30%",
        "eye_path": ["scene-1-hero-text-0", "scene-1-sub-text-0"],
        "relief_zone": "bottom-third",
    }
    base.update(overrides)
    return base


def make_depth_layers() -> list[dict]:
    return [
        {"element_id": "scene-1-bg-0", "layer": "background",
         "z_index": 0, "opacity": 0.3, "blur_px": 8},
        {"element_id": "scene-1-hero-text-0", "layer": "foreground",
         "z_index": 10, "opacity": 1.0, "blur_px": 0},
    ]


def make_scene_design(**overrides) -> dict:
    base = {
        "scene_id": "scene-1",
        "prototype_file": "prototypes/Scene1_Hook.html",
        "colors": make_color_app(),
        "focal_point": make_focal(),
        "depth_layers": make_depth_layers(),
        "grid_system": "12-column",
        "white_space_strategy": "20% generous padding",
    }
    base.update(overrides)
    return base


def make_visual_spec(**overrides) -> dict:
    base = {
        "project_id": "test-project",
        "composition_name": "TestComp",
        "canvas": {"width": 1080, "height": 1920, "prototype_scale": 3},
        "brand_palette": {"primary": "#FF6B35"},
        "scenes": [make_scene_design()],
    }
    base.update(overrides)
    return base


def make_text_element(**overrides) -> dict:
    base = {
        "element_id": "scene-1-hero-text-0",
        "role": "hero",
        "text_content": "Your money disappears",
        "type_scale_token": "hero",
        "font_size_prototype": 32,
        "font_size_canvas": 96,
        "font_weight": 900,
        "font_family_token": "sans",
        "letter_spacing": "-0.04em",
        "text_transform": "none",
        "color": "#FFFFFF",
        "alignment": "center",
        "max_width_px": 900,
        "animation_intent": "character-stagger",
    }
    base.update(overrides)
    return base


def make_sub_text_element(**overrides) -> dict:
    return make_text_element(
        element_id="scene-1-sub-text-0",
        role="sub",
        text_content="Every month",
        font_weight=400,
        font_size_prototype=24,
        font_size_canvas=72,
        **overrides,
    )


def make_scene_typography(**overrides) -> dict:
    base = {
        "scene_id": "scene-1",
        "elements": [make_text_element(), make_sub_text_element()],
        "weight_contrast": "900 vs 400",
        "type_ramp": "golden-ratio",
    }
    base.update(overrides)
    return base


def make_typography_spec(**overrides) -> dict:
    base = {
        "project_id": "test-project",
        "font_families_used": ["Inter", "JetBrains Mono"],
        "scenes": [make_scene_typography()],
    }
    base.update(overrides)
    return base


def make_element_geometry(**overrides) -> dict:
    base = {
        "element_id": "scene-1-hero-text-0",
        "scene_id": "scene-1",
        "html_tag": "h1",
        "layer": "foreground",
        "x": 30, "y": 80, "width": 300, "height": 60,
        "canvas_x": 90, "canvas_y": 240, "canvas_width": 900, "canvas_height": 180,
        "role": "hero-text",
    }
    base.update(overrides)
    return base


def make_prototype_entry(**overrides) -> dict:
    base = {
        "scene_id": "scene-1",
        "file_path": "prototypes/Scene1_Hook.html",
        "element_count": 1,
        "elements": [make_element_geometry()],
    }
    base.update(overrides)
    return base


def make_prototype_manifest(**overrides) -> dict:
    el1 = make_element_geometry(element_id="scene-1-hero-text-0", scene_id="scene-1")
    el2 = make_element_geometry(element_id="scene-2-hero-text-0", scene_id="scene-2")
    base = {
        "project_id": "test-project",
        "composition_name": "TestComp",
        "canvas": {"width": 1080, "height": 1920, "scale_factor": 3},
        "prototypes": [
            {"scene_id": "scene-1", "file_path": "prototypes/Scene1_Hook.html",
             "element_count": 1, "elements": [el1]},
            {"scene_id": "scene-2", "file_path": "prototypes/Scene2_Problem.html",
             "element_count": 1, "elements": [el2]},
        ],
        "total_elements": 2,
    }
    base.update(overrides)
    return base


# ─── Pytest Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def tmp_specs(tmp_path):
    """Create temp specs directory with minimal valid upstream files."""
    specs = tmp_path / "specs"
    specs.mkdir()

    (specs / "01-brief.md").write_text(
        "# Brief\nBrand: TestBrand\nColors: #FF6B35, #0A0A12, #FFFFFF\n" * 3
    )
    (specs / "02-script.md").write_text(
        "# Script\n## Scene 1: Hook\nYour money disappears.\n"
        "## Scene 2: Problem\nEvery month.\n"
    )

    scene_map = {
        "projectId": "test-project",
        "compositionName": "TestComp",
        "scenes": [
            {"id": "scene-1", "name": "Hook", "role": "hook",
             "prototypeFile": "Scene1_Hook.html"},
            {"id": "scene-2", "name": "Problem", "role": "problem",
             "prototypeFile": "Scene2_Problem.html"},
        ],
    }
    (specs / "03-scene-map.json").write_text(json.dumps(scene_map, indent=2))

    return specs


@pytest.fixture
def tmp_protos(tmp_path):
    """Create temp prototypes directory."""
    protos = tmp_path / "prototypes"
    protos.mkdir()
    return protos


@pytest.fixture
def full_specs(tmp_specs):
    """Create specs directory with ALL Designer artifacts (visual, typo, manifest)."""
    # Visual design spec
    (tmp_specs / "04-visual-design-spec.json").write_text(
        json.dumps(make_visual_spec(), indent=2)
    )
    # Typography spec
    (tmp_specs / "05-typography-spec.json").write_text(
        json.dumps(make_typography_spec(), indent=2)
    )
    # Prototype manifest
    (tmp_specs / "06-prototype-manifest.json").write_text(
        json.dumps(make_prototype_manifest(), indent=2)
    )
    return tmp_specs


@pytest.fixture
def mock_project(tmp_path):
    """Create a complete mock project directory."""
    specs = tmp_path / "specs"
    specs.mkdir()
    protos = tmp_path / "prototypes"
    protos.mkdir()

    (specs / "01-brief.md").write_text("# Brief\nBrand: TestBrand\nColors: #FF6B35\n" * 3)
    (specs / "02-script.md").write_text("# Script\n## Scene 1\nYour money disappears.\n" * 3)

    scene_map = {
        "projectId": "test-project",
        "compositionName": "TestComp",
        "scenes": [
            {"id": "scene-1", "name": "Hook", "role": "hook",
             "prototypeFile": "Scene1_Hook.html"},
        ],
    }
    (specs / "03-scene-map.json").write_text(json.dumps(scene_map, indent=2))

    return tmp_path, specs, protos
