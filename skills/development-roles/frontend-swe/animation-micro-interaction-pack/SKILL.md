---
name: animation-micro-interaction-pack
description: >-
  Provides reusable interaction patterns and motion presets that make UI feel polished and tactile. Includes hover effects, entrance/exit transitions, gesture feedback, spring physics, and reduced-motion accessibility support. Use when adding "animations", "transitions", "micro-interactions", or "motion design".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Animation & Micro-Interaction Pack

Craft high-performance, accessible micro-interactions and fluid motion design for modern web interfaces using Tailwind CSS and Framer Motion.

## When to Use This Skill

- Enhancing UI components with responsive hover, active, and focus transitions
- Adding smooth entrance/exit animations for modals, drawers, and notifications
- Implementing delightful feedback for buttons, toggles, form submissions, and cards
- Guaranteeing full accessibility compliance with `prefers-reduced-motion`

## Core Animation Principles

1. **Duration Guidelines**:
   - Micro-interactions (hover, click, toggle): 100ms – 200ms
   - Small transitions (dropdowns, tooltips): 150ms – 250ms
   - Large transitions (modals, slide-overs, page transitions): 250ms – 350ms
2. **GPU Acceleration**: Animate only `transform` and `opacity` to prevent browser layout reflows and repaints.
3. **Natural Easing**: Use cubic-bezier curves (e.g. `cubic-bezier(0.16, 1, 0.3, 1)` for snappy entrance; avoid linear motion).
4. **Accessibility First**: Respect `prefers-reduced-motion` by reducing motion to subtle opacity fades.

## Implementation Presets

### Tailwind CSS Micro-Interactions

```html
<!-- Interactive Button with Lift & Scale -->
<button className="px-4 py-2 font-medium bg-blue-600 text-white rounded-lg shadow-sm
  transition-all duration-150 ease-out
  hover:-translate-y-0.5 hover:shadow-md hover:bg-blue-700
  active:translate-y-0 active:scale-98 active:shadow-inner
  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
  motion-reduce:transform-none motion-reduce:transition-none">
  Click Me
</button>
```

### Framer Motion Presets

```tsx
import { motion, type Variants } from 'framer-motion';

export const springPresets = {
  snappy: { type: 'spring', stiffness: 400, damping: 30 },
  gentle: { type: 'spring', stiffness: 200, damping: 25 },
  bouncy: { type: 'spring', stiffness: 500, damping: 15 },
};

export const modalVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  visible: { 
    opacity: 1, 
    scale: 1, 
    y: 0, 
    transition: springPresets.snappy 
  },
  exit: { 
    opacity: 0, 
    scale: 0.95, 
    transition: { duration: 0.15, ease: 'easeIn' } 
  },
};
```

## Checklist for Micro-Interactions

- [ ] Animate exclusively with `transform` and `opacity`.
- [ ] All clickable elements provide immediate visual feedback on `:hover`, `:active`, and `:focus-visible`.
- [ ] Every animation supports `motion-reduce:transform-none` or `useReducedMotion()`.
- [ ] Animation execution does not exceed 350ms for user-initiated actions.
