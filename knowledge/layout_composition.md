# Layout Composition — Designer Knowledge

## The Rule of Thirds
- Divide canvas into 3×3 grid
- Place focal elements at intersection points
- Never center everything — creates static, boring compositions
- Exception: single-word hero text can center for impact

## Depth Layering (Mandatory ≥2 Layers)
| Layer | Purpose | Visual Treatment |
|-------|---------|-----------------|
| **Background** | Sets atmosphere | Blur, low opacity, gradients, patterns |
| **Midground** | Supporting content | Cards, secondary text, decorative elements |
| **Foreground** | Focal content | Sharp, high contrast, full opacity |

## White Space Strategy
- **20% more** than your instinct says — always
- White space is not empty — it's the design working
- Relief zones: areas where the eye rests between information
- Minimum 1 relief zone per scene

## Grid Systems
| Grid | Use Case |
|------|----------|
| **12-column** | Complex layouts, multiple elements |
| **6-column** | Simpler layouts, mobile-first |
| **Golden ratio** | Hero sections, focal point placement |
| **Rule of thirds** | Image composition, asymmetric layouts |

## Eye Movement Patterns
- **Z-pattern**: For minimal text, image-heavy scenes → eye goes: top-left → top-right → diagonal → bottom-left → bottom-right
- **F-pattern**: For text-heavy scenes → eye scans: top bar → left column down → horizontal sweeps

## Canvas Scaling Law
- Prototype: **360×640** (1/3 scale)
- Canvas: **1080×1920** (full scale)
- Scale factor: **×3** — ALWAYS
- Every measurement: `canvas_value = prototype_value × 3`
- Violation = broken layout at render time
