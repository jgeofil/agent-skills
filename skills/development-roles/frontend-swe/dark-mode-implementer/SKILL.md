---
name: dark-mode-implementer
description: >-
  Implements complete dark/light mode theming systems using CSS variables, Tailwind dark mode, React context, and system preference detection. Use when users request "add dark mode", "theme toggle", "dark theme", "light mode switch", or "color scheme".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Dark Mode Implementer

Build robust dark/light mode theming with system preference detection and persistent storage.

## Core Workflow

1. **Choose strategy**: CSS-only, Tailwind, or React context
2. **Define color tokens**: Create semantic color variables
3. **Implement toggle**: Add theme switch component
4. **Detect system preference**: Respect `prefers-color-scheme`
5. **Persist choice**: Store preference in localStorage
6. **Prevent flash**: Handle initial load correctly

## Strategy Comparison

| Strategy | Best For | Complexity |
|----------|----------|------------|
| Tailwind `class` | React/Vue/Svelte apps | Low |
| CSS `media` | Simple static sites | Very Low |
| CSS Variables + JS | Framework-agnostic | Medium |
| React Context | Complex React apps | Medium |

## Tailwind CSS Dark Mode

### Enable Class Strategy

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // or 'media' for system-only
  theme: {
    extend: {
      colors: {
        // Semantic color tokens
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: 'hsl(var(--primary))',
        muted: 'hsl(var(--muted))',
      },
    },
  },
};
```

### CSS Variables Setup

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222 47% 11%;
    --primary: 221 83% 53%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96%;
    --secondary-foreground: 222 47% 11%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%;
    --accent: 210 40% 96%;
    --accent-foreground: 222 47% 11%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 210 40% 98%;
    --border: 214 32% 91%;
    --input: 214 32% 91%;
    --ring: 221 83% 53%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222 47% 11%;
    --foreground: 210 40% 98%;
    --primary: 217 91% 60%;
    --primary-foreground: 222 47% 11%;
    --secondary: 217 33% 17%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217 33% 17%;
    --muted-foreground: 215 20% 65%;
    --accent: 217 33% 17%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62% 30%;
    --destructive-foreground: 210 40% 98%;
    --border: 217 33% 17%;
    --input: 217 33% 17%;
    --ring: 224 76% 48%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

### Using Dark Mode Classes

```html
<!-- Component with dark mode variants -->
<div class="bg-white dark:bg-gray-900">
  <h1 class="text-gray-900 dark:text-white">Title</h1>
  <p class="text-gray-600 dark:text-gray-300">Description</p>
  <button class="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700">
    Action
  </button>
</div>
```

## Best Practices

1. **Prevent flash**: Use inline script before React hydration
2. **Respect system preference**: Default to 'system' theme
3. **Persist choice**: Store in localStorage
4. **Use semantic tokens**: Don't hardcode colors
5. **Test both themes**: Ensure contrast and readability
6. **Handle images**: Provide dark-mode variants
7. **Consider transitions**: Add smooth color transitions
8. **Accessibility**: Maintain WCAG contrast ratios

## Output Checklist

Every dark mode implementation should include:

- [ ] Tailwind configured with `darkMode: 'class'`
- [ ] CSS variables for light and dark themes
- [ ] Theme provider with context
- [ ] System preference detection
- [ ] localStorage persistence
- [ ] Flash prevention script
- [ ] Theme toggle component
- [ ] Accessible labels on toggle
- [ ] Color tokens for all UI elements
- [ ] Dark variants for images/SVGs
- [ ] Smooth transition animations
- [ ] Playwright/Jest tests


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

