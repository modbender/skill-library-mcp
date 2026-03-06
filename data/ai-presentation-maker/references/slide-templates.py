#!/usr/bin/env python3
"""
slide-templates.py — Premade slide templates with theme support.

Generates individual per-slide HTML files OR a combined deck.
Each slide type has a layout optimized for stage presentations (1280x720).

THEMES:
  terminal  — Dark + green accent, terminal window frames (hacker/tech vibe)
  executive — Dark navy + gold, clean lines (corporate/boardroom)
  spark     — Gradient purple/teal, modern curves (startup/founder)
  clean     — White + charcoal, Swiss-style minimal (professional/universal)

SLIDE TYPES:
  title            — Hero title + subtitle + speaker name
  section          — Section divider with large heading
  text             — Simple text slide (bullets or paragraphs)
  text_and_image   — Split layout: text left, image right
  big_number       — One massive stat as the hero element
  comparison       — Side-by-side columns (before/after, us/them)
  screenshot       — Full-width image with caption overlay
  quote            — Large pull quote with attribution
  timeline         — Horizontal or vertical timeline steps
  qr_code          — QR code hero with call to action
  closing          — Final CTA slide with links/contact

Usage:
  python3 slide-templates.py --list-themes
  python3 slide-templates.py --list-types
  python3 slide-templates.py --theme terminal --type title --title "My Talk" --subtitle "The Real Story" --speaker "Jeff J Hunter" --output slide_01.html
  python3 slide-templates.py --theme spark --type big_number --number "71" --label "Leads Imported" --context "In under 5 minutes" --output slide_04.html
"""

import sys
import argparse
from html import escape

# ══════════════════════════════════════════════
# THEME DEFINITIONS
# ══════════════════════════════════════════════

THEMES = {
    "terminal": {
        "name": "Terminal",
        "description": "Dark + green accent, terminal window frames. Hacker/tech vibe.",
        "bg": "#1A1A1A",
        "card_bg": "#252525",
        "text": "#FFFFFF",
        "muted": "#B3B3B3",
        "accent": "#00E676",
        "accent_dark": "#00C853",
        "border": "#333333",
        "font_heading": "'Roboto', sans-serif",
        "font_body": "'Roboto', sans-serif",
        "font_mono": "'Roboto Mono', monospace",
        "google_fonts": "Roboto:wght@400;700;900&family=Roboto+Mono:wght@400;700",
        "has_terminal_frame": True,
        "heading_transform": "uppercase",
        "heading_spacing": "2px",
    },
    "executive": {
        "name": "Executive",
        "description": "Dark navy + gold, clean lines. Corporate/boardroom.",
        "bg": "#0D1B2A",
        "card_bg": "#1B2838",
        "text": "#FFFFFF",
        "muted": "#8899AA",
        "accent": "#FFB700",
        "accent_dark": "#E5A500",
        "border": "#2D3F52",
        "font_heading": "'Playfair Display', serif",
        "font_body": "'Source Sans 3', sans-serif",
        "font_mono": "'Source Code Pro', monospace",
        "google_fonts": "Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600&family=Source+Code+Pro:wght@400;600",
        "has_terminal_frame": False,
        "heading_transform": "none",
        "heading_spacing": "0",
    },
    "spark": {
        "name": "Spark",
        "description": "Gradient purple/teal, modern curves. Startup/founder.",
        "bg": "#0f0c29",
        "card_bg": "rgba(255,255,255,0.06)",
        "text": "#F0F0F0",
        "muted": "#A0B0C0",
        "accent": "#24C6DC",
        "accent_dark": "#514A9D",
        "border": "rgba(255,255,255,0.1)",
        "font_heading": "'Space Grotesk', sans-serif",
        "font_body": "'Inter', sans-serif",
        "font_mono": "'JetBrains Mono', monospace",
        "google_fonts": "Space+Grotesk:wght@400;700&family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;600",
        "has_terminal_frame": False,
        "heading_transform": "none",
        "heading_spacing": "-0.02em",
    },
    "clean": {
        "name": "Clean",
        "description": "White + charcoal, Swiss-style minimal. Professional/universal.",
        "bg": "#FFFFFF",
        "card_bg": "#F8F8F8",
        "text": "#1A1A1A",
        "muted": "#666666",
        "accent": "#E63946",
        "accent_dark": "#C5303C",
        "border": "#E0E0E0",
        "font_heading": "'DM Sans', sans-serif",
        "font_body": "'DM Sans', sans-serif",
        "font_mono": "'DM Mono', monospace",
        "google_fonts": "DM+Sans:wght@400;700&family=DM+Mono:wght@400",
        "has_terminal_frame": False,
        "heading_transform": "none",
        "heading_spacing": "-0.01em",
    },
}

