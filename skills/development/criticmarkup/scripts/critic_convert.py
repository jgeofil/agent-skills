#!/usr/bin/env python3
"""Convert CriticMarkup Markdown to styled HTML (and optionally PDF).

Based on the Critic Markup CLI (criticParser_CLI.py) patterns:
  additions {++ ++}, deletions {-- --}, substitutions {~~ ~> ~~},
  comments {>> <<}, highlights {== ==}{>> <<}

Usage:
  python critic_convert.py source.md
  python critic_convert.py source.md -o out.html
  python critic_convert.py source.md -o out.pdf --pdf
  python critic_convert.py source.md --css custom.css -b
  python critic_convert.py source.md --accept   # emit accepted (edited) markdown
  python critic_convert.py source.md --reject   # emit original markdown
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

# CriticMarkup patterns (from Critic Markup CLI)
ADD_PATTERN = re.compile(
    r"(?s)\{\+\+(?P<value>.*?)\+\+[ \t]*(?:\[(?P<meta>.*?)\])?[ \t]*\}"
)
DEL_PATTERN = re.compile(
    r"(?s)\{\-\-(?P<value>.*?)\-\-[ \t]*(?:\[(?P<meta>.*?)\])?[ \t]*\}"
)
COMM_PATTERN = re.compile(r"(?s)\{\>\>(?P<value>.*?)\<\<\}")
SUBS_PATTERN = re.compile(
    r"(?s)\{\~\~(?P<original>(?:[^\~\>]|(?:\~(?!\>)))+)\~\>"
    r"(?P<new>(?:[^\~\~]|(?:\~(?!\~\})))+)\~\~\}"
)
# highlight + attached comment (CLI order: mark before free comments)
MARK_PATTERN = re.compile(
    r"(?s)\{\=\=(?P<value>.*?)\=\=\}\{\>\>(?P<comment>.*?)\<\<\}"
)
# standalone highlight without comment
MARK_ONLY_PATTERN = re.compile(r"(?s)\{\=\=(?P<value>.*?)\=\=\}")


def _deletion(m: re.Match[str]) -> str:
    value = m.group("value")
    if value == "\n\n":
        return "<del>&nbsp;</del>"
    return "<del>" + value.replace("\n\n", "&nbsp;") + "</del>"


def _addition(m: re.Match[str]) -> str:
    value = m.group("value")
    if value.startswith("\n\n") and value != "\n\n":
        return (
            "\n\n<ins class='critic break'>&nbsp;</ins>\n\n"
            f"<ins>{value.replace(chr(10), ' ')}</ins>"
        )
    if value == "\n\n":
        return "\n\n<ins class='critic break'>&nbsp;</ins>\n\n"
    if value.endswith("\n\n") and value != "\n\n":
        return (
            f"<ins>{value.replace(chr(10), ' ')}</ins>"
            "\n\n<ins class='critic break'>&nbsp;</ins>\n\n"
        )
    return f"<ins>{value.replace(chr(10), ' ')}</ins>"


def _substitution(m: re.Match[str]) -> str:
    return f"<del>{m.group('original')}</del><ins>{m.group('new')}</ins>"


def _comment(m: re.Match[str]) -> str:
    return (
        '<span class="critic comment">'
        + m.group("value").replace("\n", " ")
        + "</span>"
    )


def _mark_with_comment(m: re.Match[str]) -> str:
    return (
        f"<mark>{m.group('value')}</mark>"
        f'<span class="critic comment">{m.group("comment").replace(chr(10), " ")}</span>'
    )


def _mark_only(m: re.Match[str]) -> str:
    return f"<mark>{m.group('value')}</mark>"


def critic_to_html_fragments(text: str) -> str:
    """Replace CriticMarkup with HTML tags; leave surrounding markdown intact."""
    h = DEL_PATTERN.sub(_deletion, text)
    h = ADD_PATTERN.sub(_addition, h)
    h = MARK_PATTERN.sub(_mark_with_comment, h)
    h = MARK_ONLY_PATTERN.sub(_mark_only, h)
    h = COMM_PATTERN.sub(_comment, h)
    h = SUBS_PATTERN.sub(_substitution, h)
    return h


def _collapse_ws(text: str) -> str:
    """Tidy spaces left after removing markup; keep markdown blank lines."""
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" *\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def accept_markup(text: str) -> str:
    """Resolve CriticMarkup to the edited (accepted) plain markdown."""
    h = DEL_PATTERN.sub("", text)
    h = ADD_PATTERN.sub(lambda m: m.group("value"), h)
    h = MARK_PATTERN.sub(lambda m: m.group("value"), h)
    h = MARK_ONLY_PATTERN.sub(lambda m: m.group("value"), h)
    h = COMM_PATTERN.sub("", h)
    h = SUBS_PATTERN.sub(lambda m: m.group("new"), h)
    return _collapse_ws(h)


def reject_markup(text: str) -> str:
    """Resolve CriticMarkup to the original (rejected edits) plain markdown."""
    h = DEL_PATTERN.sub(lambda m: m.group("value"), text)
    h = ADD_PATTERN.sub("", h)
    h = MARK_PATTERN.sub(lambda m: m.group("value"), h)
    h = MARK_ONLY_PATTERN.sub(lambda m: m.group("value"), h)
    h = COMM_PATTERN.sub("", h)
    h = SUBS_PATTERN.sub(lambda m: m.group("original"), h)
    return _collapse_ws(h)


def markdown_to_html(text: str, engine: str = "markdown") -> str:
    if engine == "markdown2":
        try:
            import markdown2
        except ImportError as exc:
            raise SystemExit(
                "markdown2 is not installed. pip install markdown2  (or omit --m2)"
            ) from exc
        return markdown2.markdown(
            text,
            extras=["footnotes", "fenced-code-blocks", "cuddled-lists", "code-friendly"],
        )

    try:
        import markdown
    except ImportError as exc:
        raise SystemExit(
            "Python-Markdown is not installed. pip install markdown"
        ) from exc
    return markdown.markdown(text, extensions=["extra", "codehilite", "meta", "sane_lists"])


DEFAULT_CSS = """
:root {
  --bg: #ffffff;
  --fg: #1a1a1a;
  --muted: #5c5c5c;
  --nav-bg: #f7f7f8;
  --ins-bg: #d1fae5;
  --ins-fg: #064e3b;
  --del-bg: #fee2e2;
  --del-fg: #7f1d1d;
  --mark-bg: #fef08a;
  --mark-fg: #1a1a1a;
  --comment-bg: #1d4ed8;
  --comment-fg: #ffffff;
  --border: #d4d4d8;
  --chip: 0.1em 0.28em;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #121212;
    --fg: #f0f0f0;
    --muted: #b0b0b0;
    --nav-bg: #1c1c1e;
    --ins-bg: #14532d;
    --ins-fg: #bbf7d0;
    --del-bg: #7f1d1d;
    --del-fg: #fecaca;
    --mark-bg: #854d0e;
    --mark-fg: #fef9c3;
    --comment-bg: #3b82f6;
    --comment-fg: #ffffff;
    --border: #3f3f46;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  line-height: 1.65;
  font-size: 16px;
  color: var(--fg);
  background: var(--bg);
}
#wrapper {
  max-width: 48rem;
  margin: 0 auto;
  padding: 4.5rem 1.25rem 3rem;
}
#criticnav {
  position: fixed;
  top: 0; left: 0; width: 100%;
  box-shadow: 0 1px 0 var(--border);
  background: var(--nav-bg);
  z-index: 100;
  font-size: 13px;
}
#criticnav ul {
  list-style: none;
  width: min(48rem, 94%);
  margin: 0 auto;
  padding: 0;
  display: flex;
}
#criticnav ul li {
  flex: 1;
  text-align: center;
  padding: 0.85rem 0.25rem;
  cursor: pointer;
  border-left: 1px solid var(--border);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  user-select: none;
  color: var(--fg);
}
#criticnav ul li:first-child { border-left: none; }
#criticnav ul li.active {
  background: color-mix(in srgb, var(--fg) 8%, transparent);
  font-weight: 700;
  box-shadow: inset 0 -2px 0 var(--comment-bg);
}
/* Markup view — color-coded edits with readable text */
.markup del,
.markup ins,
.markup mark {
  text-decoration: none;
  border-radius: 0.2em;
  padding: var(--chip);
}
.markup del {
  background: var(--del-bg);
  color: var(--del-fg);
  text-decoration: line-through;
  text-decoration-thickness: 1px;
}
.markup ins {
  background: var(--ins-bg);
  color: var(--ins-fg);
}
.markup mark {
  background: var(--mark-bg);
  color: var(--mark-fg);
}
.markup ins.break {
  display: block;
  line-height: 2px;
  padding: 0 !important;
  margin: 0.35rem 0 !important;
  background: var(--ins-bg);
}
.markup .popover {
  background: var(--comment-bg);
  color: var(--comment-fg);
  border-radius: 0.25rem;
  padding: 0 0.3rem;
  cursor: help;
  position: relative;
  font-weight: 600;
}
.markup .popover .critic.comment { display: none; }
.markup .popover:hover .critic.comment,
.markup .popover:focus .critic.comment {
  display: block;
  position: absolute;
  width: 16rem;
  left: 50%;
  transform: translateX(-50%);
  top: 1.5em;
  font-size: 0.85em;
  font-weight: 400;
  color: #f4f4f5;
  background: #18181b;
  z-index: 10;
  padding: 0.55em 0.8em;
  border-radius: 0.4em;
  box-shadow: 0 6px 18px rgba(0,0,0,.35);
  line-height: 1.4;
}
/* Original / Edited: clean reading modes — inherit body text color */
.original del,
.edited ins {
  text-decoration: none;
  background: transparent;
  color: inherit;
  padding: 0;
}
.original ins,
.original .popover,
.original ins.break,
.edited del,
.edited .popover,
.edited ins.break {
  display: none !important;
}
.original mark,
.edited mark {
  background: transparent;
  color: inherit;
  padding: 0;
}
pre, code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.92em;
}
pre {
  overflow: auto;
  padding: 0.75rem 1rem;
  background: color-mix(in srgb, var(--fg) 6%, transparent);
  border-radius: 0.35rem;
}
blockquote {
  margin-left: 0;
  padding-left: 1rem;
  border-left: 3px solid var(--border);
  color: var(--muted);
}
@media print {
  #criticnav { display: none !important; }
  #wrapper { padding-top: 1rem; }
  body { background: #fff; color: #111; }
}
"""

DEFAULT_JS = """
function setMode(mode) {
  var w = document.getElementById('wrapper');
  w.classList.remove('markup', 'original', 'edited');
  w.classList.add(mode);
  ['markup','original','edited'].forEach(function(id) {
    var el = document.getElementById(id + '-button');
    if (el) el.classList.toggle('active', id === mode);
  });
}
function initCritic() {
  var w = document.getElementById('wrapper');
  if (!w) return;
  // unwrap break inserts that markdown may wrap in <p>
  document.querySelectorAll('ins.break').forEach(function(el) {
    if (el.parentElement && el.parentElement.tagName === 'P' && el.parentElement.childNodes.length === 1) {
      el.parentElement.replaceWith(el);
    }
  });
  document.querySelectorAll('span.critic.comment').forEach(function(el) {
    if (el.parentElement && el.parentElement.classList.contains('popover')) return;
    var wrap = document.createElement('span');
    wrap.className = 'popover';
    wrap.tabIndex = 0;
    el.parentNode.insertBefore(wrap, el);
    wrap.appendChild(document.createTextNode('\\u2021'));
    wrap.appendChild(el);
  });
  setMode('markup');
  document.getElementById('markup-button').onclick = function() { setMode('markup'); };
  document.getElementById('original-button').onclick = function() { setMode('original'); };
  document.getElementById('edited-button').onclick = function() { setMode('edited'); };
}
window.addEventListener('DOMContentLoaded', initCritic);
"""

NAV_HTML = """
<div id="criticnav">
  <ul>
    <li id="markup-button">Markup</li>
    <li id="original-button">Original</li>
    <li id="edited-button">Edited</li>
  </ul>
</div>
"""


PDF_CSS = """
/* Print/PDF: no interactive nav; three static views on separate pages */
:root {
  --fg: #111;
  --muted: #555;
  --ins-bg: #d1fae5;
  --ins-fg: #064e3b;
  --del-bg: #fee2e2;
  --del-fg: #7f1d1d;
  --mark-bg: #fef08a;
  --mark-fg: #1a1a1a;
  --comment-bg: #dbeafe;
  --comment-fg: #1e3a8a;
  --border: #ccc;
  --chip: 0.08em 0.22em;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.65;
  font-size: 12pt;
  color: var(--fg);
  background: #fff;
}
.view-page {
  max-width: 48rem;
  margin: 0 auto;
  padding: 1.25rem 1rem 2rem;
  page-break-after: always;
  break-after: page;
  page-break-inside: avoid;
}
.view-page:last-child {
  page-break-after: auto;
  break-after: auto;
}
/* Force a hard break between views when the engine supports it */
.view-page + .view-page {
  page-break-before: always;
  break-before: page;
}
.view-label {
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 11pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  border-bottom: 2px solid var(--border);
  padding-bottom: 0.4rem;
  margin: 0 0 1.25rem;
}
/* Markup page */
.view-markup del,
.view-markup ins,
.view-markup mark {
  text-decoration: none;
  border-radius: 0.15em;
  padding: var(--chip);
}
.view-markup del {
  background: var(--del-bg);
  color: var(--del-fg);
  text-decoration: line-through;
}
.view-markup ins {
  background: var(--ins-bg);
  color: var(--ins-fg);
}
.view-markup mark {
  background: var(--mark-bg);
  color: var(--mark-fg);
}
.view-markup ins.break {
  display: block;
  line-height: 2px;
  padding: 0 !important;
  margin: 0.3rem 0 !important;
}
.view-markup .critic.comment {
  display: inline;
  font-family: system-ui, sans-serif;
  font-size: 0.85em;
  background: var(--comment-bg);
  color: var(--comment-fg);
  border-radius: 0.2em;
  padding: 0.05em 0.35em;
  margin-left: 0.2em;
}
.view-markup .critic.comment::before {
  content: "‡ ";
  font-weight: 700;
}
/* Original page: hide inserts + comments; show deletions as plain text */
.view-original ins,
.view-original ins.break,
.view-original .critic.comment,
.view-original .popover { display: none !important; }
.view-original del,
.view-original mark {
  background: transparent;
  color: inherit;
  text-decoration: none;
  padding: 0;
}
/* Edited page: hide deletions + comments; show inserts as plain text */
.view-edited del,
.view-edited ins.break,
.view-edited .critic.comment,
.view-edited .popover { display: none !important; }
.view-edited ins,
.view-edited mark {
  background: transparent;
  color: inherit;
  text-decoration: none;
  padding: 0;
}
pre, code {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 0.9em;
}
pre {
  overflow: auto;
  padding: 0.6rem 0.8rem;
  background: #f4f4f5;
  border-radius: 0.25rem;
}
"""


def wrap_document(
    body_html: str,
    title: str = "Critic Markup Output",
    custom_css: str | None = None,
    include_nav: bool = True,
    wrapper_class: str = "markup",
) -> str:
    style = custom_css if custom_css is not None else DEFAULT_CSS
    nav = NAV_HTML if include_nav else ""
    script = f"<script>\n{DEFAULT_JS}\n</script>" if include_nav else ""
    safe_title = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title}</title>
<style>
{style}
</style>
</head>
<body>
{nav}
<div id="wrapper" class="{wrapper_class}">
{body_html}
</div>
{script}
</body>
</html>
"""


def wrap_pdf_document(body_html: str, title: str = "Critic Markup Output") -> str:
    """Static three-page PDF: Markup, Original, Edited — no interactive tabs."""
    safe_title = html.escape(title)
    # Inline comments visible on markup page (no JS popovers)
    pages = []
    for view_class, label in (
        ("view-markup", "Markup"),
        ("view-original", "Original"),
        ("view-edited", "Edited"),
    ):
        pages.append(
            f'<section class="view-page {view_class}">'
            f'<h1 class="view-label">{label}</h1>'
            f"{body_html}"
            f"</section>"
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{safe_title}</title>
<style>
{PDF_CSS}
</style>
</head>
<body>
{"".join(pages)}
</body>
</html>
"""


def convert_file(
    source: Path,
    output: Path | None = None,
    engine: str = "markdown",
    css_path: Path | None = None,
    open_browser: bool = False,
    mode: str = "review",  # review | accept | reject
    pdf: bool = False,
) -> Path:
    text = source.read_text(encoding="utf-8")

    if mode == "accept":
        resolved = accept_markup(text)
        out = output or source.with_name(source.stem + "_accepted.md")
        out.write_text(resolved, encoding="utf-8")
        return out
    if mode == "reject":
        resolved = reject_markup(text)
        out = output or source.with_name(source.stem + "_original.md")
        out.write_text(resolved, encoding="utf-8")
        return out

    fragments = critic_to_html_fragments(text)
    body = markdown_to_html(fragments, engine=engine)

    custom_css = None
    if css_path:
        custom_css = css_path.read_text(encoding="utf-8")

    # Interactive HTML (with nav) always written when producing PDF too
    html_doc = wrap_document(
        body,
        title=source.stem,
        custom_css=custom_css,
        include_nav=custom_css is None,
    )

    if pdf:
        out = output or source.with_name(source.stem + "_CriticParseOut.pdf")
        if out.suffix.lower() != ".pdf":
            out = out.with_suffix(".pdf")
        html_path = out.with_suffix(".html")
        pdf_html_path = out.with_name(out.stem + "_print.html")
        html_path.write_text(html_doc, encoding="utf-8")
        pdf_doc = wrap_pdf_document(body, title=source.stem)
        pdf_html_path.write_text(pdf_doc, encoding="utf-8")
        _html_to_pdf(pdf_html_path, out)
        result = out
    else:
        out = output or source.with_name(source.stem + "_CriticParseOut.html")
        out.write_text(html_doc, encoding="utf-8")
        result = out

    if open_browser:
        target = result if result.suffix.lower() == ".html" else result.with_suffix(".html")
        if target.exists():
            webbrowser.open(target.resolve().as_uri())
        else:
            webbrowser.open(result.resolve().as_uri())

    return result


def _html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    """Render HTML→PDF. Prefer Chromium/Chrome (CSS page-breaks), then weasyprint, then pandoc."""
    last_err = ""

    # 1) Headless Chrome/Chromium — best CSS page-break support for multi-view PDFs
    for browser in (
        "google-chrome",
        "chromium",
        "chromium-browser",
        "chrome",
        "msedge",
    ):
        binary = shutil.which(browser)
        if not binary:
            continue
        cmd = [
            binary,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0 and pdf_path.exists() and pdf_path.stat().st_size > 0:
            return
        last_err = proc.stderr or proc.stdout or last_err

    # 2) WeasyPrint
    try:
        from weasyprint import HTML  # type: ignore

        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            return
    except Exception as exc:  # ImportError or render failure
        last_err = str(exc)

    # 3) pandoc engines (CSS page-breaks may be ignored by LaTeX engines)
    pandoc = shutil.which("pandoc")
    if pandoc:
        for engine in ("wkhtmltopdf", "weasyprint", "pdflatex", "xelatex", "lualatex"):
            if engine in ("wkhtmltopdf", "weasyprint") and not shutil.which(engine):
                continue
            trial = [
                pandoc,
                str(html_path),
                "-f",
                "html",
                "-t",
                "pdf",
                "-o",
                str(pdf_path),
                f"--pdf-engine={engine}",
            ]
            proc = subprocess.run(trial, capture_output=True, text=True)
            if proc.returncode == 0 and pdf_path.exists() and pdf_path.stat().st_size > 0:
                return
            last_err = proc.stderr or last_err

    # 4) Fallback: three single-view HTMLs merged with pdfunite
    if _pdf_via_merged_views(html_path, pdf_path):
        return

    raise SystemExit(
        "PDF conversion failed. Install Chrome/Chromium, weasyprint, or pandoc+engine.\n"
        f"Last error: {last_err}"
    )


def _pdf_via_merged_views(print_html: Path, pdf_path: Path) -> bool:
    """Split Markup/Original/Edited sections into separate PDFs and merge."""
    pdfunite = shutil.which("pdfunite")
    if not pdfunite:
        return False
    text = print_html.read_text(encoding="utf-8")
    # Extract body sections roughly
    sections = re.findall(
        r'(<section class="view-page[^"]*">.*?</section>)',
        text,
        flags=re.DOTALL,
    )
    if len(sections) < 2:
        return False

    style_m = re.search(r"<style>\s*(.*?)\s*</style>", text, flags=re.DOTALL)
    style = style_m.group(1) if style_m else PDF_CSS
    tmp_dir = pdf_path.parent / f".critic_pdf_{pdf_path.stem}"
    tmp_dir.mkdir(exist_ok=True)
    part_pdfs: list[Path] = []
    try:
        for i, section in enumerate(sections):
            part_html = tmp_dir / f"part_{i}.html"
            part_pdf = tmp_dir / f"part_{i}.pdf"
            part_html.write_text(
                f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
                f"<style>{style}</style></head><body>{section}</body></html>",
                encoding="utf-8",
            )
            # try chrome then pandoc for each part
            rendered = False
            for browser in ("google-chrome", "chromium", "chromium-browser"):
                binary = shutil.which(browser)
                if not binary:
                    continue
                proc = subprocess.run(
                    [
                        binary,
                        "--headless=new",
                        "--disable-gpu",
                        "--no-pdf-header-footer",
                        f"--print-to-pdf={part_pdf}",
                        part_html.resolve().as_uri(),
                    ],
                    capture_output=True,
                    text=True,
                )
                if proc.returncode == 0 and part_pdf.exists():
                    rendered = True
                    break
            if not rendered and shutil.which("pandoc"):
                subprocess.run(
                    ["pandoc", str(part_html), "-o", str(part_pdf)],
                    capture_output=True,
                    text=True,
                )
                rendered = part_pdf.exists()
            if not rendered:
                return False
            part_pdfs.append(part_pdf)

        proc = subprocess.run(
            [pdfunite, *[str(p) for p in part_pdfs], str(pdf_path)],
            capture_output=True,
            text=True,
        )
        return proc.returncode == 0 and pdf_path.exists()
    finally:
        for p in tmp_dir.glob("*"):
            try:
                p.unlink()
            except OSError:
                pass
        try:
            tmp_dir.rmdir()
        except OSError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert CriticMarkup Markdown to HTML/PDF")
    parser.add_argument("source", type=Path, help="Source .md path")
    parser.add_argument("-m2", action="store_true", help="Use markdown2 instead of markdown")
    parser.add_argument("-o", "--output", type=Path, help="Output file path")
    parser.add_argument("-css", "--css", type=Path, help="Custom CSS file (replaces default chrome)")
    parser.add_argument("-b", "--browser", action="store_true", help="Open result in browser")
    parser.add_argument("--pdf", action="store_true", help="Also/emit PDF (uses pandoc or weasyprint)")
    parser.add_argument(
        "--accept",
        action="store_true",
        help="Write accepted (edited) markdown with CriticMarkup resolved",
    )
    parser.add_argument(
        "--reject",
        action="store_true",
        help="Write original markdown with CriticMarkup resolved (edits rejected)",
    )
    args = parser.parse_args(argv)

    if not args.source.is_file():
        print(f"Source not found: {args.source}", file=sys.stderr)
        return 2
    if args.accept and args.reject:
        print("Choose only one of --accept / --reject", file=sys.stderr)
        return 2

    mode = "review"
    if args.accept:
        mode = "accept"
    elif args.reject:
        mode = "reject"

    pdf = args.pdf or (args.output is not None and args.output.suffix.lower() == ".pdf")

    try:
        result = convert_file(
            source=args.source,
            output=args.output,
            engine="markdown2" if args.m2 else "markdown",
            css_path=args.css,
            open_browser=args.browser,
            mode=mode,
            pdf=pdf and mode == "review",
        )
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"Output file created: {result.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
