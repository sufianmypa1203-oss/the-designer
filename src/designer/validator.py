"""
The Designer — DesignValidator (Evaluator-Optimizer Loop)

A SEPARATE evaluation pass that validates generated design artifacts.
15 deterministic checks + LLM evaluator (scored 0-10 per dimension).
"""
from __future__ import annotations
import json
from pathlib import Path
from pydantic import ValidationError

from .models import (
    VisualDesignSpec,
    TypographySpec,
    PrototypeManifest,
)
from .color_utils import contrast_ratio, is_valid_hex


SPECS_DIR = Path("specs")
PROTOTYPES_DIR = Path("prototypes")


class ValidationIssue:
    """Structured validation issue with severity and fix suggestion."""

    def __init__(self, severity: str, source: str, message: str, fix_hint: str = ""):
        self.severity = severity   # CRITICAL / HIGH / MEDIUM
        self.source = source       # UPSTREAM / COLOR / CONTRAST / SCALING / DEPTH / etc.
        self.message = message
        self.fix_hint = fix_hint

    def __str__(self) -> str:
        prefix = f"[{self.severity}][{self.source}]"
        hint = f" → Fix: {self.fix_hint}" if self.fix_hint else ""
        return f"{prefix} {self.message}{hint}"

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "source": self.source,
            "message": self.message,
            "fix_hint": self.fix_hint,
        }