# ══════════════════════════════════════════════
# SLIDE TYPE DEFINITIONS
# ══════════════════════════════════════════════

SLIDE_TYPES = {
    "title": {
        "name": "Title Slide",
        "description": "Hero opening slide with title, subtitle, and speaker name",
        "fields": ["title", "subtitle", "speaker"],
    },
    "section": {
        "name": "Section Divider",
        "description": "Large heading to introduce a new section of the talk",
        "fields": ["title", "subtitle"],
    },
    "text": {
        "name": "Simple Text",
        "description": "Text slide with heading and bullet points or paragraphs",
        "fields": ["title", "body"],
    },
    "text_and_image": {
        "name": "Text + Image",
        "description": "Split layout: text on left, image on right",
        "fields": ["title", "body", "image_path", "image_caption"],
    },
    "big_number": {
        "name": "Big Number",
        "description": "One massive stat as the hero element with context",
        "fields": ["number", "label", "context"],
    },
    "comparison": {
        "name": "Comparison",
        "description": "Side-by-side columns (before/after, old/new)",
        "fields": ["title", "left_title", "left_items", "right_title", "right_items"],
    },
    "screenshot": {
        "name": "Screenshot",
        "description": "Full-width image with header and caption overlay",
        "fields": ["title", "subtitle", "image_path", "caption"],
    },
    "quote": {
        "name": "Quote",
        "description": "Large pull quote with attribution",
        "fields": ["quote_text", "attribution"],
    },
    "timeline": {
        "name": "Timeline",
        "description": "Step-by-step process or chronological events",
        "fields": ["title", "steps"],
    },
    "qr_code": {
        "name": "QR Code",
        "description": "QR code hero with call to action text and link",
        "fields": ["title", "subtitle", "qr_image_path", "link_text", "cta_text"],
    },
    "closing": {
        "name": "Closing / CTA",
        "description": "Final slide with call to action, links, contact info",
        "fields": ["title", "cta_text", "links", "speaker", "contact"],
    },
}


# ══════════════════════════════════════════════
# BASE STYLES (shared across all themes)
# ══════════════════════════════════════════════

def base_css(t):
    """Generate base CSS from a theme dict."""
    return f"""
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background-color: {t['bg']};
      font-family: {t['font_body']};
      overflow: hidden;
      color: {t['text']};
    }}
    .slide {{
      width: 1280px;
      min-height: 720px;
      background-color: {t['bg']};
      display: flex;
      flex-direction: column;
      padding: 60px;
      position: relative;
    }}
    .slide.center {{
      justify-content: center;
      align-items: center;
      text-align: center;
    }}
    h1 {{
      font-family: {t['font_heading']};
      font-size: 64px;
      font-weight: 900;
      color: {t['text']};
      text-transform: {t['heading_transform']};
      letter-spacing: {t['heading_spacing']};
      line-height: 1.1;
    }}
    h2 {{
      font-family: {t['font_heading']};
      font-size: 48px;
      font-weight: 700;
      color: {t['text']};
      line-height: 1.2;
    }}
    .subtitle {{
      font-size: 28px;
      color: {t['muted']};
      font-family: {t['font_mono']};
    }}
    .accent {{ color: {t['accent']}; }}
    .muted {{ color: {t['muted']}; }}
    .accent-line {{
      height: 3px;
      width: 80px;
      background: {t['accent']};
      margin: 20px auto;
    }}
    .header-bar {{
      border-bottom: 2px solid {t['accent']};
      padding-bottom: 20px;
      margin-bottom: 40px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }}
    .body-text {{
      font-size: 32px;
      line-height: 1.6;
      color: {t['muted']};
    }}
    .body-text li {{
      margin-bottom: 12px;
      list-style: none;
      padding-left: 1.5em;
      position: relative;
    }}
    .body-text li::before {{
      content: "▸";
      color: {t['accent']};
      position: absolute;
      left: 0;
    }}
    .card {{
      background: {t['card_bg']};
      border: 1px solid {t['border']};
      border-radius: 8px;
      padding: 30px;
    }}
    @media print {{
      .slide {{ page-break-after: always; }}
      body {{ background: {t['bg']}; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    }}
    """


