---
name: menuvision
description: "Build beautiful HTML photo menus from restaurant URLs, PDFs, or photos using Gemini Vision and AI image generation"
version: 1.0.0
emoji: "🍽️"
user-invocable: true
metadata: {"openclaw": {"requires": {"env": ["GOOGLE_API_KEY"], "bins": ["python3"]}, "primaryEnv": "GOOGLE_API_KEY", "homepage": "https://github.com/ademczuk/MenuVision"}}
---

# MenuVision - Restaurant Menu Builder

Build a beautiful HTML photo menu for any restaurant from URLs, PDFs, or photos.

## When to Use

When the user wants to create a digital menu for a restaurant. Triggers: "build a menu", "create restaurant menu", "menu from PDF", "menu from photos", "digital menu", "menuvision".

## Quick Start

```
1. Extract:  URL/PDF/photo  →  menu_data.json     (Gemini Vision)
2. Generate: menu_data.json →  images/*.jpg        (Gemini Image)
3. Build:    menu_data.json + images → Menu.html   (CSS/JS inline, images relative)
```

### Example usage (ask the AI):
- "Build a menu for https://www.shoyu.at/menus"
- "Create a photo menu from this PDF" (attach file)
- "Make a digital menu from these photos of a restaurant menu"

## Pipeline Components

The AI agent creates these scripts:

| Script | Purpose |
|--------|---------|
| `extract_menu.py` | Extract menu data from URL/PDF/photo → structured JSON |
| `generate_images.py` | Generate food photos via Gemini Image |
| `build_menu.py` | Build HTML menu from JSON + images (CSS/JS inline, images as relative paths) |
| `publish_menu.py` | (Optional) Publish HTML to GitHub Pages |

---

## DATA CONTRACT (Critical)

All three pipeline stages share this exact JSON schema. The AI agent MUST use these field names — any deviation breaks the pipeline.

### menu_data.json Schema

```json
{
  "restaurant": {
    "name": "Restaurant Name (if visible)",
    "cuisine": "cuisine type (Chinese, Indian, Austrian, Japanese, etc.)",
    "tagline": "any subtitle or tagline"
  },
  "sections": [
    {
      "title": "Section Name (in primary language)",
      "title_secondary": "Section name in secondary language (if present, else empty string)",
      "category": "food or drink",
      "note": "Any section note (e.g. 'served with rice', 'Mon-Fri 11-15h')",
      "items": [
        {
          "code": "M1",
          "name": "Dish Name (primary language)",
          "name_secondary": "Name in secondary language (if present)",
          "description": "Brief description (primary language)",
          "description_secondary": "Description in secondary language (if present)",
          "price": "12,90",
          "price_prefix": "",
          "allergens": "A C F",
          "dietary": ["vegan", "spicy"],
          "variants": []
        }
      ]
    }
  ],
  "allergen_legend": {
    "A": "Gluten",
    "B": "Crustaceans"
  },
  "metadata": {
    "languages": ["German", "English"],
    "currency": "EUR"
  }
}
```

### Field Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `restaurant.name` | string | Yes | Display name in HTML header |
| `restaurant.cuisine` | string | Yes | Passed to `build_food_prompt()` as cuisine context |
| `restaurant.tagline` | string | No | Subtitle line in HTML header |
| `sections[].title` | string | Yes | Section heading in primary language |
| `sections[].title_secondary` | string | No | Section heading in secondary language |
| `sections[].category` | `"food"` or `"drink"` | Yes | Drives food grid vs drink list layout. Only `"food"` items get generated images. |
| `sections[].note` | string | No | Section-level note (e.g. "served with rice", "Mon-Fri 11-15h") |
| `items[].code` | string | Yes | Unique per item. Links to image filename. Use existing codes (M1, K2) or generate (A1, A2) |
| `items[].name` | string | Yes | Primary language. For CJK menus, this is the CJK name |
| `items[].name_secondary` | string | No | Secondary language. For CJK menus, this is the English/Latin name |
| `items[].description` | string | No | Brief description. Fed to `build_food_prompt()` for image generation |
| `items[].description_secondary` | string | No | Description in secondary language |
| `items[].price` | string | Yes | Preserve original format ("12,90" not "12.90") |
| `items[].price_prefix` | string | No | e.g. "ab" (starting from), "ca." |
| `items[].variants` | array | No | `[{"label": "6 Stk", "price": "8,90"}, ...]` — set main price to smallest variant |
| `items[].allergens` | string | No | Space-separated codes exactly as printed: "A C F" |
| `items[].dietary` | array | No | `["vegan", "vegetarian", "spicy", "gluten-free", "halal", "kosher"]` |
| `allergen_legend` | object | No | Map of allergen codes to display names: `{"A": "Gluten", ...}` |
| `metadata.currency` | string | Yes | ISO code: "EUR", "USD", "JPY", "CNY", "THB", etc. |
| `metadata.languages` | array | No | Languages detected in the menu: `["German", "English"]` |

