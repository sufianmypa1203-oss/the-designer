"""
The Designer — Pydantic Contracts (THE source of truth)

11 models enforcing every design decision at generation time.
Invalid color splits, broken canvas scaling, or missing depth layers
raise ValidationError BEFORE the artifact can be written to disk.
"""
from __future__ import annotations
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, timezone

from .color_utils import is_valid_hex, contrast_ratio


# ─── Hex Color Type ──────────────────────────────────────────────────────────

HexColor = str  # Validated by field_validator on each model


def _validate_hex(v: str, field_name: str) -> str:
    """Shared hex validation logic."""
    if not is_valid_hex(v):
        raise ValueError(
            f"'{field_name}' must be a valid hex color (#RGB or #RRGGBB). Got: '{v}'"
        )
    return v


# ─── Enums ────────────────────────────────────────────────────────────────────

class ColorTemperature(str, Enum):
    WARM = "warm"
    COOL = "cool"
    NEUTRAL = "neutral"


class IsolationTechnique(str, Enum):
    SCALE_CONTRAST = "scale-contrast"
    COLOR_POP = "color-pop"
    WHITE_SPACE = "white-space"
    Z_DEPTH = "z-depth"
    UNIQUE_SHAPE = "unique-shape"


class LayerName(str, Enum):
    BACKGROUND = "background"
    MIDGROUND = "midground"
    FOREGROUND = "foreground"


class TextRole(str, Enum):
    HERO = "hero"
    SUB = "sub"
    LABEL = "label"
    OVERLAY = "overlay"
    CAPTION = "caption"
    BADGE = "badge"
    COUNTER = "counter"


class AnimationIntent(str, Enum):
    CHARACTER_STAGGER = "character-stagger"
    WORD_ARC = "word-arc"
    KINETIC_BLOCK = "kinetic-block"
    VALUE_COUNTER = "value-counter"
    STATIC_REVEAL = "static-reveal"
    CLIP_REVEAL = "clip-reveal"


class ElementRole(str, Enum):
    HERO_TEXT = "hero-text"
    SUB_TEXT = "sub-text"
    LABEL = "label"
    OVERLAY = "overlay"
    COUNTER = "counter"
    BADGE = "badge"
    CARD = "card"
    RING = "ring"
    LINE = "line"
    ICON = "icon"
    GRADIENT = "gradient"
    PATTERN = "pattern"
    BACKGROUND = "background"
    DECORATIVE = "decorative"
    CTA = "cta"
    LOGO = "logo"


# ─── Model 1: ColorApplication ──────────────────────────────────────────────

class ColorApplication(BaseModel):
    """Per-scene color usage enforcing 60-30-10 rule."""
    scene_id: str = Field(pattern=r"^scene-\d+$")
    dominant_60: str  # Background/field color
    secondary_30: str  # Text/cards
    accent_10: str  # CTA/highlight
    color_temperature: ColorTemperature
    background_treatment: str  # e.g., "solid #0A0A12", "radial-gradient(...)"
    contrast_ratios: dict[str, float] = Field(
        description="e.g., {'hero-on-bg': 12.4, 'sub-on-bg': 8.1}"
    )

    @field_validator("dominant_60", "secondary_30", "accent_10")
    @classmethod
    def validate_hex_colors(cls, v: str) -> str:
        return _validate_hex(v, "color")

    @model_validator(mode="after")
    def validate_contrast_ratios(self) -> "ColorApplication":
        """All text contrast ratios must meet WCAG AA (≥4.5:1)."""
        for label, ratio in self.contrast_ratios.items():
            if ratio < 4.5:
                raise ValueError(
                    f"[{self.scene_id}] Contrast ratio for '{label}' is {ratio} "
                    f"(minimum 4.5:1 for WCAG AA)"
                )
        return self


# ─── Model 2: FocalPointSpec ────────────────────────────────────────────────

