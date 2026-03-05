#!/usr/bin/env python3
"""
KDP Book Validator — validate-book.py
Pre-upload quality checker for KDP book files.

Checks:
  - Interior PDF: page count, trim dimensions, image resolution
  - Cover PDF: dimensions match expected for page count + trim size
  - Metadata: required fields present
  - Images: checks for AI text artifacts (uses Gemini Vision if API key available)
  - Story consistency: description references match story content

Usage:
  python3 validate-book.py --interior output/my-book/interior.pdf
  python3 validate-book.py \\
      --interior output/my-book/interior.pdf \\
      --cover output/my-book/cover.pdf \\
      --metadata output/my-book/metadata.json \\
      --images output/my-book/images/ \\
      --check-text-in-images
  python3 validate-book.py --help
"""

import argparse
import json
import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ─── Dependency check ─────────────────────────────────────────────────────────

def check_deps():
    missing = []
    try:
        import PyPDF2
    except ImportError:
        missing.append("PyPDF2")
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print(f"   Run: pip install {' '.join(missing)}")
        sys.exit(1)

check_deps()

import PyPDF2
from PIL import Image


# ─── KDP Specs ───────────────────────────────────────────────────────────────

KDP_TRIM_SIZES = {
    "8.5x8.5":  (612.0, 612.0),    # 8.5" × 8.5" in points
    "8.5x11":   (612.0, 792.0),
    "6x9":      (432.0, 648.0),
    "5.5x8.5":  (396.0, 612.0),
    "7x10":     (504.0, 720.0),
}

SPINE_WIDTH_PER_PAGE = {
    "white-bw":    0.002252,
    "cream-bw":    0.002500,
    "white-color": 0.002347,
}

BLEED_IN = 0.125
MIN_IMAGE_DPI = 300
PAGE_COUNT_MIN = {
    "picture-book": 24,
    "activity-book": 40,
    "coloring-book": 30,
    "workbook": 60,
}
PAGE_COUNT_MAX = {
    "picture-book": 32,
    "activity-book": 100,
    "coloring-book": 80,
    "workbook": 200,
}


# ─── Validators ──────────────────────────────────────────────────────────────

class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def error(self, msg: str):
        self.errors.append(msg)
        print(f"  ❌ {msg}")

    def warn(self, msg: str):
        self.warnings.append(msg)
        print(f"  ⚠  {msg}")

    def ok(self, msg: str):
        self.passed.append(msg)
        print(f"  ✓  {msg}")

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def validate_interior_pdf(pdf_path: Path, book_type: str, trim_key: str,
                           result: ValidationResult) -> int:
    """Validate interior PDF. Returns page count."""
    print(f"\n📄 Interior PDF: {pdf_path.name}")

    if not pdf_path.exists():
        result.error(f"File not found: {pdf_path}")
        return 0

    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            page_count = len(reader.pages)

        result.ok(f"PDF opens successfully ({page_count} pages)")

        # Page count check
        min_p = PAGE_COUNT_MIN.get(book_type, 24)
        max_p = PAGE_COUNT_MAX.get(book_type, 32)
        if page_count < min_p:
            result.error(f"Page count {page_count} is below minimum {min_p} for {book_type}")
        elif page_count > max_p:
            result.warn(f"Page count {page_count} exceeds typical max {max_p} for {book_type} — ok if intentional")
        else:
            result.ok(f"Page count {page_count} within range ({min_p}-{max_p})")

        # Page count must be even (for spreads)
        if page_count % 2 != 0:
            result.warn(f"Page count {page_count} is odd — KDP prefers even page counts for print")

        # Dimension check (check first page)
        if page_count > 0:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                page = reader.pages[0]
                w = float(page.mediabox.width)
                h = float(page.mediabox.height)

            expected_w, expected_h = KDP_TRIM_SIZES.get(trim_key, (612.0, 612.0))
            tol = 2.0  # 2pt tolerance

            if abs(w - expected_w) <= tol and abs(h - expected_h) <= tol:
                result.ok(f"Page dimensions match {trim_key} ({w:.1f}×{h:.1f} pt)")
            else:
                result.error(
                    f"Page dimensions {w:.1f}×{h:.1f} pt don't match {trim_key} "
                    f"(expected {expected_w:.1f}×{expected_h:.1f} pt)"
                )

        return page_count

    except Exception as e:
        result.error(f"Could not read PDF: {e}")
        return 0