---

## EXTRACTION PROMPT

Send this exact prompt to Gemini. It defines the schema AND the extraction rules. Do not paraphrase it.

```
You are a restaurant menu data extractor. Analyze this menu content and extract ALL items into structured JSON.

Return this exact JSON structure:
{
  "restaurant": {
    "name": "Restaurant Name (if visible)",
    "cuisine": "cuisine type (Chinese, Indian, Austrian, Japanese, etc.)",
    "tagline": "any subtitle or tagline"
  },
  "sections": [
    {
      "title": "Section Name (in primary language)",
      "title_secondary": "Section name in secondary language (if present, else empty string)",
      "category": "food or drink",
      "note": "Any section note (e.g. 'served with rice', 'Mon-Fri 11-15h')",
      "items": [
        {
          "code": "M1",
          "name": "Dish Name (primary language)",
          "name_secondary": "Name in secondary language (if present)",
          "description": "Brief description (primary language)",
          "description_secondary": "Description in secondary language (if present)",
          "price": "12,90",
          "price_prefix": "",
          "allergens": "A C F",
          "dietary": ["vegan", "spicy"],
          "variants": []
        }
      ]
    }
  ],
  "allergen_legend": {
    "A": "Gluten",
    "B": "Crustaceans"
  },
  "metadata": {
    "languages": ["German", "English"],
    "currency": "EUR"
  }
}

CRITICAL RULES:
1. Extract EVERY item. Do not skip ANY dish, drink, or menu entry.
2. Preserve original item codes/numbers if present (M1, K2, S3, etc.). If none exist, generate sequential codes per section (e.g. A1, A2 for appetizers, M1, M2 for mains).
3. Extract prices EXACTLY as written (preserve comma/period format).
4. If an item has a price prefix like "ab" (starting from), capture it in "price_prefix".
5. If an item has multiple size/quantity variants (e.g. 6 Stk / 12 Stk / 18 Stk at different prices), use the "variants" array:
   [{"label": "6 Stk", "price": "8,90"}, {"label": "12 Stk", "price": "15,90"}]
   In this case, set the main "price" to the smallest variant's price.
6. Capture allergen codes exactly as shown (letters, numbers, or symbols).
7. If an allergen legend is visible anywhere, include it in "allergen_legend".
8. Identify dietary flags from descriptions/icons: vegan, vegetarian, spicy, gluten-free, halal, kosher.
9. If the menu is bilingual, capture BOTH languages. Put the primary/dominant language in name/description and the secondary in name_secondary/description_secondary.
10. For set menus or lunch specials with a fixed price covering multiple choices, create a section with note explaining the format, and list each choice as an item.
11. Classify each section as "food" or "drink".
12. For drinks, still extract name, price, and any size variants.

Return ONLY valid JSON. No markdown fences, no explanatory text.
```

### Vision Prompt Variant
For image-based inputs (screenshots, PDF pages, photos), prepend a context line before the base prompt:

```python
EXTRACTION_PROMPT_VISION = (
    "You are a restaurant menu data extractor. "
    "This is a photo/scan of a restaurant menu page.\n\n"
    "Return this exact JSON structure:"
    + EXTRACTION_PROMPT.split("Return this exact JSON structure:")[1]
)
```

Then each input type adds its own prefix:

| Input Type | Prefix prepended to `EXTRACTION_PROMPT_VISION` |
|---|---|
| Screenshot | `"This is a screenshot of a restaurant menu webpage at {url}. Extract ALL visible menu items.\n\n"` |
| PDF page | `"This is page {n} of a restaurant menu PDF. Extract ALL menu items from this page.\n\n"` |
| Photo | `"This is a photograph of a restaurant menu. Extract ALL visible menu items.\n\n"` |
| Text (static HTML) | Use `EXTRACTION_PROMPT` directly (no vision variant needed) |

