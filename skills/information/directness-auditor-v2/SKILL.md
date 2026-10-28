---
name: directness-auditor-v2
description: Audit, flag, and rewrite euphemisms, circumlocution, polite hedging, genteelisms, sugarcoating, MM Romance/BL register drift (anatomical euphemisms, heteronormative role coding, affective projection), and RLHF light censorship/pronominal evasion into direct, clinical, or grounded vernacular equivalents. Use when the user asks to evaluate LLM outputs for indirectness, strip corporate doublespeak, detect romance-trope contamination or safety avoidance in fiction/scripts, enforce blunt/clinical tone, or build automated directness evaluation pipelines.
---
# Directness Auditor v2

Audit text or LLM outputs for semantic softening, genre-corpus drift, and safety avoidance, replacing evasive phrasing with direct, clinical, or grounded vernacular equivalents (orthophemisms).

## When to Use

- The user wants to evaluate or score text/LLM responses for euphemisms, circumlocution, polite hedging, genteelisms, or sugarcoating.
- The user wants to detect and strip **MM Romance / BL corpus drift** (purple prose metaphors, feminized submission tropes, or heteronormative role coding) in fiction or scripts.
- The user wants to detect **RLHF light censorship or avoidance** (pronominal evasion, spatial metonymy, negative periphrasis, or vague fade-to-black cuts).
- The user asks to strip corporate doublespeak, compliment sandwiches, or apologetic framing from drafts, code reviews, or technical documentation.
- The user wants to implement or customize a deterministic regex pre-filter or LLM-as-a-Judge pipeline for linguistic directness.

## Detection Taxonomy

Evaluate target text against two primary domains of semantic softening and drift:

### Domain A: General & Corporate Indirectness

1. **Euphemism:** Substituting a mild or indirect expression for a harsh or blunt reality (e.g., "workforce optimization" instead of "layoffs").
2. **Circumlocution / Periphrasis:** Speaking around a point with bloated phrasing instead of direct subject-verb-object statements (e.g., "due to the fact that" instead of "because"; "not entirely accurate" instead of "inaccurate").
3. **Polite Terms / Hedging:** Epistemic or social cushioning used to soften a refusal, correction, or negative fact (e.g., "I'm afraid that", "gently point out", "might potentially").
4. **Genteelism:** Replacing plain, standard terms with artificially refined vocabulary (e.g., "utilize" instead of "use", "perspire" instead of "sweat", "pre-owned" instead of "used").
5. **Sugarcoating:** Framing failures, defects, or bugs as positive outcomes or compliment sandwiches (e.g., "Great start, though there is an opportunity for optimization" instead of "Line 42 has a memory leak").

### Domain B: Fiction Register Drift (MM Romance / BL) & RLHF Light Censorship

6. **Anatomical & Act Euphemism (Romance Drift):** Replacing plain vernacular or clinical anatomical terms with romance-novel metaphors or polite social phrasing (e.g., "slept with", "made love", "shared a bed", "his length/member/shaft/heat/entrance", "their bodies joined" instead of plain vernacular like "fucked", "cock", "ass", "hard" or direct clinical terms).
7. **Affective & Gaze Projection (BL Drift):** Injecting bashful, melodramatic, or feminized submission tropes into adult male behavior (e.g., "melted into his touch", "surrendered/yielded to him", "whimpered", "flushed crimson", "unblock the want" instead of concrete physical mechanics, verbal negotiation, or direct agency).
8. **Heteronormative Role Coding:** Framing sexual positions (top/bottom) as fixed personality archetypes, emotional submission, or "conversion" arcs (e.g., "the softer/submissive one", "gave up control", "converted him" instead of explicit positional mechanics like "bottomed", "topped", "switched").
9. **Pronominal & Metonymic Evasion (Light Censorship):** Using vague pronouns ("it", "that", "the rest") or spatial metonymy ("in the same bed") to avoid naming an explicit act (e.g., "Everything that isn't that. ... They do.", "Sound carries the rest", "been in the same bed" instead of "They do oral and handjobs", "Off-camera audio carries the sex", "already fucked him").
10. **Negative Periphrasis & Fade-to-Black Avoidance:** Defining a physical act by what it is not, or citing abstract modesty boundaries instead of concrete physical or platform cuts (e.g., "have sex that is not one man penetrating the other", "before anything explicit", "past what a feed will hold" instead of "oral and handjobs", "before penetration shows on camera", "before violating platform nudity rules").

### Exemptions (Do Not Flag)

