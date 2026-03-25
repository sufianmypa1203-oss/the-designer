# Component Registry — Designer's Reference

> **Purpose**: When the Designer agent specifies a scene, it selects components from this
> registry and fills in the required properties. The Builder then maps semantic labels
> ("snappy spring," "thick liquid wipe") to concrete code parameters.
>
> **Rule**: The Designer specifies WHAT it should look/feel like. The Builder implements HOW.

---

## Designer vs Builder Boundary

The Designer specifies per component:
1. Visual state at key frames (start, mid, end)
2. Timing relationships (durations, delays, overlaps, stagger)
3. Motion *qualities* in semantic language → maps to Builder presets
4. Compositional role (hero, background, de-emphasized)

The Builder maps these to curves, springs, easing, physics, and code.

---

## Scene Role → Component Selection Guide

| Scene Role | Primary Components | Supporting Components |
|------------|-------------------|----------------------|
| **Hook** | `KineticText`, `ClipRevealPro`, `AnimatedElement` | `GrainOverlay`, `VignetteOverlay`, `SvgMorpher` |
| **Build** | `AnimatedElement`, `ValueCounter`, `ParticleSystem`* | `3DPerspective`*, `SplitScreen`* |
| **Reveal** | `ValueCounter`, `ClipRevealPro`, `SvgMorpher` | `MaskingMatte`*, `LiquidTransition`* |
| **Resolve** | `AnimatedElement`, `SceneTransition`, `KineticText` | `GrainOverlay`, `VignetteOverlay` |

*\* = Missing components (spec included below for future implementation)*

---

## Existing Components

### AnimatedElement
**Role**: Simple entrance/exit wrapper — supports narrative without stealing focus.

**When to use**: Hook (slide/fade with energy), Build (cards assembling), Resolve (gentle exit)

**Designer must specify**:
- `entrance_style`: fade | slide-left | slide-right | slide-up | slide-down | scale | rotate | combo
- `motion_feel`: "snappy-spring" | "soft-ease" | "bouncy-overshoot" | "crisp-linear"
- `duration`: short (100–250ms) | medium (300–600ms) | long (800ms+)
- `stagger`: "all-at-once" | "cascade-left" | "cascade-right" | "stagger-by-row" | delay in ms
- `rest_state`: "perfectly-still" | "micro-bounce" | "subtle-float"

**Anti-patterns**:
- ❌ Same big motion on everything → nothing feels focal
- ❌ Heavy springiness on small utility elements → feels childish
- ❌ Combining scale + rotate + large position shift → visually unstable

---

### ValueCounter
**Role**: Animate a number that IS the story — KPI, metric, countdown.

**When to use**: Reveal (key number introduction), Build (stat updates)

**Designer must specify**:
- `start_value`, `end_value`: numeric range
- `format`: currency | percent | abbreviated ("1.2K") | raw
- `emphasis`: hero size, weight, color contrast vs background
- `motion_feel`: "fast-punch" | "gradual-count" | "looping-pulse"
- `context`: supporting labels, icons, micro-copy

**Anti-patterns**:
- ❌ Long count-up from 0 on large numbers → wastes time, feels gimmicky
- ❌ Animating trivial numbers that don't carry narrative weight
- ❌ Counter + camera move + particle burst → metric becomes unreadable

---

### SvgMorpher
**Role**: Show one concept becoming another via continuous shape transformation.

**When to use**: Hook (surprise transformation), Reveal (before→after)

**Designer must specify**:
- `source_shape`, `target_shape`: clearly defined path states
- `style_consistency`: stroke vs fill, corner roundness, visual weight
- `morph_character`: "liquid-organic" | "mechanical-interpolation"
- `duration`: quick snap (150–250ms) | slow transform (600–1000ms)

**Anti-patterns**:
- ❌ Morphing unrelated silhouettes → confusing in-between frames
- ❌ Overusing morphing → every change feels like a magic trick
- ❌ Morphing tiny icons → shape change imperceptible

---