def terminal_frame(t, terminal_path="~/presentation"):
    """Generate the terminal window wrapper (only for terminal theme)."""
    if not t.get('has_terminal_frame'):
        return "", ""
    
    open_html = f"""
    <div style="width:1000px; border:1px solid {t['border']}; border-radius:8px;
                background:{t['card_bg']}; box-shadow:0 0 30px rgba(0,230,118,0.1); overflow:hidden;">
      <div style="background:#333; padding:10px 15px; display:flex; align-items:center;
                  border-bottom:1px solid {t['border']};">
        <div style="display:flex; gap:8px;">
          <span style="width:12px;height:12px;border-radius:50%;background:#FF5F56;display:inline-block;"></span>
          <span style="width:12px;height:12px;border-radius:50%;background:#FFBD2E;display:inline-block;"></span>
          <span style="width:12px;height:12px;border-radius:50%;background:#27C93F;display:inline-block;"></span>
        </div>
        <span style="margin-left:15px; font-size:14px; color:{t['muted']};
                     font-family:monospace;">user@stage:{escape(terminal_path)}</span>
      </div>
      <div style="padding:50px 40px; text-align:center;">
    """
    close_html = """
      </div>
    </div>
    """
    return open_html, close_html


# ══════════════════════════════════════════════
# SLIDE GENERATORS
# ══════════════════════════════════════════════

def google_font_link(t):
    return f'<link href="https://fonts.googleapis.com/css2?family={t["google_fonts"]}&display=swap" rel="stylesheet">'

def fa_link():
    return '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">'

