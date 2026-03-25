"""
The Designer — ACI-Engineered Tools

Each tool does ONE thing with CLEAR boundaries.
Error messages are actionable — tell the agent exactly what to fix.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from .models import VisualDesignSpec, TypographySpec, PrototypeManifest
from .validator import DesignValidator, ValidationIssue


# Default directories — can be overridden
SPECS_DIR = Path("specs")
PROTOTYPES_DIR = Path("prototypes")


# ─── Upstream Validation Tool ────────────────────────────────────────────────

def validate_upstream(specs_dir: Path | None = None) -> dict[str, Any]:
    """
    Validates that Director's upstream artifacts exist and are schema-valid.
    MUST be called before any design work begins.
    If this fails → STOP and tell user to re-run /director.
    """
    target_dir = specs_dir or SPECS_DIR
    validator = DesignValidator(specs_dir=target_dir)

    issues = validator.validate_upstream_artifacts()
    issues.extend(validator.validate_scene_map_schema())

    # Extract scene info if valid
    scene_info = []
    scene_map_path = target_dir / "03-scene-map.json"
    if scene_map_path.exists():
        try:
            data = json.loads(scene_map_path.read_text())
            for s in data.get("scenes", []):
                scene_info.append({
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "role": s.get("role"),
                    "prototypeFile": s.get("prototypeFile"),
                })
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "valid": len(issues) == 0,
        "issues": [i.to_dict() for i in issues],
        "scene_count": len(scene_info),
        "scenes": scene_info,
    }


# ─── Prototype Write Tool ───────────────────────────────────────────────────

def write_prototype(
    filename: str,
    content: str,
    prototypes_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Writes an HTML prototype file to the prototypes/ directory.
    Validates that the filename matches expected pattern.

    Filename must match: Scene{N}_{SceneName}.html
    Content must contain data-element-id attributes.
    """
    target_dir = prototypes_dir or PROTOTYPES_DIR

    # Validate filename pattern
    if not filename.endswith(".html") or not filename.startswith("Scene"):
        return {
            "success": False,
            "error": f"Invalid prototype filename: '{filename}'. "
                     f"Must match pattern: Scene{{N}}_{{Name}}.html",
        }

    # Check for required attributes
    if "data-element-id" not in content:
        return {
            "success": False,
            "error": "Prototype HTML must contain data-element-id attributes "
                     "on every element. Add them and retry.",
        }

    if "data-layer" not in content:
        return {
            "success": False,
            "error": "Prototype HTML must contain data-layer attributes "
                     "(background/midground/foreground). Add them and retry.",
        }

    target_dir.mkdir(exist_ok=True)
    filepath = target_dir / filename
    filepath.write_text(content, encoding="utf-8")

    return {
        "success": True,
        "path": str(filepath),
        "size_bytes": filepath.stat().st_size,
    }


# ─── Visual Design Spec Write Tool ──────────────────────────────────────────

def write_visual_spec(
    content: str,
    specs_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Writes specs/04-visual-design-spec.json after Pydantic validation.
    Content must be valid JSON that passes VisualDesignSpec validation.
    """
    target_dir = specs_dir or SPECS_DIR

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON: {e}. Fix and retry.",
        }

    try:
        validated = VisualDesignSpec(**data)
    except Exception as e:
        return {
            "success": False,
            "error": f"Schema validation failed:\n{e}\n\n"
                     f"Fix the issues and retry.",
        }

    target_dir.mkdir(exist_ok=True)
    filepath = target_dir / "04-visual-design-spec.json"
    filepath.write_text(validated.model_dump_json(indent=2), encoding="utf-8")

    return {
        "success": True,
        "path": str(filepath),
        "scene_count": len(validated.scenes),
    }


# ─── Typography Spec Write Tool ─────────────────────────────────────────────

def write_typography_spec(
    content: str,
    specs_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Writes specs/05-typography-spec.json after Pydantic validation.
    Content must be valid JSON that passes TypographySpec validation.
    """
    target_dir = specs_dir or SPECS_DIR

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON: {e}. Fix and retry.",
        }

    try:
        validated = TypographySpec(**data)
    except Exception as e:
        return {
            "success": False,
            "error": f"Schema validation failed:\n{e}\n\n"
                     f"Fix the issues and retry.",
        }

    target_dir.mkdir(exist_ok=True)
    filepath = target_dir / "05-typography-spec.json"
    filepath.write_text(validated.model_dump_json(indent=2), encoding="utf-8")

    return {
        "success": True,
        "path": str(filepath),
        "scene_count": len(validated.scenes),
    }


# ─── Prototype Manifest Write Tool ──────────────────────────────────────────

