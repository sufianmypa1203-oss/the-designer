# Design System Token Architecture — Video Motion Graphics

> **Purpose**: Single source of truth for all design tokens consumed by the Designer agent.
> Three-tier architecture: Primitive → Semantic → Component.
> Adapted from Linear, Vercel, Stripe, and Apple HIG for video context.
>
> **Rule**: Components reference semantic tokens only. Never reference primitives directly.

---

## Architecture Overview

```
Primitive Tokens     →  Semantic Tokens      →  Component Tokens
(raw values)            (purpose-driven)         (deviations only)
blue.500                color.text.accent        button.text: color.text.inverse
neutral.900             color.background.inverse
```

- **Primitives**: Raw values. Private — never used directly in specs.
- **Semantics**: Purpose-driven names. Public API — stable interface for specs.
- **Components**: Only created when a component deviates from semantic defaults.

---

## Color Tokens

### Primitives

```json
{
  "color": {
    "neutral": {
      "0": "#FFFFFF",
      "50": "#FAFAFA",
      "100": "#F5F5F5",
      "200": "#E5E5E5",
      "300": "#D4D4D4",
      "400": "#A3A3A3",
      "500": "#737373",
      "600": "#525252",
      "700": "#404040",
      "800": "#262626",
      "900": "#171717",
      "1000": "#000000"
    },
    "blue": {
      "50": "#EFF6FF", "100": "#DBEAFE", "200": "#BFDBFE",
      "300": "#93C5FD", "400": "#60A5FA", "500": "#3B82F6",
      "600": "#2563EB", "700": "#1D4ED8", "800": "#1E40AF",
      "900": "#1E3A8A"
    },
    "data": {
      "positive": { "50": "#ECFDF5", "500": "#10B981", "700": "#047857" },
      "negative": { "50": "#FEF2F2", "500": "#EF4444", "700": "#B91C1C" },
      "neutral":  { "50": "#F0F9FF", "500": "#0EA5E9", "700": "#0369A1" },
      "warning":  { "50": "#FFFBEB", "500": "#F59E0B", "700": "#B45309" }
    }
  }
}
```

**Video-specific**: Limited palette vs web. Recommended: 1 primary + 1 accent + neutral + 4 semantic data colors. Fast-moving scenes = cognitive load, fewer colors = better comprehension.

### Semantic Color Tokens

```json
{
  "color": {
    "background": {
      "primary": "neutral.0",
      "secondary": "neutral.50",
      "tertiary": "neutral.100",
      "inverse": "neutral.900"
    },
    "surface": {
      "default": "neutral.0",
      "overlay": "neutral.50",
      "elevated": "neutral.100",
      "sunken": "neutral.200"
    },
    "text": {
      "default": "neutral.900",
      "secondary": "neutral.600",
      "tertiary": "neutral.400",
      "inverse": "neutral.0",
      "accent": "blue.600"
    },
    "action": {
      "primary": "blue.600",
      "primaryHover": "blue.700",
      "secondary": "neutral.700"
    },
    "feedback": {
      "success": "data.positive.500",
      "error": "data.negative.500",
      "warning": "data.warning.500",
      "info": "data.neutral.500"
    },
    "dataVisualization": {
      "series1": "blue.500",
      "series2": "data.positive.500",
      "series3": "data.warning.500",
      "series4": "data.neutral.500",
      "series5": "neutral.500"
    }
  }
}
```

### Light/Dark Mode

```json
{
  "color": {
    "mode": {
      "light": {
        "background": "neutral.0",
        "text": "neutral.900",
        "surface": "neutral.50"
      },
      "dark": {
        "background": "neutral.900",
        "text": "neutral.0",
        "surface": "neutral.800"
      }
    }
  }
}
```

Video scenes toggle between modes. Light = better for dense data. Dark = dramatic reveals, emphasis.

---

## Typography Tokens

### Font Families

```json
{
  "typography": {
    "fontFamily": {
      "primary": {
        "name": "Inter",
        "fallback": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "usage": "UI text, data labels, body content"
      },
      "display": {
        "name": "Lexend",
        "fallback": "'Helvetica Neue', Arial, sans-serif",
        "usage": "Headlines, hero numbers, emphasis"
      },
      "monospace": {
        "name": "JetBrains Mono",
        "fallback": "'Courier New', Courier, monospace",
        "usage": "Code, data tables, technical content"
      }
    }
  }
}
```

