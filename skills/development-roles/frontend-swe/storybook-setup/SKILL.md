---
name: storybook-setup
description: >-
  Sets up Storybook for component documentation with controls, actions, accessibility testing, and visual regression. Use when users request "Storybook setup", "component documentation", "UI library", "component stories", or "design system docs".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Storybook Setup

Configure Storybook for comprehensive component documentation and testing.

## Core Workflow

1. **Initialize Storybook**: Setup with framework
2. **Configure addons**: Controls, actions, a11y
3. **Write stories**: Document components
4. **Add documentation**: MDX pages
5. **Setup testing**: Visual regression
6. **Deploy docs**: Static hosting

## Installation

```bash
# Initialize Storybook
npx storybook@latest init

# Or with specific framework
npx storybook@latest init --type react
npx storybook@latest init --type nextjs
npx storybook@latest init --type vue3
```

## Configuration

### Main Configuration

```typescript
// .storybook/main.ts
import type { StorybookConfig } from '@storybook/react-vite';

const config: StorybookConfig = {
  stories: [
    '../src/**/*.mdx',
    '../src/**/*.stories.@(js|jsx|mjs|ts|tsx)',
  ],

  addons: [
    '@storybook/addon-onboarding',
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@chromatic-com/storybook',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y',
    '@storybook/addon-designs',
    '@storybook/addon-coverage',
  ],

  framework: {
    name: '@storybook/react-vite',
    options: {},
  },

  docs: {
    autodocs: 'tag',
  },

  staticDirs: ['../public'],

  typescript: {
    reactDocgen: 'react-docgen-typescript',
    reactDocgenTypescriptOptions: {
      shouldExtractLiteralValuesFromEnum: true,
      shouldRemoveUndefinedFromOptional: true,
      propFilter: (prop) =>
        prop.parent ? !/node_modules/.test(prop.parent.fileName) : true,
    },
  },

  viteFinal: async (config) => {
    // Customize Vite config
    return config;
  },
};

export default config;
```

### Preview Configuration

```typescript
// .storybook/preview.ts
import type { Preview } from '@storybook/react';
import { themes } from '@storybook/theming';
import '../src/styles/globals.css';

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark', value: '#1a1a1a' },
        { name: 'gray', value: '#f5f5f5' },
      ],
    },
    layout: 'centered',
    docs: {
      theme: themes.light,
    },
    a11y: {
      config: {
        rules: [
          { id: 'color-contrast', enabled: true },
          { id: 'label', enabled: true },
        ],
      },
    },
    viewport: {
      viewports: {
        mobile: {
          name: 'Mobile',
          styles: { width: '375px', height: '667px' },
        },
        tablet: {
          name: 'Tablet',
          styles: { width: '768px', height: '1024px' },
        },
        desktop: {
          name: 'Desktop',
          styles: { width: '1440px', height: '900px' },
        },
      },
    },
  },
  globalTypes: {
    theme: {
      description: 'Global theme',
      defaultValue: 'light',
      toolbar: {
        title: 'Theme',
        icon: 'circlehollow',
        items: ['light', 'dark'],
        dynamicTitle: true,
      },
    },
  },
  decorators: [
    (Story, context) => {
      const theme = context.globals.theme;
      return (
        <div className={theme === 'dark' ? 'dark' : ''}>
          <div className="bg-white dark:bg-gray-900 p-4">
            <Story />
          </div>
        </div>
      );
    },
  ],
};

export default preview;
```

## Best Practices

1. **One component per file**: Clear organization
2. **Use autodocs**: Generate documentation
3. **Add controls**: Interactive exploration
4. **Include a11y addon**: Accessibility testing
5. **Write play functions**: Interactive tests
6. **Document with MDX**: Rich documentation
7. **Use decorators**: Consistent context
8. **Visual regression**: Catch UI changes

## Output Checklist

Every Storybook setup should include:

- [ ] Main configuration with addons
- [ ] Preview with global decorators
- [ ] Stories in CSF3 format
- [ ] Autodocs enabled
- [ ] Controls for all props
- [ ] Accessibility addon
- [ ] Dark mode support
- [ ] Viewport presets
- [ ] MDX documentation
- [ ] Test runner setup
- [ ] CI deployment
- [ ] Static build script


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

