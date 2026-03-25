# Emotion → Visual Design Matrix

> **Purpose**: Machine-consumable lookup table. When the Designer agent receives a scene
> with an emotion tag (from the Director's script), it looks up the exact visual parameters here.
> No guessing, no improvisation — every design decision is grounded in color psychology,
> Gestalt principles, and attention science.

## How to Use This File

1. Read the scene's `emotion` field from the Director's script/scene-map
2. Look up the emotion in the table below
3. Apply ALL parameters as defaults — override only with explicit brief instructions
4. When transitioning between scenes, interpolate HSL/spacing/parallax smoothly

---

## Quick Reference: Emotion → Key Visual Signature

| Emotion | Temperature | Saturation | Lightness | Density | Focal Technique | Weight |
|---------|-------------|------------|-----------|---------|-----------------|--------|
| **Shock** | Warm | 0.8–1.0 | 0.45–0.6 | Dense (10–20% WS) | Unexpected Scale | 700–900 |
| **Tension** | Cool-neutral | 0.4–0.7 | 0.25–0.4 | Moderate (15–25%) | Contrast | 500–700 |
| **Build** | Cool→Warm shift | 0.6–0.9 | 0.35–0.55 | Moderate (25–35%) | Motion Contrast | 500→800 |
| **Reveal** | Warm-neutral | 0.7–1.0 | 0.6–0.8 | Open (30–40%) | Unique Hue | 700–900 |
| **Resolve** | Neutral-warm | 0.4–0.7 | 0.6–0.75 | Open (35–50%) | Contrast | 500–600 |
| **Calm** | Cool | 0.25–0.5 | 0.6–0.8 | Very open (45–65%) | Motion Contrast | 300–400 |
| **Urgency** | Warm | 0.8–1.0 | 0.45–0.65 | Dense (15–25%) | Motion Contrast | 700–900 |
| **Triumph** | Warm | 0.7–1.0 | 0.55–0.7 | Balanced (30–45%) | Unexpected Scale | 700–900 |
| **Melancholy** | Cool | 0.2–0.5 | 0.2–0.45 | Spacious (35–55%) | Unique Hue | 300–500 |

---

## Full Parameter Specs

### Shock
```
color:
  temperature: warm
  hue_range: [350, 20]        # wraps around 0° (reds)
  saturation: [0.8, 1.0]
  lightness: [0.45, 0.6]

background:
  mode: dark_solid | sharp_radial_burst
  overlay_opacity: [0.1, 0.25]
  blur_px: [0, 4]             # crisp, abrupt — no softness

spacing:
  padding_ratio: [0.03, 0.05] # nearly edge-to-edge
  whitespace: [0.1, 0.2]      # dense

focal:
  technique: unexpected_scale
  scale_factor: [1.4, 1.8]    # focal element jump-cut scaled up

shapes: jagged_triangles, acute_angles, fractured_diagonals

typography:
  weight: [700, 900]
  tracking: [-0.02, 0]        # tight, heavy for impact
  rationale: "Heavy weights convey strength, power, and assertiveness"

depth:
  layers: [2, 3]
  parallax:
    L1_foreground: [1.1, 1.3]  # fast snap
    L2_midground: [0.9, 1.0]
    L3_background: 0.8

rhythm:
  grid_density: fine_near_focal
  element_count: [3, 6]
  relief_zone: tiny_band_behind_text

visual_metaphors:
  - Screen flash/pop frame
  - Shattering glass or HUD crack
  - Sudden zoom into eye or phone screen
```

### Tension
```
color:
  temperature: cool_neutral
  hue_range: [190, 230]       # deep blues/teals
  saturation: [0.4, 0.7]
  lightness: [0.25, 0.4]      # dark, desaturated

background:
  mode: dark_gradient_top_darker
  overlay_opacity: [0.25, 0.4]
  blur_px: [8, 16]            # ambiguous background shapes

spacing:
  padding_ratio: [0.05, 0.07]
  whitespace: [0.15, 0.25]    # closing in on subject

focal:
  technique: contrast
  detail: localized_high_contrast_strip_or_spotlight

shapes: long_narrow_rectangles, sharp_triangles_pointing_at_focal

typography:
  weight: [500, 700]
  tracking: [-0.01, 0]        # slightly compact, firm
  rationale: "Serious and constrained while maintaining legibility"

depth:
  layers: 3
  parallax:
    L1_foreground: [1.0, 1.1]
    L2_midground: [0.9, 1.0]  # obstructing bars/shapes
    L3_background: [0.7, 0.8] # subtle, claustrophobic

rhythm:
  grid_density: medium_with_vertical_strips
  element_count: [5, 9]
  relief_zone: thin_vertical_gutter

visual_metaphors:
  - Slowly closing doorway or bars
  - Tightening spotlight cone
  - Creeping shadow or progress bar approaching critical point
```

### Build (Rising Anticipation)
```
color:
  temperature: cool_shifting_to_warm
  hue_range: [200, 220] → [30, 40]  # ramps over time
  saturation: [0.6, 0.9]
  lightness: [0.35, 0.55]

background:
  mode: angled_gradient
  overlay_opacity: [0.15, 0.3]
  blur_px: [4, 10]            # decreasing blur = "coming into focus"

spacing:
  padding_ratio: [0.06, 0.08]
  whitespace: [0.25, 0.35]    # slowly compresses

focal:
  technique: motion_contrast
  detail: foreground_easing_slow_to_faster

shapes: repeated_lines, stepped_rectangles, ramps_arcs_toward_focal

typography:
  weight: [500, 700] → [700, 800]  # ramps as build approaches climax
  tracking: 0                       # neutral — boldness carries intensity
  rationale: "Weight increase parallels rising anticipation"

depth:
  layers: [3, 4]
  parallax:
    early: { L1: [1.0, 1.05], L3: 0.9 }
    late:  { L1: 1.15, L2: 1.0, L3: 0.8 }

rhythm:
  grid_density: medium
  element_count: [5, 9]
  relief_zone: bottom_or_center_for_countdown

visual_metaphors:
  - Filling progress rings
  - Staircase of cards lighting up in sequence
  - Particles/icons flowing upward toward reveal mask
```

### Reveal
```
color:
  temperature: warm_neutral
  hue_range: [30, 70]         # bright yellows/oranges
  saturation: [0.7, 1.0]
  lightness: [0.6, 0.8]       # bright

background:
  mode: light | bright_gradient
  overlay_opacity: [0.05, 0.15]
  blur_px: [2, 6] → 0         # quick drop to sharp at reveal frame

spacing:
  padding_ratio: [0.07, 0.09]
  whitespace: [0.3, 0.4]      # clear space for instant legibility

focal:
  technique: unique_hue
  detail: key_element_shifts_to_only_warm_bright_hue

shapes: large_rectangles, rounded_rectangles_that_open_or_slide

typography:
  weight: [700, 900]          # headline impact
  tracking: [0, 0.01]         # slightly open for scanning
  rationale: "Bold for impact, tracking aids single-frame scanning"

depth:
  layers: 3
  parallax:
    L1_foreground: [1.1, 1.2]  # reveal motion
    L2_midground: [0.95, 1.0]
    L3_background: 0.9
  note: briefly_freeze_parallax_at_reveal_for_lock_on

rhythm:
  grid_density: coarse
  element_count: [2, 4]       # maximum clarity
  relief_zone: center_40_60_percent_width

visual_metaphors:
  - Curtain pull or card flip
  - Spotlight opening onto product/number
  - Fog/blur wiping away to expose clear figure
```

### Resolve
```
color:
  temperature: neutral_warm
  hue_range: [40, 70]         # soft golds/greens
  saturation: [0.4, 0.7]
  lightness: [0.6, 0.75]

background:
  mode: soft_light_gradient
  overlay_opacity: [0.1, 0.2]
  blur_px: [8, 14]            # gentle defocus signals closure

spacing:
  padding_ratio: [0.08, 0.12]
  whitespace: [0.35, 0.5]     # breathing room after intensity

focal:
  technique: contrast
  detail: crisp_subject_against_softened_background

shapes: stable_horizontal_rectangles, subtle_rounded_corners

typography:
  weight: [500, 600]
  tracking: [0.01, 0.02]      # slightly airy = relaxed yet confident
  rationale: "Mid-weight communicates settled confidence without aggression"

depth:
  layers: 3
  parallax:
    L1_foreground: 1.0
    L2_midground: [0.9, 1.0]
    L3_background: 0.8
  note: camera_motion_easing_to_stop

rhythm:
  grid_density: coarse
  element_count: [3, 5]
  relief_zone: lower_third_for_CTA

visual_metaphors:
  - Storm clouds parting to blue sky
  - Tangled lines straightening into simple path
  - Slider/needle settling into safe range
```

### Calm
```
color:
  temperature: cool
  hue_range: [190, 220]       # light desaturated blues/teals
  saturation: [0.25, 0.5]
  lightness: [0.6, 0.8]

background:
  mode: light | mid_tone_wash
  overlay_opacity: [0.05, 0.15]
  blur_px: [10, 20]           # soft, low-frequency

spacing:
  padding_ratio: [0.1, 0.14]
  whitespace: [0.45, 0.65]    # very open, low density

focal:
  technique: motion_contrast
  detail: slow_smooth_focal_vs_near_static_background

shapes: circles, rounded_blobs  # safety, harmony, pleasantness

typography:
  weight: [300, 400]
  tracking: [0.02, 0.04]      # light, open = elegance + low arousal
  rationale: "Light weights associated with elegance and calm"

depth:
  layers: 3
  parallax:
    L1_foreground: [1.0, 1.05]
    L2_midground: [0.95, 1.0]
    L3_background: [0.9, 0.95] # very subtle, slow

rhythm:
  grid_density: coarse
  element_count: [2, 4]
  relief_zone: central_band_for_eye_rest

visual_metaphors:
  - Floating bubbles or orbs
  - Slow waves or gentle sine curves
  - Breathing circle expanding/contracting
```

### Urgency
```
color:
  temperature: warm
  hue_range: [0, 25] | [340, 360]  # high-chroma reds/oranges
  saturation: [0.8, 1.0]
  lightness: [0.45, 0.65]

background:
  mode: dark_to_mid_gradient
  overlay_opacity: [0.2, 0.35]
  blur_px: [4, 10]            # readable but secondary

spacing:
  padding_ratio: [0.04, 0.06]
  whitespace: [0.15, 0.25]    # tight, compressed, "full" frame

focal:
  technique: motion_contrast
  detail: focal_pulses_faster_than_supporting + countdown_temporal_change

shapes: triangles, arrows_pointing_at_deadline_or_CTA

typography:
  weight: [700, 900]
  tracking: [-0.01, 0]        # dense, bold = importance + command
  rationale: "Bold weights command attention and signal critical importance"

depth:
  layers: [3, 4]
  parallax:
    L1_foreground: [1.2, 1.3]  # noticeable speed
    L2_midground: [1.0, 1.1]
    L3_background: [0.8, 0.9]

rhythm:
  grid_density: medium_to_fine
  element_count: [6, 10]
  relief_zone: small_center_or_upper_third_for_timer

visual_metaphors:
  - Countdown timer or ticking bar
  - Shrinking safe zone / frame margins closing in
  - Particles streaking past faster over time
```

### Triumph
```
color:
  temperature: warm
  hue_range: [30, 55]         # golden/orange high-chroma
  saturation: [0.7, 1.0]
  lightness: [0.55, 0.7]

background:
  mode: light_with_radial_glow
  overlay_opacity: [0.05, 0.15]
  blur_px: [6, 12]            # bokeh/confetti softly blurred

spacing:
  padding_ratio: [0.07, 0.1]
  whitespace: [0.3, 0.45]     # balanced, celebratory but not chaotic

focal:
  technique: unexpected_scale
  detail: winner_scales_up_overshoots_then_settles

shapes: upward_triangles, starbursts, arcs + circles_for_friendly_celebration

typography:
  weight: [700, 900]          # hero text
  weight_supporting: [400, 500]
  tracking: 0.01              # bold but slightly opened = expansive
  rationale: "Expansive tracking on bold type communicates confident celebration"

depth:
  layers: [3, 4]
  parallax:
    L1_foreground: [1.15, 1.25]
    L2_midground: [1.0, 1.1]
    L3_background: [0.85, 0.95] # confetti lags slightly

rhythm:
  grid_density: medium
  element_count: [5, 9]
  relief_zone: center_for_hero_text

visual_metaphors:
  - Confetti bursts behind subject
  - Trophy or medal popping in
  - Upward beams/rays emanating from center
```

### Melancholy
```
color:
  temperature: cool
  hue_range: [210, 260]       # dark desaturated blues/purples
  saturation: [0.2, 0.5]
  lightness: [0.2, 0.45]

background:
  mode: dark | vignetting_gradient
  overlay_opacity: [0.25, 0.4]
  blur_px: [12, 20]           # soft, slight grain

spacing:
  padding_ratio: [0.08, 0.12]
  whitespace: [0.35, 0.55]    # spacious but empty/lonely

focal:
  technique: unique_hue
  detail: subject_slightly_warmer_less_desaturated_but_still_muted

shapes: drooping_arcs, elongated_vertical_rectangles, soft_edge_circles

typography:
  weight: [300, 500]
  tracking: [0.01, 0.03]      # slightly lighter, more open = fragile
  rationale: "Light weights feel fragile, not assertive — sad not angry"

depth:
  layers: 3
  parallax:
    L1_foreground: [1.0, 1.1]
    L2_midground: [0.9, 1.0]
    L3_background: [0.8, 0.9] # slow, drifting

rhythm:
  grid_density: coarse
  element_count: [2, 5]
  relief_zone: off_center_lower_left_with_large_negative_space

visual_metaphors:
  - Single figure under rain
  - Fading Polaroid drifting away
  - Slow-falling particles like dust or ash
```

---

## Transition Rules Between Emotions

When scenes transition between emotions, follow these interpolation rules:

1. **HSL Interpolation**: Lerp hue/saturation/lightness over 15-20 frames
2. **Spacing**: Gradually compress or expand whitespace — never jump
3. **Parallax**: Ease parallax intensity changes over scene transitions
4. **Exception**: Shock intentionally BREAKS smooth transitions — it's the only
   emotion that can jump-cut without interpolation
5. **Build → Reveal**: Is the most common pair. Build's parameters should
   ramp toward Reveal's parameters in the final 25% of the build scene

## Anti-Rules (What NOT to Do)

- **Never mix multiple focal techniques** in one scene — pick ONE
- **Never use sharp triangles for calm** — they activate threat/alertness
- **Never use light weights for urgency** — undermines the commanded attention
- **Never exceed 6 main elements in a reveal** — clarity is the reveal's weapon
- **Never use high blur on shock backgrounds** — crispness is part of the impact