def write_prototype_manifest(
    content: str,
    specs_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Writes specs/06-prototype-manifest.json after Pydantic validation.
    Content must be valid JSON that passes PrototypeManifest validation.
    """
    target_dir = specs_dir or SPECS_DIR

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON: {e}. Fix and retry.",
        }

    try:
        validated = PrototypeManifest(**data)
    except Exception as e:
        return {
            "success": False,
            "error": f"Schema validation failed:\n{e}\n\n"
                     f"Fix the issues and retry.",
        }

    target_dir.mkdir(exist_ok=True)
    filepath = target_dir / "06-prototype-manifest.json"
    filepath.write_text(validated.model_dump_json(indent=2), encoding="utf-8")

    return {
        "success": True,
        "path": str(filepath),
        "total_elements": validated.total_elements,
    }


# ─── Validation Tool ────────────────────────────────────────────────────────

def run_design_validation(
    specs_dir: Path | None = None,
    prototypes_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Runs ALL deterministic validation passes on design artifacts.
    Returns structured issues with severity, source, and fix hints.

    Call this BEFORE generating the handoff block.
    If any CRITICAL issues exist, handoff is blocked.
    """
    validator = DesignValidator(
        specs_dir=specs_dir or SPECS_DIR,
        prototypes_dir=prototypes_dir or PROTOTYPES_DIR,
    )
    issues = validator.run_all_deterministic()

    return {
        "passed": len(issues) == 0,
        "total_issues": len(issues),
        "critical_count": sum(1 for i in issues if i.severity == "CRITICAL"),
        "handoff_blocked": validator.has_critical_issues(issues),
        "issues": [i.to_dict() for i in issues],
        "report": validator.format_report(issues),
    }


# ─── Handoff Tool ───────────────────────────────────────────────────────────

def generate_handoff_block(
    project_id: str | None = None,
    specs_dir: Path | None = None,
    prototypes_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Generates the handoff block for /motion-architect.
    Will REFUSE to generate if validation has critical issues.
    """
    target_dir = specs_dir or SPECS_DIR
    proto_dir = prototypes_dir or PROTOTYPES_DIR

    validator = DesignValidator(specs_dir=target_dir, prototypes_dir=proto_dir)
    issues = validator.run_all_deterministic()

    if validator.has_critical_issues(issues):
        return {
            "success": False,
            "error": "Cannot generate handoff — CRITICAL issues exist.",
            "report": validator.format_report(issues),
        }

    # Extract projectId from scene-map if not provided
    scene_map_path = target_dir / "03-scene-map.json"
    if scene_map_path.exists() and not project_id:
        try:
            data = json.loads(scene_map_path.read_text())
            project_id = data.get("projectId", "unknown")
        except (json.JSONDecodeError, OSError):
            pass

    pid = project_id or "unknown"

    risks = [i.message for i in issues if i.severity != "CRITICAL"]
    risks_text = ", ".join(risks) if risks else "None"

    handoff = f"""## 📦 Handoff — Designer → Motion Architect
| Field | Value |
|-------|-------|
| **Project** | `{pid}` |
| **Phase completed** | Designer (Agent 2 of 5) |
| **Artifacts created** | `specs/04-visual-design-spec.json`, `specs/05-typography-spec.json`, `specs/06-prototype-manifest.json`, `prototypes/*.html` |
| **Validations passed** | ✅ upstream ✅ color-60-30-10 ✅ contrast-wcag ✅ canvas-scaling ✅ depth-layers ✅ focal-isolation ✅ 6-layer-QA |
| **Unresolved risks** | {risks_text} |
| **Next agent** | `/motion-architect` |

### Prompt for /motion-architect:
> I'm working on `{pid}`. Designer phase is locked.
> Upstream specs are in `specs/`:
> - `01-brief.md` — brand identity, emotion arc, scene plan
> - `02-script.md` — approved script, exact on-screen text per scene
> - `03-scene-map.json` — machine-readable scene contract
> - `04-visual-design-spec.json` — color, focal points, depth layers per scene (read this first)
> - `05-typography-spec.json` — every text element with type scale tokens and animation intents
> - `06-prototype-manifest.json` — DOM element IDs, positions, sizes, layers
> - `prototypes/*.html` — frozen frames for each scene
>
> Run `/motion-architect` to define motion physics, choreography, and transitions."""

    return {
        "success": True,
        "handoff_block": handoff,
        "project_id": pid,
        "non_critical_risks": risks,
    }


# ─── Schema Export Tool ──────────────────────────────────────────────────────

def export_schemas(output_dir: str | Path = "schemas") -> dict[str, Any]:
    """
    Exports all Pydantic model JSON schemas to a schemas/ directory.
    Downstream agents (Motion Architect, Builder) can validate against these.
    """
    out = Path(output_dir)
    out.mkdir(exist_ok=True)

    schemas = {
        "visual-design-spec.schema.json": VisualDesignSpec.model_json_schema(),
        "typography-spec.schema.json": TypographySpec.model_json_schema(),
        "prototype-manifest.schema.json": PrototypeManifest.model_json_schema(),
    }

    for filename, schema in schemas.items():
        filepath = out / filename
        filepath.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    return {
        "success": True,
        "schemas_exported": list(schemas.keys()),
        "output_dir": str(out),
    }


# ─── Tool Registry ──────────────────────────────────────────────────────────

DESIGNER_TOOLS = {
    "validate_upstream": validate_upstream,
    "write_prototype": write_prototype,
    "write_visual_spec": write_visual_spec,
    "write_typography_spec": write_typography_spec,
    "write_prototype_manifest": write_prototype_manifest,
    "run_design_validation": run_design_validation,
    "generate_handoff_block": generate_handoff_block,
    "export_schemas": export_schemas,
}