class FocalPointSpec(BaseModel):
    """Per-scene focal point decisions."""
    scene_id: str = Field(pattern=r"^scene-\d+$")
    focal_element_id: str
    isolation_technique: IsolationTechnique
    eye_entry_point: str  # Where the eye lands first (x%, y%)
    eye_path: list[str] = Field(
        min_length=1,
        description="Ordered list of element IDs the eye follows"
    )
    relief_zone: str  # Where the eye rests


# ─── Model 3: DepthLayer ────────────────────────────────────────────────────

class DepthLayer(BaseModel):
    """An element in the depth stack."""
    element_id: str
    layer: LayerName
    z_index: int = Field(ge=0)
    opacity: float = Field(ge=0, le=1, default=1.0)
    blur_px: float = Field(ge=0, default=0)


# ─── Model 4: SceneDesignSpec ───────────────────────────────────────────────

class SceneDesignSpec(BaseModel):
    """Complete design spec for one scene."""
    scene_id: str = Field(pattern=r"^scene-\d+$")
    prototype_file: str  # Path relative to project root
    colors: ColorApplication
    focal_point: FocalPointSpec
    depth_layers: list[DepthLayer] = Field(min_length=2)
    grid_system: str = Field(default="12-column")
    white_space_strategy: str

    @model_validator(mode="after")
    def validate_scene_id_consistency(self) -> "SceneDesignSpec":
        """Scene ID must be consistent across nested models."""
        if self.colors.scene_id != self.scene_id:
            raise ValueError(
                f"colors.scene_id '{self.colors.scene_id}' "
                f"≠ scene_id '{self.scene_id}'"
            )
        if self.focal_point.scene_id != self.scene_id:
            raise ValueError(
                f"focal_point.scene_id '{self.focal_point.scene_id}' "
                f"≠ scene_id '{self.scene_id}'"
            )
        return self

    @model_validator(mode="after")
    def validate_focal_element_in_layers(self) -> "SceneDesignSpec":
        """Focal element must exist in depth layers."""
        layer_ids = {dl.element_id for dl in self.depth_layers}
        if self.focal_point.focal_element_id not in layer_ids:
            raise ValueError(
                f"Focal element '{self.focal_point.focal_element_id}' "
                f"not found in depth layers: {layer_ids}"
            )
        return self


# ─── Model 5: VisualDesignSpec ──────────────────────────────────────────────

class VisualDesignSpec(BaseModel):
    """The full visual design spec — output of the Designer."""
    project_id: str
    composition_name: str = Field(pattern=r"^[A-Z][a-zA-Z0-9]+$")
    canvas: dict  # {"width": 1080, "height": 1920, "prototype_scale": 3}
    brand_palette: dict  # Full palette from brief
    scenes: list[SceneDesignSpec] = Field(min_length=1)
    version: int = Field(default=1, ge=1)
    generated_by: str = Field(default="designer")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @model_validator(mode="after")
    def validate_unique_scene_ids(self) -> "VisualDesignSpec":
        """All scene IDs must be unique."""
        ids = [s.scene_id for s in self.scenes]
        if len(ids) != len(set(ids)):
            dupes = [sid for sid in ids if ids.count(sid) > 1]
            raise ValueError(f"Duplicate scene IDs in visual spec: {set(dupes)}")
        return self


# ─── Model 6: TextElement ───────────────────────────────────────────────────

# Minimum font sizes on the 1080×1920 canvas
MIN_CANVAS_FONT_SIZES: dict[str, int] = {
    "hero": 96,
    "counter": 150,
    "sub": 72,
    "label": 36,
    "caption": 27,
    "badge": 24,
    "overlay": 36,
}