def validate_cover_pdf(cover_path: Path, page_count: int, trim_key: str,
                        paper: str, result: ValidationResult):
    """Validate cover PDF dimensions."""
    print(f"\n📕 Cover PDF: {cover_path.name}")

    if not cover_path.exists():
        result.error(f"File not found: {cover_path}")
        return

    try:
        with open(cover_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            if len(reader.pages) != 1:
                result.warn(f"Cover PDF has {len(reader.pages)} pages (expected 1)")
            page = reader.pages[0]
            w_pt = float(page.mediabox.width)
            h_pt = float(page.mediabox.height)

        result.ok(f"Cover PDF dimensions: {w_pt:.2f}×{h_pt:.2f} pt")

        trim_w, trim_h = KDP_TRIM_SIZES.get(trim_key, (612.0, 612.0))
        trim_w_in = trim_w / 72
        trim_h_in = trim_h / 72

        # Calculate expected cover dimensions
        spine_in = page_count * SPINE_WIDTH_PER_PAGE.get(paper, SPINE_WIDTH_PER_PAGE["white-color"])
        expected_w_in = trim_w_in + spine_in + trim_w_in + (2 * BLEED_IN)
        expected_h_in = trim_h_in + (2 * BLEED_IN)
        expected_w_pt = expected_w_in * 72
        expected_h_pt = expected_h_in * 72

        tol = 5.0  # 5pt tolerance for cover
        w_ok = abs(w_pt - expected_w_pt) <= tol
        h_ok = abs(h_pt - expected_h_pt) <= tol

        if w_ok and h_ok:
            result.ok(
                f"Cover dimensions correct for {page_count} pages "
                f"({expected_w_in:.3f}\"×{expected_h_in:.3f}\")"
            )
        else:
            result.warn(
                f"Cover dimensions {w_pt/72:.3f}\"×{h_pt/72:.3f}\" differ from expected "
                f"{expected_w_in:.3f}\"×{expected_h_in:.3f}\" "
                f"(spine: {spine_in:.4f}\"). May be ok if you used KDP's calculator directly."
            )

    except Exception as e:
        result.error(f"Could not read cover PDF: {e}")


def validate_metadata(meta_path: Path, result: ValidationResult) -> Dict:
    """Validate metadata.json fields."""
    print(f"\n📋 Metadata: {meta_path.name}")

    if not meta_path.exists():
        result.warn("No metadata.json found — skipping metadata checks")
        return {}

    try:
        with open(meta_path) as f:
            meta = json.load(f)
    except Exception as e:
        result.error(f"Could not read metadata: {e}")
        return {}

    required = ["title", "author", "description", "keywords"]
    for field in required:
        if meta.get(field):
            result.ok(f"Field '{field}' present")
        else:
            result.error(f"Required field '{field}' is missing or empty")

    # Keywords check
    keywords = meta.get("keywords", [])
    if isinstance(keywords, list):
        if len(keywords) < 7:
            result.warn(f"Only {len(keywords)} keywords — KDP allows 7, use all slots")
        else:
            result.ok(f"7 keywords provided")
        for kw in keywords:
            if len(kw) > 50:
                result.warn(f"Keyword too long (>50 chars): '{kw[:30]}...'")

    # Description check
    desc = meta.get("description", "")
    if len(desc) < 50:
        result.warn("Description is very short — aim for 150-400 characters")
    elif len(desc) > 4000:
        result.error(f"Description too long ({len(desc)} chars) — KDP max is 4000")
    else:
        result.ok(f"Description length: {len(desc)} chars")

    # Title length
    title = meta.get("title", "")
    if len(title) > 200:
        result.error(f"Title too long ({len(title)} chars) — KDP max is 200")
    elif len(title) == 0:
        result.error("Title is empty")
    else:
        result.ok(f"Title: '{title}'")

    # AI disclosure check
    if meta.get("ai_disclosure") is None:
        result.warn("ai_disclosure not set in metadata — remember to disclose on KDP if content is AI-generated")

    return meta


def validate_images(images_dir: Path, result: ValidationResult) -> List[Path]:
    """Validate image files for resolution."""
    print(f"\n🎨 Images: {images_dir}")

    if not images_dir.exists():
        result.warn(f"Images directory not found: {images_dir}")
        return []

    image_files = sorted(
        list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg"))
    )

    if not image_files:
        result.warn("No images found in images directory")
        return []

    result.ok(f"Found {len(image_files)} image files")

    low_res_count = 0
    for img_path in image_files:
        try:
            with Image.open(img_path) as img:
                w, h = img.size
                # For 8.5x8.5 at 300 DPI: need 2550×2550 px
                # For embedded at 8" at 300 DPI: need 2400 px
                # Imagen outputs 1024px — at 3.4" that's 300 DPI
                # When scaled to 8", that's 128 DPI — technically below spec
                # but KDP often accepts it for full-page images
                if w < 800 or h < 800:
                    result.warn(f"{img_path.name}: Low resolution {w}×{h} — may fail KDP preflight")
                    low_res_count += 1
                elif w < 1500 or h < 1500:
                    result.warn(
                        f"{img_path.name}: {w}×{h} px — acceptable for smaller images, "
                        "but 2550×2550+ recommended for full-page"
                    )
                else:
                    result.ok(f"{img_path.name}: {w}×{h} px")
        except Exception as e:
            result.error(f"Could not open image {img_path.name}: {e}")

    if low_res_count > 0:
        result.warn(f"{low_res_count} image(s) may be too low resolution for print")

    return image_files


def check_text_in_images(image_files: List[Path], api_key: str,
                          result: ValidationResult):
    """Use Gemini Vision to detect text artifacts in AI illustrations."""
    print(f"\n🔍 Checking for text in images (Gemini Vision)...")

    try:
        import google.genai as genai
    except ImportError:
        result.warn("google-genai not installed — skipping AI text detection")
        return

    if not api_key:
        result.warn("No API key — skipping AI text detection. Manually inspect all images.")
        return

    client = genai.Client(api_key=api_key)

    # Check a sample (all if ≤10, otherwise every 3rd)
    to_check = image_files if len(image_files) <= 10 else image_files[::3]
    text_found = []

    for img_path in to_check:
        try:
            with open(img_path, "rb") as f:
                img_data = f.read()

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": __import__("base64").b64encode(img_data).decode(),
                                }
                            },
                            {
                                "text": (
                                    "Does this image contain any text, letters, numbers, words, "
                                    "or writing of any kind? Answer YES or NO first, then if YES, "
                                    "describe exactly what text you see."
                                )
                            },
                        ]
                    }
                ],
            )
            answer = response.text.strip()
            if answer.upper().startswith("YES"):
                text_found.append((img_path.name, answer))
                result.error(
                    f"TEXT DETECTED in {img_path.name}: {answer[:100]}"
                )
            else:
                result.ok(f"No text in {img_path.name}")

        except Exception as e:
            result.warn(f"Could not check {img_path.name}: {e}")

    if not text_found:
        result.ok(f"No text artifacts found in {len(to_check)} images checked")


