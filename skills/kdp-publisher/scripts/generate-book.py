#!/usr/bin/env python3
"""
KDP Book Generator — generate-book.py
Generates KDP-ready print books using Google Gemini (text) and Imagen (illustrations).

Supported book types:
  picture-book  — Children's illustrated story (8.5x8.5, full color)
  activity-book — Kids activity pages (8.5x11, color)
  coloring-book — Line art coloring pages (8.5x11, B&W)
  workbook      — Math/practice workbook (8.5x11, B&W)

Usage:
  python3 generate-book.py "a brave fox who learns kindness" --type picture-book
  python3 generate-book.py "addition facts 1-20" --type workbook --grade 1
  python3 generate-book.py --help
"""

import os
import sys
import json
import time
import argparse
import re
import io
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


# ─── Dependency check ────────────────────────────────────────────────────────

def check_deps():
    missing = []
    try:
        from reportlab.lib.pagesizes import inch
    except ImportError:
        missing.append("reportlab")
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    try:
        import google.genai
    except ImportError:
        missing.append("google-genai")
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print(f"   Run: pip install {' '.join(missing)}")
        sys.exit(1)

check_deps()

from reportlab.lib.pagesizes import inch as INCH
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import google.genai as genai


# ─── Constants ───────────────────────────────────────────────────────────────

BOOK_CONFIGS = {
    "picture-book": {
        "trim": (8.5 * INCH, 8.5 * INCH),
        "margin": 0.25 * INCH,
        "gutter": 0.625 * INCH,
        "color": True,
        "aspect_ratio": "1:1",
        "min_pages": 24,
        "max_pages": 32,
        "description": "Children's illustrated picture book (8.5×8.5, full color)",
    },
    "activity-book": {
        "trim": (8.5 * INCH, 11.0 * INCH),
        "margin": 0.5 * INCH,
        "gutter": 0.75 * INCH,
        "color": True,
        "aspect_ratio": "3:4",
        "min_pages": 50,
        "max_pages": 80,
        "description": "Kids activity book (8.5×11, color)",
    },
    "coloring-book": {
        "trim": (8.5 * INCH, 11.0 * INCH),
        "margin": 0.5 * INCH,
        "gutter": 0.75 * INCH,
        "color": False,
        "aspect_ratio": "3:4",
        "min_pages": 40,
        "max_pages": 60,
        "description": "Coloring book (8.5×11, B&W line art)",
    },
    "workbook": {
        "trim": (8.5 * INCH, 11.0 * INCH),
        "margin": 1.0 * INCH,
        "gutter": 1.0 * INCH,
        "color": False,
        "aspect_ratio": None,
        "min_pages": 80,
        "max_pages": 150,
        "description": "Math/practice workbook (8.5×11, B&W)",
    },
}

STYLE_PRESETS = {
    "watercolor": "children's book illustration, soft watercolor painting, gentle pastel colors, whimsical, no text, no words, no letters",
    "cartoon": "children's book illustration, bright bold cartoon style, vibrant colors, clean lines, no text, no words, no letters",
    "digital": "children's book illustration, smooth digital painting, modern clean style, no text, no words, no letters",
    "line-art": "simple black and white coloring book page, thick clean lines, no shading, no gray tones, white background, no text, no words",
}

AGE_CONFIGS = {
    "3-5": {"words_per_page": "10-20", "complexity": "very simple sentences, repetitive structure, one idea per page"},
    "5-8": {"words_per_page": "20-40", "complexity": "simple sentences, clear story arc, relatable situations"},
}

DEFAULT_AUTHOR = os.environ.get("KDP_AUTHOR_NAME", "Your Name")
IMAGE_SIZE = 1024


# ─── Utilities ───────────────────────────────────────────────────────────────

def load_api_key(api_key_arg: Optional[str]) -> str:
    """Load Google AI API key from arg, env var, or credentials file."""
    key = api_key_arg or os.environ.get("GOOGLE_AI_API_KEY")
    if key:
        return key
    creds_path = Path.home() / ".clawdbot" / "credentials" / "google_ai.json"
    if creds_path.exists():
        with open(creds_path) as f:
            return json.load(f).get("api_key", "")
    print("❌ No API key found.")
    print("   Provide --api-key, set GOOGLE_AI_API_KEY env var, or create")
    print("   ~/.clawdbot/credentials/google_ai.json with {\"api_key\": \"...\"}")
    sys.exit(1)


