---
name: form-wizard-builder
description: >-
  Builds multi-step forms with validation schemas (Zod/Yup), step components, shared state management, progress indicators, review steps, and error handling. Use when creating "multi-step forms", "wizard flows", "onboarding forms", or "checkout processes".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Form Wizard Builder

Create multi-step form experiences with validation, state persistence, and review steps.

## Core Workflow

1. **Define steps**: Break form into logical sections
2. **Create schema**: Zod/Yup validation for each step
3. **Build step components**: Individual form sections
4. **State management**: Shared state across steps (Zustand/Context)
5. **Navigation**: Next/Back/Skip logic
6. **Progress indicator**: Visual step tracker
7. **Review step**: Summary before submission
8. **Error handling**: Per-step and final validation

## Basic Wizard Structure

```typescript
// types/wizard.ts
export type WizardStep = {
  id: string;
  title: string;
  description?: string;
  component: React.ComponentType<StepProps>;
  schema: z.ZodSchema;
  isOptional?: boolean;
};

export type WizardData = {
  personal: PersonalInfoData;
  contact: ContactData;
  preferences: PreferencesData;
};
```

## Validation Schemas (Zod)

```typescript
// schemas/wizard.schema.ts
import { z } from "zod";

export const personalInfoSchema = z.object({
  firstName: z.string().min(2, "First name must be at least 2 characters"),
  lastName: z.string().min(2, "Last name must be at least 2 characters"),
  dateOfBirth: z.string().refine((date) => {
    const age = new Date().getFullYear() - new Date(date).getFullYear();
    return age >= 18;
  }, "Must be at least 18 years old"),
});

export const contactSchema = z.object({
  email: z.string().email("Invalid email address"),
  phone: z.string().regex(/^\+?[\d\s-()]+$/, "Invalid phone number"),
  address: z.object({
    street: z.string().min(1, "Street is required"),
    city: z.string().min(1, "City is required"),
    zipCode: z.string().regex(/^\d{5}(-\d{4})?$/, "Invalid ZIP code"),
  }),
});

export const preferencesSchema = z.object({
  notifications: z.object({
    email: z.boolean(),
    sms: z.boolean(),
    push: z.boolean(),
  }),
  interests: z.array(z.string()).min(1, "Select at least one interest"),
});

// Complete wizard schema
export const wizardSchema = z.object({
  personal: personalInfoSchema,
  contact: contactSchema,
  preferences: preferencesSchema,
});

export type WizardFormData = z.infer<typeof wizardSchema>;
```

## Best Practices

1. **Validate per step**: Don't wait until end
2. **Save progress**: Persist to localStorage/server
3. **Allow navigation**: Let users go back and edit
4. **Show progress**: Clear visual indicator
5. **Review before submit**: Summary step is crucial
6. **Handle errors gracefully**: Show which step has errors
7. **Mobile responsive**: Stack progress on mobile
8. **Accessibility**: Keyboard navigation, ARIA labels

## Output Checklist

- [ ] Step definitions with schemas
- [ ] Validation with Zod/Yup
- [ ] State management (Zustand/Context)
- [ ] Progress indicator component
- [ ] Individual step components
- [ ] Navigation controls (Next/Back/Skip)
- [ ] Review/summary step
- [ ] Error handling per step
- [ ] Persistence mechanism
- [ ] Mobile-responsive design


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