def check_description_consistency(meta: Dict, story_path: Path,
                                   result: ValidationResult):
    """Check that description mentions names/themes from the actual story."""
    print(f"\n📝 Description vs. Story Consistency")

    description = meta.get("description", "")
    if not description:
        result.warn("No description to check")
        return

    if not story_path or not story_path.exists():
        result.warn("No story.json found — cannot verify description consistency")
        return

    try:
        with open(story_path) as f:
            story = json.load(f)
    except Exception as e:
        result.warn(f"Could not read story.json: {e}")
        return

    story_content = story.get("content", "") + " " + story.get("title", "")
    story_words = set(re.findall(r"\b[A-Z][a-z]+\b", story_content))  # Proper nouns

    desc_words = set(re.findall(r"\b[A-Z][a-z]+\b", description))
    desc_lower = description.lower()

    # Check that description doesn't mention names not in story
    potential_mismatches = []
    for word in desc_words:
        if (
            len(word) > 3
            and word not in story_words
            and word not in {"This", "The", "A", "An", "In", "On", "With", "From", "For"}
        ):
            potential_mismatches.append(word)

    if potential_mismatches:
        result.warn(
            f"Description contains names/words not found in story: {', '.join(potential_mismatches[:5])} "
            f"— verify these are correct (may be fine if story uses them in different case)"
        )
    else:
        result.ok("Description names appear consistent with story content")

    # Check description isn't just the prompt
    title = meta.get("title", "")
    if title and title.lower() in description.lower() and len(description) < 80:
        result.warn(
            "Description appears to be a summary of the prompt rather than the finished story — rewrite from final text"
        )
    else:
        result.ok("Description appears to be written from finished content")


