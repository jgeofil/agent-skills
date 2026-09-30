# CriticMarkup syntax

Source: [criticmarkup.com](http://criticmarkup.com)

Use these markers inside Markdown files. The converter turns them into
`<ins>`, `<del>`, `<mark>`, and comment spans, then runs Markdown → HTML.

## Addition

```text
{++added text++}
```

Paragraph break addition:

```text
{++

++}
```

## Deletion

```text
{--deleted text--}
```

## Substitution

```text
{~~old text~>new text~~}
```

## Comment

```text
{>>Reviewer note goes here.<<}
```

## Highlight (with comment)

```text
{==highlighted phrase==}{>>Why this matters<<}
```

## Highlight only

```text
{==highlighted phrase==}
```

## Processing order (converter)

1. Deletions  
2. Additions  
3. Highlight + comment pairs  
4. Standalone highlights  
5. Free comments  
6. Substitutions  
7. Markdown → HTML  

Comments should be processed after highlight+comment pairs so attached notes stay bound to marks.

## View modes (HTML chrome)

The default HTML wrapper includes a nav bar:

| Mode | Shows |
|------|--------|
| **Markup** | All edits color-coded; comments as ‡ popovers |
| **Original** | Pre-edit text (hides insertions / comments) |
| **Edited** | Post-edit text (hides deletions / comments) |

## Accept / reject (plain Markdown)

- `--accept` keeps additions and substitution *new* text; drops deletions and comments  
- `--reject` keeps deletions’ content and substitution *old* text; drops additions and comments  
