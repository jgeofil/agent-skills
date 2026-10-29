---
name: structured-output-extractor
description: >-
  Extracts structured data from LLM responses using JSON schemas, Zod validation, and function calling for reliable parsing. Use when users request "structured output", "JSON extraction", "parse LLM response", "function calling", or "typed responses".
license: MIT
metadata:
  version: "1.0"
  category: ai-engineering-swe
---

# Structured Output Extractor

Extract reliable, typed data from LLM responses.

## Core Workflow

1. **Define schema**: Create data structure
2. **Choose method**: Function calling vs prompting
3. **Generate response**: Call LLM with structure
4. **Validate output**: Parse and verify
5. **Handle errors**: Retry or fallback

## Methods Comparison

| Method | Reliability | Flexibility | Best For |
|--------|-------------|-------------|----------|
| OpenAI JSON Mode | High | Medium | Simple JSON |
| Function Calling | Very High | High | Complex schemas |
| Instructor | Very High | High | Python/TS apps |
| Zod + Prompting | Medium | High | Custom parsing |

## OpenAI Structured Outputs

### JSON Mode

```typescript
// extractors/json-mode.ts
import OpenAI from 'openai';

const openai = new OpenAI();

interface ExtractedData {
  name: string;
  email: string;
  phone?: string;
  company?: string;
}

export async function extractContactInfo(text: string): Promise<ExtractedData> {
  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    response_format: { type: 'json_object' },
    messages: [
      {
        role: 'system',
        content: `Extract contact information from text. Return JSON with:
{
  "name": "string",
  "email": "string",
  "phone": "string or null",
  "company": "string or null"
}`,
      },
      { role: 'user', content: text },
    ],
  });

  return JSON.parse(response.choices[0].message.content!);
}
```

### Structured Outputs (Beta)

```typescript
// extractors/structured.ts
import OpenAI from 'openai';
import { z } from 'zod';
import { zodResponseFormat } from 'openai/helpers/zod';

const ContactSchema = z.object({
  name: z.string().describe('Full name of the contact'),
  email: z.string().email().describe('Email address'),
  phone: z.string().nullable().describe('Phone number if available'),
  company: z.string().nullable().describe('Company name if mentioned'),
  role: z.string().nullable().describe('Job title or role'),
});

type Contact = z.infer<typeof ContactSchema>;

export async function extractContact(text: string): Promise<Contact> {
  const response = await openai.beta.chat.completions.parse({
    model: 'gpt-4o-2024-08-06',
    messages: [
      {
        role: 'system',
        content: 'Extract contact information from the provided text.',
      },
      { role: 'user', content: text },
    ],
    response_format: zodResponseFormat(ContactSchema, 'contact'),
  });

  return response.choices[0].message.parsed!;
}
```

## Best Practices

1. **Use structured outputs**: OpenAI's native feature when available
2. **Define clear schemas**: Descriptive field names and descriptions
3. **Validate with Zod**: Type-safe runtime validation
4. **Retry on failure**: With error context
5. **Use function calling**: For complex schemas
6. **Handle edge cases**: Null values, empty arrays
7. **Stream for UX**: Partial results during extraction
8. **Test with variations**: Different input formats

## Output Checklist

Every structured extraction should include:

- [ ] Zod schema with descriptions
- [ ] Appropriate extraction method (JSON/function/tools)
- [ ] Runtime validation
- [ ] Retry logic with error context
- [ ] Error handling and typing
- [ ] Streaming support (if needed)
- [ ] Edge case handling
- [ ] Type-safe return values
- [ ] Comprehensive tests


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