def slugify(text: str) -> str:
    """Convert text to filesystem-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-")[:60]


def wrap_text(c, text: str, max_width: float, font_name: str, font_size: int) -> List[str]:
    """Word-wrap text to fit within max_width."""
    words = text.split()
    lines, current = [], []
    for word in words:
        test = " ".join(current + [word])
        if c.stringWidth(test, font_name, font_size) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def try_register_font(font_name: str, bold: bool = False) -> str:
    """Try to register a system TTF font; fall back to Helvetica."""
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
        f"/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            reg_name = f"CustomFont{'Bold' if bold else ''}"
            try:
                pdfmetrics.registerFont(TTFont(reg_name, path))
                return reg_name
            except Exception:
                pass
    return "Helvetica-Bold" if bold else "Helvetica"


# ─── Core Classes ─────────────────────────────────────────────────────────────

class StoryGenerator:
    """Generates story content via Google Gemini."""

    def __init__(self, client):
        self.client = client

    def generate(self, prompt: str, book_type: str, age_group: str = "3-5",
                 num_spreads: int = 12, grade: int = None) -> Dict:
        """Generate story/content structure for the given book type."""

        if book_type == "workbook":
            return self._generate_workbook(prompt, grade or 1)
        elif book_type == "coloring-book":
            return self._generate_coloring_book(prompt, num_spreads)
        elif book_type == "activity-book":
            return self._generate_activity_book(prompt, age_group, num_spreads)
        else:
            return self._generate_picture_book(prompt, age_group, num_spreads)

    def _generate_picture_book(self, prompt: str, age_group: str, num_spreads: int) -> Dict:
        age_cfg = AGE_CONFIGS.get(age_group, AGE_CONFIGS["3-5"])
        story_prompt = f"""Write a children's picture book for ages {age_group} about: {prompt}

Rules:
- Title: catchy, max 60 characters
- Exactly {num_spreads} spreads
- Each spread: {age_cfg['words_per_page']} words of story text
- Sentence style: {age_cfg['complexity']}
- Include a positive moral/lesson
- Content: kid-safe, no scary themes
- Each spread has a distinct, illustratable scene (NO text in scenes)

Respond ONLY with valid JSON (no markdown fences):
{{
  "title": "...",
  "subtitle": "...",
  "moral": "...",
  "dedication": "...",
  "description": "2-3 sentence back-cover description",
  "keywords": ["kw1","kw2","kw3","kw4","kw5","kw6","kw7"],
  "spreads": [
    {{"page": 1, "text": "...", "scene": "Illustration description, no text in image"}},
    ...
  ]
}}"""

        return self._call_gemini(story_prompt, f"picture book: {prompt}")

    def _generate_coloring_book(self, prompt: str, num_pages: int) -> Dict:
        cb_prompt = f"""Create a coloring book with {num_pages} pages themed around: {prompt}

Each page is a distinct scene or subject for coloring. Keep descriptions suitable for ages 4-10.

Respond ONLY with valid JSON:
{{
  "title": "...",
  "subtitle": "...",
  "description": "2-3 sentence description",
  "keywords": ["kw1","kw2","kw3","kw4","kw5","kw6","kw7"],
  "pages": [
    {{"page": 1, "scene": "Simple illustration description for line art, no text in image"}},
    ...
  ]
}}"""
        return self._call_gemini(cb_prompt, f"coloring book: {prompt}")

    def _generate_activity_book(self, prompt: str, age_group: str, num_pages: int) -> Dict:
        act_prompt = f"""Plan an activity book for ages {age_group} about: {prompt}
{num_pages} activity pages total. Variety: I Spy, matching, mazes, counting, coloring.

Respond ONLY with valid JSON:
{{
  "title": "...",
  "subtitle": "...",
  "description": "2-3 sentence description",
  "keywords": ["kw1","kw2","kw3","kw4","kw5","kw6","kw7"],
  "pages": [
    {{"page": 1, "activity_type": "i-spy", "title": "I Spy on the Farm!", "scene": "Detailed illustration description, no text in image", "instruction": "Can you find 5 chickens?"}},
    ...
  ]
}}"""
        return self._call_gemini(act_prompt, f"activity book: {prompt}")

    def _generate_workbook(self, prompt: str, grade: int) -> Dict:
        wb_prompt = f"""Plan a math workbook for Grade {grade} covering: {prompt}

