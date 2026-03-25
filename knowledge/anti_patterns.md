# Anti-Pattern Library — Video Design Quality Rejection Criteria

> **Purpose**: Machine-consumable rejection library. When the Designer agent or its LLM
> evaluator reviews a design spec, it checks against these anti-patterns. Any match
> triggers a rejection with a specific fix prescription.
>
> **Quality bar**: Professional studios Buck, Ordinary Folk, Gunner, and Tendril.

## How to Use This File

1. After generating a visual design spec, run each anti-pattern's detection heuristic
2. Any match = REJECT with the corresponding fix prescription
3. Fix prescriptions are specific — apply them directly, don't improvise
4. A single scene can trigger multiple anti-patterns — fix all before re-evaluation

---

## Quick Reference: Anti-Pattern → Detection Signal

| Anti-Pattern | Category | Key Signal | Severity |
|-------------|----------|-----------|----------|
| Template transitions | CapCut Look | Homogeneous timing curves | CRITICAL |
| Flat depth | CapCut Look | All elements on one z-plane | CRITICAL |
| Decorative gradients | CapCut Look | Gradient with no hierarchy purpose | HIGH |
| Uniform motion | PowerPoint+Springs | All elements same easing/duration | CRITICAL |
| No type hierarchy | PowerPoint+Springs | Font size CV < 0.3 | CRITICAL |
| Linear motion | PowerPoint+Springs | Equidistant keyframes | HIGH |
| Inverted focal weight | Decoration vs Comm | Non-focal moves more than focal | CRITICAL |
| Background competition | Decoration vs Comm | BG motion > 30% of FG motion | HIGH |
| Unjustified effects | Decoration vs Comm | Effects not connected to focal/data | HIGH |
| Static dead time | Dead Frames | No motion + low complexity > 800ms | CRITICAL |
| Constant velocity | Dead Frames | Keyframe spacing CV < 0.15 | HIGH |
| Timing gaps | Dead Frames | >200ms gap with no visual interest | HIGH |
| Flat hierarchy | Broken Hierarchy | Unimodal font size distribution | CRITICAL |
| No entry point | Broken Hierarchy | No clear saliency peak | CRITICAL |
| Weight-importance mismatch | Broken Hierarchy | Correlation < 0.6 | HIGH |

---

## Category 1: "The CapCut Look"

### What It Looks Like
- Overused transition presets (glitch flash, spiral, rocker, explosion)
- Pre-made animations applied without customization
- Flat compositions lacking depth layering or parallax
- Generic gradient fills applied decoratively without strategic purpose
- Everything moves the same way with the same timing

### Root Cause
**Convenience over craft.** Template workflows encourage pattern replication over
intentional design. No understanding of depth layering, parallax, or z-space.

### Detection Heuristics
```
check_capcut_look:
  1. transition_fingerprinting:
     - Match timing curves against known preset signatures
     - Flag if transition pattern matches any CapCut template library entry

  2. homogeneity_scoring:
     - Calculate std_dev of: easing curves, durations, movement patterns
     - REJECT if std_dev < threshold (all elements behave identically)

  3. depth_analysis:
     - Count distinct z-depth planes used
     - REJECT if all elements on same focal plane (no parallax or scale variation)

  4. gradient_purposelessness:
     - For each gradient: does direction reinforce hierarchy or encode data?
     - REJECT if gradient has no connection to visual hierarchy or data relationships
```

### Fix Prescription
1. **Replace with intentional motion** — every transition must serve the narrative
2. **Build 3+ depth layers** — background (slow), midground (standard), foreground (fast)
3. **Custom easing per element** — heavy objects ease slowly, light objects snap quickly
4. **Remove gradients unless functional** — must communicate rank, progression, or spatial relationship

---

## Category 2: "PowerPoint with Springs"

