# Design QA — 6-Layer Quality Assurance Checklist

Every design must pass ALL 6 layers before handoff. This is non-negotiable.

## Layer 1: Concept
- [ ] Communicates the idea in 2 seconds without reading?
- [ ] ONE dominant visual metaphor per scene?
- [ ] ONE clear entry point (Fixation #1) per scene?
- [ ] Visual matches the brief's core emotion?

## Layer 2: Typography
- [ ] Golden Ratio type ramp applied (or justified alternative)?
- [ ] Strong weight contrast (≥300 weight difference between hero and body)?
- [ ] All-caps labels have tracking ≥ 0.35em?
- [ ] Hero headline ≤ 7 words?
- [ ] All text from `02-script.md` — no invented copy?
- [ ] Minimum font sizes met (hero ≥96px, sub ≥72px, body ≥36px, caption ≥27px on canvas)?
- [ ] Font sizes: canvas = prototype × 3?

## Layer 3: Color
- [ ] 60-30-10 rule named explicitly per scene?
- [ ] Focal element isolated by exactly ONE tactic?
- [ ] Works in grayscale (value contrast test)?
- [ ] No more than 3 colors per scene?
- [ ] WCAG AA contrast ≥4.5:1 for ALL text?
- [ ] Color temperature matches brief specification?
- [ ] Colors come from brief palette — no invented colors?

## Layer 4: Space
- [ ] At least ONE relief zone per scene?
- [ ] White space 20% more than instinct suggests?
- [ ] Z or F eye movement pattern identifiable?
- [ ] Grid system applied consistently?
- [ ] Safe zones respected (top/bottom of vertical video)?

## Layer 5: Emotion
- [ ] Target emotion (from brief) mapped to EVERY element choice?
- [ ] Color temperature matches scene emotion?
- [ ] Shape psychology aligned (circles = trust, triangles = energy)?
- [ ] Energy level matches brief specification?
- [ ] Emotion arc flows naturally between scenes?

## Layer 6: Craft
- [ ] Every element earns its place (removing it loses something)?
- [ ] Holds as a still frame at thumbnail size?
- [ ] All decorative elements serve the focal point, not compete?
- [ ] data-element-id on EVERY DOM element?
- [ ] data-layer on EVERY DOM element?
- [ ] ≥2 depth layers per scene (background, midground, or foreground)?
- [ ] All element IDs globally unique across all prototypes?
