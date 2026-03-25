# Prototype Reference Library — Scene Role Design Patterns

> **Purpose**: Machine-consumable reference for what PERFECT 360×640 HTML prototypes
> look like for each scene role in a data explainer video. The Designer agent looks up
> the scene role and applies these patterns as defaults.
>
> **Principle**: In a data explainer, the DATA is the hero, not the brand.

---

## Quick Reference: Scene Role → Key Constraints

| Role | Duration | Focal Position | Element Count | Type Scale | Hold Time |
|------|----------|---------------|---------------|------------|-----------|
| Hook | 2s | Top-third / center | 1–2 | Display/Hero | 300ms entrance, fast |
| Context | 3–5s | Center / above-center | 3–5 | Heading + Subheading | 800–1000ms |
| Build | 4–6s | Varies by data type | 4–8 | Heading + Caption | 1000–1200ms |
| Reveal | 5–7s | Dead center | 1–2 | Display | 1500–2000ms |
| Resolution | 4–5s | Center-bottom third | 1–3 | Heading + Body | 2000ms |

---

## Scene Role 1: Hook (First 2 Seconds)

**Purpose**: Capture attention before scroll. Create curiosity gap.

### Layout Pattern
- Focal point: Top-third or center
- ONE dominant element: shocking number OR visual question mark
- Supporting text: 3–5 words maximum, nothing more

### Typography Hierarchy
- Hero/Display scale (68–110px proto): The hook number or phrase
- Optional Body scale (16px proto): Single-line micro-context
- NO supporting text — curiosity gap pulls viewer to Scene 2

### Color Distribution (60-30-10)
- 60%: High-contrast solid background (not gradient — maximum clarity)
- 30%: Focal element color (maximum saturation/contrast)
- 10%: Accent for micro-details if needed

### Background Treatment
- Solid color strongly preferred over gradient
- Strong image OK with 70–80% overlay for text contrast
- NO patterns — they compete with focal number/phrase

### Element Count
- Minimum: 1 (just the hook number/phrase)
- Maximum: 2 (hook + tiny context label)
- Beyond 2 = diluted punch

### Prototype Structure
```html
<section class="hook">
  <div class="focal-number">[Shocking statistic]</div>
  <div class="micro-context">[3-word label]</div>
</section>
```

### Common Mistakes
- ❌ Too much text (explaining defeats curiosity gap)
- ❌ Multiple competing elements (no single focal point)
- ❌ Low contrast (hook must be instantly readable)
- ❌ Slow reveal (must be on-screen within 300ms)

---

## Scene Role 2: Context (Seconds 3–8)

**Purpose**: Establish problem, situation, or question. Provide comparative frame.

### Layout Pattern
- Focal point: Center or slightly above center
- 2–3 comparison points for reference framing
- Layout: Vertical stack or horizontal comparison

### Typography Hierarchy
- Heading scale (42px proto): Context headline
- Subheading scale (26px proto): 2–3 supporting data points
- Body scale (16px proto): Labels for each data point

### Color Distribution
- 60%: Background (can introduce subtle gradient for progression)
- 30%: Primary data color (introduce brand palette)
- 10%: Accent differentiating comparison points

### Background Treatment
- Gradient acceptable (light→dark suggesting depth or timeline)
- Subtle pattern OK at 10–15% opacity maximum
- Background image with 60–70% overlay if it provides context

### Element Count
- Minimum: 3 (headline + 2 comparison data points)
- Maximum: 5 (headline + 3–4 data points + labels)

### Prototype Structure
```html
<section class="context">
  <h2 class="context-headline">[Problem statement]</h2>
  <div class="comparison-group">
    <div class="data-point">
      <span class="value">[Number]</span>
      <span class="label">[What it represents]</span>
    </div>
    <div class="data-point">
      <span class="value">[Comparison number]</span>
      <span class="label">[What it represents]</span>
    </div>
  </div>
</section>
```

### Common Mistakes
- ❌ Burying the lede (most important context at bottom)
- ❌ No comparison (raw numbers need reference points)
- ❌ Too much historical detail (stay focused on present problem)
- ❌ Weak hierarchy (headline must clearly dominate supporting data)

---

## Scene Role 3: Build (Scenes 3–4, Seconds 9–20)

**Purpose**: Progressive revelation of evidence. Each Build scene adds one piece of proof.

### Layout Pattern
- Focal point: varies (center for charts, top-third for text-heavy)
- Data visualization: charts, graphs, structured data display
- Progressive: each Build scene adds to what came before

### Typography Hierarchy
- Subheading scale (26px proto): Scene label — what this evidence shows
- Heading scale (42px proto): Data values — the numbers themselves
- Caption scale (10px proto): Axis labels, data labels
- Body scale (16px proto): Annotations calling out insights

### Color Distribution
- 60%: Neutral background (data takes visual focus)
- 30%: Data viz colors (semantic: green=positive, red=negative, blue=neutral)
- 10%: Annotations and emphasis highlights

### Background Treatment
- Minimal: solid light background or very subtle gradient (5–10% shift)
- Background should recede — all attention on data visualization
- AVOID: busy patterns, high-contrast backgrounds, competing imagery