### What It Looks Like
- Motion applied to flat, lifeless layouts with no visual hierarchy
- All text same size and weight
- Decorative animations with no communicative purpose
- Multiple conflicting effects on same composition
- Mechanical linear motion that never accelerates or decelerates

### Root Cause
**Misunderstanding animation's purpose.** Animation treated as decoration rather than
attention management. Default easing habits. No hierarchy foundation — if a frame
looks bad paused, motion won't save it.

### Detection Heuristics
```
check_powerpoint_springs:
  1. typography_homogeneity:
     - Measure font size/weight variation across all text elements
     - REJECT if coefficient_of_variation < 0.3
     - Professional: 3-5 distinct type sizes with clear roles

  2. linear_motion_detection:
     - Analyze keyframe spacing in animation curves
     - REJECT if frames are equidistant (constant velocity)
     - Natural motion requires: slow in → fast middle → slow out

  3. purpose_free_animation_count:
     - Count animated elements that are NOT focal points
     - Count animated elements that do NOT guide attention toward focal
     - REJECT if > 30% of animations serve neither role

  4. multi_effect_stacking:
     - Count distinct transition types per scene
     - REJECT if > 2 different transition types in one scene
```

### Fix Prescription
1. **Establish hierarchy BEFORE animating** — size, contrast, weight, position must create
   clear visual weight order in the static frame
2. **Apply intentional easing** — ease-out for 80% of animations, ease-in only for exits
3. **Animate with purpose** — motion without intention is showing off, not communicating
4. **Use visual metaphors** — text-heavy content needs charts, icons, or imagery

---

## Category 3: "Decoration vs Communication"

### What It Looks Like
- Particles, glows, shadows applied with no information purpose
- Excessive animation on non-focal elements
- Background elements competing with foreground content
- Multiple elements demanding attention simultaneously
- Technically complex but communicatively empty

### Root Cause
**Skill display over communication.** Effects added because designer knows how to
create them, not because they serve content. No focal point discipline — professional
work subordinates everything to support one hero element per frame.

### Detection Heuristics
```
check_decoration_vs_communication:
  1. focal_point_analysis:
     - Identify semantic focal point (titles > labels, data values > axis marks)
     - Measure motion intensity: distance, rotation, scale change
     - REJECT if non-focal elements have higher motion intensity than focal

  2. background_motion_scoring:
     - Measure background layer animation intensity
     - REJECT if background_motion > 0.3 × foreground_motion

  3. effect_purposefulness:
     - For each glow, shadow, particle: does it guide to focal or encode data?
     - REJECT if effect has no connection to focal points or data architecture

  4. simultaneous_motion_count:
     - At any frame, count elements actively animating
     - REJECT if > 4 elements move simultaneously without choreography
     - Professional: 1-3 elements with clear primary/secondary motion
```

### Fix Prescription
1. **One hero per frame** — size, contrast, motion, position all reinforce which element matters
2. **Animate foreground, stabilize background** — BG motion intensity ≤ 20-30% of FG
3. **Justify every effect** — if it doesn't guide eye or encode information, remove it
4. **Choreograph attention** — stagger delays guide viewer focus in intended processing order

---

## Category 4: "Dead Frames"

### What It Looks Like
- Nothing moves AND nothing has visual interest to hold attention
- Empty transitions between scenes (dead air)
- Static compositions held too long for their visual complexity
- Constant-speed motion with no velocity variation
- Rigid straight transitions with no arcs or curves

### Root Cause
**Ignoring pause frames.** No consideration for visual interest during static moments.
**No motion variation.** Constant speed feels artificial — nothing in nature moves at
perfectly steady velocity. **Poor timing coordination.** Gaps between animations.