class TextElement(BaseModel):
    """A single text element in a scene."""
    element_id: str
    role: TextRole
    text_content: str = Field(min_length=1)
    type_scale_token: str  # From typeScale: "hero", "display", etc.
    font_size_prototype: int = Field(gt=0)
    font_size_canvas: int = Field(gt=0)
    font_weight: int = Field(ge=100, le=900)
    font_family_token: str  # "sans" or "mono"
    letter_spacing: str  # e.g., "-0.04em" or "0.05em"
    text_transform: Literal["none", "uppercase", "capitalize"] = "none"
    color: str
    alignment: Literal["left", "center", "right"] = "left"
    max_width_px: int | None = None
    animation_intent: AnimationIntent

    @field_validator("color")
    @classmethod
    def validate_color_hex(cls, v: str) -> str:
        return _validate_hex(v, "color")

    @model_validator(mode="after")
    def validate_canvas_scaling(self) -> "TextElement":
        """Canvas font size must be exactly prototype × 3."""
        expected = self.font_size_prototype * 3
        if self.font_size_canvas != expected:
            raise ValueError(
                f"Canvas font size {self.font_size_canvas} ≠ prototype "
                f"{self.font_size_prototype} × 3 = {expected}"
            )
        return self

    @model_validator(mode="after")
    def validate_minimum_canvas_size(self) -> "TextElement":
        """Font size must meet minimum for its role."""
        min_size = MIN_CANVAS_FONT_SIZES.get(self.role.value, 24)
        if self.font_size_canvas < min_size:
            raise ValueError(
                f"'{self.role.value}' at {self.font_size_canvas}px is below "
                f"minimum {min_size}px for 1080×1920 canvas"
            )
        return self

    @model_validator(mode="after")
    def validate_label_tracking(self) -> "TextElement":
        """All-caps labels must have tracking ≥ 0.35em."""
        if self.text_transform == "uppercase" and self.role in (TextRole.LABEL, TextRole.BADGE):
            if self.letter_spacing.endswith("em"):
                try:
                    spacing_val = float(self.letter_spacing.replace("em", ""))
                except (ValueError, AttributeError):
                    spacing_val = None
                if spacing_val is not None and spacing_val < 0.35:
                    raise ValueError(
                        f"All-caps {self.role.value} must have letter-spacing ≥ 0.35em, "
                        f"got {self.letter_spacing}"
                    )
        return self


# ─── Model 7: SceneTypography ───────────────────────────────────────────────

class SceneTypography(BaseModel):
    """All text elements for one scene."""
    scene_id: str = Field(pattern=r"^scene-\d+$")
    elements: list[TextElement] = Field(min_length=1)
    weight_contrast: str  # e.g., "900 vs 400"
    type_ramp: str  # e.g., "golden-ratio" or "custom"

    @model_validator(mode="after")
    def validate_weight_contrast(self) -> "SceneTypography":
        """Weight contrast between heaviest and lightest must be ≥300."""
        weights = [e.font_weight for e in self.elements]
        if len(weights) >= 2:
            diff = max(weights) - min(weights)
            if diff < 300:
                raise ValueError(
                    f"[{self.scene_id}] Weight contrast is {diff} "
                    f"(weights: {sorted(set(weights))}). Minimum 300 required "
                    f"for strong visual hierarchy."
                )
        return self


# ─── Model 8: TypographySpec ────────────────────────────────────────────────

class TypographySpec(BaseModel):
    """Full typography spec — every text element, every scene."""
    project_id: str
    font_families_used: list[str] = Field(min_length=1)
    scenes: list[SceneTypography] = Field(min_length=1)
    version: int = Field(default=1, ge=1)
    generated_by: str = Field(default="designer")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @model_validator(mode="after")
    def validate_unique_scene_ids(self) -> "TypographySpec":
        ids = [s.scene_id for s in self.scenes]
        if len(ids) != len(set(ids)):
            dupes = [sid for sid in ids if ids.count(sid) > 1]
            raise ValueError(f"Duplicate scene IDs in typography spec: {set(dupes)}")
        return self


# ─── Model 9: ElementGeometry ───────────────────────────────────────────────