### ClipRevealPro
**Role**: Controlled geometric reveal — wipes, iris, diagonal reveals.

**When to use**: Hook (iris reveal of hero), Reveal (wiping in charts/headlines)

**Designer must specify**:
- `reveal_geometry`: direction (L→R, T→B) + shape (rectangle | circle/iris | diagonal)
- `edge_softness`: hard | feathered
- `speed_curve`: "camera-shutter" | "soft-curtain" | "digital-scan-line"
- `context`: section-transition | local-text-reveal | logo-reveal

**Anti-patterns**:
- ❌ Heavy wipes on every small element → PowerPoint 2005
- ❌ Multiple wipe directions on same frame → visual chaos
- ❌ Wipes when simple fades would suffice → overdesigned

---

### SceneTransition
**Role**: Narrative boundary between scenes — signals chapter change.

**When to use**: Between any scenes, aligned to emotional tone.

**Designer must specify**:
- `transition_type`: crossfade | directional-wipe | push-slide | stylized (liquid/flash)
- `duration`: quick snap (related scenes) | slow drift (mood shifts)
- `visual_motif`: brand shapes, colors, or grid patterns in transition

**Anti-patterns**:
- ❌ Overly long transitions → kills pacing in short video
- ❌ Stylized transitions for tiny content changes → save for big beats
- ❌ Inconsistent transition language → template collage feel

**Tone matching**:
- Calm continuity → crossfade/dissolve
- Energetic progression → wipe/push
- Big chapter break → stylized (liquid, light flash)

---

### KineticText
**Role**: Words ARE the hero — typography with rhythm and motion.

**When to use**: Hook (hero line), Build (adding words over time), Resolve (tagline lock-up)

**Designer must specify**:
- `granularity`: per-character | per-syllable | per-word | per-line
- `motion_style`: type-on | fly-in | pop | flip | zoom | rotate
- `stagger`: sequential | random | directional (L→R, center→edges)
- `stagger_delay`: ms between units (e.g., 40ms chars, 80ms words)
- `emotional_tone`: "punchy-bold" | "elegant-minimal" | "playful-bouncy"

**Anti-patterns**:
- ❌ Complex kinetic typography on long paragraphs → unreadable
- ❌ Over-staggering → viewer waits forever for words to finish
- ❌ Conflicting effects (chars flipping different axes) → fights legibility

---

### GrainOverlay
**Role**: Tactile, cinematic texture — unifies CGI + UI into one visual world.

**When to use**: Global treatment, especially Hook and Resolve.

**Designer must specify**:
- `intensity`: subtle | medium | heavy
- `visibility`: shadows-only | midtones | full-frame
- `scale`: fine-film | chunky-digital
- `blend_color`: monochrome | tinted
- `scope`: full-frame | hero-cards-only

**Anti-patterns**:
- ❌ Over-strong grain → reduces text legibility
- ❌ Inconsistent application without narrative reason
- ❌ Stacking grain on already noisy footage

---

### VignetteOverlay
**Role**: Subtle focus control — darkened edges push attention to center.

**When to use**: Hook (spotlight hero), Resolve (polished final frame)

**Designer must specify**:
- `shape`: radial-center | off-center (specify region)
- `intensity`: how dark edges become (0.1–0.5 opacity range)
- `falloff`: soft-invisible | hard-artistic
- `color`: neutral-darkening | warm-tinted | cool-tinted

**Anti-patterns**:
- ❌ Heavy obvious vignettes → 2010 Instagram filter look
- ❌ Vignette center ≠ focal point → fights attention
- ❌ Layering on high-contrast footage → shadows crush to black

---

## Missing Components (Future Implementation)

### ParticleSystem* (Data Visualization)
**Role**: Visualize many small entities as a system — flows, funnels, swarms.

**When to use**: Build (data aggregating), Reveal (abstract→tangible)