Include sections with specific problem types. Problems must be appropriate for grade {grade}.

Respond ONLY with valid JSON:
{{
  "title": "Grade {grade} {prompt.title()} Workbook",
  "subtitle": "...",
  "description": "2-3 sentence description for parents and teachers",
  "keywords": ["kw1","kw2","kw3","kw4","kw5","kw6","kw7"],
  "sections": [
    {{
      "title": "Section 1: ...",
      "pages": 20,
      "problem_type": "addition",
      "difficulty": "easy",
      "sample_problems": ["3 + 4 = ___", "7 + 2 = ___", "5 + 5 = ___"]
    }},
    ...
  ],
  "has_answer_key": true
}}"""
        return self._call_gemini(wb_prompt, f"workbook: grade {grade} {prompt}")

    def _call_gemini(self, prompt: str, fallback_context: str) -> Dict:
        """Call Gemini and parse JSON response."""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            text = response.text.strip()
            # Strip markdown fences if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            data = json.loads(text)
            print(f"✓ Content generated: '{data.get('title', 'Untitled')}'")
            return data
        except Exception as e:
            print(f"⚠ Content generation failed ({e}), using fallback structure")
            return self._fallback(fallback_context)

    def _fallback(self, context: str) -> Dict:
        return {
            "title": context.title()[:60],
            "subtitle": "",
            "moral": "Every day is a chance to grow.",
            "dedication": "For curious minds everywhere.",
            "description": f"A wonderful book about {context}.",
            "keywords": ["children", "kids", "picture book", "bedtime", "story", "educational", "fun"],
            "spreads": [
                {"page": i + 1, "text": f"Page {i + 1} of our story...", "scene": f"Scene {i + 1}"}
                for i in range(12)
            ],
        }


class ImageGenerator:
    """Generates illustrations using Google Imagen."""

    def __init__(self, client, model: str = "imagen-4.0-fast-generate-001"):
        self.client = client
        self.model = model

    def generate(self, scene: str, style: str = "watercolor",
                 character_ref: str = "", aspect_ratio: str = "1:1",
                 retries: int = 3) -> Optional[Image.Image]:
        """Generate a single illustration."""
        style_prefix = STYLE_PRESETS.get(style, STYLE_PRESETS["watercolor"])
        char_part = f"{character_ref}, " if character_ref else ""
        full_prompt = (
            f"{style_prefix}, {char_part}{scene}, "
            f"suitable for children, no text, no words, no writing, clean composition"
        )

        for attempt in range(retries):
            try:
                resp = self.client.models.generate_images(
                    model=self.model,
                    prompt=full_prompt,
                    config={"number_of_images": 1, "aspect_ratio": aspect_ratio},
                )
                if resp.generated_images:
                    data = resp.generated_images[0].image.image_bytes
                    img = Image.open(io.BytesIO(data)).convert("RGB")
                    print(f"     ✓ {img.size[0]}×{img.size[1]} px")
                    return img
            except Exception as e:
                err = str(e).lower()
                if "quota" in err or "rate" in err:
                    wait = (attempt + 1) * 10
                    print(f"     ⚠ Rate limit, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"     ⚠ Error: {e}")
                    if attempt < retries - 1:
                        time.sleep(3)

        print("     ⚠ Using placeholder image")
        return self._placeholder(scene)

    def _placeholder(self, text: str) -> Image.Image:
        """Create a simple placeholder image."""
        from PIL import ImageDraw
        img = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), "#EEF4FB")
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, IMAGE_SIZE - 20, IMAGE_SIZE - 20], outline="#4A90E2", width=5)
        # Simple center text
        draw.text((IMAGE_SIZE // 2, IMAGE_SIZE // 2), text[:40], fill="#4A90E2", anchor="mm")
        return img


class PDFAssembler:
    """Assembles KDP-ready interior PDFs."""

    def __init__(self, book_type: str, author: str = DEFAULT_AUTHOR):
        self.config = BOOK_CONFIGS[book_type]
        self.book_type = book_type
        self.author = author
        self.width, self.height = self.config["trim"]
        self.margin = self.config["margin"]

    def assemble(self, content: Dict, images: List[Image.Image], out_path: Path) -> int:
        """Build the interior PDF. Returns final page count."""
        c = pdf_canvas.Canvas(str(out_path), pagesize=self.config["trim"])

        if self.book_type == "picture-book":
            return self._assemble_picture_book(c, content, images, out_path)
        elif self.book_type in ("activity-book", "coloring-book"):
            return self._assemble_image_book(c, content, images, out_path)
        elif self.book_type == "workbook":
            return self._assemble_workbook(c, content, out_path)
        else:
            c.save()
            return 0

    def _assemble_picture_book(self, c, content: Dict, images: List[Image.Image],
                                out_path: Path) -> int:
        w, h = self.width, self.height
        m = self.margin

        # Page 1: Title page
        c.setFillColor(HexColor("#2C5F8A"))
        c.rect(0, 0, w, h, fill=1, stroke=0)
        title = content.get("title", "Untitled")
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 36)
        title_lines = wrap_text(c, title, w - 2 * m, "Helvetica-Bold", 36)
        y = h * 0.65 + (len(title_lines) * 22)
        for line in title_lines:
            c.drawCentredString(w / 2, y, line)
            y -= 44
        if content.get("subtitle"):
            c.setFont("Helvetica", 22)
            c.drawCentredString(w / 2, h * 0.48, content["subtitle"])
        c.setFont("Helvetica", 18)
        c.drawCentredString(w / 2, h * 0.3, f"by {self.author}")
        c.showPage()

        # Page 2: Dedication
        c.setFillColor(white)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        dedication = content.get("dedication", "For curious minds everywhere.")
        c.setFillColor(HexColor("#555555"))
        c.setFont("Helvetica-Oblique", 18)
        ded_lines = wrap_text(c, dedication, w - 2 * m, "Helvetica-Oblique", 18)
        y = h * 0.55 + (len(ded_lines) * 12)
        for line in ded_lines:
            c.drawCentredString(w / 2, y, line)
            y -= 26
        c.showPage()

        # Story spreads
        spreads = content.get("spreads", [])
        for idx, spread in enumerate(spreads):
            # Illustration page
            if idx < len(images):
                self._draw_image_page(c, images[idx])
            else:
                c.setFillColor(HexColor("#F0F8FF"))
                c.rect(0, 0, w, h, fill=1, stroke=0)
            c.showPage()

            # Text page
            c.setFillColor(white)
            c.rect(0, 0, w, h, fill=1, stroke=0)
            text = spread.get("text", "")
            c.setFillColor(black)
            c.setFont("Helvetica", 22)
            lines = wrap_text(c, text, w - 2 * m, "Helvetica", 22)
            total_h = len(lines) * 34
            y = h / 2 + total_h / 2
            for line in lines:
                c.drawCentredString(w / 2, y, line)
                y -= 34
            c.showPage()

        # "The End" page
        c.setFillColor(HexColor("#2C5F8A"))
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 72)
        c.drawCentredString(w / 2, h / 2, "The End")
        c.showPage()

        # About the Author page
        c.setFillColor(white)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(HexColor("#2C5F8A"))
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(w / 2, h * 0.72, f"About the Author")
        c.setFillColor(HexColor("#444444"))
        c.setFont("Helvetica", 14)
        bio = (
            f"{self.author} writes stories that help children "
            "discover their inner strength and embrace who they are."
        )
        bio_lines = wrap_text(c, bio, w - 2 * m, "Helvetica", 14)
        y = h * 0.62
        for line in bio_lines:
            c.drawCentredString(w / 2, y, line)
            y -= 22

        # Review request
        c.setFont("Helvetica-Oblique", 11)
        c.setFillColor(HexColor("#888888"))
        c.drawCentredString(w / 2, h * 0.25, "If you enjoyed this book, please leave a review on Amazon!")
        c.showPage()

        # Pad to minimum page count
        page_count = c.getPageNumber() - 1
        min_pages = self.config["min_pages"]
        while page_count < min_pages:
            c.showPage()
            page_count += 1

        c.save()
        print(f"✓ Interior PDF: {out_path} ({page_count} pages)")
        return page_count

    def _assemble_image_book(self, c, content: Dict, images: List[Image.Image],
                              out_path: Path) -> int:
        w, h = self.width, self.height
        m = self.margin

        # Title page
        c.setFillColor(HexColor("#1A1A2E"))
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 42)
        c.drawCentredString(w / 2, h * 0.6, content.get("title", "Untitled"))
        c.setFont("Helvetica", 20)
        c.drawCentredString(w / 2, h * 0.5, f"by {self.author}")
        c.showPage()

        pages = content.get("pages", [])
        for idx, page in enumerate(pages):
            c.setFillColor(white)
            c.rect(0, 0, w, h, fill=1, stroke=0)

            # Page title/instruction
            instruction = page.get("instruction") or page.get("title", "")
            if instruction:
                c.setFillColor(HexColor("#2C5F8A"))
                c.setFont("Helvetica-Bold", 18)
                inst_lines = wrap_text(c, instruction, w - 2 * m, "Helvetica-Bold", 18)
                y = h - m - 10
                for line in inst_lines:
                    c.drawCentredString(w / 2, y, line)
                    y -= 24

            # Illustration
            if idx < len(images):
                img_top = h - m - (len(inst_lines) * 24 + 20 if instruction else 0) - 10
                img_bottom = m
                img_h = img_top - img_bottom
                self._draw_image_region(c, images[idx], m, img_bottom, w - 2 * m, img_h)
            c.showPage()

        # Back matter
        self._add_back_matter(c, content)

        page_count = c.getPageNumber() - 1
        min_pages = self.config["min_pages"]
        while page_count < min_pages:
            c.showPage()
            page_count += 1

        c.save()
        print(f"✓ Interior PDF: {out_path} ({page_count} pages)")
        return page_count

    def _assemble_workbook(self, c, content: Dict, out_path: Path) -> int:
        w, h = self.width, self.height
        m = self.margin

        # Title page
        c.setFillColor(white)
        c.setFillColor(HexColor("#003366"))
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 36)
        title_lines = wrap_text(c, content.get("title", "Workbook"), w - 2 * m, "Helvetica-Bold", 36)
        y = h * 0.65
        for line in title_lines:
            c.drawCentredString(w / 2, y, line)
            y -= 44
        c.setFont("Helvetica", 20)
        c.drawCentredString(w / 2, h * 0.42, f"by {self.author}")
        c.drawCentredString(w / 2, h * 0.35, "Name: _______________________________")
        c.showPage()

        # Sections
        for section in content.get("sections", []):
            # Section header page
            c.setFillColor(HexColor("#003366"))
            c.rect(0, 0, w, 1.5 * INCH, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(w / 2, 1.5 * INCH - 28, section.get("title", "Section"))

            # Generate sample problem pages
            problems = section.get("sample_problems", [])
            if not problems:
                problems = [f"Problem {i + 1}" for i in range(10)]

            # Render problems in a grid
            c.setFillColor(black)
            cols = 2
            col_w = (w - 2 * m) / cols
            row_h = 1.0 * INCH
            x_starts = [m + i * col_w for i in range(cols)]
            y = h - 2.5 * INCH
            col = 0
            for i, prob in enumerate(problems):
                if y < m + row_h:
                    c.showPage()
                    y = h - m
                    col = 0

                x = x_starts[col]
                # Problem number
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x, y, f"{i + 1}.")
                # Problem text
                c.setFont("Helvetica", 20)
                c.drawString(x + 0.25 * INCH, y, prob)
                # Answer line — DO NOT add a separate line below equations
                # (kids write directly below/on the existing line structure)
                y -= row_h
                col = (col + 1) % cols
                if col == 0:
                    pass  # y already decremented

            c.showPage()

        # Answer key
        if content.get("has_answer_key"):
            c.setFillColor(HexColor("#F0F0F0"))
            c.rect(0, 0, w, h, fill=1, stroke=0)
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 28)
            c.drawCentredString(w / 2, h * 0.9, "Answer Key")
            c.setFont("Helvetica", 12)
            c.drawCentredString(w / 2, h * 0.82, "(Answers will vary based on generated content)")
            c.showPage()

        page_count = c.getPageNumber() - 1
        min_pages = self.config["min_pages"]
        while page_count < min_pages:
            c.showPage()
            page_count += 1

        c.save()
        print(f"✓ Interior PDF: {out_path} ({page_count} pages)")
        return page_count

    def _draw_image_page(self, c, img: Image.Image):
        """Draw a full-page illustration within safe margins."""
        w, h = self.width, self.height
        m = self.margin
        self._draw_image_region(c, img, m, m, w - 2 * m, h - 2 * m)

    def _draw_image_region(self, c, img: Image.Image, x: float, y: float,
                            max_w: float, max_h: float):
        """Draw an image within a specified region, preserving aspect ratio."""
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        reader = ImageReader(buf)
        c.drawImage(reader, x, y, max_w, max_h, preserveAspectRatio=True, anchor="c")

    def _add_back_matter(self, c, content: Dict):
        """Add a simple back matter / copyright page."""
        w, h = self.width, self.height
        m = self.margin
        c.setFillColor(white)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(HexColor("#888888"))
        c.setFont("Helvetica", 10)
        lines = [
            content.get("title", ""),
            f"Copyright © {datetime.now().year} {self.author}",
            "All rights reserved.",
            "Printed in the United States of America",
        ]
        y = h / 2 + 30
        for line in lines:
            c.drawCentredString(w / 2, y, line)
            y -= 18
        c.showPage()


# ─── Main Pipeline ────────────────────────────────────────────────────────────

class BookGenerator:
    """Orchestrates the full book generation pipeline."""

    def __init__(self, api_key: str, output_dir: str = "output",
                 book_type: str = "picture-book", author: str = DEFAULT_AUTHOR):
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.book_type = book_type
        self.author = author
        self.config = BOOK_CONFIGS[book_type]

        client = genai.Client(api_key=api_key)
        self.story_gen = StoryGenerator(client)
        self.image_gen = ImageGenerator(client)
        self.pdf = PDFAssembler(book_type, author)

        print(f"✓ Book type: {self.config['description']}")

    def generate(self, prompt: str, age_group: str = "3-5", style: str = "watercolor",
                 num_spreads: int = 12, grade: int = 1, skip_images: bool = False) -> Path:
        """Run the full pipeline. Returns the book output directory."""
        print(f"\n{'='*60}")
        print("KDP BOOK GENERATOR")
        print(f"{'='*60}")
        print(f"Prompt : {prompt}")
        print(f"Type   : {self.book_type}")
        if self.book_type == "picture-book":
            print(f"Ages   : {age_group}  |  Style: {style}")
        if self.book_type == "workbook":
            print(f"Grade  : {grade}")

        # 1. Generate content structure
        print("\n📖 Generating content structure...")
        content = self.story_gen.generate(prompt, self.book_type, age_group, num_spreads, grade)

        # 2. Set up output directory
        slug = slugify(content.get("title", prompt))
        book_dir = self.output_dir / slug
        book_dir.mkdir(parents=True, exist_ok=True)
        images_dir = book_dir / "images"
        images_dir.mkdir(exist_ok=True)
        print(f"\n📁 Output: {book_dir}")

        # 3. Generate illustrations
        images = []
        if self.book_type != "workbook":
            pages_to_illustrate = content.get("spreads") or content.get("pages") or []
            total = len(pages_to_illustrate)
            aspect = self.config.get("aspect_ratio", "1:1")
            style_key = "line-art" if self.book_type == "coloring-book" else style

            if not skip_images and total > 0:
                print(f"\n🎨 Generating {total} illustrations...")
                char_ref = f"consistent character style for: {prompt}" if self.book_type == "picture-book" else ""

                for idx, page in enumerate(pages_to_illustrate):
                    scene = page.get("scene", f"Scene {idx + 1}")
                    print(f"\n  [{idx+1}/{total}] {scene[:60]}...")
                    img = self.image_gen.generate(scene, style_key, char_ref, aspect)
                    if img:
                        img_path = images_dir / f"page_{idx+1:02d}.png"
                        img.save(img_path, "PNG")
                        images.append(img)
                    if idx < total - 1:
                        time.sleep(2)  # Rate limiting

                # Cover illustration
                print(f"\n  [cover] Generating cover image...")
                cover_scene = f"book cover: {prompt}, inviting, exciting"
                cover_img = self.image_gen.generate(cover_scene, style_key, "", aspect)
                if cover_img:
                    cover_img.save(images_dir / "cover.png", "PNG")
            else:
                print("\n⚠ Skipping image generation (--skip-images)")
                for idx, page in enumerate(pages_to_illustrate):
                    scene = page.get("scene", f"Scene {idx + 1}")
                    img = self.image_gen._placeholder(scene)
                    img_path = images_dir / f"page_{idx+1:02d}.png"
                    img.save(img_path, "PNG")
                    images.append(img)

        # 4. Assemble interior PDF
        print("\n📄 Assembling interior PDF...")
        interior_path = book_dir / "interior.pdf"
        page_count = self.pdf.assemble(content, images, interior_path)

        # 5. Save metadata
        metadata = {
            "title": content.get("title", ""),
            "subtitle": content.get("subtitle", ""),
            "author": self.author,
            "description": content.get("description", ""),
            "keywords": content.get("keywords", [])[:7],
            "book_type": self.book_type,
            "page_count": page_count,
            "trim_size": f"{self.config['trim'][0]/INCH:.1f}x{self.config['trim'][1]/INCH:.1f}",
            "color_interior": self.config["color"],
            "age_group": age_group if self.book_type == "picture-book" else "",
            "grade": grade if self.book_type == "workbook" else None,
            "created_at": datetime.now().isoformat(),
            "ai_disclosure": True,
        }
        meta_path = book_dir / "metadata.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # 6. Save story JSON for portal compatibility
        story_json = {
            "id": slug,
            "title": content.get("title", ""),
            "content": "\n\n".join(
                s.get("text", "") for s in content.get("spreads", [])
            ),
            "moral": content.get("moral", ""),
            "metadata": {
                "author": self.author,
                "page_count": page_count,
                "images": [f"images/page_{i+1:02d}.png" for i in range(len(images))],
            },
        }
        with open(book_dir / "story.json", "w") as f:
            json.dump(story_json, f, indent=2)

        print(f"\n{'='*60}")
        print("✅ BOOK GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"  Title      : {content.get('title')}")
        print(f"  Pages      : {page_count}")
        print(f"  Interior   : {interior_path.name}")
        print(f"  Metadata   : {meta_path.name}")
        print(f"  Images     : {len(images)}")
        print(f"\nNext step: python3 create-cover.py --title \"{content.get('title')}\" "
              f"--author \"{self.author}\" --pages {page_count}")
        print(f"Then:      python3 validate-book.py --interior {interior_path}")
        print(f"{'='*60}\n")

        return book_dir


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="KDP Book Generator — create KDP-ready books with AI content and illustrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate-book.py "a brave fox who learns kindness" --type picture-book --age-group 3-5
  python3 generate-book.py "ocean animals" --type coloring-book --spreads 40
  python3 generate-book.py "addition and subtraction" --type workbook --grade 1
  python3 generate-book.py "I Spy on the farm" --type activity-book --skip-images
""",
    )
    parser.add_argument("prompt", help="Book concept or topic")
    parser.add_argument(
        "--type",
        choices=list(BOOK_CONFIGS.keys()),
        default="picture-book",
        help="Book type (default: picture-book)",
    )
    parser.add_argument(
        "--age-group",
        choices=["3-5", "5-8"],
        default="3-5",
        help="Target age group for picture/activity books (default: 3-5)",
    )
    parser.add_argument(
        "--style",
        choices=list(STYLE_PRESETS.keys()),
        default="watercolor",
        help="Illustration style (default: watercolor)",
    )
    parser.add_argument(
        "--spreads",
        type=int,
        default=12,
        help="Number of story spreads / illustration pages (default: 12)",
    )
    parser.add_argument(
        "--grade",
        type=int,
        default=1,
        help="Grade level for workbooks (default: 1)",
    )
    parser.add_argument(
        "--author",
        default=os.environ.get("KDP_AUTHOR_NAME", DEFAULT_AUTHOR),
        help="Author name (default: from KDP_AUTHOR_NAME env var)",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory (default: output/)",
    )
    parser.add_argument(
        "--api-key",
        help="Google AI API key (or use GOOGLE_AI_API_KEY env var)",
    )
    parser.add_argument(
        "--skip-images",
        action="store_true",
        help="Skip image generation, use placeholder images",
    )

    args = parser.parse_args()
    api_key = load_api_key(args.api_key)

    gen = BookGenerator(
        api_key=api_key,
        output_dir=args.output_dir,
        book_type=args.type,
        author=args.author,
    )
    gen.generate(
        prompt=args.prompt,
        age_group=args.age_group,
        style=args.style,
        num_spreads=args.spreads,
        grade=args.grade,
        skip_images=args.skip_images,
    )


if __name__ == "__main__":
    main()
