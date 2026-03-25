# Cinematic Video Layout — Designer Knowledge

## The Poster Test
Every frame must work as a poster. If you screenshot any frame and it doesn't communicate:
- The topic (within 2 seconds)
- The visual hierarchy
- The emotion
→ Motion won't save it. Redesign the still frame first.

## Vertical Video Composition (1080×1920)
| Zone | Y Range | Purpose |
|------|---------|---------|
| **Safe zone top** | 0-180px | Platform UI (status bar, etc.) |
| **Hero zone** | 180-800px | Primary content, headlines |
| **Action zone** | 800-1400px | Supporting content, data, visuals |
| **Anchor zone** | 1400-1770px | CTA, labels, logo |
| **Safe zone bottom** | 1770-1920px | Platform UI (navigation, etc.) |

## Focal Point Isolation Techniques
| Technique | How | When |
|-----------|-----|------|
| **Scale contrast** | Focal element 3× larger than surrounding | Numbers, key stats |
| **Color pop** | Only saturated element on desaturated field | Single highlight |
| **White space** | 3× padding around focal element | Clean, premium feel |
| **Z-depth** | Foreground sharp, background blurred | Depth emphasis |
| **Unique shape** | Only circle among rectangles (or vice versa) | Visual disruption |

## Scene Transition Design
The Designer specifies the VISUAL state at scene boundaries. The Motion Architect owns the transition technique, but the Designer ensures:
- Exit state of scene N is compatible with entry state of scene N+1
- Color temperature transitions are smooth (no jarring jumps)
- Focal point position has eye continuity across scenes

## Typography in Video
- **Hero text**: 96px+ on canvas, bold (700-900), center or rule-of-thirds placement
- **Sub text**: 72px+ on canvas, regular (400-500), below hero
- **Labels**: 36px+ on canvas, uppercase with tracking ≥0.35em, all-caps
- **Captions**: 27px+ on canvas, light, bottom anchor
- **Never** go below 24px on 1080×1920 canvas (8px in prototype)
