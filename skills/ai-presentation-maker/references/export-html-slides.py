#!/usr/bin/env python3
"""
export-html-slides.py — Convert a Presentation Maker markdown deck to beautiful HTML slides.
Zero dependencies beyond Python 3 standard library.

Features:
- Full-screen slide presentation in browser
- Keyboard navigation (arrow keys, space)
- Print-optimized (each slide = one page)
- Speaker notes toggle (press 'N')
- Progress bar
- Dark/light theme toggle
- Self-contained single HTML file

Usage:
  python3 export-html-slides.py <deck.md> <output.html> [metadata.json] [--theme dark|light|gradient]
"""

import sys
import re
import json
from pathlib import Path
from html import escape


def parse_markdown_slides(md_path: str) -> dict:
    """Parse markdown into title + slides with content and speaker notes."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    title_text = ""
    subtitle_text = ""
    slides = []
    current_slide = None
    in_notes = False

    for line in content.split('\n'):
        # Main title
        if line.startswith('# ') and not line.startswith('## '):
            title_text = line[2:].strip()
            continue

        # Subtitle line (italic)
        if line.startswith('*') and not title_text == "" and not slides:
            subtitle_text = line.strip('* ')
            continue

        # New slide
        if line.startswith('## '):
            if current_slide:
                slides.append(current_slide)
            title = line[3:].strip()
            title = re.sub(r'^Slide \d+:\s*', '', title)
            current_slide = {
                'title': title,
                'content': [],
                'notes': [],
                'raw_content': ''
            }
            in_notes = False
            continue

        if not current_slide:
            continue

        # Detect speaker notes section
        if '**Speaker Notes' in line or '**What to say' in line or '**Say:**' in line:
            in_notes = True
            continue

        # Horizontal rule resets notes
        if line.strip() == '---':
            in_notes = False
            continue

        if in_notes:
            clean = line.strip()
            clean = re.sub(r'^>\s*', '', clean)
            if clean:
                current_slide['notes'].append(clean)
        else:
            stripped = line.strip()
            if stripped and stripped != '---':
                current_slide['content'].append(line)

    if current_slide:
        slides.append(current_slide)

    return {
        'title': title_text,
        'subtitle': subtitle_text,
        'slides': slides
    }


def md_to_html(lines: list) -> str:
    """Convert markdown lines to HTML."""
    html_parts = []
    in_list = False
    in_table = False
    table_rows = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            continue

        # Table detection
        if '|' in stripped and stripped.startswith('|'):
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if all(re.match(r'^[-:]+$', c) for c in cells):
                continue  # Skip separator row
            if not in_table:
                in_table = True
                html_parts.append('<table>')
                tag = 'th'
            else:
                tag = 'td'
            row = ''.join(f'<{tag}>{escape(c)}</{tag}>' for c in cells)
            html_parts.append(f'<tr>{row}</tr>')
            continue
        elif in_table:
            html_parts.append('</table>')
            in_table = False

        # List items
        if re.match(r'^[-*•]\s', stripped):
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            item = re.sub(r'^[-*•]\s+', '', stripped)
            item = apply_inline(item)
            html_parts.append(f'<li>{item}</li>')
            continue

        # Numbered list
        if re.match(r'^\d+\.\s', stripped):
            item = re.sub(r'^\d+\.\s+', '', stripped)
            item = apply_inline(item)
            html_parts.append(f'<li>{item}</li>')
            continue

        if in_list:
            html_parts.append('</ul>')
            in_list = False

        # Blockquote
        if stripped.startswith('>'):
            text = apply_inline(stripped.lstrip('> '))
            html_parts.append(f'<blockquote>{text}</blockquote>')
            continue

        # Regular paragraph
        text = apply_inline(stripped)
        html_parts.append(f'<p>{text}</p>')

    if in_list:
        html_parts.append('</ul>')
    if in_table:
        html_parts.append('</table>')

    return '\n'.join(html_parts)


def apply_inline(text: str) -> str:
    """Apply inline markdown formatting."""
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    # Code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def generate_html(data: dict, metadata: dict = None, theme: str = "gradient") -> str:
    """Generate a complete self-contained HTML presentation."""

    slides_html = []

    # Title slide
    speaker_info = ""
    if metadata:
        sp = metadata.get('speaker', {})
        parts = [sp.get('name', ''), sp.get('title', '')]
        speaker_info = ' — '.join(p for p in parts if p)

    slides_html.append(f"""
    <section class="slide title-slide">
      <div class="slide-content">
        <h1>{escape(data['title'])}</h1>
        <p class="subtitle">{escape(speaker_info or data['subtitle'])}</p>
      </div>
    </section>""")

    # Content slides
    for i, slide in enumerate(data['slides']):
        content_html = md_to_html(slide['content'])
        notes_html = ''
        if slide['notes']:
            notes_items = '\n'.join(f'<li>{apply_inline(escape(n))}</li>' for n in slide['notes'])
            notes_html = f'<div class="speaker-notes"><h4>Speaker Notes</h4><ul>{notes_items}</ul></div>'

        slides_html.append(f"""
    <section class="slide" data-index="{i + 1}">
      <div class="slide-content">
        <h2>{escape(slide['title'])}</h2>
        <div class="body">{content_html}</div>
      </div>
      {notes_html}
    </section>""")

    all_slides = '\n'.join(slides_html)
    total = len(data['slides']) + 1

    # Theme colors
    themes = {
        "dark": {
            "bg": "#1a1a2e",
            "card": "#16213e",
            "text": "#e8e8e8",
            "accent": "#4a90d9",
            "highlight": "#e94560",
            "title_bg": "linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%)",
        },
        "light": {
            "bg": "#f5f5f5",
            "card": "#ffffff",
            "text": "#2d2d2d",
            "accent": "#4a90d9",
            "highlight": "#e74c3c",
            "title_bg": "linear-gradient(135deg, #4a90d9 0%, #357abd 100%)",
        },
        "gradient": {
            "bg": "#0f0c29",
            "card": "rgba(255,255,255,0.05)",
            "text": "#f0f0f0",
            "accent": "#302b63",
            "highlight": "#24c6dc",
            "title_bg": "linear-gradient(135deg, #24c6dc 0%, #514a9d 50%, #302b63 100%)",
        },
        "terminal": {
            "bg": "#1A1A1A",
            "card": "#252525",
            "text": "#FFFFFF",
            "accent": "#333333",
            "highlight": "#00E676",
            "title_bg": "linear-gradient(135deg, #252525 0%, #1A1A1A 100%)",
        },
        "executive": {
            "bg": "#0D1B2A",
            "card": "#1B2838",
            "text": "#FFFFFF",
            "accent": "#2D3F52",
            "highlight": "#FFB700",
            "title_bg": "linear-gradient(135deg, #1B2838 0%, #0D1B2A 100%)",
        },
        "spark": {
            "bg": "#0f0c29",
            "card": "rgba(255,255,255,0.05)",
            "text": "#f0f0f0",
            "accent": "#302b63",
            "highlight": "#24c6dc",
            "title_bg": "linear-gradient(135deg, #24c6dc 0%, #514a9d 50%, #302b63 100%)",
        },
        "clean": {
            "bg": "#FFFFFF",
            "card": "#F8F8F8",
            "text": "#1A1A1A",
            "accent": "#E0E0E0",
            "highlight": "#E63946",
            "title_bg": "linear-gradient(135deg, #E63946 0%, #C5303C 100%)",
        },
    }
    t = themes.get(theme, themes["gradient"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(data['title'])}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg: {t['bg']};
    --card: {t['card']};
    --text: {t['text']};
    --accent: {t['accent']};
    --highlight: {t['highlight']};
    --title-bg: {t['title_bg']};
  }}

  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }}

  /* ── SLIDE CONTAINER ── */
  .deck {{ position: relative; width: 100vw; height: 100vh; }}

  .slide {{
    position: absolute;
    top: 0; left: 0;
    width: 100vw;
    height: 100vh;
    display: none;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 5vh 8vw;
    opacity: 0;
    transition: opacity 0.4s ease;
  }}
  .slide.active {{ display: flex; opacity: 1; }}

  .slide-content {{
    max-width: 1100px;
    width: 100%;
  }}

  /* ── TITLE SLIDE ── */
  .title-slide {{
    background: var(--title-bg);
    text-align: center;
  }}
  .title-slide h1 {{
    font-size: clamp(2.5rem, 5vw, 4.5rem);
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 1rem;
    color: #fff;
  }}
  .title-slide .subtitle {{
    font-size: clamp(1rem, 2vw, 1.5rem);
    font-weight: 300;
    opacity: 0.85;
    color: #fff;
  }}

  /* ── CONTENT SLIDES ── */
  .slide:not(.title-slide) {{
    background: var(--bg);
  }}
  h2 {{
    font-size: clamp(1.8rem, 3.5vw, 3rem);
    font-weight: 700;
    margin-bottom: 2rem;
    color: var(--highlight);
    letter-spacing: -0.01em;
  }}
  .body {{ font-size: clamp(1rem, 1.8vw, 1.35rem); line-height: 1.7; }}
  .body p {{ margin-bottom: 1rem; }}
  .body ul {{ margin: 1rem 0 1rem 1.5rem; }}
  .body li {{ margin-bottom: 0.6rem; }}
  .body strong {{ color: var(--highlight); font-weight: 600; }}
  .body table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
  }}
  .body th, .body td {{
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }}
  .body th {{ font-weight: 600; color: var(--highlight); }}
  .body blockquote {{
    border-left: 4px solid var(--highlight);
    padding: 0.5rem 1.5rem;
    margin: 1rem 0;
    opacity: 0.9;
    font-style: italic;
  }}
  .body code {{
    background: rgba(255,255,255,0.1);
    padding: 0.15em 0.4em;
    border-radius: 4px;
    font-size: 0.9em;
  }}
  .body a {{ color: var(--highlight); text-decoration: underline; }}

  /* ── SPEAKER NOTES ── */
  .speaker-notes {{
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0,0,0,0.92);
    color: #ccc;
    padding: 1.5rem 3rem;
    font-size: 0.85rem;
    max-height: 35vh;
    overflow-y: auto;
    border-top: 2px solid var(--highlight);
    z-index: 100;
  }}
  .speaker-notes h4 {{ color: var(--highlight); margin-bottom: 0.5rem; }}
  .speaker-notes ul {{ margin-left: 1.2rem; }}
  .speaker-notes li {{ margin-bottom: 0.3rem; }}
  body.show-notes .slide.active .speaker-notes {{ display: block; }}

  /* ── PROGRESS BAR ── */
  .progress {{
    position: fixed;
    bottom: 0;
    left: 0;
    height: 4px;
    background: var(--highlight);
    transition: width 0.3s ease;
    z-index: 200;
  }}

  /* ── CONTROLS ── */
  .controls {{
    position: fixed;
    top: 1.5rem;
    right: 2rem;
    display: flex;
    gap: 0.5rem;
    z-index: 200;
    opacity: 0.3;
    transition: opacity 0.3s;
  }}
  .controls:hover {{ opacity: 1; }}
  .controls button {{
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: var(--text);
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.75rem;
    font-family: inherit;
  }}
  .controls button:hover {{ background: rgba(255,255,255,0.2); }}
  .controls button.active {{ background: var(--highlight); color: #fff; }}

  .slide-counter {{
    position: fixed;
    bottom: 1.5rem;
    right: 2rem;
    font-size: 0.8rem;
    opacity: 0.4;
    z-index: 200;
  }}

  /* ── PRINT STYLES ── */
  @media print {{
    body {{ overflow: visible; background: #fff; color: #222; }}
    .deck {{ position: static; }}
    .slide {{
      position: relative !important;
      display: flex !important;
      opacity: 1 !important;
      page-break-after: always;
      height: 100vh;
      width: 100vw;
      background: #fff !important;
      color: #222 !important;
    }}
    .title-slide {{
      background: var(--title-bg) !important;
      color: #fff !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    h2 {{ color: #333 !important; }}
    .body strong {{ color: #333 !important; font-weight: 700; }}
    .body th {{ color: #333 !important; }}
    .body td, .body th {{ border-bottom-color: #ddd !important; }}
    .speaker-notes {{ display: none !important; }}
    .controls, .slide-counter, .progress {{ display: none !important; }}
  }}

  /* ── RESPONSIVE ── */
  @media (max-width: 768px) {{
    .slide {{ padding: 3vh 5vw; }}
    .controls {{ top: 0.5rem; right: 0.5rem; }}
  }}
</style>
</head>
<body>

<div class="controls">
  <button onclick="toggleNotes()" id="notesBtn" title="Toggle speaker notes (N)">Notes</button>
  <button onclick="window.print()" title="Print / Save as PDF">Print</button>
</div>

<div class="deck" id="deck">
{all_slides}
</div>

<div class="progress" id="progress"></div>
<div class="slide-counter" id="counter"></div>

<script>
  let current = 0;
  const slides = document.querySelectorAll('.slide');
  const total = slides.length;

  function showSlide(n) {{
    slides.forEach(s => s.classList.remove('active'));
    current = Math.max(0, Math.min(n, total - 1));
    slides[current].classList.add('active');
    document.getElementById('progress').style.width = ((current + 1) / total * 100) + '%';
    document.getElementById('counter').textContent = (current + 1) + ' / ' + total;
  }}

  function next() {{ showSlide(current + 1); }}
  function prev() {{ showSlide(current - 1); }}

  function toggleNotes() {{
    document.body.classList.toggle('show-notes');
    document.getElementById('notesBtn').classList.toggle('active');
  }}

  document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); next(); }}
    else if (e.key === 'ArrowLeft') {{ e.preventDefault(); prev(); }}
    else if (e.key === 'n' || e.key === 'N') {{ toggleNotes(); }}
    else if (e.key === 'Home') {{ showSlide(0); }}
    else if (e.key === 'End') {{ showSlide(total - 1); }}
  }});

  // Touch support
  let touchStartX = 0;
  document.addEventListener('touchstart', e => {{ touchStartX = e.touches[0].clientX; }});
  document.addEventListener('touchend', e => {{
    const diff = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(diff) > 50) {{ diff > 0 ? prev() : next(); }}
  }});

  showSlide(0);
</script>

</body>
</html>"""


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 export-html-slides.py <deck.md> <output.html> [metadata.json] [--theme dark|light|gradient]")
        sys.exit(1)

    md_path = sys.argv[1]
    output_path = sys.argv[2]
    meta_path = None
    theme = "gradient"

    for i, arg in enumerate(sys.argv[3:], 3):
        if arg == '--theme' and i + 1 < len(sys.argv):
            theme = sys.argv[i + 1]
        elif not arg.startswith('--') and arg.endswith('.json'):
            meta_path = arg

    metadata = None
    if meta_path and Path(meta_path).exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

    data = parse_markdown_slides(md_path)
    if not data['slides']:
        print("ERROR: No slides found in markdown", file=sys.stderr)
        sys.exit(1)

    html = generate_html(data, metadata, theme)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ HTML slides saved: {output_path} ({len(data['slides']) + 1} slides, theme: {theme})")


if __name__ == '__main__':
    main()