def html_doc(t, body_content, extra_css="", center=False):
    """Wrap content in a full HTML document."""
    cls = "slide center" if center else "slide"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{google_font_link(t)}
{fa_link()}
<style>{base_css(t)}{extra_css}</style>
</head>
<body>
<div class="{cls}">
{body_content}
</div>
</body>
</html>"""


def gen_title(t, title="Title", subtitle="", speaker=""):
    tf_open, tf_close = terminal_frame(t, "~/keynote")
    cursor = '<span style="display:inline-block;width:15px;height:72px;background:%s;animation:blink 1s infinite;vertical-align:bottom;margin-left:10px;"></span>' % t['accent'] if t.get('has_terminal_frame') else ""
    blink_css = "@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }" if t.get('has_terminal_frame') else ""
    
    body = f"""
    {tf_open}
    <h1 style="font-size:72px;margin-bottom:20px;">{escape(title)}{cursor}</h1>
    <div class="accent-line"></div>
    <p class="subtitle" style="margin-bottom:40px;">{escape(subtitle)}</p>
    <p class="accent" style="font-size:24px;font-weight:700;{'border-top:1px solid '+t['border']+';padding-top:20px;' if speaker else ''}">{escape(speaker)}</p>
    {tf_close}
    """
    return html_doc(t, body, blink_css, center=True)


def gen_section(t, title="Section", subtitle=""):
    body = f"""
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;">
      <p class="muted subtitle" style="margin-bottom:20px;">{escape(subtitle)}</p>
      <h1 style="font-size:80px;">{escape(title)}</h1>
      <div class="accent-line" style="margin-top:30px;"></div>
    </div>
    """
    return html_doc(t, body)


def gen_text(t, title="Heading", body=""):
    items = [l.strip() for l in body.split('\n') if l.strip()]
    if items:
        list_html = '\n'.join(f'<li>{escape(item.lstrip("- •"))}</li>' for item in items)
        content = f'<ul class="body-text">{list_html}</ul>'
    else:
        content = f'<p class="body-text">{escape(body)}</p>'
    
    body_html = f"""
    <div class="header-bar">
      <h2>{escape(title)}</h2>
    </div>
    <div style="flex:1;display:flex;align-items:center;">
      {content}
    </div>
    """
    return html_doc(t, body_html)


def gen_big_number(t, number="0", label="", context=""):
    body = f"""
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;">
      <p class="muted" style="font-size:28px;margin-bottom:10px;font-family:{t['font_mono']};">{escape(context)}</p>
      <div style="font-size:180px;font-weight:900;color:{t['accent']};font-family:{t['font_mono']};line-height:1;">{escape(str(number))}</div>
      <div style="font-size:40px;color:{t['text']};margin-top:20px;font-weight:700;">{escape(label)}</div>
    </div>
    """
    return html_doc(t, body)


def gen_comparison(t, title="Comparison", left_title="Before", left_items=None, right_title="After", right_items=None):
    left_items = left_items or []
    right_items = right_items or []
    
    def col_html(col_title, items, is_accent=False):
        color = t['accent'] if is_accent else t['muted']
        lis = '\n'.join(f'<li style="margin-bottom:12px;font-size:24px;color:{t["muted"]};">{escape(i)}</li>' for i in items)
        return f"""
        <div class="card" style="flex:1;">
          <h3 style="font-size:32px;color:{color};margin-bottom:20px;text-align:center;font-family:{t['font_heading']};">{escape(col_title)}</h3>
          <ul style="list-style:none;padding-left:1em;">{lis}</ul>
        </div>"""
    
    body = f"""
    <div class="header-bar"><h2>{escape(title)}</h2></div>
    <div style="display:flex;gap:40px;flex:1;align-items:stretch;">
      {col_html(left_title, left_items, False)}
      <div style="width:2px;background:{t['accent']};align-self:stretch;"></div>
      {col_html(right_title, right_items, True)}
    </div>
    """
    return html_doc(t, body)


def gen_screenshot(t, title="Demo", subtitle="", image_path="", caption=""):
    body = f"""
    <div class="header-bar">
      <h2>{escape(title)}</h2>
      <span class="subtitle">{escape(subtitle)}</span>
    </div>
    <div style="flex:1;display:flex;justify-content:center;align-items:center;background:#000;
                border:1px solid {t['border']};border-radius:8px;overflow:hidden;position:relative;">
      <img src="{escape(image_path)}" alt="{escape(caption)}" style="max-width:100%;max-height:450px;object-fit:contain;">
      {'<div style="position:absolute;bottom:20px;right:20px;background:'+t['accent']+';color:'+t['bg']+';padding:10px 20px;font-family:'+t['font_mono']+';font-weight:700;font-size:20px;border-radius:4px;">'+escape(caption)+'</div>' if caption else ''}
    </div>
    """
    return html_doc(t, body)


def gen_quote(t, quote_text="", attribution=""):
    body = f"""
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;max-width:900px;margin:0 auto;">
      <div style="font-size:120px;color:{t['accent']};line-height:0.5;margin-bottom:30px;font-family:serif;">&ldquo;</div>
      <p style="font-size:40px;font-style:italic;line-height:1.5;color:{t['text']};margin-bottom:30px;">{escape(quote_text)}</p>
      <div class="accent-line"></div>
      <p style="font-size:24px;color:{t['muted']};margin-top:20px;">— {escape(attribution)}</p>
    </div>
    """
    return html_doc(t, body)


def gen_timeline(t, title="Timeline", steps=None):
    steps = steps or []
    steps_html = ""
    for i, step in enumerate(steps):
        label = step.get("label", f"Step {i+1}")
        desc = step.get("description", "")
        active = "border-color:" + t['accent'] if i == len(steps) - 1 else ""
        steps_html += f"""
        <div style="flex:1;text-align:center;position:relative;">
          <div style="width:40px;height:40px;border-radius:50%;background:{t['accent'] if i <= len(steps)-1 else t['border']};
                      margin:0 auto 15px;display:flex;align-items:center;justify-content:center;
                      font-weight:700;color:{t['bg']};font-size:18px;">{i+1}</div>
          <div style="font-size:22px;font-weight:700;color:{t['text']};margin-bottom:8px;">{escape(label)}</div>
          <div style="font-size:16px;color:{t['muted']};">{escape(desc)}</div>
        </div>"""
    
    body = f"""
    <div class="header-bar"><h2>{escape(title)}</h2></div>
    <div style="flex:1;display:flex;align-items:center;">
      <div style="display:flex;width:100%;gap:10px;align-items:flex-start;position:relative;">
        <div style="position:absolute;top:20px;left:5%;right:5%;height:2px;background:{t['border']};z-index:0;"></div>
        {steps_html}
      </div>
    </div>
    """
    return html_doc(t, body)


def gen_qr_code(t, title="Scan Me", subtitle="", qr_image_path="", link_text="", cta_text=""):
    body = f"""
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;">
      <h1 style="font-size:72px;margin-bottom:10px;">{escape(title)}</h1>
      <p class="accent" style="font-size:36px;margin-bottom:30px;font-family:{t['font_mono']};">{escape(subtitle)}</p>
      <div style="background:#fff;padding:20px;border-radius:16px;margin-bottom:25px;
                  box-shadow:0 0 40px {'rgba(0,230,118,0.2)' if t.get('has_terminal_frame') else 'rgba(0,0,0,0.1)'};">
        <img src="{escape(qr_image_path)}" alt="QR Code" style="width:280px;height:280px;display:block;">
      </div>
      <div style="background:{'rgba('+t['accent'].lstrip('#')[:2]+','+t['accent'].lstrip('#')[2:4]+','+t['accent'].lstrip('#')[4:]+',0.1)' if len(t['accent'])==7 else t['card_bg']};
                  border:2px solid {t['accent']};padding:15px 30px;border-radius:8px;">
        <span style="font-size:24px;font-family:{t['font_mono']};color:{t['text']};">{escape(link_text)}</span>
      </div>
      <p class="muted" style="margin-top:15px;font-size:22px;"><i class="fas fa-camera"></i>&nbsp; {escape(cta_text)}</p>
    </div>
    """
    return html_doc(t, body)


def gen_closing(t, title="Thank You", cta_text="", links=None, speaker="", contact=""):
    links = links or []
    links_html = '\n'.join(
        f'<a href="{escape(l.get("url","#"))}" style="display:block;color:{t["accent"]};font-size:22px;margin-bottom:8px;text-decoration:none;font-family:{t["font_mono"]};">{escape(l.get("label",""))}</a>'
        for l in links
    )
    
    body = f"""
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;">
      <h1 style="font-size:72px;margin-bottom:15px;">{escape(title)}</h1>
      <div class="accent-line"></div>
      <p style="font-size:32px;color:{t['muted']};margin:20px 0 30px;">{escape(cta_text)}</p>
      <div style="margin-bottom:30px;">{links_html}</div>
      <div style="border-top:1px solid {t['border']};padding-top:20px;">
        <p class="accent" style="font-size:24px;font-weight:700;">{escape(speaker)}</p>
        <p class="muted" style="font-size:18px;margin-top:5px;">{escape(contact)}</p>
      </div>
    </div>
    """
    return html_doc(t, body, center=False)


# ══════════════════════════════════════════════
# CUSTOM STYLE INSTRUCTION SUPPORT
# ══════════════════════════════════════════════

def build_theme_from_instruction(si: dict) -> dict:
    """
    Build a theme dict from a style_instruction object.
    
    style_instruction format (from OpenClaw dev guide):
    {
        "aesthetic_direction": "A stark, high-contrast design for maximum stage presence.",
        "color_palette": "Background: #1A1A1A, Title: #FFFFFF, Body: #B3B3B3, Accent: #00E676",
        "typography": "Font Family: Inter. Headline: 64px, Body: 32px, Caption: 18px."
    }
    """
    import re
    
    # Parse color palette
    palette_str = si.get("color_palette", "")
    colors = {}
    for pair in palette_str.split(","):
        pair = pair.strip()
        match = re.match(r'(\w+)\s*:\s*(#[0-9A-Fa-f]{6})', pair)
        if match:
            colors[match.group(1).lower()] = match.group(2)
    
    bg = colors.get("background", "#1A1A1A")
    title_color = colors.get("title", "#FFFFFF")
    body_color = colors.get("body", "#B3B3B3")
    accent = colors.get("accent", "#00E676")
    
    # Parse typography
    typo_str = si.get("typography", "")
    font_match = re.search(r'Font Family:\s*([^.]+)', typo_str)
    font_family = font_match.group(1).strip() if font_match else "Inter"
    
    # Build google fonts URL-safe name
    gf_name = font_family.replace(" ", "+")
    
    # Determine if dark or light background
    bg_brightness = sum(int(bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    is_dark = bg_brightness < 384
    
    return {
        "name": "Custom",
        "description": si.get("aesthetic_direction", "Custom style"),
        "bg": bg,
        "card_bg": _adjust_brightness(bg, 15 if is_dark else -10),
        "text": title_color,
        "muted": body_color,
        "accent": accent,
        "accent_dark": _adjust_brightness(accent, -20),
        "border": _adjust_brightness(bg, 30 if is_dark else -20),
        "font_heading": f"'{font_family}', sans-serif",
        "font_body": f"'{font_family}', sans-serif",
        "font_mono": "'JetBrains Mono', monospace",
        "google_fonts": f"{gf_name}:wght@400;700;900&family=JetBrains+Mono:wght@400",
        "has_terminal_frame": False,
        "heading_transform": "none",
        "heading_spacing": "-0.01em",
    }


def _adjust_brightness(hex_color: str, amount: int) -> str:
    """Lighten or darken a hex color by amount (positive = lighter)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return "#333333"
    r = max(0, min(255, int(hex_color[0:2], 16) + amount))
    g = max(0, min(255, int(hex_color[2:4], 16) + amount))
    b = max(0, min(255, int(hex_color[4:6], 16) + amount))
    return f"#{r:02x}{g:02x}{b:02x}"


