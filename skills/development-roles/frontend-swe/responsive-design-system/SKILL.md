---
name: responsive-design-system
description: >-
  Implements responsive design systems with mobile-first breakpoints, container queries, fluid typography, and adaptive layouts using Tailwind CSS. Use when users request "responsive design", "mobile-first", "breakpoints", "fluid typography", or "adaptive layout".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Responsive Design System

Build adaptive, mobile-first layouts with modern CSS features and Tailwind.

## Core Workflow

1. **Define breakpoints**: Establish responsive breakpoint system
2. **Set fluid typography**: Clamp-based responsive fonts
3. **Create layout grid**: Responsive grid system
4. **Add container queries**: Component-level responsiveness
5. **Build responsive components**: Adaptive patterns
6. **Test across devices**: Verify on all viewports

## Breakpoint System

### Tailwind Default Breakpoints

| Breakpoint | Min Width | Target Devices |
|------------|-----------|----------------|
| `sm` | 640px | Large phones (landscape) |
| `md` | 768px | Tablets |
| `lg` | 1024px | Laptops |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Large screens |

### Custom Breakpoints

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'xs': '475px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
      '3xl': '1920px',
      // Max-width breakpoints
      'max-sm': { max: '639px' },
      'max-md': { max: '767px' },
      'max-lg': { max: '1023px' },
      // Range breakpoints
      'tablet': { min: '768px', max: '1023px' },
      // Feature queries
      'touch': { raw: '(hover: none) and (pointer: coarse)' },
      'stylus': { raw: '(hover: none) and (pointer: fine)' },
      'mouse': { raw: '(hover: hover) and (pointer: fine)' },
    },
  },
};
```

## Fluid Typography

### CSS Clamp Function

```css
/* globals.css */
:root {
  /* Fluid type scale: min, preferred, max */
  --text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
  --text-sm: clamp(0.875rem, 0.8rem + 0.35vw, 1rem);
  --text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-lg: clamp(1.125rem, 1rem + 0.6vw, 1.25rem);
  --text-xl: clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem);
  --text-2xl: clamp(1.5rem, 1.2rem + 1.5vw, 2rem);
  --text-3xl: clamp(1.875rem, 1.4rem + 2.25vw, 2.5rem);
  --text-4xl: clamp(2.25rem, 1.5rem + 3.75vw, 3.5rem);
  --text-5xl: clamp(3rem, 1.8rem + 6vw, 5rem);

  /* Fluid spacing */
  --space-xs: clamp(0.25rem, 0.2rem + 0.25vw, 0.5rem);
  --space-sm: clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem);
  --space-md: clamp(1rem, 0.8rem + 1vw, 1.5rem);
  --space-lg: clamp(1.5rem, 1rem + 2.5vw, 3rem);
  --space-xl: clamp(2rem, 1.2rem + 4vw, 5rem);
}
```

### Tailwind Fluid Typography

```javascript
// tailwind.config.js
const plugin = require('tailwindcss/plugin');

module.exports = {
  theme: {
    extend: {
      fontSize: {
        'fluid-xs': 'clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem)',
        'fluid-sm': 'clamp(0.875rem, 0.8rem + 0.35vw, 1rem)',
        'fluid-base': 'clamp(1rem, 0.9rem + 0.5vw, 1.125rem)',
        'fluid-lg': 'clamp(1.125rem, 1rem + 0.6vw, 1.25rem)',
        'fluid-xl': 'clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem)',
        'fluid-2xl': 'clamp(1.5rem, 1.2rem + 1.5vw, 2rem)',
        'fluid-3xl': 'clamp(1.875rem, 1.4rem + 2.25vw, 2.5rem)',
        'fluid-4xl': 'clamp(2.25rem, 1.5rem + 3.75vw, 3.5rem)',
        'fluid-5xl': 'clamp(3rem, 1.8rem + 6vw, 5rem)',
      },
    },
  },
};
```

### Usage

```html
<h1 class="text-fluid-4xl font-bold">Responsive Headline</h1>
<p class="text-fluid-base">Body text that scales smoothly.</p>
```

## Best Practices

1. **Mobile-first**: Start with mobile styles, enhance for larger screens
2. **Use relative units**: `rem`, `em`, `%`, `vw/vh` over `px`
3. **Test real devices**: Emulators don't catch everything
4. **Fluid over fixed**: Use `clamp()` for smooth scaling
5. **Container queries**: For component-level responsiveness
6. **Touch targets**: Minimum 44x44px for interactive elements
7. **Content priority**: Show most important content first on mobile
8. **Performance**: Serve appropriate image sizes

## Output Checklist

Every responsive implementation should include:

- [ ] Mobile-first approach
- [ ] Breakpoints defined and consistent
- [ ] Fluid typography with clamp()
- [ ] Container queries for components
- [ ] Responsive images with srcset
- [ ] Touch-friendly tap targets (44px+)
- [ ] Tested on real devices
- [ ] Horizontal scroll prevented
- [ ] Navigation adapts to screen size
- [ ] Tables readable on mobile


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