def check_blank_pages(pdf_path: Path, result: ValidationResult):
    """Render pages and detect all-white (blank) pages that shouldn't be blank."""
    print(f"\n🔲 Blank page detection...")
    # Note: This requires pdf2image / poppler. If not available, skip gracefully.
    try:
        from pdf2image import convert_from_path
        import numpy as np
    except ImportError:
        result.warn("pdf2image/numpy not installed — skipping blank page detection")
        result.warn("   Install with: pip install pdf2image numpy (+ apt install poppler-utils)")
        return

    try:
        pages = convert_from_path(str(pdf_path), dpi=72, first_page=1, last_page=10)
        blank_pages = []
        for i, page_img in enumerate(pages):
            arr = __import__("numpy").array(page_img.convert("L"))
            if arr.std() < 3.0:  # Near-zero variance = blank white page
                blank_pages.append(i + 1)

        if blank_pages:
            result.warn(f"Possible blank pages detected (first 10): pages {blank_pages}")
        else:
            result.ok("No unexpected blank pages in first 10 pages")
    except Exception as e:
        result.warn(f"Could not perform blank page check: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="KDP Book Validator — pre-upload quality checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  python3 validate-book.py --interior output/my-book/interior.pdf

  # Full validation with all checks
  python3 validate-book.py \\
      --interior output/my-book/interior.pdf \\
      --cover output/my-book/cover.pdf \\
      --metadata output/my-book/metadata.json \\
      --images output/my-book/images/ \\
      --check-text-in-images

  # Validate from book directory
  python3 validate-book.py --book-dir output/my-book/
""",
    )
    parser.add_argument("--interior", metavar="PATH", help="Interior PDF path")
    parser.add_argument("--cover", metavar="PATH", help="Cover PDF path")
    parser.add_argument("--metadata", metavar="PATH", help="metadata.json path")
    parser.add_argument("--images", metavar="DIR", help="Images directory path")
    parser.add_argument(
        "--book-dir", metavar="DIR",
        help="Book output directory (auto-discovers interior.pdf, cover.pdf, metadata.json, images/)"
    )
    parser.add_argument(
        "--book-type",
        choices=list(PAGE_COUNT_MIN.keys()),
        default="picture-book",
        help="Book type for page count validation (default: picture-book)",
    )
    parser.add_argument(
        "--trim",
        default="8.5x8.5",
        choices=list(KDP_TRIM_SIZES.keys()),
        help="Trim size (default: 8.5x8.5)",
    )
    parser.add_argument(
        "--paper",
        default="white-color",
        choices=list(SPINE_WIDTH_PER_PAGE.keys()),
        help="Paper type for cover dimension check (default: white-color)",
    )
    parser.add_argument(
        "--check-text-in-images",
        action="store_true",
        help="Use Gemini Vision to check for AI text artifacts in images",
    )
    parser.add_argument(
        "--api-key",
        help="Google AI API key (for --check-text-in-images)",
    )

    args = parser.parse_args()

    # Resolve paths
    interior_path = None
    cover_path = None
    metadata_path = None
    images_dir = None
    story_path = None

    if args.book_dir:
        bd = Path(args.book_dir)
        interior_path = bd / "interior.pdf"
        cover_path = bd / "cover.pdf"
        metadata_path = bd / "metadata.json"
        images_dir = bd / "images"
        story_path = bd / "story.json"
    else:
        if args.interior:
            interior_path = Path(args.interior)
            # Auto-discover siblings
            parent = interior_path.parent
            if not cover_path and (parent / "cover.pdf").exists():
                cover_path = parent / "cover.pdf"
            if not metadata_path and (parent / "metadata.json").exists():
                metadata_path = parent / "metadata.json"
            if not images_dir and (parent / "images").exists():
                images_dir = parent / "images"
            story_path = parent / "story.json"
        if args.cover:
            cover_path = Path(args.cover)
        if args.metadata:
            metadata_path = Path(args.metadata)
        if args.images:
            images_dir = Path(args.images)

    if not interior_path and not cover_path and not metadata_path:
        parser.print_help()
        print("\n❌ Provide at least --interior, --cover, or --book-dir")
        sys.exit(1)

    # Load API key for image text check
    api_key = args.api_key or os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        creds_path = Path.home() / ".clawdbot" / "credentials" / "google_ai.json"
        if creds_path.exists():
            try:
                with open(creds_path) as f:
                    api_key = json.load(f).get("api_key")
            except Exception:
                pass

    # Get book type from metadata if available
    book_type = args.book_type
    trim_key = args.trim
    paper = args.paper
    if metadata_path and metadata_path.exists():
        try:
            with open(metadata_path) as f:
                meta_quick = json.load(f)
            book_type = meta_quick.get("book_type", book_type)
            trim_raw = meta_quick.get("trim_size", "").replace(" x ", "x").replace(" ", "")
            if trim_raw in KDP_TRIM_SIZES:
                trim_key = trim_raw
        except Exception:
            pass

    print(f"\n{'='*60}")
    print("KDP BOOK VALIDATOR")
    print(f"{'='*60}")
    print(f"Book type : {book_type}")
    print(f"Trim size : {trim_key}")
    print(f"Paper     : {paper}")

    result = ValidationResult()

    # Run checks
    page_count = 0
    if interior_path:
        page_count = validate_interior_pdf(interior_path, book_type, trim_key, result)
        if interior_path.exists():
            check_blank_pages(interior_path, result)

    if cover_path:
        validate_cover_pdf(cover_path, page_count, trim_key, paper, result)

    meta = {}
    if metadata_path:
        meta = validate_metadata(metadata_path, result)

    image_files = []
    if images_dir:
        image_files = validate_images(images_dir, result)

    if args.check_text_in_images and image_files:
        check_text_in_images(image_files, api_key, result)
    elif image_files and not args.check_text_in_images:
        print(f"\n  ℹ  Run with --check-text-in-images to scan illustrations for AI text artifacts")

    if meta and story_path:
        check_description_consistency(meta, story_path, result)

    # Summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"  ✅ Passed  : {len(result.passed)}")
    print(f"  ⚠  Warnings: {len(result.warnings)}")
    print(f"  ❌ Errors  : {len(result.errors)}")

    if result.errors:
        print(f"\n🚫 ERRORS (must fix before upload):")
        for e in result.errors:
            print(f"   • {e}")

    if result.warnings:
        print(f"\n⚠  WARNINGS (review before upload):")
        for w in result.warnings:
            print(f"   • {w}")

    if result.is_valid:
        print(f"\n✅ Book passed validation — ready to upload to KDP!")
        sys.exit(0)
    else:
        print(f"\n❌ Fix {len(result.errors)} error(s) before uploading to KDP.")
        sys.exit(1)


if __name__ == "__main__":
    main()