**Designer must specify**:
- `particle_metaphor`: dots | capsules | tiny-icons | strokes | light-streaks
- `density`: sparse-readable | massive-cloud (impressionistic)
- `behavior`: "stream" (directed flow) | "swarm" (boids) | "orbit" (circular) | "explode-settle"
- `color_encoding`: categories | states | value-ranges
- `data_relationship`: "1 particle ≈ 1000 events" | "purely illustrative"

**Anti-patterns**: ❌ Eye candy with no data connection ❌ TV static density ❌ Complex choreography unreadable in 2s

---

### LiquidTransition*
**Role**: Organic, brand-playful transitions — shapes "melt" into each other.

**When to use**: Hook (blob wipe into brand world), Reveal (section morph)

**Designer must specify**:
- `personality`: thick-elastic | watery-syrupy
- `shape_language`: blobs | droplets | waves | ink-spreads
- `color_blending`: brand colors, gradient fills, occludes vs blends
- `scope`: local (liquid headline underline) | full-screen wipe
- `edge_quality`: crisp | gooey-blurred

**Anti-patterns**: ❌ Liquid in serious/enterprise contexts ❌ Slow sluggish blobs ❌ On small UI needing sharpness

---

### 3DPerspective* (2.5D / CSS 3D)
**Role**: Express depth, hierarchy, spatial relationships — card stacks, rotating panels.

**When to use**: Hook (feature stack), Build (rotating panels per step), Resolve (premium 3D arrangement)

**Designer must specify**:
- `camera_framing`: locked-isometric | implied-camera-movement
- `perspective_strength`: subtle-parallax | strong-forced-perspective
- `object_hierarchy`: which panels foreground vs background, overlap amount
- `motion_archetype`: "card-flip" | "carousel" | "stack-expand-collapse"
- `lighting_suggestion`: lit sides vs shaded sides (via gradients/shadows)

**Anti-patterns**: ❌ Extreme perspective on text-heavy UI ❌ Unmotivated rotation flips ❌ Inconsistent perspective breaking 3D illusion

---

### SplitScreen*
**Role**: Compare/juxtapose multiple views — before/after, parallel stories.

**When to use**: Build (adding panes), Reveal (comparison frame)

**Designer must specify**:
- `layout`: 2-panel | 3-panel | 4-panel | grid
- `arrangement`: vertical-split | horizontal-split | mosaic
- `panel_hierarchy`: primary (larger/brighter) vs secondary
- `borders`: gap size, stroke thickness, frame style
- `choreography`: "all-at-once" | "sequential-slide" | "one-grows-others-shrink"

**Anti-patterns**: ❌ Dense UI in tiny panels ❌ Split when sequence would be clearer ❌ Inconsistent color grading between panels

---

### MaskingMatte*
**Role**: Reveal content THROUGH another element — text filled with footage, shapes as windows.

**When to use**: Hook (logo filled with motion), Reveal (content through brand shapes)

**Designer must specify**:
- `mask_layer`: which layer is "window" (text/logo/shape)
- `content_layer`: what appears behind the mask
- `mask_shape_style`: solid | textured-edges | geometric | organic
- `interaction`: "content-moves-behind-static-mask" | "mask-moves-over-static" | "both-animate"
- `edge_treatment`: feathered | rough-handdrawn | crisp

**Anti-patterns**: ❌ Busy content in thin text → illegible ❌ Luma mattes on high-contrast footage → flickering ❌ Masked content competing with unmasked elements

---

### PerspectiveText*
**Role**: Text physically integrated into 3D space — floor labels, receding panels.

**When to use**: Hook (hero word on 3D plane), Build (stacked tilting panels)

**Designer must specify**:
- `plane_orientation`: floor-receding | wall-angled | skewed-billboard
- `perspective_strength`: subtle-UI-skew | strong-environmental
- `legibility_priority`: "graphic-poster" (more skew) | "information-UI" (less skew)
- `integration`: shadows, surface attachment, intersection with 3D objects

**Anti-patterns**: ❌ Heavy perspective on body copy ❌ Multi-direction skewing → chaotic ❌ Inconsistent vanishing points in same scene