class DesignValidator:
    """
    Two-phase validation:
    1. Deterministic (15 checks: Pydantic schema + WCAG + scaling) — no LLM needed
    2. Semantic (LLM evaluator call) — visual quality, emotion alignment (scored 0-10)

    Returns structured issues that feed directly into the optimizer pass.
    """

    def __init__(
        self,
        specs_dir: Path | None = None,
        prototypes_dir: Path | None = None,
    ):
        self.specs_dir = specs_dir or SPECS_DIR
        self.prototypes_dir = prototypes_dir or PROTOTYPES_DIR

    # ── Check 1: Upstream Artifacts Exist ─────────────────────────────────

    def validate_upstream_artifacts(self) -> list[ValidationIssue]:
        """Verify Director's artifacts exist and are substantial."""
        issues: list[ValidationIssue] = []
        required = ["01-brief.md", "02-script.md", "03-scene-map.json"]

        for filename in required:
            path = self.specs_dir / filename
            if not path.exists():
                issues.append(ValidationIssue(
                    severity="CRITICAL",
                    source="UPSTREAM",
                    message=f"Missing upstream artifact: specs/{filename}",
                    fix_hint=f"Run /director to generate {filename} first",
                ))
            elif path.stat().st_size < 50:
                issues.append(ValidationIssue(
                    severity="CRITICAL",
                    source="UPSTREAM",
                    message=f"Upstream artifact specs/{filename} is empty ({path.stat().st_size} bytes)",
                    fix_hint=f"Re-run /director to regenerate {filename}",
                ))

        return issues

    # ── Check 2: Scene-Map Schema Valid ──────────────────────────────────

    def validate_scene_map_schema(self) -> list[ValidationIssue]:
        """Validate upstream scene-map against Director's contract."""
        issues: list[ValidationIssue] = []
        scene_map_path = self.specs_dir / "03-scene-map.json"

        if not scene_map_path.exists():
            return issues

        try:
            raw = json.loads(scene_map_path.read_text())
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                severity="CRITICAL",
                source="UPSTREAM",
                message=f"Invalid JSON in scene-map: {e}",
                fix_hint="Re-run /director — scene-map has JSON errors",
            ))
            return issues

        if "scenes" not in raw:
            issues.append(ValidationIssue(
                severity="CRITICAL",
                source="UPSTREAM",
                message="scene-map.json missing 'scenes' array",
                fix_hint="Re-run /director to regenerate scene-map",
            ))

        return issues

    # ── Check 3: One Prototype Per Scene ─────────────────────────────────

    def validate_prototype_coverage(self) -> list[ValidationIssue]:
        """Every scene in scene-map must have a prototype HTML file."""
        issues: list[ValidationIssue] = []
        scene_map_path = self.specs_dir / "03-scene-map.json"

        if not scene_map_path.exists():
            return issues

        try:
            raw = json.loads(scene_map_path.read_text())
        except (json.JSONDecodeError, OSError):
            return issues

        scenes = raw.get("scenes", [])
        for scene in scenes:
            proto_file = scene.get("prototypeFile", "")
            if proto_file:
                proto_path = self.prototypes_dir / proto_file
                if not proto_path.exists():
                    issues.append(ValidationIssue(
                        severity="CRITICAL",
                        source="PROTOTYPE",
                        message=f"Missing prototype: {proto_file} for {scene.get('id', '?')}",
                        fix_hint=f"Generate prototypes/{proto_file}",
                    ))

        return issues

    # ── Check 4: Visual Design Spec Schema ───────────────────────────────

    def validate_visual_spec_schema(self) -> list[ValidationIssue]:
        """Validate 04-visual-design-spec.json against VisualDesignSpec."""
        issues: list[ValidationIssue] = []
        spec_path = self.specs_dir / "04-visual-design-spec.json"

        if not spec_path.exists():
            issues.append(ValidationIssue(
                severity="CRITICAL",
                source="SCHEMA",
                message="specs/04-visual-design-spec.json does not exist",
                fix_hint="Generate the visual design spec",
            ))
            return issues

        try:
            raw = json.loads(spec_path.read_text())
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                severity="CRITICAL",
                source="SCHEMA",
                message=f"Invalid JSON in visual design spec: {e}",
                fix_hint="Fix JSON syntax errors",
            ))
            return issues

        try:
            VisualDesignSpec(**raw)
        except ValidationError as e:
            for err in e.errors():
                loc = ".".join(str(x) for x in err["loc"])
                issues.append(ValidationIssue(
                    severity="CRITICAL" if "contrast" in loc.lower() else "HIGH",
                    source="SCHEMA",
                    message=f"Visual spec {loc}: {err['msg']}",
                    fix_hint=f"Fix field '{loc}' in 04-visual-design-spec.json",
                ))

        return issues

    # ── Check 5: Typography Spec Schema ──────────────────────────────────

    def validate_typography_spec_schema(self) -> list[ValidationIssue]:
        """Validate 05-typography-spec.json against TypographySpec."""
        issues: list[ValidationIssue] = []
        spec_path = self.specs_dir / "05-typography-spec.json"

        if not spec_path.exists():
            issues.append(ValidationIssue(
                severity="CRITICAL",
                source="SCHEMA",
                message="specs/05-typography-spec.json does not exist",
                fix_hint="Generate the typography spec",
            ))
            return issues

        try:
            raw = json.loads(spec_path.read_text())
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                severity="CRITICAL",
                source="SCHEMA",
                message=f"Invalid JSON in typography spec: {e}",
                fix_hint="Fix JSON syntax errors",
            ))
            return issues

        try:
            TypographySpec(**raw)
        except ValidationError as e:
            for err in e.errors():
                loc = ".".join(str(x) for x in err["loc"])
                issues.append(ValidationIssue(
                    severity="CRITICAL" if "canvas" in loc.lower() else "HIGH",
                    source="SCHEMA",
                    message=f"Typography spec {loc}: {err['msg']}",
                    fix_hint=f"Fix field '{loc}' in 05-typography-spec.json",
                ))

        return issues

    # ── Check 6: Prototype Manifest Schema ───────────────────────────────

    def validate_manifest_schema(self) -> list[ValidationIssue]:
        """Validate 06-prototype-manifest.json against PrototypeManifest."""
        issues: list[ValidationIssue] = []
        spec_path = self.specs_dir / "06-prototype-manifest.json"

        if not spec_path.exists():
            issues.append(ValidationIssue(
                severity="CRITICAL",
                source="SCHEMA",
                message="specs/06-prototype-manifest.json does not exist",
                fix_hint="Generate the prototype manifest",
            ))
            return issues

        try:
            raw = json.loads(spec_path.read_text())
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                severity="CRITICAL",
                source="SCHEMA",
                message=f"Invalid JSON in prototype manifest: {e}",
                fix_hint="Fix JSON syntax errors",
            ))
            return issues

        try:
            PrototypeManifest(**raw)
        except ValidationError as e:
            for err in e.errors():
                loc = ".".join(str(x) for x in err["loc"])
                issues.append(ValidationIssue(
                    severity="CRITICAL" if "element" in loc.lower() else "HIGH",
                    source="SCHEMA",
                    message=f"Manifest {loc}: {err['msg']}",
                    fix_hint=f"Fix field '{loc}' in 06-prototype-manifest.json",
                ))

        return issues

    # ── Check 7: Scene ID Cross-Validation ───────────────────────────────

    def validate_scene_id_consistency(self) -> list[ValidationIssue]:
        """Scene IDs must match across scene-map and all Designer specs."""
        issues: list[ValidationIssue] = []

        scene_map_path = self.specs_dir / "03-scene-map.json"
        visual_spec_path = self.specs_dir / "04-visual-design-spec.json"
        typo_spec_path = self.specs_dir / "05-typography-spec.json"
        manifest_path = self.specs_dir / "06-prototype-manifest.json"

        if not scene_map_path.exists():
            return issues

        try:
            scene_map = json.loads(scene_map_path.read_text())
        except (json.JSONDecodeError, OSError):
            return issues

        upstream_ids = {s.get("id") for s in scene_map.get("scenes", [])}

        for spec_path, spec_name, key in [
            (visual_spec_path, "visual-design-spec", "scenes"),
            (typo_spec_path, "typography-spec", "scenes"),
            (manifest_path, "prototype-manifest", "prototypes"),
        ]:
            if not spec_path.exists():
                continue
            try:
                data = json.loads(spec_path.read_text())
            except (json.JSONDecodeError, OSError):
                continue

            spec_ids = {s.get("scene_id") for s in data.get(key, [])}
            missing = upstream_ids - spec_ids
            extra = spec_ids - upstream_ids

            if missing:
                issues.append(ValidationIssue(
                    severity="CRITICAL",
                    source="CROSS_REF",
                    message=f"Scenes in scene-map but missing from {spec_name}: {missing}",
                    fix_hint=f"Add missing scenes to {spec_path.name}",
                ))
            if extra:
                issues.append(ValidationIssue(
                    severity="HIGH",
                    source="CROSS_REF",
                    message=f"Scenes in {spec_name} but not in scene-map: {extra}",
                    fix_hint=f"Remove extra scenes from {spec_path.name}",
                ))

        return issues

    # ── Check 8: Focal Point Not Logo in Hook ────────────────────────────

    def validate_focal_not_logo_in_hook(self) -> list[ValidationIssue]:
        """Focal point cannot be a logo in hook/shock scenes."""
        issues: list[ValidationIssue] = []

        scene_map_path = self.specs_dir / "03-scene-map.json"
        visual_spec_path = self.specs_dir / "04-visual-design-spec.json"

        if not scene_map_path.exists() or not visual_spec_path.exists():
            return issues

        try:
            scene_map = json.loads(scene_map_path.read_text())
            visual_spec = json.loads(visual_spec_path.read_text())
        except (json.JSONDecodeError, OSError):
            return issues

        hook_ids = {
            s.get("id") for s in scene_map.get("scenes", [])
            if s.get("role") in ("hook", "shock")
        }

        for scene in visual_spec.get("scenes", []):
            sid = scene.get("scene_id")
            if sid in hook_ids:
                focal = scene.get("focal_point", {})
                focal_id = focal.get("focal_element_id", "").lower()
                if "logo" in focal_id:
                    issues.append(ValidationIssue(
                        severity="HIGH",
                        source="FOCAL",
                        message=f"[{sid}] Focal point is a logo in hook/shock scene",
                        fix_hint="Lead with number or pain point, not logo",
                    ))

        return issues

    # ── Check 9: Color Count Per Scene (FIXED — detects duplicates) ──────

    def validate_color_count(self) -> list[ValidationIssue]:
        """Detect duplicate colors across 60-30-10 roles (no visual separation)."""
        issues: list[ValidationIssue] = []
        visual_spec_path = self.specs_dir / "04-visual-design-spec.json"

        if not visual_spec_path.exists():
            return issues

        try:
            data = json.loads(visual_spec_path.read_text())
        except (json.JSONDecodeError, OSError):
            return issues

        for scene in data.get("scenes", []):
            colors_data = scene.get("colors", {})
            color_values = [
                colors_data.get("dominant_60", "").upper(),
                colors_data.get("secondary_30", "").upper(),
                colors_data.get("accent_10", "").upper(),
            ]
            color_values = [c for c in color_values if c]

            # Check if any two colors are identical (no visual separation)
            unique_colors = set(color_values)
            if len(color_values) >= 2 and len(unique_colors) < len(color_values):
                duplicates = [c for c in color_values if color_values.count(c) > 1]
                issues.append(ValidationIssue(
                    severity="HIGH",
                    source="COLOR",
                    message=f"[{scene.get('scene_id')}] Duplicate colors in 60-30-10 roles: "
                            f"{set(duplicates)} — no visual separation between roles",
                    fix_hint="Each color role (60/30/10) must use a distinct color",
                ))

        return issues

    # ── Check 10: Live WCAG Contrast Recalculation ───────────────────────

    def validate_contrast_recalc(self) -> list[ValidationIssue]:
        """Re-calculate contrast ratios from raw hex values and verify against WCAG AA."""
        issues: list[ValidationIssue] = []
        visual_spec_path = self.specs_dir / "04-visual-design-spec.json"
        typo_spec_path = self.specs_dir / "05-typography-spec.json"

        if not visual_spec_path.exists() or not typo_spec_path.exists():
            return issues

        try:
            visual_data = json.loads(visual_spec_path.read_text())
            typo_data = json.loads(typo_spec_path.read_text())
        except (json.JSONDecodeError, OSError):
            return issues

        # Build scene → background color map
        scene_bg: dict[str, str] = {}
        for scene in visual_data.get("scenes", []):
            colors = scene.get("colors", {})
            bg = colors.get("dominant_60", "")
            if bg and is_valid_hex(bg):
                scene_bg[scene.get("scene_id", "")] = bg

        # Check every text element's color against its scene background
        for scene in typo_data.get("scenes", []):
            sid = scene.get("scene_id", "")
            bg_color = scene_bg.get(sid)
            if not bg_color:
                continue

            for element in scene.get("elements", []):
                text_color = element.get("color", "")
                if not is_valid_hex(text_color):
                    continue

                actual_ratio = contrast_ratio(text_color, bg_color)
                if actual_ratio < 4.5:
                    issues.append(ValidationIssue(
                        severity="CRITICAL",
                        source="CONTRAST",
                        message=f"[{sid}] '{element.get('element_id')}' "
                                f"contrast {actual_ratio:.1f}:1 "
                                f"(text {text_color} on bg {bg_color}). "
                                f"WCAG AA requires ≥4.5:1",
                        fix_hint="Change text color or background to increase contrast",
                    ))

        return issues

    # ── Check 11: Canvas Scaling ×3 Spot-Check ───────────────────────────

    def validate_canvas_scaling_spotcheck(self) -> list[ValidationIssue]:
        """Re-verify canvas = prototype × 3 for typography AND manifest elements."""
        issues: list[ValidationIssue] = []

        # Check typography spec font sizes
        typo_path = self.specs_dir / "05-typography-spec.json"
        if typo_path.exists():
            try:
                typo_data = json.loads(typo_path.read_text())
                for scene in typo_data.get("scenes", []):
                    for el in scene.get("elements", []):
                        proto = el.get("font_size_prototype", 0)
                        canvas = el.get("font_size_canvas", 0)
                        if proto > 0 and canvas != proto * 3:
                            issues.append(ValidationIssue(
                                severity="CRITICAL",
                                source="SCALING",
                                message=f"[{scene.get('scene_id')}] "
                                        f"'{el.get('element_id')}' "
                                        f"font_size_canvas={canvas} ≠ "
                                        f"{proto} × 3 = {proto * 3}",
                                fix_hint="Set font_size_canvas to "
                                         "font_size_prototype × 3",
                            ))
            except (json.JSONDecodeError, OSError):
                pass

        # Check manifest element positions
        manifest_path = self.specs_dir / "06-prototype-manifest.json"
        if manifest_path.exists():
            try:
                manifest_data = json.loads(manifest_path.read_text())
                for proto in manifest_data.get("prototypes", []):
                    for el in proto.get("elements", []):
                        for dim in ["x", "y", "width", "height"]:
                            proto_val = el.get(dim, 0)
                            canvas_val = el.get(f"canvas_{dim}", 0)
                            if proto_val > 0 and canvas_val != proto_val * 3:
                                issues.append(ValidationIssue(
                                    severity="CRITICAL",
                                    source="SCALING",
                                    message=f"[{proto.get('scene_id')}] "
                                            f"'{el.get('element_id')}' "
                                            f"canvas_{dim}={canvas_val} ≠ "
                                            f"{dim}={proto_val} × 3 = "
                                            f"{proto_val * 3}",
                                    fix_hint=f"Set canvas_{dim} to "
                                             f"{dim} × 3",
                                ))
            except (json.JSONDecodeError, OSError):
                pass

        return issues

    # ── Check 12: Depth Layers ≥2 Per Scene ──────────────────────────────

    def validate_depth_layers(self) -> list[ValidationIssue]:
        """Every scene must have ≥2 depth layers with distinct z-indices."""
        issues: list[ValidationIssue] = []
        visual_spec_path = self.specs_dir / "04-visual-design-spec.json"

        if not visual_spec_path.exists():
            return issues

        try:
            data = json.loads(visual_spec_path.read_text())
        except (json.JSONDecodeError, OSError):
            return issues

        for scene in data.get("scenes", []):
            sid = scene.get("scene_id", "?")
            layers = scene.get("depth_layers", [])

            if len(layers) < 2:
                issues.append(ValidationIssue(
                    severity="CRITICAL",
                    source="DEPTH",
                    message=f"[{sid}] Only {len(layers)} depth layer(s) "
                            f"— minimum 2 required",
                    fix_hint="Add background + foreground layers minimum",
                ))
                continue

            z_indices = [dl.get("z_index", 0) for dl in layers]
            if len(set(z_indices)) < 2:
                issues.append(ValidationIssue(
                    severity="HIGH",
                    source="DEPTH",
                    message=f"[{sid}] All depth layers have same "
                            f"z_index={z_indices[0]} — no visual depth",
                    fix_hint="Use distinct z_index values for each layer",
                ))

        return issues

    # ── Check 13: Weight Contrast ≥300 Cross-Check ───────────────────────

    def validate_weight_contrast(self) -> list[ValidationIssue]:
        """Re-verify weight contrast (max − min ≥ 300) per scene."""
        issues: list[ValidationIssue] = []
        typo_path = self.specs_dir / "05-typography-spec.json"

        if not typo_path.exists():
            return issues

        try:
            data = json.loads(typo_path.read_text())
        except (json.JSONDecodeError, OSError):
            return issues

        for scene in data.get("scenes", []):
            sid = scene.get("scene_id", "?")
            elements = scene.get("elements", [])
            weights = [e.get("font_weight", 400) for e in elements]

            if len(weights) >= 2:
                diff = max(weights) - min(weights)
                if diff < 300:
                    issues.append(ValidationIssue(
                        severity="HIGH",
                        source="TYPOGRAPHY",
                        message=f"[{sid}] Weight contrast {diff} "
                                f"(weights: {sorted(set(weights))}). "
                                f"Minimum 300 for hierarchy.",
                        fix_hint="Increase weight spread — e.g., 900 vs 400",
                    ))

        return issues

    # ── Check 14: Element IDs Globally Unique ────────────────────────────

    def validate_element_ids_unique(self) -> list[ValidationIssue]:
        """Element IDs must be unique across ALL prototypes in manifest."""
        issues: list[ValidationIssue] = []
        manifest_path = self.specs_dir / "06-prototype-manifest.json"

        if not manifest_path.exists():
            return issues

        try:
            data = json.loads(manifest_path.read_text())
        except (json.JSONDecodeError, OSError):
            return issues

        all_ids: list[str] = []
        for proto in data.get("prototypes", []):
            for el in proto.get("elements", []):
                eid = el.get("element_id", "")
                if eid:
                    all_ids.append(eid)

        if len(all_ids) != len(set(all_ids)):
            dupes = {eid for eid in all_ids if all_ids.count(eid) > 1}
            issues.append(ValidationIssue(
                severity="CRITICAL",
                source="ELEMENT_ID",
                message=f"Duplicate element IDs across prototypes: {dupes}",
                fix_hint="Every element ID must be globally unique",
            ))

        return issues

    # ── Check 15: Text Matches Script ────────────────────────────────────

    def validate_text_matches_script(self) -> list[ValidationIssue]:
        """Cross-reference text_content in typography spec against script."""
        issues: list[ValidationIssue] = []
        script_path = self.specs_dir / "02-script.md"
        typo_path = self.specs_dir / "05-typography-spec.json"

        if not script_path.exists() or not typo_path.exists():
            return issues

        try:
            script_text = script_path.read_text().lower()
            typo_data = json.loads(typo_path.read_text())
        except (json.JSONDecodeError, OSError):
            return issues

        for scene in typo_data.get("scenes", []):
            for el in scene.get("elements", []):
                text = el.get("text_content", "").strip()
                role = el.get("role", "")
                # Skip very short text (labels, badges) and counters
                if len(text) < 4 or role in ("counter", "badge", "label"):
                    continue
                if text.lower() not in script_text:
                    issues.append(ValidationIssue(
                        severity="MEDIUM",
                        source="SCRIPT_MATCH",
                        message=f"[{scene.get('scene_id')}] Text "
                                f"'{text[:50]}' not found in script "
                                f"— was it invented?",
                        fix_hint="Ensure all text comes from the "
                                 "approved script",
                    ))

        return issues

    # ── Master Validation ─────────────────────────────────────────────────

    def run_all_deterministic(self) -> list[ValidationIssue]:
        """Run all 15 deterministic validation passes."""
        all_issues: list[ValidationIssue] = []
        all_issues.extend(self.validate_upstream_artifacts())       # 1
        all_issues.extend(self.validate_scene_map_schema())         # 2
        all_issues.extend(self.validate_prototype_coverage())       # 3
        all_issues.extend(self.validate_visual_spec_schema())       # 4
        all_issues.extend(self.validate_typography_spec_schema())   # 5
        all_issues.extend(self.validate_manifest_schema())          # 6
        all_issues.extend(self.validate_scene_id_consistency())     # 7
        all_issues.extend(self.validate_focal_not_logo_in_hook())   # 8
        all_issues.extend(self.validate_color_count())              # 9
        all_issues.extend(self.validate_contrast_recalc())          # 10
        all_issues.extend(self.validate_canvas_scaling_spotcheck()) # 11
        all_issues.extend(self.validate_depth_layers())             # 12
        all_issues.extend(self.validate_weight_contrast())          # 13
        all_issues.extend(self.validate_element_ids_unique())       # 14
        all_issues.extend(self.validate_text_matches_script())      # 15
        return all_issues

    def has_critical_issues(self, issues: list[ValidationIssue]) -> bool:
        return any(i.severity == "CRITICAL" for i in issues)

    def format_report(self, issues: list[ValidationIssue]) -> str:
        """Format issues into a human-readable validation report."""
        if not issues:
            return "✅ All 15 design validations passed. Artifacts are clean."

        report_lines = [
            f"## ⚠️ Design Validation Report — {len(issues)} Issue(s) Found\n",
            "| Severity | Source | Issue | Fix |",
            "|----------|--------|-------|-----|",
        ]
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}
        for i in sorted(issues, key=lambda x: severity_order.get(x.severity, 3)):
            report_lines.append(
                f"| **{i.severity}** | {i.source} | {i.message} | {i.fix_hint} |"
            )

        critical_count = sum(1 for i in issues if i.severity == "CRITICAL")
        if critical_count:
            report_lines.append(
                f"\n❌ **{critical_count} CRITICAL issue(s) must be fixed before handoff.**"
            )
        else:
            report_lines.append(
                f"\n⚠️ **{len(issues)} non-critical issue(s). Review recommended.**"
            )

        return "\n".join(report_lines)

    # ── LLM Evaluator — Scoring Mode (0-10 Per Dimension) ────────────────

    def build_llm_evaluator_prompt(
        self, brief: str, visual_spec: str, typography_spec: str
    ) -> str:
        """
        Builds the prompt for the LLM evaluator pass.
        SEPARATE call — not the Designer reviewing its own work.
        Returns a scored evaluation across 6 design dimensions.
        Any dimension below 7 blocks handoff.
        """
        return f"""You are a strict visual design evaluator for short-form vertical video (1080×1920).
Score these design specs on 6 dimensions. Return ONLY a JSON object.

BRIEF (brand colors, tone, energy):
{brief[:2000]}

VISUAL DESIGN SPEC:
{visual_spec[:3000]}

TYPOGRAPHY SPEC:
{typography_spec[:2000]}

SCORE EACH DIMENSION FROM 0-10:
1. "color" — Does the palette serve the emotion? Is 60-30-10 applied? Any invented colors?
2. "typography" — Weight contrast ≥300? Golden ratio ramp? Readable at 1080px? Tracking on CAPS?
3. "focal" — ONE clear entry point per scene? Isolation technique applied? No competing elements?
4. "depth" — ≥2 layers per scene? Z-index separation? Background blur for depth illusion?
5. "emotion" — Does each scene's design match its intended emotion? Color temperature aligned?
6. "craft" — Grain texture mentioned? Vignette? Clip reveals over fades? Relief zones present?

Also provide a "violations" array of specific issues found.

Output format (JSON only, no markdown):
{{"color": 8, "typography": 9, "focal": 7, "depth": 8, "emotion": 6, "craft": 7, "violations": ["issue 1", "issue 2"]}}

SCORING GUIDE:
- 9-10: Production-ready, elite quality
- 7-8: Good, minor polish needed
- 5-6: Acceptable but has gaps
- 3-4: Below standard, major issues
- 0-2: Fundamentally broken

Any dimension below 7 blocks handoff. Be strict."""