class ElementGeometry(BaseModel):
    """A single DOM element's measured position and size."""
    element_id: str
    scene_id: str = Field(pattern=r"^scene-\d+$")
    html_tag: str  # "div", "span", "h1", "svg", etc.
    layer: LayerName
    # Bounding box in PROTOTYPE coordinates (360×640)
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    # Bounding box in CANVAS coordinates (1080×1920) — auto-validated
    canvas_x: int = Field(ge=0)
    canvas_y: int = Field(ge=0)
    canvas_width: int = Field(gt=0)
    canvas_height: int = Field(gt=0)
    # Semantic role
    role: ElementRole
    # Suggestion for Motion Architect
    suggested_component: str | None = None

    @model_validator(mode="after")
    def validate_canvas_coordinates(self) -> "ElementGeometry":
        """Canvas coordinates must be exactly prototype × 3."""
        errors = []
        if self.canvas_x != self.x * 3:
            errors.append(f"canvas_x {self.canvas_x} ≠ x {self.x} × 3 = {self.x * 3}")
        if self.canvas_y != self.y * 3:
            errors.append(f"canvas_y {self.canvas_y} ≠ y {self.y} × 3 = {self.y * 3}")
        if self.canvas_width != self.width * 3:
            errors.append(
                f"canvas_width {self.canvas_width} ≠ width {self.width} × 3 = {self.width * 3}"
            )
        if self.canvas_height != self.height * 3:
            errors.append(
                f"canvas_height {self.canvas_height} ≠ height {self.height} × 3 = {self.height * 3}"
            )
        if errors:
            raise ValueError(
                f"[{self.element_id}] Canvas scaling errors: " + "; ".join(errors)
            )
        return self


# ─── Model 10: PrototypeEntry ───────────────────────────────────────────────

class PrototypeEntry(BaseModel):
    """One prototype file and all its elements."""
    scene_id: str = Field(pattern=r"^scene-\d+$")
    file_path: str  # e.g., "prototypes/Scene1_Hook.html"
    viewport: dict = Field(default_factory=lambda: {"width": 360, "height": 640})
    element_count: int = Field(gt=0)
    elements: list[ElementGeometry]

    @model_validator(mode="after")
    def validate_element_count(self) -> "PrototypeEntry":
        if len(self.elements) != self.element_count:
            raise ValueError(
                f"element_count ({self.element_count}) ≠ "
                f"actual elements ({len(self.elements)})"
            )
        return self

    @model_validator(mode="after")
    def validate_unique_element_ids(self) -> "PrototypeEntry":
        ids = [e.element_id for e in self.elements]
        if len(ids) != len(set(ids)):
            dupes = [eid for eid in ids if ids.count(eid) > 1]
            raise ValueError(
                f"[{self.scene_id}] Duplicate element IDs: {set(dupes)}"
            )
        return self


# ─── Model 11: PrototypeManifest ────────────────────────────────────────────

class PrototypeManifest(BaseModel):
    """Registry of all prototypes and their elements."""
    project_id: str
    composition_name: str = Field(pattern=r"^[A-Z][a-zA-Z0-9]+$")
    canvas: dict  # {"width": 1080, "height": 1920, "scale_factor": 3}
    prototypes: list[PrototypeEntry] = Field(min_length=1)
    total_elements: int = Field(gt=0)
    version: int = Field(default=1, ge=1)
    generated_by: str = Field(default="designer")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @model_validator(mode="after")
    def validate_total_elements(self) -> "PrototypeManifest":
        actual = sum(len(p.elements) for p in self.prototypes)
        if actual != self.total_elements:
            raise ValueError(
                f"total_elements ({self.total_elements}) ≠ "
                f"sum of all prototype elements ({actual})"
            )
        return self

    @model_validator(mode="after")
    def validate_unique_scene_ids(self) -> "PrototypeManifest":
        ids = [p.scene_id for p in self.prototypes]
        if len(ids) != len(set(ids)):
            dupes = [sid for sid in ids if ids.count(sid) > 1]
            raise ValueError(f"Duplicate scene IDs in manifest: {set(dupes)}")
        return self

    @model_validator(mode="after")
    def validate_globally_unique_element_ids(self) -> "PrototypeManifest":
        """Element IDs must be unique across ALL prototypes."""
        all_ids: list[str] = []
        for proto in self.prototypes:
            all_ids.extend(e.element_id for e in proto.elements)
        if len(all_ids) != len(set(all_ids)):
            dupes = [eid for eid in all_ids if all_ids.count(eid) > 1]
            raise ValueError(
                f"Duplicate element IDs across prototypes: {set(dupes)}"
            )
        return self