**Video font recommendations**:
- Primary reading: Inter, Lexend (optimized readability)
- Impact headlines: Gotham, Bebas Neue (geometric, clean)
- Data display: Morro, UniSans (blocky, animates well)
- Motion graphics: Fonts with straight strokes + perfect circles (no wobble)

### Type Scale (Golden Ratio 1.618)

```json
{
  "typography": {
    "size": {
      "caption":    { "prototype": "10px",  "canvas": "30px"  },
      "body":       { "prototype": "16px",  "canvas": "48px"  },
      "subheading": { "prototype": "26px",  "canvas": "78px"  },
      "heading":    { "prototype": "42px",  "canvas": "126px" },
      "hero":       { "prototype": "68px",  "canvas": "204px" },
      "display":    { "prototype": "110px", "canvas": "330px" }
    },
    "lineHeight": {
      "caption":    { "prototype": "15px",  "canvas": "45px",  "ratio": 1.5  },
      "body":       { "prototype": "24px",  "canvas": "72px",  "ratio": 1.5  },
      "subheading": { "prototype": "36px",  "canvas": "108px", "ratio": 1.38 },
      "heading":    { "prototype": "54px",  "canvas": "162px", "ratio": 1.29 },
      "hero":       { "prototype": "84px",  "canvas": "252px", "ratio": 1.24 },
      "display":    { "prototype": "126px", "canvas": "378px", "ratio": 1.15 }
    },
    "fontWeight": {
      "light": 300,
      "regular": 400,
      "medium": 500,
      "semibold": 600,
      "bold": 700,
      "extrabold": 800
    },
    "letterSpacing": {
      "tight":  "-0.025em",
      "snug":   "-0.015em",
      "normal": "0em",
      "wide":   "0.01em"
    }
  }
}
```

**Weight mapping**: Display/Hero → bold/extrabold. Heading → semibold/bold. Subheading → medium/semibold. Body → regular. Caption → regular/light.

**Spacing mapping**: Display/Hero → tight. Heading → snug. Body and below → normal to wide.

---

## Spacing Tokens (8px Base Grid)

```json
{
  "spacing": {
    "xxxs":    { "prototype": "2px",   "canvas": "6px"   },
    "xxs":     { "prototype": "4px",   "canvas": "12px"  },
    "xs":      { "prototype": "8px",   "canvas": "24px"  },
    "sm":      { "prototype": "12px",  "canvas": "36px"  },
    "md":      { "prototype": "16px",  "canvas": "48px"  },
    "lg":      { "prototype": "24px",  "canvas": "72px"  },
    "xl":      { "prototype": "32px",  "canvas": "96px"  },
    "xxl":     { "prototype": "48px",  "canvas": "144px" },
    "xxxl":    { "prototype": "64px",  "canvas": "192px" },
    "massive": { "prototype": "96px",  "canvas": "288px" },
    "ultra":   { "prototype": "128px", "canvas": "384px" }
  }
}
```

### Semantic Spacing

```json
{
  "spacing": {
    "semantic": {
      "elementGap":     "xs",
      "componentPadding": "md",
      "sectionGap":     "xl",
      "sceneMargin":    "xxxl",
      "safeZoneTop":    "ultra",
      "safeZoneBottom":  "massive",
      "safeZoneLeft":   "lg",
      "safeZoneRight":  "xxl"
    }
  }
}
```

---

## Border Radius Tokens

```json
{
  "borderRadius": {
    "none": { "prototype": "0px",  "canvas": "0px"  },
    "xs":   { "prototype": "2px",  "canvas": "6px"  },
    "sm":   { "prototype": "4px",  "canvas": "12px" },
    "md":   { "prototype": "8px",  "canvas": "24px" },
    "lg":   { "prototype": "12px", "canvas": "36px" },
    "xl":   { "prototype": "16px", "canvas": "48px" },
    "xxl":  { "prototype": "24px", "canvas": "72px" },
    "pill": "999px",
    "circle": "50%"
  }
}
```