# ══════════════════════════════════════════════
# PLACEHOLDER TEMPLATE SUPPORT
# ══════════════════════════════════════════════

def generate_placeholder_template(slide_type: str, theme_name: str = "terminal") -> str:
    """
    Generate an HTML template with {{PLACEHOLDER}} tokens for a given slide type.
    This follows the OpenClaw dev guide pattern for injectable templates.
    
    Returns HTML with placeholders like {{TITLE}}, {{SUBTITLE}}, {{BODY_TEXT}}, etc.
    that can be replaced via string substitution.
    """
    t = THEMES.get(theme_name, THEMES["terminal"])
    
    placeholder_map = {
        "title": {"title": "{{TITLE}}", "subtitle": "{{SUBTITLE}}", "speaker": "{{SPEAKER}}"},
        "section": {"title": "{{TITLE}}", "subtitle": "{{SUBTITLE}}"},
        "text": {"title": "{{TITLE}}", "body": "{{BODY_TEXT}}"},
        "big_number": {"number": "{{NUMBER}}", "label": "{{LABEL}}", "context": "{{CONTEXT}}"},
        "screenshot": {"title": "{{TITLE}}", "subtitle": "{{SUBTITLE}}", "image_path": "{{IMAGE_SRC}}", "caption": "{{CAPTION}}"},
        "quote": {"quote_text": "{{QUOTE_TEXT}}", "attribution": "{{ATTRIBUTION}}"},
        "qr_code": {"title": "{{TITLE}}", "subtitle": "{{SUBTITLE}}", "qr_image_path": "{{QR_IMAGE_SRC}}", "link_text": "{{LINK_TEXT}}", "cta_text": "{{CTA_TEXT}}"},
        "closing": {"title": "{{TITLE}}", "cta_text": "{{CTA_TEXT}}", "speaker": "{{SPEAKER}}", "contact": "{{CONTACT}}"},
    }
    
    kwargs = placeholder_map.get(slide_type, {})
    kwargs['t'] = t
    
    gen_func = GENERATORS.get(slide_type)
    if gen_func:
        return gen_func(**kwargs)
    return ""


