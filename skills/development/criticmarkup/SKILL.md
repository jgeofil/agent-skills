---
name: criticmarkup
description: >
  Convert CriticMarkup Markdown (additions, deletions, substitutions, comments,
  highlights using brace-plus/minus/tilde/angle/equals markers) into styled HTML
  review documents or PDF, and optionally accept or reject edits to plain
  Markdown. Use whenever the user mentions CriticMarkup, Critic Markup, tracked
  changes in Markdown, editorial markup in .md files, converting CM or critic
  markup to HTML or PDF, reviewing redlines, or opening markup with Original /
  Edited / Markup views. Also use when they paste critic-style braces in a draft
  and want a browser-ready review file — even if they only say "render the
  edits" or "show track changes as HTML." Prefer this skill over generic
  Markdown conversion when CriticMarkup syntax is present.
---

# CriticMarkup → HTML / PDF

Turn CriticMarkup-annotated Markdown into a reviewable HTML document (with
Markup / Original / Edited views) or PDF. Also resolve markup to plain Markdown
by accepting or rejecting edits.

Syntax reference: read `references/syntax.md` when markers are unfamiliar.

## When this skill applies

- Source contains CriticMarkup: `{++ ++}`, `{-- --}`, `{~~ ~> ~~}`, `{>> <<}`, `{== ==}`
- User wants HTML preview, PDF export, or clean accepted/original Markdown
- Editorial / peer-review workflows on `.md` files

Do **not** use for Word track-changes, Google Docs suggestions, or git diffs —
those are different formats.

## Default workflow

1. Locate the source `.md` (or write pasted markup to a temp file).
2. Convert with the bundled CLI (paths relative to this skill directory):

```bash
python scripts/critic_convert.py path/to/file.md
# → path/to/file_CriticParseOut.html
```

3. Open the HTML in a browser (or pass `-b`). Use the top nav:
   - **Markup** — color-coded edits + comment popovers
   - **Original** — before edits
   - **Edited** — after edits

4. Deliver the output path(s) to the user. Summarize what was converted
   (counts of add/del/sub/comment if easy to tally).

### Common flags

| Goal | Command |
|------|---------|
| Custom output path | `python scripts/critic_convert.py src.md -o out.html` |
| Open in browser | `... -b` |
| markdown2 engine | `... -m2` (requires `markdown2` package) |
| Custom CSS (full chrome replace) | `... -css theme.css` |
| PDF | `... -o out.pdf` or `... --pdf` |
| Accept all edits → plain MD | `... --accept -o accepted.md` |
| Reject all edits → plain MD | `... --reject -o original.md` |

**HTML vs PDF layout**

- **HTML** — interactive top nav (Markup / Original / Edited); dark-mode aware colors with explicit foreground on `ins`/`del`/`mark` so cleaned modes stay legible.
- **PDF** — no nav tabs. One document with **three page sections** labeled Markup, Original, and Edited (page breaks between). Comments print inline on the Markup pages only.

Dependencies:

- **Required for HTML:** `markdown` (`pip install markdown`) — or `markdown2` with `-m2`
- **PDF:** `pandoc` plus a PDF engine (`wkhtmltopdf`, `weasyprint`, etc.), or `pip install weasyprint`

If PDF fails, still produce HTML and tell the user how to print-to-PDF from the browser.

## Implementation notes

- Prefer the bundled `scripts/critic_convert.py` over re-implementing regexes.
  It modernizes the classic Critic Markup CLI (Python 3, UTF-8, local CSS/JS —
  no remote jQuery).
- Processing order matters (deletes → adds → mark+comment → marks → comments →
  subs → Markdown). Do not reorder without reading the script.
- Critic tags become real HTML (`<ins>`, `<del>`, `<mark>`) *before* Markdown
  conversion so paragraph structure stays sane.
- Custom `-css` replaces the default stylesheet **and** disables the built-in
  nav/JS chrome (same behavior as the original CLI). Document that for users
  who only wanted colors changed — they may want to copy `DEFAULT_CSS` from the
  script instead.
- For accept/reject, write `.md` outputs; do not HTML-escape the result.

## Output expectations

When helping the user:

1. Run the converter (or show the exact command if they must run it elsewhere).
2. Return the absolute path to HTML/PDF/Markdown outputs.
3. Mention view modes for HTML review files.
4. If conversion errors, check encoding, unclosed markers, and missing deps;
   show a minimal failing snippet.

## Quick smoke test

```bash
python scripts/critic_convert.py references/sample.md -o /tmp/critic_sample.html
```

(If `references/sample.md` is missing, create a tiny fixture with one of each
marker type and convert that.)