---

## GEMINI API CONFIGURATION

```python
import os
from google import genai

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

def gemini_config():
    return genai.types.GenerateContentConfig(
        max_output_tokens=65536,          # 64K — needed for large menus
        response_mime_type="application/json",  # JSON mode — critical
    )

# Model: gemini-2.5-flash (default)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_text,    # or [image, prompt_text] for vision
    config=gemini_config(),
)

# ALWAYS check for truncation
if response.candidates[0].finish_reason.name == "MAX_TOKENS":
    print("WARNING: Response truncated. Menu may be incomplete.")
```

---

## IMAGE PROMPT TEMPLATE

Use this exact function. It produces the casual phone-photo aesthetic that makes menus look authentic.

```python
def build_food_prompt(name: str, description: str, cuisine: str = "") -> str:
    cuisine_context = f" {cuisine}" if cuisine else ""
    food_desc = f"{name}"
    if description and description != name:
        food_desc += f" ({description})"

    return (
        f"A photo of {food_desc} at a{cuisine_context} restaurant. "
        f"Taken casually with a phone from across the table at a 45-degree angle. "
        f"The plate sits on a dark wooden table and takes up only 30% of the frame. "
        f"Lots of visible table surface around the plate. Chopsticks, napkins, "
        f"a glass of water, and small side dishes scattered naturally nearby. "
        f"Blurred restaurant interior in the background — other diners, pendant lights, "
        f"wooden chairs visible but out of focus. Warm ambient lighting. "
        f"NOT a close-up. NOT professional food photography. "
        f"It looks like someone quickly snapped a photo before eating."
    )
```

---

## IMAGE GENERATION API CALLS

### Gemini 2.5 Flash Image

```python
import os, io
from PIL import Image
from google import genai

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

def generate_gemini(client, name, description, output_path, cuisine=""):
    prompt = build_food_prompt(name, description, cuisine)

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",       # NOT gemini-2.5-flash (that's text-only)
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],  # critical — requests image output
        ),
    )

    # Extract generated image from response parts
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            img = Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
            # Center-crop to square, resize to 800x800
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            img = img.crop((left, top, left + side, top + side))
            img = img.resize((800, 800), Image.LANCZOS)
            img.save(str(output_path), "JPEG", quality=82)
            return
    raise RuntimeError("No image in Gemini response")
```

### Skip drinks
Only generate images for `category == "food"` sections. Drinks get a text-only list in the HTML output.

---

## MULTILINGUAL / CJK HANDLING

Menus can be in ANY language. The pipeline handles this through bilingual fields and smart prompt routing.

### Extraction (all languages)
- `name` / `description` = primary language (whatever the menu is mostly written in)
- `name_secondary` / `description_secondary` = secondary language (if bilingual)
- Works for: German/English, Chinese/English, Japanese/English, Thai/English, Arabic/English, Korean/English, etc.

### Image Generation (CJK-safe prompting)
CJK characters produce bad image prompts. Before calling `build_food_prompt()`, swap to the Latin name:

```python
def prepare_for_image_gen(name, name_secondary, description):
    """Use Latin-script name for image prompts. CJK → use secondary name."""
    display_name = name
    if name_secondary:
        if any(ord(c) > 0x2E80 for c in name):  # CJK/Hangul/Kana detection
            display_name = name_secondary
            description = description or name
        else:
            description = description or name_secondary
    return display_name, description
```

**Unicode ranges covered by `ord(c) > 0x2E80`:**
- CJK Unified Ideographs (Chinese characters)
- Hiragana / Katakana (Japanese)
- Hangul (Korean)
- CJK Compatibility, Radicals, Extensions

### HTML Output (all scripts)
- `name` renders as the large display text
- `name_secondary` renders below it in smaller text
- Both use Google Fonts with CJK fallback (`Noto Sans SC`, `Noto Sans JP`, `Noto Sans KR`)

---

## FILE NAMING CONVENTIONS

### Auto-derivation
All filenames are derived from the restaurant name or source URL:
```python
stem = "shoyu"  # derived from URL domain, PDF filename, or restaurant name
data_file = f"menu_data_{stem}.json"
images_dir = Path(f"images/{stem}")
html_file = f"{restaurant_name}_Menu.html"  # e.g. "Shoyu_Menu.html"
```

