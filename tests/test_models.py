"""
The Designer — Model Contract Tests

Every Pydantic model must reject invalid data at construction time.
These tests prove that the type system catches design errors
BEFORE artifacts are written to disk.
"""
import pytest
from pydantic import ValidationError

from designer.models import (
    ColorApplication,
    ColorTemperature,
    FocalPointSpec,
    IsolationTechnique,
    DepthLayer,
    LayerName,
    SceneDesignSpec,
    VisualDesignSpec,
    TextElement,
    TextRole,
    AnimationIntent,
    SceneTypography,
    TypographySpec,
    ElementGeometry,
    ElementRole,
    PrototypeEntry,
    PrototypeManifest,
)


# ─── Factories ────────────────────────────────────────────────────────────────

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
        {"element_id": "scene-1-bg-0", "layer": "background", "z_index": 0, "opacity": 0.3, "blur_px": 8},
        {"element_id": "scene-1-hero-text-0", "layer": "foreground", "z_index": 10, "opacity": 1.0, "blur_px": 0},
    ]


def make_scene_design(**overrides) -> dict:
    base = {
        "scene_id": "scene-1",
        "prototype_file": "prototypes/Scene1_Hook.html",
        "colors": make_color_app(),
        "focal_point": make_focal(),
        "depth_layers": make_depth_layers(),
        "grid_system": "12-column",
        "white_space_strategy": "20% generous padding, bottom relief zone",
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


# ─── ColorApplication Tests ──────────────────────────────────────────────────

class TestColorApplication:
    def test_valid_color_app(self):
        ca = ColorApplication(**make_color_app())
        assert ca.scene_id == "scene-1"
        assert ca.color_temperature == ColorTemperature.WARM

    def test_invalid_hex_rejects(self):
        with pytest.raises(ValidationError, match="valid hex color"):
            ColorApplication(**make_color_app(dominant_60="red"))

    def test_short_hex_accepted(self):
        ca = ColorApplication(**make_color_app(accent_10="#F00"))
        assert ca.accent_10 == "#F00"

    def test_contrast_below_aa_rejects(self):
        with pytest.raises(ValidationError, match="4.5"):
            ColorApplication(**make_color_app(
                contrast_ratios={"hero-on-bg": 2.1}
            ))

    def test_scene_id_pattern_enforced(self):
        with pytest.raises(ValidationError):
            ColorApplication(**make_color_app(scene_id="hook"))


# ─── FocalPointSpec Tests ────────────────────────────────────────────────────

class TestFocalPointSpec:
    def test_valid_focal(self):
        fp = FocalPointSpec(**make_focal())
        assert fp.isolation_technique == IsolationTechnique.SCALE_CONTRAST

    def test_empty_eye_path_rejects(self):
        with pytest.raises(ValidationError, match="too_short"):
            FocalPointSpec(**make_focal(eye_path=[]))


# ─── DepthLayer Tests ────────────────────────────────────────────────────────

class TestDepthLayer:
    def test_valid_layer(self):
        dl = DepthLayer(element_id="el-1", layer="foreground", z_index=10)
        assert dl.opacity == 1.0

    def test_negative_z_rejects(self):
        with pytest.raises(ValidationError):
            DepthLayer(element_id="el-1", layer="foreground", z_index=-1)

    def test_opacity_out_of_range_rejects(self):
        with pytest.raises(ValidationError):
            DepthLayer(element_id="el-1", layer="foreground", z_index=0, opacity=1.5)


# ─── SceneDesignSpec Tests ───────────────────────────────────────────────────

class TestSceneDesignSpec:
    def test_valid_scene(self):
        sd = SceneDesignSpec(**make_scene_design())
        assert sd.scene_id == "scene-1"

    def test_mismatched_color_scene_id_rejects(self):
        with pytest.raises(ValidationError, match="≠ scene_id"):
            SceneDesignSpec(**make_scene_design(
                colors=make_color_app(scene_id="scene-2")
            ))

    def test_focal_element_not_in_layers_rejects(self):
        with pytest.raises(ValidationError, match="not found in depth layers"):
            SceneDesignSpec(**make_scene_design(
                focal_point=make_focal(focal_element_id="nonexistent-el")
            ))

    def test_single_depth_layer_rejects(self):
        with pytest.raises(ValidationError):
            SceneDesignSpec(**make_scene_design(
                depth_layers=[make_depth_layers()[0]]
            ))


# ─── TextElement Tests ───────────────────────────────────────────────────────

class TestTextElement:
    def test_valid_text_element(self):
        te = TextElement(**make_text_element())
        assert te.font_size_canvas == 96

    def test_canvas_scaling_wrong_rejects(self):
        with pytest.raises(ValidationError, match="× 3"):
            TextElement(**make_text_element(
                font_size_prototype=32, font_size_canvas=90
            ))

    def test_hero_below_minimum_rejects(self):
        with pytest.raises(ValidationError, match="below minimum"):
            TextElement(**make_text_element(
                font_size_prototype=10, font_size_canvas=30
            ))

    def test_canvas_exactly_3x(self):
        te = TextElement(**make_text_element(
            font_size_prototype=40, font_size_canvas=120
        ))
        assert te.font_size_canvas == 120

    def test_invalid_color_rejects(self):
        with pytest.raises(ValidationError, match="valid hex"):
            TextElement(**make_text_element(color="white"))

    def test_label_uppercase_tracking_enforced(self):
        with pytest.raises(ValidationError, match="0.35em"):
            TextElement(**make_text_element(
                role="label",
                text_transform="uppercase",
                letter_spacing="0.1em",
                font_size_prototype=12,
                font_size_canvas=36,
                font_weight=500,
            ))

    def test_label_uppercase_valid_tracking_passes(self):
        te = TextElement(**make_text_element(
            role="label",
            text_transform="uppercase",
            letter_spacing="0.4em",
            font_size_prototype=12,
            font_size_canvas=36,
            font_weight=500,
        ))
        assert te.letter_spacing == "0.4em"


# ─── SceneTypography Tests ──────────────────────────────────────────────────

class TestSceneTypography:
    def test_valid_scene_typography(self):
        st = SceneTypography(
            scene_id="scene-1",
            elements=[
                TextElement(**make_text_element(font_weight=900)),
                TextElement(**make_text_element(
                    element_id="scene-1-sub-text-0",
                    role="sub",
                    font_weight=400,
                    font_size_prototype=24,
                    font_size_canvas=72,
                    text_content="Every month",
                )),
            ],
            weight_contrast="900 vs 400",
            type_ramp="golden-ratio",
        )
        assert len(st.elements) == 2

    def test_weight_contrast_below_300_rejects(self):
        with pytest.raises(ValidationError, match="300"):
            SceneTypography(
                scene_id="scene-1",
                elements=[
                    TextElement(**make_text_element(font_weight=500)),
                    TextElement(**make_text_element(
                        element_id="scene-1-sub-text-0",
                        role="sub",
                        font_weight=400,
                        font_size_prototype=24,
                        font_size_canvas=72,
                        text_content="Every month",
                    )),
                ],
                weight_contrast="500 vs 400",
                type_ramp="golden-ratio",
            )


# ─── ElementGeometry Tests ──────────────────────────────────────────────────

class TestElementGeometry:
    def test_valid_geometry(self):
        eg = ElementGeometry(**make_element_geometry())
        assert eg.canvas_width == 900

    def test_wrong_canvas_x_rejects(self):
        with pytest.raises(ValidationError, match="canvas_x"):
            ElementGeometry(**make_element_geometry(canvas_x=100))

    def test_wrong_canvas_width_rejects(self):
        with pytest.raises(ValidationError, match="canvas_width"):
            ElementGeometry(**make_element_geometry(canvas_width=800))

    def test_all_coordinates_must_be_3x(self):
        eg = ElementGeometry(**make_element_geometry(
            x=100, y=200, width=50, height=30,
            canvas_x=300, canvas_y=600, canvas_width=150, canvas_height=90,
        ))
        assert eg.canvas_x == eg.x * 3
        assert eg.canvas_y == eg.y * 3


# ─── PrototypeEntry Tests ───────────────────────────────────────────────────

class TestPrototypeEntry:
    def test_valid_entry(self):
        elements = [make_element_geometry()]
        pe = PrototypeEntry(
            scene_id="scene-1",
            file_path="prototypes/Scene1_Hook.html",
            element_count=1,
            elements=[ElementGeometry(**e) for e in elements],
        )
        assert pe.element_count == 1

    def test_wrong_element_count_rejects(self):
        elements = [make_element_geometry()]
        with pytest.raises(ValidationError, match="element_count"):
            PrototypeEntry(
                scene_id="scene-1",
                file_path="prototypes/Scene1_Hook.html",
                element_count=5,
                elements=[ElementGeometry(**e) for e in elements],
            )

    def test_duplicate_element_ids_rejects(self):
        el = make_element_geometry()
        with pytest.raises(ValidationError, match="Duplicate element IDs"):
            PrototypeEntry(
                scene_id="scene-1",
                file_path="prototypes/Scene1_Hook.html",
                element_count=2,
                elements=[ElementGeometry(**el), ElementGeometry(**el)],
            )


# ─── PrototypeManifest Tests ────────────────────────────────────────────────

class TestPrototypeManifest:
    def _make_manifest(self, **overrides) -> dict:
        el1 = make_element_geometry(element_id="scene-1-hero-text-0", scene_id="scene-1")
        el2 = make_element_geometry(element_id="scene-2-hero-text-0", scene_id="scene-2")
        base = {
            "project_id": "test-project",
            "composition_name": "TestComp",
            "canvas": {"width": 1080, "height": 1920, "scale_factor": 3},
            "prototypes": [
                {
                    "scene_id": "scene-1",
                    "file_path": "prototypes/Scene1_Hook.html",
                    "element_count": 1,
                    "elements": [el1],
                },
                {
                    "scene_id": "scene-2",
                    "file_path": "prototypes/Scene2_Problem.html",
                    "element_count": 1,
                    "elements": [el2],
                },
            ],
            "total_elements": 2,
        }
        base.update(overrides)
        return base

    def test_valid_manifest(self):
        pm = PrototypeManifest(**self._make_manifest())
        assert pm.total_elements == 2

    def test_wrong_total_rejects(self):
        with pytest.raises(ValidationError, match="total_elements"):
            PrototypeManifest(**self._make_manifest(total_elements=10))

    def test_duplicate_scene_ids_rejects(self):
        el1 = make_element_geometry(element_id="el-a", scene_id="scene-1")
        el2 = make_element_geometry(element_id="el-b", scene_id="scene-1")
        with pytest.raises(ValidationError, match="Duplicate scene IDs"):
            PrototypeManifest(
                project_id="test",
                composition_name="TestComp",
                canvas={"width": 1080, "height": 1920, "scale_factor": 3},
                prototypes=[
                    {"scene_id": "scene-1", "file_path": "p1.html", "element_count": 1, "elements": [el1]},
                    {"scene_id": "scene-1", "file_path": "p2.html", "element_count": 1, "elements": [el2]},
                ],
                total_elements=2,
            )

    def test_globally_duplicate_element_ids_rejects(self):
        el = make_element_geometry(element_id="same-id", scene_id="scene-1")
        el2_data = make_element_geometry(element_id="same-id", scene_id="scene-2")
        with pytest.raises(ValidationError, match="Duplicate element IDs across"):
            PrototypeManifest(
                project_id="test",
                composition_name="TestComp",
                canvas={"width": 1080, "height": 1920, "scale_factor": 3},
                prototypes=[
                    {"scene_id": "scene-1", "file_path": "p1.html", "element_count": 1, "elements": [el]},
                    {"scene_id": "scene-2", "file_path": "p2.html", "element_count": 1, "elements": [el2_data]},
                ],
                total_elements=2,
            )


# ─── VisualDesignSpec Tests ─────────────────────────────────────────────────

class TestVisualDesignSpec:
    def test_valid_visual_spec(self):
        vs = VisualDesignSpec(
            project_id="test-proj",
            composition_name="TestComp",
            canvas={"width": 1080, "height": 1920, "prototype_scale": 3},
            brand_palette={"primary": "#FF6B35"},
            scenes=[SceneDesignSpec(**make_scene_design())],
        )
        assert vs.version == 1

    def test_duplicate_scene_ids_rejects(self):
        scene = make_scene_design()
        with pytest.raises(ValidationError, match="Duplicate scene IDs"):
            VisualDesignSpec(
                project_id="test-proj",
                composition_name="TestComp",
                canvas={"width": 1080, "height": 1920},
                brand_palette={},
                scenes=[
                    SceneDesignSpec(**scene),
                    SceneDesignSpec(**scene),
                ],
            )

    def test_composition_name_pattern(self):
        with pytest.raises(ValidationError):
            VisualDesignSpec(
                project_id="test",
                composition_name="bad-name",  # Must be PascalCase
                canvas={},
                brand_palette={},
                scenes=[SceneDesignSpec(**make_scene_design())],
            )
