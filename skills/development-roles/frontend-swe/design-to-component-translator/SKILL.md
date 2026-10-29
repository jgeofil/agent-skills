---
name: design-to-component-translator
description: >-
  Converts Figma/design specifications into production-ready UI components with accurate spacing, typography, color tokens, responsive rules, and interaction states (hover, focus, disabled, active). Generates Tailwind/shadcn code with design system tokens mapping. Use when translating "Figma to code", "design specs to components", or "implement design system".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Design-to-Component Translator

Convert design specifications into pixel-perfect, production-ready React components.

## Core Workflow

1. **Analyze design specs**: Extract spacing, colors, typography, dimensions
2. **Map to tokens**: Convert design values to design system tokens
3. **Generate structure**: Create semantic HTML structure
4. **Apply styles**: Implement Tailwind/CSS with exact measurements
5. **Add states**: Include hover, focus, active, disabled states
6. **Handle responsive**: Implement breakpoint-specific rules
7. **Ensure accessibility**: Add ARIA labels, keyboard navigation
8. **Document variants**: List all visual states and props

## Design Spec Analysis

### Extract from Figma/Design

**Spacing & Layout:**

- Padding: `p-4` (16px), `px-6` (24px horizontal)
- Margin: `m-2` (8px), `mt-4` (16px top)
- Gap: `gap-3` (12px between flex items)
- Width/Height: `w-64` (256px), `h-10` (40px)

**Typography:**

- Font family: `font-sans`, `font-mono`
- Font size: `text-sm` (14px), `text-base` (16px), `text-lg` (18px)
- Font weight: `font-normal` (400), `font-medium` (500), `font-semibold` (600)
- Line height: `leading-tight`, `leading-normal`, `leading-relaxed`
- Letter spacing: `tracking-tight`, `tracking-normal`, `tracking-wide`

**Colors:**

- Background: `bg-blue-500`, `bg-gray-100`
- Text: `text-gray-900`, `text-white`
- Border: `border-gray-300`, `border-blue-600`
- Opacity: `bg-opacity-50`, `text-opacity-75`

**Borders & Radius:**

- Border width: `border`, `border-2`, `border-t-4`
- Border radius: `rounded` (4px), `rounded-md` (6px), `rounded-lg` (8px), `rounded-full`

**Shadows:**

- `shadow-sm`, `shadow`, `shadow-md`, `shadow-lg`, `shadow-xl`

## Design Token Mapping

### Create Token System

```typescript
// tokens.ts
export const tokens = {
  colors: {
    primary: {
      50: "#eff6ff",
      100: "#dbeafe",
      500: "#3b82f6",
      600: "#2563eb",
      700: "#1d4ed8",
    },
    gray: {
      100: "#f3f4f6",
      300: "#d1d5db",
      500: "#6b7280",
      700: "#374151",
      900: "#111827",
    },
  },
  spacing: {
    xs: "0.25rem", // 4px
    sm: "0.5rem", // 8px
    md: "1rem", // 16px
    lg: "1.5rem", // 24px
    xl: "2rem", // 32px
  },
  fontSize: {
    xs: ["0.75rem", { lineHeight: "1rem" }],
    sm: ["0.875rem", { lineHeight: "1.25rem" }],
    base: ["1rem", { lineHeight: "1.5rem" }],
    lg: ["1.125rem", { lineHeight: "1.75rem" }],
    xl: ["1.25rem", { lineHeight: "1.75rem" }],
  },
  borderRadius: {
    sm: "0.25rem", // 4px
    md: "0.375rem", // 6px
    lg: "0.5rem", // 8px
    full: "9999px",
  },
  shadows: {
    sm: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
    md: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
    lg: "0 10px 15px -3px rgb(0 0 0 / 0.1)",
  },
};
```

### Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
      },
      spacing: {
        18: "4.5rem",
        88: "22rem",
      },
      fontSize: {
        "2xs": "0.625rem",
      },
    },
  },
};
```

## Best Practices

1. **Measure twice**: Verify all measurements match Figma exactly
2. **Use design tokens**: Map to tokens, not hardcoded values
3. **All states**: Include hover, focus, active, disabled, error
4. **Responsive**: Implement all breakpoints from design
5. **Accessibility**: Add ARIA where Figma shows states
6. **Animations**: Match transition timings to design
7. **Dark mode**: If designs exist, implement with class variants
8. **Component variants**: Create reusable variant props
9. **Documentation**: Note any deviations from design
10. **Review**: Get designer approval on implementation

## Output Checklist

Every design-to-component translation should include:

- [ ] Exact spacing matching Figma measurements
- [ ] Typography scales and weights
- [ ] All color values from design system
- [ ] Border radius and shadows
- [ ] Hover state styling
- [ ] Focus state styling (accessible)
- [ ] Active/pressed state styling
- [ ] Disabled state styling
- [ ] Responsive breakpoint rules
- [ ] Design token mapping documented
- [ ] Accessibility attributes
- [ ] Component variants for states


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