# ══════════════════════════════════════════════
# DISPATCH
# ══════════════════════════════════════════════

GENERATORS = {
    "title": gen_title,
    "section": gen_section,
    "text": gen_text,
    "big_number": gen_big_number,
    "comparison": gen_comparison,
    "screenshot": gen_screenshot,
    "quote": gen_quote,
    "timeline": gen_timeline,
    "qr_code": gen_qr_code,
    "closing": gen_closing,
    "text_and_image": gen_screenshot,  # Alias — uses same layout
}


def main():
    if '--list-themes' in sys.argv:
        print("Available themes:")
        for key, t in THEMES.items():
            print(f"  {key:12s} — {t['description']}")
        return

    if '--list-types' in sys.argv:
        print("Available slide types:")
        for key, s in SLIDE_TYPES.items():
            fields = ', '.join(s['fields'])
            print(f"  {key:18s} — {s['description']}")
            print(f"  {'':18s}   Fields: {fields}")
        return

    # Support --style-instruction JSON for custom themes (handle before argparse)
    cleaned_argv = list(sys.argv[1:])
    if '--style-instruction' in cleaned_argv:
        idx = cleaned_argv.index('--style-instruction')
        if idx + 1 < len(cleaned_argv):
            import json as _json
            try:
                si = _json.loads(cleaned_argv[idx + 1])
                custom = build_theme_from_instruction(si)
                THEMES['custom'] = custom
                print(f"Custom theme loaded: {si.get('aesthetic_direction', 'custom')}")
            except Exception as e:
                print(f"ERROR: Invalid style_instruction JSON: {e}", file=sys.stderr)
                sys.exit(1)
            # Remove from argv so argparse doesn't choke
            del cleaned_argv[idx:idx+2]

    parser = argparse.ArgumentParser(description='Generate themed slide HTML')
    parser.add_argument('--theme', default='terminal', help='Theme name (terminal/executive/spark/clean/custom)')
    parser.add_argument('--type', required=True, choices=list(SLIDE_TYPES.keys()))
    parser.add_argument('--output', default='slide.html')
    parser.add_argument('--placeholder-mode', action='store_true', help='Generate template with {{PLACEHOLDER}} tokens instead of content')
    # Common fields
    parser.add_argument('--title', default='')
    parser.add_argument('--subtitle', default='')
    parser.add_argument('--speaker', default='')
    parser.add_argument('--body', default='')
    parser.add_argument('--number', default='')
    parser.add_argument('--label', default='')
    parser.add_argument('--context', default='')
    parser.add_argument('--image-path', default='')
    parser.add_argument('--caption', default='')
    parser.add_argument('--quote-text', default='')
    parser.add_argument('--attribution', default='')
    parser.add_argument('--link-text', default='')
    parser.add_argument('--cta-text', default='')
    parser.add_argument('--contact', default='')
    
    args = parser.parse_args(cleaned_argv)
    
    if args.theme not in THEMES:
        print(f"ERROR: Unknown theme '{args.theme}'. Available: {', '.join(THEMES.keys())}", file=sys.stderr)
        sys.exit(1)
    
    t = THEMES[args.theme]
    
    # Placeholder mode: generate injectable template
    if args.placeholder_mode:
        html = generate_placeholder_template(args.type, args.theme)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ {args.output} (PLACEHOLDER TEMPLATE — {THEMES[args.theme]['name']} / {SLIDE_TYPES[args.type]['name']})")
        return
    
    gen_func = GENERATORS.get(args.type)
    if not gen_func:
        print(f"ERROR: Unknown type: {args.type}", file=sys.stderr)
        sys.exit(1)
    
    # Build kwargs based on type
    kwargs = {'t': t}
    if args.title: kwargs['title'] = args.title
    if args.subtitle: kwargs['subtitle'] = args.subtitle
    if args.speaker: kwargs['speaker'] = args.speaker
    if args.body: kwargs['body'] = args.body
    if args.number: kwargs['number'] = args.number
    if args.label: kwargs['label'] = args.label
    if args.context: kwargs['context'] = args.context
    if args.image_path: kwargs['image_path'] = args.image_path
    if args.caption: kwargs['caption'] = args.caption
    if args.quote_text: kwargs['quote_text'] = args.quote_text
    if args.attribution: kwargs['attribution'] = args.attribution
    if args.link_text: kwargs['link_text'] = args.link_text
    if args.cta_text: kwargs['cta_text'] = args.cta_text
    if args.contact: kwargs['contact'] = args.contact
    
    html = gen_func(**kwargs)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ {args.output} ({THEMES[args.theme]['name']} / {SLIDE_TYPES[args.type]['name']})")


if __name__ == '__main__':
    main()