### Image files
```
images/{restaurant_stem}/{code}.jpg

# restaurant_stem = data filename minus "menu_data_" prefix
# Example: menu_data_shoyu.json → images/shoyu/M1.jpg
```

### Image path matching (in build step)
Returns POSIX-style string paths with `./` prefix for cross-platform HTML compatibility:
```python
def find_image(code: str, images_dir: Path):
    """Return relative POSIX path string to image, or None."""
    if not images_dir.is_dir():
        return None
    rel = images_dir.as_posix()
    if not rel.startswith("./"):
        rel = "./" + rel
    # 1. Exact match
    for ext in ("jpg", "jpeg", "webp", "png"):
        candidate = images_dir / f"{code}.{ext}"
        if candidate.exists():
            return f"{rel}/{code}.{ext}"
    # 2. Case-insensitive fallback
    for f in images_dir.iterdir():
        if f.stem.lower() == code.lower() and f.suffix.lower() in (".jpg", ".jpeg", ".webp", ".png"):
            return f"{rel}/{f.name}"
    return None
```

### Output HTML
```
{RestaurantName}_Menu.html    # CSS/JS inline, images as relative file paths
```

### Image rendering (build step)
The build script uses `find_image()` to resolve each food item's photo, falling back to a gradient SVG placeholder when no image exists:

```python
import base64
import html as html_mod

GRADIENT_COLORS = [
    ("#c41e3a", "#8b0000"), ("#ff6b6b", "#ee5a24"), ("#fdcb6e", "#e17055"),
    ("#00b894", "#00cec9"), ("#6c5ce7", "#a29bfe"), ("#e17055", "#d63031"),
    ("#00cec9", "#0984e3"), ("#fab1a0", "#e17055"), ("#e8a87c", "#d4956b"),
    ("#fd79a8", "#e84393"),
]

def make_placeholder_svg(code: str, name: str, secondary: str = "") -> str:
    """Generate a base64-encoded SVG placeholder when no image exists."""
    idx = hash(code) % len(GRADIENT_COLORS)
    c1, c2 = GRADIENT_COLORS[idx]
    display = html_mod.escape(secondary[:12] if secondary else name[:12])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="220" height="180" viewBox="0 0 220 180">
  <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:{c1}"/>
    <stop offset="100%" style="stop-color:{c2}"/>
  </linearGradient></defs>
  <rect width="220" height="180" fill="url(#g)" rx="12"/>
  <text x="110" y="75" text-anchor="middle" fill="rgba(255,255,255,0.25)" font-size="56" font-family="serif">{html_mod.escape(code)}</text>
  <text x="110" y="120" text-anchor="middle" fill="white" font-size="26" font-family="serif" opacity="0.9">{display}</text>
  <text x="110" y="148" text-anchor="middle" fill="rgba(255,255,255,0.6)" font-size="11" font-family="sans-serif">{html_mod.escape(name[:30])}</text>
</svg>'''
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def image_tag(code: str, name: str, secondary: str, images_dir: Path, portable: bool = False) -> str:
    """Return <img> tag — real image OR gradient SVG placeholder.
    If portable=True, embed the real image as base64 data URI for single-file output."""
    real = find_image(code, images_dir)
    if real:
        if portable:
            img_path = images_dir.parent / real  # resolve relative path
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            return f'<img src="data:image/jpeg;base64,{b64}" alt="{html_mod.escape(name)}">'
        return f'<img src="{html_mod.escape(real)}" alt="{html_mod.escape(name)}" loading="lazy">'
    else:
        src = make_placeholder_svg(code, name, secondary)
        return f'<img src="{src}" alt="{html_mod.escape(name)}">'
```

### Output Modes

The HTML builder supports two output modes controlled by a `--portable` flag:

| Mode | Flag | Images | Output | Use Case |
|------|------|--------|--------|----------|
| **Portable** (default) | `--portable` or no `GITHUB_*` env vars | Base64 embedded in HTML | Single self-contained `.html` file | Open locally, email, drag-drop to any host |
| **Deployable** | `--no-portable` or `GITHUB_*` env vars set | Relative paths (`./images/stem/code.jpg`) | HTML + `images/` directory | GitHub Pages, Netlify, any static host |

