# /designer

Run the Designer agent — visual design specification and HTML prototype generation.

## Usage
```
/designer                          # Start design from upstream specs
/designer --validate-only          # Validate existing design artifacts without regeneration
```

## What This Command Does
1. Validates upstream Director artifacts exist and are schema-valid (`01-brief.md`, `02-script.md`, `03-scene-map.json`)
2. Creates HTML prototypes for each scene in `prototypes/` (360×640 viewport, self-contained)
3. Generates three design specification artifacts in `specs/`:
   - `specs/04-visual-design-spec.json` — Color, focal points, depth layers per scene
   - `specs/05-typography-spec.json` — Every text element with type scale tokens
   - `specs/06-prototype-manifest.json` — DOM element registry with positions and sizes
4. Runs 6-layer QA pass (concept, typography, color, space, emotion, craft)
5. Self-validates all artifacts (Pydantic schema + WCAG contrast + evaluator-optimizer pass)
6. Outputs Handoff block for `/motion-architect`

## This Command Does NOT
- Write or modify Director's artifacts (→ `/director`)
- Specify motion physics, springs, or transitions (→ `/motion-architect`)
- Choose components or write `.tsx` code (→ `/builder`)
- Modify script text or frame timing (→ `/director`)

## Pipeline Position
```
/director → [/designer] → /motion-architect → /builder → /inspector
                ↑ YOU ARE HERE
```

## Gate Criteria
The Designer will not hand off until ALL of these pass:
- Upstream artifacts validated (brief, script, scene-map)
- One prototype per scene, matching scene-map exactly
- All text matches script — no invented copy
- WCAG AA contrast ≥4.5:1 for all text elements
- Canvas scaling ×3 verified for all measurements
- 60-30-10 color split applied per scene
- ≥2 depth layers per scene
- 6-layer QA pass complete
- Evaluator-optimizer loop reports zero critical issues
