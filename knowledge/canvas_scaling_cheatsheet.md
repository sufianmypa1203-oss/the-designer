# Canvas Scaling Cheatsheet — 360×640 → 1080×1920

> **Purpose**: Zero-calculation lookup tables. All values pre-computed for ×3 scaling.
> The Designer agent NEVER multiplies — it looks up the canvas value directly.
>
> **Rule**: Prototype (360×640) × 3 = Canvas (1080×1920). Every table below has both.

---

## Typography Scale (Golden Ratio 1.618, base 16px)

| Role | Proto Size | Canvas Size | Line Height (P) | Line Height (C) | Letter Spacing | Max Chars/Line |
|------|-----------|-------------|-----------------|-----------------|---------------|----------------|
| Caption | 10px | 30px | 15px | 45px | 0.01em | 45-55 |
| Body | 16px | 48px | 24px | 72px | 0em | 40-50 |
| Subheading | 26px | 78px | 36px | 108px | -0.01em | 30-40 |
| Heading | 42px | 126px | 54px | 162px | -0.015em | 20-30 |
| Hero | 68px | 204px | 84px | 252px | -0.02em | 15-25 |
| Display | 110px | 330px | 126px | 378px | -0.025em | 10-15 |

**Calculation basis**: Each level = previous × 1.618. Line height = size × 1.5.
Letter spacing becomes negative at larger sizes for optical balance.

**Role usage**:
- **Caption**: Labels, annotations, fine print
- **Body**: Primary reading text (use sparingly in video — prefer larger)
- **Subheading**: Scene context, supporting info
- **Heading**: Section titles, key phrases
- **Hero**: Primary message per scene (most common for data explainers)
- **Display**: Opening titles, climactic reveals

---

## Spacing System (8px Base Grid)

| Token | Proto (px) | Canvas (×3) | When to Use |
|-------|-----------|-------------|-------------|
| Hairline | 2 | 6 | Icon padding, minimal separation |
| Tight | 4 | 12 | Compact spacing in dense UI |
| Small | 8 | 24 | Gaps inside components, related elements |
| Default | 16 | 48 | Standard element spacing |
| Medium | 24 | 72 | Between component groups |
| Large | 32 | 96 | Between sections |
| XL | 48 | 144 | Major section breaks |
| Huge | 64 | 192 | Scene-level spacing |
| Massive | 96 | 288 | Safe zone margins |
| Ultra | 128 | 384 | Top/bottom safe zones |

**Rules**: Use multiples of 8px for all dimensions. 4px sub-grid for fine adjustments.

---

## Safe Zones (1080×1920 Canvas)

| Zone | Canvas (px) | Proto Equiv (÷3) | Notes |
|------|------------|-------------------|-------|
| Top margin | 108–380 | 36–127 | Keep important content below 380px |
| Bottom margin | 320–380 | 107–127 | Keep important content above this from bottom |
| Left padding | 60 | 20 | Content inset from left edge |
| Right padding | 120 | 40 | Content inset from right (profile icons) |
| Text safe zone | 1080×1350 | 360×450 | Guaranteed visible area (~4:5 ratio) |

**Platform variations**:
- Instagram Reels: 108px top, 320px bottom
- YouTube Shorts: 380px top, 380px bottom (most restrictive)
- TikTok: Similar to Instagram
- LinkedIn: 108px top, 320px bottom

**Safe content area**: center important content in 540–1540px vertical range (180–513px proto).

---

## Common Element Sizes

### Icons

| Size | Proto | Canvas | Usage |
|------|-------|--------|-------|
| Small | 16px | 48px | Inline with body text, compact indicators |
| Medium | 24px | 72px | Standard UI icons, list bullets |
| Large | 32px | 96px | Feature icons, primary actions |
| XL | 48px | 144px | Hero icons, focal graphics |

### Buttons

| Property | Proto | Canvas | Notes |
|----------|-------|--------|-------|
| Height | 40px | 120px | Standard |
| Height (small) | 32px | 96px | Compact |
| Height (large) | 48px | 144px | Prominent CTA |
| H-Padding | 16px | 48px | Internal text padding |
| V-Padding | 8px | 24px | Top/bottom padding |
| Border radius | 8px | 24px | Rounded corners |

### Cards

| Property | Proto | Canvas | Notes |
|----------|-------|--------|-------|
| Min height | 120px | 360px | Smallest functional card |
| Standard height | 200px | 600px | Common card size |
| Padding | 16px | 48px | Internal content padding |
| Gap | 16px | 48px | Between cards in grid |
| Border radius | 12px | 36px | Corner rounding |

### Logo Placement Zones

| Position | Proto Coords | Canvas Coords | Notes |
|----------|-------------|---------------|-------|
| Top-left | (16, 16) | (48, 48) | Safe from platform UI |
| Top-right | (344, 16) | (1032, 48) | Account for right padding |
| Bottom-right | (344, 624) | (1032, 1872) | Closing frame standard |
| Center-bottom | (180, 600) | (540, 1800) | Centered branding |

### Data Visualization Elements

| Element | Proto | Canvas | Notes |
|---------|-------|--------|-------|
| Bar height (thin) | 8px | 24px | Progress indicator |
| Bar height (chunky) | 16px | 48px | Prominent data bar |
| Gauge stroke | 12px | 36px | Circular progress |
| Dot (scatter) | 6px | 18px | Small data point |
| Dot (featured) | 12px | 36px | Emphasized data point |

---

## Border Radius Scale

| Token | Proto | Canvas | When to Use |
|-------|-------|--------|-------------|
| None | 0px | 0px | Sharp corners, technical/strict |
| Hairline | 2px | 6px | Subtle softening |
| Small | 4px | 12px | Standard UI components |
| Medium | 8px | 24px | Cards, containers |
| Large | 12px | 36px | Feature panels |
| XL | 16px | 48px | Hero cards, major sections |
| Huge | 24px | 72px | Playful/casual aesthetic |
| Pill | 999px | 999px | Fully rounded ends |
| Circle | 50% | 50% | Avatars, badges |

**Personality mapping**:
- Subtle (2–4px proto): Professional, technical, strict
- Medium (8–12px proto): Friendly, modern, approachable
- Large (16–24px proto): Playful, casual, consumer-facing

---

## Motion Duration Reference

| Action Type | Duration | Easing | Usage |
|------------|----------|--------|-------|
| Micro | 100–150ms | ease-out | Hover states, subtle feedback |
| Quick | 200–250ms | ease-out | Standard transitions |
| Standard | 300–350ms | ease-out | Most content reveals |
| Emphasis | 400–500ms | ease-in-out | Hero reveals, important moments |
| Stagger delay | 80–120ms | n/a | Between grouped elements |
| Hold (text) | 800–1000ms | n/a | Time to read text |
| Hold (numbers) | 1000–1500ms | n/a | Numbers need longer processing |

**Easing defaults**:
- **ease-out** (80% of animations): Starts fast, ends slow. Feels responsive.
- **ease-in**: Starts slow, ends fast. Only for elements leaving screen.
- **ease-in-out**: Smooth, organic. Hero moments only.
- **linear**: AVOID — feels mechanical.
