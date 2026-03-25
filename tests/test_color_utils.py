"""
The Designer — Color Utility Tests

WCAG contrast ratio calculator, hex parsing, and luminance math.
Tests against known WCAG reference values.
"""
import pytest
from designer.color_utils import (
    is_valid_hex,
    normalize_hex,
    hex_to_rgb,
    relative_luminance,
    contrast_ratio,
    check_wcag_aa,
    check_wcag_aaa,
    check_wcag_aa_large,
)


class TestHexValidation:
    def test_valid_6_digit(self):
        assert is_valid_hex("#FF6B35")

    def test_valid_3_digit(self):
        assert is_valid_hex("#F00")

    def test_valid_lowercase(self):
        assert is_valid_hex("#aabbcc")

    def test_invalid_no_hash(self):
        assert not is_valid_hex("FF6B35")

    def test_invalid_word(self):
        assert not is_valid_hex("red")

    def test_invalid_4_digit(self):
        assert not is_valid_hex("#ABCD")


class TestNormalizeHex:
    def test_3_to_6_digit(self):
        assert normalize_hex("#abc") == "#AABBCC"

    def test_6_digit_uppercase(self):
        assert normalize_hex("#ff6b35") == "#FF6B35"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid hex"):
            normalize_hex("not-a-color")


class TestHexToRgb:
    def test_black(self):
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_white(self):
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_red(self):
        assert hex_to_rgb("#FF0000") == (255, 0, 0)

    def test_short_hex(self):
        assert hex_to_rgb("#F00") == (255, 0, 0)


class TestRelativeLuminance:
    def test_black_luminance(self):
        assert relative_luminance("#000000") == pytest.approx(0.0, abs=0.001)

    def test_white_luminance(self):
        assert relative_luminance("#FFFFFF") == pytest.approx(1.0, abs=0.001)


class TestContrastRatio:
    def test_black_white_21(self):
        assert contrast_ratio("#000000", "#FFFFFF") == 21.0

    def test_same_color_1(self):
        assert contrast_ratio("#FF6B35", "#FF6B35") == 1.0

    def test_commutative(self):
        r1 = contrast_ratio("#000000", "#FFFFFF")
        r2 = contrast_ratio("#FFFFFF", "#000000")
        assert r1 == r2


class TestWcagChecks:
    def test_black_on_white_passes_aa(self):
        assert check_wcag_aa("#000000", "#FFFFFF") is True

    def test_black_on_white_passes_aaa(self):
        assert check_wcag_aaa("#000000", "#FFFFFF") is True

    def test_low_contrast_fails_aa(self):
        # Light gray on white — very low contrast
        assert check_wcag_aa("#CCCCCC", "#FFFFFF") is False

    def test_medium_contrast_passes_large(self):
        # Check that a moderate contrast passes large text threshold
        assert check_wcag_aa_large("#000000", "#FFFFFF") is True