**Portable mode** embeds all food images as base64 data URIs directly in the HTML. File sizes are larger (~4-6MB for an 80-item menu) but the output is a single file that works everywhere with zero hosting setup. This is the default when no `GITHUB_*` environment variables are set.

**Deployable mode** uses relative image paths and requires the HTML file and `images/` directory to be hosted together. Use this when publishing to GitHub Pages or any static hosting service.

---

## ROBUSTNESS PATTERNS

### Retry Logic
All Gemini API calls should retry on transient failures:
```python
import time

def call_with_retry(fn, *args, max_retries=3, **kwargs):
    """Retry API calls with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  Retry {attempt + 1}/{max_retries} in {wait}s: {e}")
            time.sleep(wait)
```

### JSON Response Parsing
Gemini sometimes wraps JSON in markdown fences or produces trailing commas. Parse defensively — try raw parse first, apply trailing comma fix only as last resort (unconditional fix can corrupt valid JSON strings containing `,]` patterns):
```python
import re, json

def parse_gemini_json(raw: str) -> dict:
    """Parse JSON from Gemini, handling markdown fences and quirks."""
    text = raw.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    text = text.strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting JSON object from surrounding text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        # Fix trailing commas and retry
        candidate = re.sub(r",\s*([\]}])", r"\1", candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    # Last resort: fix trailing commas on original
    text = re.sub(r",\s*([\]}])", r"\1", text)
    return json.loads(text)
```

### Post-Processing
After extraction, run these cleanups:
```python
def generate_codes(data: dict) -> dict:
    """Ensure every item has a unique code. Generates sequential codes per section
    if items have empty/missing codes (e.g. A1, A2 for appetizers, M1, M2 for mains)."""
    # ... assign prefix by section title, increment counter per section
    return data

def normalize_prices(data: dict) -> dict:
    """Normalize price formats: numeric → string, strip currency symbols,
    preserve comma/period format as-is."""
    # ... convert float/int to string, strip €/$, etc.
    return data
```

### CURRENCY_MAP
Maps ISO currency codes to display symbols for the HTML output:
```python
CURRENCY_MAP = {
    "EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF ",
    "JPY": "¥", "CNY": "¥", "INR": "₹", "AUD": "A$",
    "CAD": "C$", "SEK": "kr ", "NOK": "kr ", "DKK": "kr ",
    "THB": "฿", "KRW": "₩", "HKD": "HK$", "SGD": "S$",
    "CZK": "Kč ", "HUF": "Ft ", "PLN": "zł ", "TRY": "₺",
}
```

---

## EXTRACTION DETAILS

### HTML URLs
1. Fetch page with `requests`
2. Check text density to detect static vs JS-rendered:
   `density = len(soup.get_text(strip=True)) / len(raw_html)`
3. **Density override**: If 5+ price patterns found (`r"[$€£¥₹CHF]\s*\d+[.,]\d{2}|\d+[.,]\d{2}\s*[$€£¥₹]"`), force density to 1.0 (treat as static)
4. **Static** (density >= 0.02): Clean HTML, send text to Gemini 2.5 Flash (JSON mode)
5. **JS-rendered** (density < 0.02, e.g. Wix, Framer): Screenshot with Playwright, send to Gemini Vision
6. **Screenshot height cap**: If screenshot > 6000px tall, resize proportionally to fit
7. **Large menus** (>12k chars text): Chunked extraction, merge like PDF multi-page. Deduplicate by tracking `seen_codes = set()` across chunks — for each item in each chunk's sections, skip if `item["code"]` already in `seen_codes`. Only append sections that still have items after dedup.

### PDF Files
1. Convert each page to image via PyMuPDF (200 DPI)
2. Send each page image to Gemini Vision
3. Merge results across pages (deduplicate items by code)

### Photos
1. Load image directly
2. Resize if >10MB
3. Send to Gemini Vision

---