### Detection Heuristics
```
check_dead_frames:
  1. static_moment_analysis:
     - Identify frames where no elements animate
     - Calculate visual complexity: color variation, element count, detail density
     - REJECT if complexity_score < threshold AND static_duration > 800ms

  2. velocity_variation:
     - Analyze keyframe spacing across animated properties
     - Calculate coefficient_of_variation for inter-keyframe distances
     - REJECT if CV < 0.15 (nearly constant speed)

  3. arc_analysis:
     - For motion paths, fit curves to trajectory points
     - Measure deviation from straight-line interpolation
     - REJECT if deviation < 5% (rigid straight movement)

  4. timing_gap_detection:
     - Build timeline of all animation start/end times
     - Identify gaps > 200ms where no animation is active
     - REJECT if gap has no static visual interest filling it
```

### Fix Prescription
1. **Vary keyframe spacing** — closer together at start/end (slow in/out), farther apart in middle
2. **Use arcs in motion paths** — offset midpoints 5-10% perpendicular to direct path
3. **Design for pause frames** — every static moment needs: high-contrast focal, clear hierarchy,
   compositional balance, or dynamic typography with visual presence
4. **Coordinate timing overlap** — as one animation ends, start next 50-150ms before
5. **Match hold to content** — numbers: 1000-1500ms, labels: 800-1000ms, transitions: 200-300ms

---

## Category 5: "Broken Hierarchy"

### What It Looks Like
- Multiple elements competing for attention with no clear winner
- No obvious entry point for viewer's eye (Z/F pattern violated)
- Typography all same weight and scale — no separation
- Elements sized, colored, positioned as though equally important

### Root Cause
**Equal treatment of unequal elements.** No distinction between primary/secondary/tertiary.
**No intentional focus choreography.** Arrangement based on aesthetics rather than
information hierarchy. **Fighting perceptual defaults** — human eye follows:
large → small, high-contrast → low-contrast, moving → static, foreground → background.

### Detection Heuristics
```
check_broken_hierarchy:
  1. scale_analysis:
     - Measure font sizes across all text elements
     - Calculate distribution statistics
     - REJECT if unimodal or bimodal with < 1.25× ratio between levels
     - Professional: multimodal with 3-5 distinct clusters

  2. contrast_measurement:
     - Calculate luminance contrast of each element vs background
     - Professional tiers: focal ≥ 7:1, supporting ≥ 4.5:1, background ≥ 3:1
     - REJECT if focal/supporting contrast ratio < 2:1

  3. attention_competition:
     - Model saliency map (size, color, contrast, position, motion)
     - Identify high-saliency regions of similar intensity
     - REJECT if > 2 equally-salient regions exist

  4. entry_point_detection:
     - Check composition for clear entry using Z-pattern (top-left) or F-pattern
     - REJECT if highest-saliency element is not at expected entry point
     - REJECT if no clear entry point exists (scattered attention)

  5. weight_importance_correlation:
     - Rank elements by semantic importance (title > label > value)
     - Rank elements by visual weight (size × contrast × saturation)
     - Calculate correlation coefficient
     - REJECT if correlation < 0.6
```

### Fix Prescription
1. **Size hierarchy** — golden ratio (1.618) or major third (1.25) between adjacent levels
2. **Contrast hierarchy** — focal gets highest contrast, decreasing for supporting elements
3. **Weight hierarchy** — bold for primary, medium for secondary, light for tertiary
4. **Color hierarchy** — highest saturation reserved for focal points only
5. **Position hierarchy** — most important element in top third or center
6. **Motion hierarchy** — primary first, secondary 80-120ms later, tertiary last
7. **Design entry point** — place hero where eye naturally enters (top-left for western readers)

---

## Cross-Pattern Rules

1. **A single scene can fail multiple categories** — check all 5 independently
2. **Static frame test**: If a composition looks bad when paused, motion cannot save it
3. **Focal point rule**: Every frame must have exactly ONE most-important element
4. **Motion budget**: Only 1-3 elements should animate simultaneously
5. **Hierarchy is continuous** — not binary. Each element gets exactly the attention its
   role deserves, fine-tuned via size + contrast + weight + color + position + timing