**Brand personality**: Sharp (0–4px) = professional/strict. Moderate (8–12px) = friendly/modern. Soft (16–24px) = playful/casual.

---

## Motion Tokens

> These are for the Designer to SUGGEST in specs, not implement.

### Duration

```json
{
  "motion": {
    "duration": {
      "instant":   "100ms",
      "quick":     "200ms",
      "standard":  "300ms",
      "emphasis":  "400ms",
      "dramatic":  "500ms"
    }
  }
}
```

### Easing

```json
{
  "motion": {
    "easing": {
      "linear":    "cubic-bezier(0, 0, 1, 1)",
      "easeIn":    "cubic-bezier(0.42, 0, 1, 1)",
      "easeOut":   "cubic-bezier(0, 0, 0.58, 1)",
      "easeInOut": "cubic-bezier(0.42, 0, 0.58, 1)",
      "sharp":     "cubic-bezier(0.4, 0, 0.6, 1)"
    }
  }
}
```

**Default**: easeOut for 80% of animations.

### Stagger

```json
{
  "motion": {
    "stagger": {
      "minimal":     "50ms",
      "standard":    "80ms",
      "pronounced":  "120ms",
      "dramatic":    "200ms"
    }
  }
}
```

### Hold Duration

```json
{
  "motion": {
    "hold": {
      "label":      "800ms",
      "text":       "1000ms",
      "number":     "1200ms",
      "heroNumber": "1500ms",
      "transition": "300ms"
    }
  }
}
```

### Entrance by Priority

```json
{
  "motion": {
    "entrance": {
      "hero":       { "duration": "500ms", "easing": "easeInOut", "delay": "0ms"   },
      "supporting": { "duration": "300ms", "easing": "easeOut",   "delay": "100ms" },
      "background": { "duration": "400ms", "easing": "easeOut",   "delay": "0ms"   }
    }
  }
}
```

---

## Elevation / Depth Tokens

### Shadow Scale

```json
{
  "elevation": {
    "shadow": {
      "none": "none",
      "sm": { "prototype": "0 2px 4px rgba(0,0,0,0.1)",    "canvas": "0 6px 12px rgba(0,0,0,0.1)"   },
      "md": { "prototype": "0 4px 8px rgba(0,0,0,0.12)",   "canvas": "0 12px 24px rgba(0,0,0,0.12)" },
      "lg": { "prototype": "0 8px 16px rgba(0,0,0,0.14)",  "canvas": "0 24px 48px rgba(0,0,0,0.14)" },
      "xl": { "prototype": "0 16px 32px rgba(0,0,0,0.16)", "canvas": "0 48px 96px rgba(0,0,0,0.16)" }
    }
  }
}
```

### Blur for Depth

```json
{
  "elevation": {
    "blur": {
      "background": { "prototype": "8px", "canvas": "24px" },
      "midground":  { "prototype": "4px", "canvas": "12px" },
      "foreground": { "prototype": "0px", "canvas": "0px"  }
    }
  }
}
```

### Layer Depth (Z-axis)

```json
{
  "elevation": {
    "layerDepth": {
      "farBackground":  "-2000",
      "background":     "-1000",
      "midground":      "0",
      "foreground":     "1000",
      "nearForeground": "2000"
    }
  }
}
```

### Scale for Depth Perception

```json
{
  "elevation": {
    "scaleForDepth": {
      "background": "0.85",
      "midground":  "1.0",
      "foreground": "1.15"
    }
  }
}
```

---

## Why This Architecture Works for Video

1. **Dual sizing eliminates calculation errors** — every token has prototype + canvas values
2. **Semantic layer provides flexibility** — brand pivot only changes primitive-to-semantic mapping
3. **Motion tokens guide, don't constrain** — Designer suggests, Builder implements
4. **Video-specific concerns baked in** — safe zones, hold durations, layer depth for parallax
5. **Limited palette reduces cognitive load** — scenes move fast, complexity costs comprehension

## Maintenance Rules

- **Primitives are private** — never reference directly in component specs
- **Semantics are public API** — stable interface for all specs
- **Component tokens only for deviations** — don't create unless component must deviate from semantic default
