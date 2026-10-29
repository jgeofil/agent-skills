---
name: tailwind-gradient-builder
description: >-
  Creates modern CSS gradients using Tailwind CSS including linear, radial, conic, mesh gradients, animated gradients, glassmorphism, and gradient text effects. Use when users request "gradient background", "tailwind gradient", "modern gradient", "mesh gradient", or "animated gradient".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Tailwind Gradient Builder

Create stunning modern gradients with Tailwind CSS for backgrounds, text, borders, and animations.

## Core Workflow

1. **Choose gradient type**: Linear, radial, conic, or mesh
2. **Select color palette**: Define color stops and positions
3. **Add direction/angle**: Configure gradient orientation
4. **Apply effects**: Blur, animation, glassmorphism
5. **Optimize**: Ensure performance and accessibility

## Basic Linear Gradients

### Simple Two-Color Gradient

```html
<!-- Left to Right -->
<div class="bg-gradient-to-r from-blue-500 to-purple-600"></div>

<!-- Top to Bottom -->
<div class="bg-gradient-to-b from-cyan-400 to-blue-600"></div>

<!-- Diagonal -->
<div class="bg-gradient-to-br from-pink-500 to-orange-400"></div>
```

### Direction Classes

| Class | Direction |
|-------|-----------|
| `bg-gradient-to-t` | Bottom to Top |
| `bg-gradient-to-tr` | Bottom-left to Top-right |
| `bg-gradient-to-r` | Left to Right |
| `bg-gradient-to-br` | Top-left to Bottom-right |
| `bg-gradient-to-b` | Top to Bottom |
| `bg-gradient-to-bl` | Top-right to Bottom-left |
| `bg-gradient-to-l` | Right to Left |
| `bg-gradient-to-tl` | Bottom-right to Top-left |

### Three-Color Gradients

```html
<!-- With via for middle color -->
<div class="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>

<!-- Sunset gradient -->
<div class="bg-gradient-to-r from-orange-500 via-red-500 to-pink-500"></div>

<!-- Ocean gradient -->
<div class="bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500"></div>
```

## Modern Gradient Presets

### Aurora Borealis

```html
<div class="bg-gradient-to-r from-green-300 via-blue-500 to-purple-600"></div>
```

### Sunset Vibes

```html
<div class="bg-gradient-to-r from-amber-200 via-rose-400 to-violet-500"></div>
```

### Neon Glow

```html
<div class="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500"></div>
```

### Forest Mist

```html
<div class="bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-600"></div>
```

### Midnight City

```html
<div class="bg-gradient-to-b from-gray-900 via-purple-900 to-violet-600"></div>
```

### Peach Sunset

```html
<div class="bg-gradient-to-r from-rose-100 via-pink-300 to-orange-200"></div>
```

## Best Practices

1. **Maintain contrast**: Ensure text is readable over gradients
2. **Consistent palette**: Use colors from your design system
3. **Subtle animations**: Avoid distracting motion
4. **Fallback colors**: Provide solid color fallback
5. **Test in dark mode**: Gradients should work in both themes
6. **Accessibility**: Check contrast ratios for overlaid text

## Output Checklist

Every gradient implementation should include:

- [ ] Appropriate gradient type for use case
- [ ] Colors from design system palette
- [ ] Dark mode variant if applicable
- [ ] Animation config added to tailwind.config.js
- [ ] Performance optimization for animated gradients
- [ ] Fallback for older browsers
- [ ] Text contrast verification
- [ ] Mobile device testing


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

