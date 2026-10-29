# Storybook Setup - Implementation Guide & Code Recipes

## Writing Stories

### Component Story Format (CSF3)

```typescript
// src/components/Button/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { Button } from './Button';

const meta = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile button component with multiple variants and sizes.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline', 'ghost'],
      description: 'Visual style variant',
      table: {
        type: { summary: 'string' },
        defaultValue: { summary: 'primary' },
      },
    },
    size: {
      control: 'radio',
      options: ['sm', 'md', 'lg'],
      description: 'Button size',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable the button',
    },
    loading: {
      control: 'boolean',
      description: 'Show loading state',
    },
    children: {
      control: 'text',
      description: 'Button content',
    },
  },
  args: {
    onClick: fn(),
    children: 'Button',
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

// Basic stories
export const Primary: Story = {
  args: {
    variant: 'primary',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
  },
};

export const Outline: Story = {
  args: {
    variant: 'outline',
  },
};

export const Ghost: Story = {
  args: {
    variant: 'ghost',
  },
};

// Size variants
export const Small: Story = {
  args: {
    size: 'sm',
  },
};

export const Large: Story = {
  args: {
    size: 'lg',
  },
};

// States
export const Disabled: Story = {
  args: {
    disabled: true,
  },
};

export const Loading: Story = {
  args: {
    loading: true,
  },
};

// With icons
export const WithIcon: Story = {
  args: {
    children: (
      <>
        <PlusIcon className="mr-2 h-4 w-4" />
        Add Item
      </>
    ),
  },
};

// All variants showcase
export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-4">
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
    </div>
  ),
};
```

### Interactive Stories

```typescript
// src/components/Form/Form.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { within, userEvent, expect, fn } from '@storybook/test';
import { Form } from './Form';

const meta: Meta<typeof Form> = {
  title: 'Components/Form',
  component: Form,
  args: {
    onSubmit: fn(),
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const FilledForm: Story = {
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    // Fill out the form
    const emailInput = canvas.getByLabelText('Email');
    await userEvent.type(emailInput, 'test@example.com', { delay: 50 });

    const passwordInput = canvas.getByLabelText('Password');
    await userEvent.type(passwordInput, 'password123', { delay: 50 });

    // Submit the form
    const submitButton = canvas.getByRole('button', { name: /submit/i });
    await userEvent.click(submitButton);

    // Assert the form was submitted
    await expect(args.onSubmit).toHaveBeenCalled();
  },
};

export const ValidationError: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Submit without filling
    const submitButton = canvas.getByRole('button', { name: /submit/i });
    await userEvent.click(submitButton);

    // Check for error messages
    await expect(canvas.getByText('Email is required')).toBeInTheDocument();
  },
};
```

### MDX Documentation

```mdx
{/* src/components/Button/Button.mdx */}
import { Meta, Story, Canvas, Controls, ArgTypes } from '@storybook/blocks';
import * as ButtonStories from './Button.stories';
import { Button } from './Button';

<Meta of={ButtonStories} />

# Button

The Button component is used to trigger actions or navigation.

## Import

```tsx
import { Button } from '@/components/Button';
```

## Usage

<Canvas of={ButtonStories.Primary} />

## Variants

Buttons come in four variants to communicate different levels of emphasis.

<Canvas>
  <Story of={ButtonStories.AllVariants} />
</Canvas>

### Primary
Use for primary actions that are the main call to action on a page.

### Secondary
Use for secondary actions that complement the primary action.

### Outline
Use for tertiary actions or when you want less visual emphasis.

### Ghost
Use for navigation or very subtle actions.

## Sizes

<Canvas>
  <div className="flex items-center gap-4">
    <Button size="sm">Small</Button>
    <Button size="md">Medium</Button>
    <Button size="lg">Large</Button>
  </div>
</Canvas>

## States

### Disabled

<Canvas of={ButtonStories.Disabled} />

### Loading

<Canvas of={ButtonStories.Loading} />

## Props

<ArgTypes of={Button} />

## Accessibility

- Buttons use the native `<button>` element
- Loading state announces to screen readers
- Focus states are clearly visible
- Disabled buttons maintain proper ARIA attributes

## Design Guidelines

1. Use descriptive button text
2. Limit to one primary button per section
3. Keep button text concise (2-4 words)
4. Use icons to reinforce meaning, not replace text
```

## Testing Integration

### Visual Regression with Chromatic

```typescript
// .storybook/main.ts
const config: StorybookConfig = {
  addons: [
    '@chromatic-com/storybook',
  ],
};
```

```json
// package.json
{
  "scripts": {
    "chromatic": "chromatic --project-token=$CHROMATIC_PROJECT_TOKEN"
  }
}
```

### Test Runner

```bash
npm install @storybook/test-runner -D
```

```typescript
// .storybook/test-runner.ts
import type { TestRunnerConfig } from '@storybook/test-runner';
import { getStoryContext } from '@storybook/test-runner';
import { injectAxe, checkA11y } from 'axe-playwright';

const config: TestRunnerConfig = {
  async preVisit(page) {
    await injectAxe(page);
  },
  async postVisit(page, context) {
    // Run accessibility tests
    const storyContext = await getStoryContext(page, context);
    if (!storyContext.parameters?.a11y?.disable) {
      await checkA11y(page, '#storybook-root', {
        detailedReport: true,
        detailedReportOptions: { html: true },
      });
    }
  },
};

export default config;
```

```json
// package.json
{
  "scripts": {
    "test-storybook": "test-storybook",
    "test-storybook:ci": "test-storybook --ci"
  }
}
```

## Design Tokens Integration

```typescript
// .storybook/preview.ts
import { ThemeProvider } from 'styled-components';
import { theme } from '../src/styles/theme';

const preview: Preview = {
  decorators: [
    (Story) => (
      <ThemeProvider theme={theme}>
        <Story />
      </ThemeProvider>
    ),
  ],
};
```

```typescript
// src/styles/theme.ts (document in Storybook)
export const theme = {
  colors: {
    primary: {
      50: '#eff6ff',
      500: '#3b82f6',
      900: '#1e3a8a',
    },
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
  radii: {
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    full: '9999px',
  },
};
```

## Publishing

### Static Export

```json
// package.json
{
  "scripts": {
    "build-storybook": "storybook build",
    "storybook:serve": "npx http-server storybook-static"
  }
}
```

### GitHub Pages

```yaml
# .github/workflows/storybook.yml
name: Deploy Storybook

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - run: npm ci
      - run: npm run build-storybook

      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./storybook-static
```
