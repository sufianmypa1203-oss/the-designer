"""
The Designer — Visual Design Specification Agent

Pipeline Position: 2 of 5
/director → /designer → /motion-architect → /builder → /inspector

Create frozen frames. Every frame is a poster before it moves.
"""
from .models import (
    ColorApplication,
    FocalPointSpec,
    DepthLayer,
    SceneDesignSpec,
    VisualDesignSpec,
    TextElement,
    SceneTypography,
    TypographySpec,
    ElementGeometry,
    PrototypeEntry,
    PrototypeManifest,
    ColorTemperature,
    IsolationTechnique,
    LayerName,
    TextRole,
    AnimationIntent,
    ElementRole,
)
from .agent import DesignerAgent, __version__
from .validator import DesignValidator
from .tools import DESIGNER_TOOLS
from .color_utils import (
    contrast_ratio,
    relative_luminance,
    hex_to_rgb,
    check_wcag_aa,
    check_wcag_aaa,
)

__all__ = [
    # Models
    "ColorApplication",
    "FocalPointSpec",
    "DepthLayer",
    "SceneDesignSpec",
    "VisualDesignSpec",
    "TextElement",
    "SceneTypography",
    "TypographySpec",
    "ElementGeometry",
    "PrototypeEntry",
    "PrototypeManifest",
    # Enums
    "ColorTemperature",
    "IsolationTechnique",
    "LayerName",
    "TextRole",
    "AnimationIntent",
    "ElementRole",
    # Agent
    "DesignerAgent",
    "__version__",
    # Validator
    "DesignValidator",
    # Tools
    "DESIGNER_TOOLS",
    # Color Utils
    "contrast_ratio",
    "relative_luminance",
    "hex_to_rgb",
    "check_wcag_aa",
    "check_wcag_aaa",
]