- **High-Precision Technical Jargon:** Domain-accurate clinical or engineering terminology (e.g., "myocardial infarction", "idempotent") when used for precision rather than evasion.
- **Valid Epistemic Uncertainty:** Objective probabilistic statements or confidence intervals (e.g., "The model estimates a 60% probability").
- **Authentic First-Person Dialogue:** Idiomatic character dialogue or intentional in-world lies (e.g., a character saying "I'll take it" or introducing a partner as "Friend of mine"), provided the surrounding stage directions or narrative prose state the mechanics plainly.
- **Direct Quotations:** Verbatim quotes from external sources being analyzed.

## Workflow

### Mode 1: Direct Text Audit & Surgical Rewrite

When asked to audit or rewrite a piece of text directly in conversation:

1. **Scan and Extract:** Identify every verbatim span matching the ten violation categories across Domain A and Domain B.
2. **Anchor on the Orthophemism:** Formulate the shortest, most direct clinical or grounded vernacular equivalent for each flagged span. If the replacement conveys the same factual or narrative truth with greater brevity, bluntness, or groundedness, confirm the violation.
3. **Report Findings:** Present a concise Markdown table with columns: `Flagged Span`, `Category`, `Direct Orthophemism`, and `Rationale`. When auditing multiple texts, include a cross-document summary table comparing violation counts, severity scores (`0.0-1.0`), and primary drift sources.
4. **Deliver Surgical Rewrite:** Output the revised text (or modified lines) with all flagged spans replaced by their orthophemisms. Preserve all code blocks, technical identifiers, and unflagged sentences verbatim.

### Mode 2: Automated Pipeline Implementation

When asked to generate code for an automated evaluation or rewrite pipeline, structure it as a three-tier state machine:

1. **Tier 1 (Deterministic Regex Pre-Filter):** Compile case-insensitive regex rules covering high-frequency triggers across both domains:
   - *Corporate / Hedging:* `\b(?:room|opportunity)\s+for\s+(?:improvement|optimization)\b`, `\bdue\s+to\s+the\s+fact\s+that\b`, `\b(?:utilize|utilization|commence|endeavor)\b`
   - *MM Romance / BL Drift:* `\b(?:his\s+(?:length|member|shaft|manhood|hardness|heat|entrance|channel|core)|their\s+bodies\s+joined)\b`, `\b(?:melted\s+into|surrendered\s+to|yielded\s+to|submitted\s+to|whimpered|flushed\s+crimson)\b`, `\b(?:slept\s+with|sleeping\s+with|sleep\s+with|made\s+love|been\s+intimate\s+with|shared\s+a\s+bed)\b`
   - *Light Censorship / Pronominal Evasion:* `\b(?:sound|audio|imagination)\s+(?:carries|does|fills\s+in)\s+(?:the\s+rest|it)\b`, `\b(?:before\s+anything\s+explicit|past\s+what\s+a\s+feed\s+will\s+hold|not\s+one\s+man\s+penetrating\s+the\s+other|everything\s+that\s+isn'?t\s+that)\b`
2. **Tier 2 (Threshold Routing & Guided LLM Judge):**
   - If pre-filter hits meet or exceed the hard-fail threshold (default `>= 3`), bypass the Judge LLM call to save latency and tokens, routing directly to the surgical rewriter.
   - If pre-filter hits are `0-2`, invoke the LLM Judge (`temperature=0.0`) bound to a structured Pydantic schema (`DirectnessEvaluationResult` containing `passed: bool`, `severity_score: float`, and `violations: list[EvasionInstance]`). Inject any regex matches as diagnostic hints in the prompt.
3. **Tier 3 (Surgical Rewrite):** Replace flagged spans with their `orthophemism_rewrite` using a constrained `temperature=0.0` LLM pass (or deterministic `.replace()` when spans are isolated and syntactically self-contained), adjusting only immediate clause boundaries while leaving code fences untouched.

## Gotchas

- **Assistant-Mode Regression Trap:** When an LLM is asked to add "plain explanations" or summaries to an existing script, its RLHF safety training often re-introduces polite euphemisms (e.g., reverting direct verbs to "slept with" or "seeing"). Audit explanatory blocks just as strictly as narrative blocks.
- **Counterfactual Grounding:** Never flag a span without first generating its `orthophemism_rewrite`. If you cannot write a more direct equivalent without losing factual accuracy, the span is not a violation.
- **Compliment Sandwiches:** Deleting introductory praise (e.g., "Your code is a solid start, however...") often leaves dangling conjunctions or lowercase sentence starts. Ensure grammatical stitching fixes capitalization and clause boundaries.
- **Code Block Integrity:** Never run regex replacements or surgical rewrites inside fenced code blocks or inline code identifiers unless explicitly asked to refactor variable names or comments.