## HTML OUTPUT FEATURES
- 3-column Instagram-style grid (9:16 portrait tiles)
- Gradient text overlay with name + secondary language + price
- Tap-to-select with green checkmark
- Receipt/bill on Selection tab with +/- quantity controls
- Category pill navigation with scroll sync
- Drinks section below grid with currency-prefixed prices
- Allergen legend
- **Currency converter** — minimalist button in header (e.g. `€` pill) that cycles or opens a picker for: EUR, USD, AUD, CAD, GBP. Converts all displayed prices client-side using snapshot exchange rates embedded at build time. Updates grid overlays, receipt totals, drink prices, and variant prices. Source currency comes from `metadata.currency`.
- Fully responsive, dark mode
- All CSS/JS inline, images via relative file paths (`./images/{stem}/{code}.jpg`), only Google Fonts external
- Gradient SVG placeholders for missing images (inline base64 SVG, not raster)
- **CJK font loading** via Google Fonts link tag:
  `family=Noto+Sans+SC:wght@400;700&family=Noto+Sans+JP:wght@400;700&family=Noto+Sans+KR:wght@400;700`
- CSS `font-family` stack: primary font, then `'Noto Sans SC', 'Noto Sans JP', 'Noto Sans KR', sans-serif`

### Currency Converter

A minimalist currency toggle built into the HTML output. All client-side, no API calls at runtime.

**Implementation:**
- The build script embeds a `RATES` object with snapshot exchange rates (base: USD) at build time
- Source currency is read from `metadata.currency` in the JSON data
- All prices are stored in `data-price` attributes as **numeric** values (not raw strings like "12,90")
- A small pill button in the header shows the current currency symbol (e.g. `€`)
- Tapping opens a mini-picker or cycles through: EUR (`€`), USD (`$`), GBP (`£`), AUD (`A$`), CAD (`C$`)
- On currency change, JavaScript converts all `data-price` values and updates displayed text
- Receipt totals in the Selection tab also convert via `convertPrice()` using `SOURCE_CURRENCY` and `currentCurrency`
- Variant prices also update
- Selected currency persists in `localStorage`

**Price parsing helper** (build-time — converts string prices to numeric for `data-price` attributes):
```python
import re

def _parse_price_numeric(price: str) -> str:
    """Parse price string to numeric float for data-price attribute."""
    matches = re.findall(r"(\d+[.,]\d+)", price)
    if matches:
        return str(float(matches[-1].replace(",", ".")))
    return "0"

# Usage in HTML template:
# <div class="price" data-price="{_parse_price_numeric(item['price'])}">€12,90</div>
```

```javascript
// Snapshot rates embedded at build time (base: USD)
const RATES = { EUR: 0.92, USD: 1.00, GBP: 0.79, AUD: 1.54, CAD: 1.36 };
const SYMBOLS = { EUR: "€", USD: "$", GBP: "£", AUD: "A$", CAD: "C$" };
const SOURCE_CURRENCY = "EUR";  // from metadata.currency

function convertPrice(amount, fromCurrency, toCurrency) {
    const inUSD = amount / RATES[fromCurrency];
    return inUSD * RATES[toCurrency];
}

// Applied to: grid overlay prices, drink list prices, variant prices,
// AND receipt/selection tab totals (all elements with data-price attribute)
```

The build script should fetch current rates at build time (or use reasonable defaults if offline). Prices display with 2 decimal places in the target currency, using the target locale's format.

## Branding Customization
```bash
--name "Restaurant Name"     # Header brand text
--tagline "Cuisine · City"   # Subtitle
--accent "#ff6b00"           # Primary color (pills, active tab, drink prices)
--bg "#0a0a0a"               # Background color
```

---

## COST SUMMARY

| Component | Cost |
|-----------|------|
| Extraction (per page) | ~$0.001 |
| Image generation (per food item) | $0.039 |
| **80 food items** | **~$3.12** |
| Time (80 food items) | ~8 min |

Drinks are not image-generated (text-only list), so actual cost depends on food-to-drink ratio.

## DEPENDENCIES

Requires **Python 3.9+**.

Required:
- `google-genai` (extraction + image generation)
- `Pillow` (image processing)

For HTML URLs:
- `requests` (HTTP fetching)
- `beautifulsoup4` (HTML parsing)

For JS-rendered sites:
- `playwright` (headless browser screenshots)

For PDF files:
- `PyMuPDF` (PDF to image conversion)

```bash
pip install google-genai Pillow requests beautifulsoup4 PyMuPDF
pip install playwright && playwright install chromium
```

