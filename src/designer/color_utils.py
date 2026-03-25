"""
The Designer — Color Utilities

WCAG contrast ratio calculator, hex color parser, and luminance math.
Used by models.py and validator.py for accessibility enforcement.
"""
from __future__ import annotations
import re


# ─── Hex Validation ──────────────────────────────────────────────────────────

HEX_PATTERN = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def is_valid_hex(color: str) -> bool:
    """Check if a string is a valid hex color (#RGB or #RRGGBB)."""
    return bool(HEX_PATTERN.match(color))


def normalize_hex(color: str) -> str:
    """
    Normalize a hex color to 6-digit uppercase format.
    '#abc' → '#AABBCC', '#1a2b3c' → '#1A2B3C'
    Raises ValueError if invalid.
    """
    if not is_valid_hex(color):
        raise ValueError(f"Invalid hex color: '{color}'. Expected #RGB or #RRGGBB.")
    color = color.upper()
    if len(color) == 4:  # #RGB → #RRGGBB
        return f"#{color[1]*2}{color[2]*2}{color[3]*2}"
    return color


# ─── Color Parsing ───────────────────────────────────────────────────────────

def hex_to_rgb(color: str) -> tuple[int, int, int]:
    """
    Convert hex color to (R, G, B) tuple.
    Accepts both #RGB and #RRGGBB formats.
    """
    normalized = normalize_hex(color)
    r = int(normalized[1:3], 16)
    g = int(normalized[3:5], 16)
    b = int(normalized[5:7], 16)
    return (r, g, b)


# ─── WCAG Luminance & Contrast ──────────────────────────────────────────────

def _srgb_to_linear(channel: int) -> float:
    """Convert an sRGB channel (0-255) to linear RGB (0.0-1.0)."""
    s = channel / 255.0
    if s <= 0.04045:
        return s / 12.92
    return ((s + 0.055) / 1.055) ** 2.4


def relative_luminance(color: str) -> float:
    """
    Calculate relative luminance per WCAG 2.1.
    https://www.w3.org/TR/WCAG21/#dfn-relative-luminance

    Returns value between 0.0 (black) and 1.0 (white).
    """
    r, g, b = hex_to_rgb(color)
    r_lin = _srgb_to_linear(r)
    g_lin = _srgb_to_linear(g)
    b_lin = _srgb_to_linear(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate WCAG 2.1 contrast ratio between two hex colors.
    Returns a value between 1.0 and 21.0.

    WCAG AA requires ≥4.5:1 for normal text, ≥3:1 for large text.
    WCAG AAA requires ≥7:1 for normal text, ≥4.5:1 for large text.
    """
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return round((lighter + 0.05) / (darker + 0.05), 2)


def check_wcag_aa(foreground: str, background: str) -> bool:
    """Check if two colors meet WCAG AA contrast ratio (≥4.5:1)."""
    return contrast_ratio(foreground, background) >= 4.5


def check_wcag_aaa(foreground: str, background: str) -> bool:
    """Check if two colors meet WCAG AAA contrast ratio (≥7:1)."""
    return contrast_ratio(foreground, background) >= 7.0


def check_wcag_aa_large(foreground: str, background: str) -> bool:
    """Check if two colors meet WCAG AA for large text (≥3:1)."""
    return contrast_ratio(foreground, background) >= 3.0
