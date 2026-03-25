# Video Factory — Agent Persistent Memory

## Project Context
This is a multi-agent video production pipeline.
Pipeline order: `/director` → `/designer` → `/motion-architect` → `/builder` → `/inspector`
Contract file: `specs/03-scene-map.json` is THE source of truth from Director.
Designer reads 3 upstream artifacts and produces 3 specs + HTML prototypes.

## Designer Rules (Always Active)
- Never start without validated upstream artifacts (brief, script, scene-map)
- Never use placeholder text — all text comes from `02-script.md`
- Never hardcode colors outside the brief's palette
- Never skip the 6-layer QA pass
- Canvas is 360×640 prototype (1/3 scale of 1080×1920)
- All font sizes: canvas = prototype × 3. Always.
- Minimum font sizes on 1080×1920: hero ≥96px, sub ≥72px, body ≥36px, caption ≥27px
- WCAG AA contrast ≥4.5:1 for ALL text elements
- Every DOM element gets `data-element-id` and `data-layer` attributes
- Maximum 3 colors per scene (60-30-10)
- Focal point is NEVER a logo in hook scene
- Never modify Director's artifacts
- Prototype HTML must include viewport meta tag targeting 360×640

## Pydantic Contract Enforcement
- `src/designer/models.py` contains 11 Pydantic models — source of truth for all types
- `VisualDesignSpec` validates the complete design before write
- `DesignValidator` runs **15 deterministic checks** + LLM evaluator (0-10 scoring, 6 dimensions) before handoff
- **Any dimension score <7 blocks handoff** — handoff is gated, not advisory
- Invalid artifacts raise `ValidationError` — handoff is blocked until resolved

## Knowledge Base (12 files in `knowledge/`)
- `emotion_design_matrix.md` — 9 emotions → concrete visual parameters (HSL, spacing, depth, shapes)
- `component_registry.md` — 14 components (8 existing + 6 future) with Designer properties + anti-patterns
- `design_system_tokens.md` — Type scales, spacing tokens, color tokens
- `canvas_scaling_cheatsheet.md` — ×3 scaling rules and reference tables
- `prototype_reference_library.md` — HTML prototype templates and patterns
- `anti_patterns.md` — Comprehensive list of design mistakes to avoid
- `color_theory.md`, `visual_psychology.md`, `layout_composition.md`, `cinematic_video_layout.md`, `design_laws.md`, `design_qa.md`

## Current Project State
<!-- Designer writes this block after each session -->
projectId: (none)
phase: (none)
upstream_validated: false
artifacts_locked: false