## ENVIRONMENT VARIABLES
- `GOOGLE_API_KEY` — Required for extraction and image generation
- `GITHUB_PAT` — Required for GitHub Pages publishing
- `GITHUB_OWNER` — Your GitHub username (default: reads from git config)
- `GITHUB_REPO` — Your GitHub Pages repo name (default: `menus`)

## PUBLISHING

### Default: Portable HTML (no setup)

When no `GITHUB_*` environment variables are set, the pipeline generates a **self-contained HTML file** with base64-embedded images. Users can:
- Open the file directly in any browser
- Email it or share via any file-sharing service
- Upload to any static host (Netlify Drop, Vercel, GitHub Pages, S3)

No hosting setup, no API keys beyond `GOOGLE_API_KEY`, no git configuration needed.

### Optional: GitHub Pages (requires setup)

For users who want a persistent gallery with multiple menus:

1. Create a GitHub repo for your menus (e.g. `your-username/menus`)
2. Enable GitHub Pages on the `main` branch
3. Set environment variables (must be accessible to the Python process):
```bash
export GITHUB_PAT="your-personal-access-token"   # Required — used for git push auth
export GITHUB_OWNER="your-username"               # Required — YOUR GitHub username
export GITHUB_REPO="menus"                        # Optional — defaults to "menus"
```

**Important:** `publish_menu.py` MUST read `GITHUB_OWNER` and `GITHUB_REPO` from environment variables. Never hardcode a specific user's repo. The generated code should construct the repo URL dynamically:
```python
owner = os.environ["GITHUB_OWNER"]
repo = os.environ.get("GITHUB_REPO", "menus")
GITHUB_REPO = f"{owner}/{repo}"
GITHUB_PAGES_BASE = f"https://{owner}.github.io/{repo}"
```

### Publish
```bash
python publish_menu.py Restaurant_Menu.html --name "Restaurant" --tagline "Cuisine · City" --cuisine Type
```

Gallery: `https://<your-username>.github.io/<repo>/`

### How publishing works

`publish_menu.py` clones the menus repo to a **temp directory on native filesystem** (`git clone --depth=1`), copies files there, commits, and pushes. This avoids all NTFS bind mount permission issues that occur when operating directly on mounted volumes in Docker containers.

Key implementation details:
1. `git clone --depth=1` to a `tempfile.mkdtemp()` directory (native FS, proper POSIX permissions)
2. Copies HTML + images using `shutil.copy()` (not `copy2` — avoids `os.chmod()` EPERM on NTFS)
3. `find_image_dirs` regex uses `[^/"]+` (not `[a-z_]+`) to match Unicode chars in image dir names
4. Writes `.meta_` JSON sidecar for gallery metadata
5. Rebuilds gallery `index.html`
6. Authenticates push via `GITHUB_PAT` env var embedded in the clone URL
7. Temp directory is cleaned up after push
8. `MENUS_REPO_DIR` (bind mount path) is only used for `--list` read-only queries

## EXTERNAL ENDPOINTS

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| `generativelanguage.googleapis.com` | Menu text, page screenshots, PDF page images, food photo prompts | Gemini API for extraction (JSON mode) and image generation |
| Target restaurant URL | HTTP GET only | Fetching the menu page HTML for extraction |
| `api.github.com` | Generated HTML file, image files | Publishing menu to GitHub Pages (optional, requires `GITHUB_PAT`) |
| `fonts.googleapis.com` | None (CSS link in HTML output) | Google Fonts loaded client-side when menu HTML is opened in browser |

No analytics, telemetry, or tracking. No data is sent to any endpoint beyond those listed above.

## SECURITY & PRIVACY

- **API keys**: `GOOGLE_API_KEY` is read from environment variables, never hardcoded or logged
- **GitHub PAT**: Used only for authenticated pushes to the user's own repo; never transmitted elsewhere
- **Restaurant data**: Menu content is sent to the Gemini API for processing. No data is stored server-side beyond Google's standard API retention
- **Generated images**: Stored locally in `images/` directory. When published, uploaded only to the user's own GitHub Pages repo
- **No telemetry**: The pipeline collects no analytics, metrics, or usage data
- **Local-first**: All processing happens locally except Gemini API calls. The HTML output and images remain on the user's machine unless they explicitly publish

## KNOWN LIMITATIONS
- Tabbed Wix menus: Only first visible tab extracted
- Google Maps photo URLs: Not supported (use direct image files)
- Very large menus (300+ items): May need manual chunk review
