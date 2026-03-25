"""
The Designer — DesignValidator (Evaluator-Optimizer Loop)

A SEPARATE evaluation pass that validates generated design artifacts.
12 deterministic checks + LLM evaluator for semantic/visual quality.
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
    1. Deterministic (Pydantic schema + WCAG + scaling) — no LLM needed
    2. Semantic (LLM evaluator call) — visual quality, emotion alignment

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

        # Basic structural checks without importing Director models
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

        # Cross-check each Designer spec
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

        # Find hook/shock scene IDs
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

    # ── Check 9: Color Count Per Scene ───────────────────────────────────

    def validate_color_count(self) -> list[ValidationIssue]:
        """No more than 3 colors per scene."""
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
            unique_colors = {
                colors_data.get("dominant_60", "").upper(),
                colors_data.get("secondary_30", "").upper(),
                colors_data.get("accent_10", "").upper(),
            }
            unique_colors.discard("")
            if len(unique_colors) > 3:
                issues.append(ValidationIssue(
                    severity="MEDIUM",
                    source="COLOR",
                    message=f"[{scene.get('scene_id')}] {len(unique_colors)} unique colors (max 3)",
                    fix_hint="Reduce to 3 colors max per scene",
                ))

        return issues

    # ── Master Validation ─────────────────────────────────────────────────

    def run_all_deterministic(self) -> list[ValidationIssue]:
        """Run all deterministic validation passes. Returns combined issues."""
        all_issues: list[ValidationIssue] = []
        all_issues.extend(self.validate_upstream_artifacts())
        all_issues.extend(self.validate_scene_map_schema())
        all_issues.extend(self.validate_prototype_coverage())
        all_issues.extend(self.validate_visual_spec_schema())
        all_issues.extend(self.validate_typography_spec_schema())
        all_issues.extend(self.validate_manifest_schema())
        all_issues.extend(self.validate_scene_id_consistency())
        all_issues.extend(self.validate_focal_not_logo_in_hook())
        all_issues.extend(self.validate_color_count())
        return all_issues

    def has_critical_issues(self, issues: list[ValidationIssue]) -> bool:
        return any(i.severity == "CRITICAL" for i in issues)

    def format_report(self, issues: list[ValidationIssue]) -> str:
        """Format issues into a human-readable validation report."""
        if not issues:
            return "✅ All design validations passed. Artifacts are clean."

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

    # ── LLM Evaluator Prompt Builder ──────────────────────────────────────

    def build_llm_evaluator_prompt(
        self, brief: str, visual_spec: str, typography_spec: str
    ) -> str:
        """
        Builds the prompt for the LLM evaluator pass.
        SEPARATE call — not the Designer reviewing its own work.
        """
        return f"""You are a strict visual design evaluator.
Evaluate these design specs against the brief and design laws.
Return ONLY a JSON array of violation strings. Return [] if no violations.

BRIEF (brand colors, tone, energy):
{brief[:2000]}

VISUAL DESIGN SPEC:
{visual_spec[:3000]}

TYPOGRAPHY SPEC:
{typography_spec[:2000]}

CHECK FOR:
1. Color temperature mismatches (brief says "warm" but scene uses cool palette)
2. Typography hierarchy breakdown (no clear size progression)
3. Focal point competing with other elements (multiple high-contrast items)
4. White space violations (elements too cramped, no relief zone)
5. Brand color misuse (accent used > 10%, dominant < 50%)
6. Depth layering absent (everything on same z-plane)
7. Eye path unclear (squint test: can you identify ONE dominant element?)
8. Shape consistency violations (mixed border radii, inconsistent angles)
9. Text elements not from design system type scale
10. Emotion mismatch (design feels energetic but brief calls for calm)

Output format: ["violation 1", "violation 2"] or []
Only output the JSON array — no explanation, no markdown."""