### Element Count
- Minimum: 4 (label + 3 data points in visualization)
- Maximum: 8 (label + 6 data points + annotation)

### Chart Type Selection
- **Bar chart**: Comparing categories at a glance
- **Line chart**: Showing trend over time
- **Tree map**: Hierarchical data or parts-of-whole
- **Ranking list**: Top 10, bottom 5, fastest growing
- Each type chosen deliberately to make pattern intuitive

### Prototype Structure
```html
<section class="build">
  <h3 class="scene-label">[What this data shows]</h3>
  <div class="data-viz">[Chart/graph/structured display]</div>
  <div class="annotation">[Key insight from this data]</div>
</section>
```

### Common Mistakes
- ❌ Too much data at once (progressive = step-by-step, not data dump)
- ❌ Charts without focal point (every chart needs one highlighted insight)
- ❌ No annotations (raw chart without interpretation = too much viewer effort)
- ❌ Inconsistent styling between Build scenes (maintain visual continuity)

---

## Scene Role 4: Reveal / Climax (Seconds 21–30)

**Purpose**: The "aha" moment. Maximum visual impact. Data insight becomes crystal clear.

### Layout Pattern
- Focal point: Dead center (equal margins all sides)
- ONE dominant insight: synthesis number or visual metaphor
- Maximum visual weight: largest type, highest contrast, most dynamic composition

### Typography Hierarchy
- Display scale (110px proto): The main revelation
- Subheading scale (26px proto): Brief "what this means"
- NO body text — if revelation needs explanation, it's not clear enough

### Color Distribution
- 60%: Clean background (white, black, or brand primary for maximum drama)
- 30%: Hero insight in maximum contrast color
- 10%: Minimal accent (underline or highlight only)

### Background Treatment
- Pure solid color (white, black, or brand color)
- OR radial gradient emanating from insight (spotlight effect)
- AVOID: busy backgrounds — nothing competes with the insight

### Element Count
- Minimum: 1 (just the insight)
- Maximum: 2 (insight + one-line implication)

### Motion Treatment
- Longest entrance: 400–500ms ease-in-out for weight
- Hold duration: 1500–2000ms (longest in video — let insight sink in)
- Scale animation: 80% → 100% for emphasis
- All supporting elements already on-screen before reveal

### Prototype Structure
```html
<section class="reveal">
  <div class="hero-insight">[The key takeaway]</div>
  <div class="implication">[What this means — 5 words max]</div>
</section>
```

### Common Mistakes
- ❌ Multiple competing insights (dilutes the payoff)
- ❌ Weak visual treatment (must look different from Build scenes)
- ❌ Too much explanation (three sentences = not clear enough)
- ❌ Rushed timing (this moment deserves breathing room)

---

## Scene Role 5: Resolution (Final 5 Seconds)

**Purpose**: Brand placement, CTA, or key takeaway. Clean, open, confident.

### Layout Pattern
- Focal point: Center-bottom third for branding, or center for takeaway
- Open composition: generous whitespace, minimal elements
- Logo: bottom-right corner or centered below message

### Typography Hierarchy
- Heading scale (42px proto): Takeaway or CTA
- Body scale (16px proto): Brand/source
- Logo: 32–48px height (proto)

### Color Distribution
- 60%: Clean, open background (white or very light brand color)
- 30%: CTA/takeaway in readable mid-contrast
- 10%: Logo and brand accents

### Background Treatment
- Minimal: solid color or very subtle gradient (5% value shift)
- The "breath" after climax — calming and conclusive
- If brand color as background, ensure sufficient text contrast

### Element Count
- Minimum: 1 (logo only or takeaway only)
- Maximum: 3 (logo + takeaway + CTA)

### Prototype Structure
```html
<section class="resolution">
  <div class="takeaway">[One-sentence summary or CTA]</div>
  <div class="brand">
    <img src="logo.svg" alt="Brand" class="logo" />
    <span class="source-label">[Brand name or data source]</span>
  </div>
</section>
```

### Common Mistakes
- ❌ Cramming new information (Resolution = no new data)
- ❌ Weak branding (after delivering value, claim credit clearly)
- ❌ Cluttered composition (should be the most open, breathable frame)
- ❌ No CTA (if you want action, state it: "Follow for daily data insights")

---

## Cross-Scene Continuity Rules

### Color Consistency
- Establish 3–4 brand colors in Context scene, maintain throughout
- Semantic coding (green=positive, red=negative) consistent in all data viz

### Typography Consistency
- Once Hero scale is used for hero insights, never use it for lesser elements
- Maintain role-to-scale mapping throughout entire video

### Pacing Rhythm
```
Scenes 1-2:  Fast   (2–3 seconds each)
Scenes 3-4:  Medium (4–6 seconds each)
Scene 5:     Slow   (5–7 seconds)
Scene 6:     Breath (4–5 seconds)
```

### Transition Strategy
- Hook → Context: Quick cut or minimal fade (200ms) — maintain urgency
- Context → Build: Crossfade (300ms)
- Build → Build: Match cut or data morphing (elements transform, not cut)
- Into Reveal: Dramatic pause (400ms black/white) then reveal
- Into Resolution: Gentle fade (400ms)
