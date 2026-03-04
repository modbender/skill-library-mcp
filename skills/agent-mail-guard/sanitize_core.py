#!/usr/bin/env python3
"""
Shared sanitization core — used by both email and calendar sanitizers.

All text-cleaning, injection-detection, and sender-classification logic
lives here.  Callers import individual functions.

Python 3.11+ stdlib only.
"""

__version__ = "1.4.0"

import html
import json
import os
import re
import unicodedata
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_BODY_LENGTH = 2000

CONTACTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.json")

# Zero-width and invisible characters to strip
INVISIBLE_CHARS = set(
    "\u200b\u200c\u200d\ufeff"           # ZWS, ZWNJ, ZWJ, BOM
    "\u200e\u200f"                         # LRM, RLM
    "\u202a\u202b\u202c\u202d\u202e"       # LRE, RLE, PDF, LRO, RLO
    "\u2066\u2067\u2068\u2069"             # LRI, RLI, FSI, PDI
    "\u00ad"                               # Soft hyphen
    "\u180e"                               # Mongolian vowel separator
    "\u2060\u2061\u2062\u2063\u2064"       # Word joiner, invisible operators
)

# Variation selectors (U+FE00-U+FE0F and U+E0100-U+E01EF)
VARIATION_SELECTOR_RE = re.compile(r"[\ufe00-\ufe0f\U000e0100-\U000e01ef]")

# Unicode tag characters (U+E0001-U+E007F)
TAG_CHAR_RE = re.compile(r"[\U000e0001-\U000e007f]")

# HTML tag stripper
HTML_TAG_RE = re.compile(r"<[^>]+>")

# HTML comments
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# Base64 blobs (40+ chars of base64 alphabet, including URL-safe variant)
BASE64_BLOB_RE = re.compile(r"[A-Za-z0-9+/\-_=]{40,}")

# Hex strings (long sequences of hex pairs)
HEX_STRING_RE = re.compile(r"(?:[0-9a-fA-F]{2}\s*){15,}")

# Markdown image tags — the exfiltration vector
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")

# Reference-style markdown images: ![alt][ref]
MD_REF_IMAGE_RE = re.compile(r"!\s*\[[^\]]*\]\s*\[[^\]]*\]")

# Reference-style link definitions: [ref]: http://...
MD_REF_LINK_DEF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*https?://[^\s]+", re.MULTILINE)

# data: URIs (potential exfiltration / script injection)
DATA_URI_RE = re.compile(r"data:[a-zA-Z0-9/+.\-]+;?(?:base64,)?[A-Za-z0-9+/=]{20,}", re.I)

# Markdown hyperlinks: [text](http://...) — potential phishing/exfil vector
MARKDOWN_HYPERLINK_RE = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)")

# Reference-style markdown links: [text][ref]
MD_REF_LINK_RE = re.compile(r"\[[^\]]+\]\s*\[[^\]]*\]")

# Bare URLs: https://... or http://...
BARE_URL_RE = re.compile(r"https?://[^\s<>\"'\])+,]+")

# Autolinks: <https://...>
AUTOLINK_RE = re.compile(r"<https?://[^>]+>")

# Code blocks: fenced (```) and inline (`)
FENCED_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```")
INLINE_CODE_RE = re.compile(r"`[^`]+`")

# Multiple whitespace-only lines (hidden text indicator)
MULTI_BLANK_LINES_RE = re.compile(r"(\n\s*\n){3,}")

# ---------------------------------------------------------------------------
# Injection pattern regexes (case-insensitive)
# ---------------------------------------------------------------------------

INJECTION_PATTERNS = [
    # Direct instruction overrides
    (re.compile(r"ignore\s+(all\s+)?previous\s+(instructions?|context|prompts?)", re.I),
     "injection_pattern: 'ignore previous instructions'"),
    (re.compile(r"ignore\s+above", re.I),
     "injection_pattern: 'ignore above'"),
    (re.compile(r"disregard\s+(all\s+)?(previous\s+)?(instructions?|context|prompts?)", re.I),
     "injection_pattern: 'disregard instructions'"),
    (re.compile(r"forget\s+(your|all|previous)\s+(instructions?|context|rules)", re.I),
     "injection_pattern: 'forget instructions'"),

    # System prompt markers
    (re.compile(r"(?:^|\n)\s*system\s*:", re.I),
     "injection_pattern: 'system: prefix'"),
    (re.compile(r"\[SYSTEM\]", re.I),
     "injection_pattern: '[SYSTEM] tag'"),
    (re.compile(r"<<SYS>>", re.I),
     "injection_pattern: '<<SYS>> tag'"),
    (re.compile(r"<\|im_start\|>system", re.I),
     "injection_pattern: 'im_start system'"),
    (re.compile(r"\[INST\]", re.I),
     "injection_pattern: '[INST] tag'"),
    (re.compile(r"###\s*System", re.I),
     "injection_pattern: '### System'"),
    (re.compile(r"<\|system\|>", re.I),
     "injection_pattern: '<|system|> tag'"),
    (re.compile(r"<\|user\|>", re.I),
     "injection_pattern: '<|user|> tag'"),
    (re.compile(r"<\|assistant\|>", re.I),
     "injection_pattern: '<|assistant|> tag'"),

    # Authority claims
    (re.compile(r"(?:^|\n)\s*IMPORTANT\s*:", re.I),
     "injection_pattern: 'IMPORTANT: prefix'"),
    (re.compile(r"(?:^|\n)\s*NEW\s+INSTRUCTIONS?\s*:", re.I),
     "injection_pattern: 'NEW INSTRUCTIONS: prefix'"),
    (re.compile(r"(?:^|\n)\s*ADMIN\s*:", re.I),
     "injection_pattern: 'ADMIN: prefix'"),
    (re.compile(r"(?:^|\n)\s*OVERRIDE\s*:", re.I),
     "injection_pattern: 'OVERRIDE: prefix'"),

    # Fake conversation / thread injection
    (re.compile(r"(?:^|\n)\s*(?:Human|User|Assistant)\s*:", re.I),
     "injection_pattern: 'fake conversation turn'"),

    # Broader ignore/disregard/forget variants
    (re.compile(r"ignore\s+(?:the\s+)?(?:original|above|any|all|last|following)\s+\w*\s*instruction", re.I),
     "injection_pattern: 'ignore instructions variant'"),
    (re.compile(r"forget\s+everything", re.I),
     "injection_pattern: 'forget everything'"),
    (re.compile(r"disregard\s+(?:the\s+|my\s+)?(?:last|previous|above)", re.I),
     "injection_pattern: 'disregard variant'"),

    # Roleplay / identity override
    (re.compile(r"(?:pretend|act)\s+(?:as|like|you\s*(?:are|'re))", re.I),
     "injection_pattern: 'role play attack'"),
    (re.compile(r"you\s+are\s+now\b", re.I),
     "injection_pattern: 'identity override'"),
    (re.compile(r"from\s+now\s+on\s+you\s+(?:will|shall|must|are)", re.I),
     "injection_pattern: 'behavioral override'"),
    (re.compile(r"\bdo\s+anything\s+now\b", re.I),
     "injection_pattern: 'DAN jailbreak'"),

    # Hypothetical/scenario bypass
    (re.compile(r"imagine\s+(?:you|that|a\s+scenario)", re.I),
     "injection_pattern: 'hypothetical bypass'"),
    (re.compile(r"hypothetical\s+scenario", re.I),
     "injection_pattern: 'hypothetical bypass'"),
    (re.compile(r"let'?s\s+play\s+a\s+game", re.I),
     "injection_pattern: 'game framing bypass'"),

    # Output manipulation
    (re.compile(r"(?:repeat|say|print|output|write)\s+(?:after\s+me|the\s+following|exactly|only)", re.I),
     "injection_pattern: 'output manipulation'"),
    (re.compile(r"your\s+(?:first|next)\s+(?:word|response|output)\s+(?:should|must|will)\s+be", re.I),
     "injection_pattern: 'output manipulation'"),
]

# ---------------------------------------------------------------------------
# Contacts loader
# ---------------------------------------------------------------------------

_contacts_cache: dict | None = None


def _load_contacts() -> dict:
    """Load known contacts from contacts.json, normalized to lowercase sets."""
    global _contacts_cache
    if _contacts_cache is not None:
        return _contacts_cache
    try:
        with open(CONTACTS_PATH, "r") as f:
            raw = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raw = {}
    # Normalize once on load: lowercase and store as sets for O(1) lookup
    _contacts_cache = {
        "known_domains": {d.lower() for d in raw.get("known_domains", [])},
        "known_emails": {e.lower() for e in raw.get("known_emails", [])},
        "trusted_senders": {s.lower() for s in raw.get("trusted_senders", [])},
    }
    return _contacts_cache


def classify_sender(sender: str) -> str:
    """Return 'known' or 'unknown' based on sender email/domain."""
    contacts = _load_contacts()
    email_match = re.search(r"[\w.+-]+@[\w.-]+", sender)
    if not email_match:
        return "unknown"
    email = email_match.group(0).lower()
    domain = email.split("@", 1)[1] if "@" in email else ""

    if email in contacts["known_emails"]:
        return "known"
    if domain in contacts["known_domains"]:
        return "known"
    if domain in contacts["trusted_senders"]:
        return "known"
    for trusted in contacts["trusted_senders"]:
        if domain.endswith("." + trusted) or domain == trusted:
            return "known"
    return "unknown"


# ---------------------------------------------------------------------------
# Sanitization functions
# ---------------------------------------------------------------------------

def strip_html(text: str) -> str:
    """Remove all HTML tags, decode entities (recursive), strip comments."""
    text = HTML_COMMENT_RE.sub("", text)
    text = HTML_TAG_RE.sub("", text)
    # Recursive unescape: loop until stable to defeat nested entities like &#38;#105;
    prev = None
    iterations = 0
    while prev != text and iterations < 10:
        prev = text
        text = html.unescape(text)
        iterations += 1
    return text


def strip_invisible_unicode(text: str) -> str:
    """Strip zero-width, bidi overrides, variation selectors, tag chars."""
    text = "".join(ch for ch in text if ch not in INVISIBLE_CHARS)
    text = VARIATION_SELECTOR_RE.sub("", text)
    text = TAG_CHAR_RE.sub("", text)
    return text


# Backward-compatible alias
remove_invisible_unicode = strip_invisible_unicode


def normalize_unicode(text: str) -> str:
    """NFKC normalization to collapse homoglyphs."""
    return unicodedata.normalize("NFKC", text)


def strip_base64_blobs(text: str) -> str:
    """Replace large base64 blobs with placeholder."""
    return BASE64_BLOB_RE.sub("[base64 blob removed]", text)


def strip_hex_strings(text: str) -> str:
    """Replace long hex-encoded strings with placeholder.

    Prevents LLMs from decoding hex payloads containing injection instructions.
    """
    return HEX_STRING_RE.sub("[hex string removed]", text)


def strip_markdown_images(text: str) -> str:
    """Remove markdown image tags (inline and reference-style)."""
    text = MARKDOWN_IMAGE_RE.sub("[markdown image removed]", text)
    text = MD_REF_IMAGE_RE.sub("[markdown image removed]", text)
    text = MD_REF_LINK_DEF_RE.sub("[markdown link ref removed]", text)
    return text


def strip_data_uris(text: str) -> str:
    """Remove data: URIs that could contain embedded scripts or exfiltration payloads."""
    return DATA_URI_RE.sub("[data uri removed]", text)


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks and inline code."""
    text = FENCED_CODE_BLOCK_RE.sub("[code block removed]", text)
    text = INLINE_CODE_RE.sub("[inline code removed]", text)
    return text


def strip_markdown_hyperlinks(text: str) -> str:
    """Remove markdown hyperlinks [text](url), flag as potential phishing."""
    return MARKDOWN_HYPERLINK_RE.sub("[markdown link removed]", text)


def strip_reference_links(text: str) -> str:
    """Remove reference-style markdown links [text][ref]."""
    return MD_REF_LINK_RE.sub("[markdown link removed]", text)


def strip_urls(text: str) -> str:
    """Remove bare URLs (https://...) and autolinks (<https://...>)."""
    text = AUTOLINK_RE.sub("[url removed]", text)
    text = BARE_URL_RE.sub("[url removed]", text)
    return text


def strip_combining_chars(text: str) -> str:
    """Strip combining diacritical marks (Zalgo text) for detection purposes.

    Decomposes to NFD first so precomposed characters (e.g. ṋ → n + combining)
    are split before stripping. Only used for pattern detection normalization.
    """
    # NFD decompose so precomposed chars become base + combining
    text = unicodedata.normalize("NFD", text)
    # Strip all combining marks (category M: Mn, Mc, Me)
    return ''.join(c for c in text if not unicodedata.category(c).startswith('M'))



# ---------------------------------------------------------------------------
# Homoglyph / confusable character mapping
# ---------------------------------------------------------------------------

CONFUSABLES_MAP: dict[str, str] = {
    # Cyrillic → Latin
    "\u0430": "a",  # а
    "\u0435": "e",  # е
    "\u043e": "o",  # о
    "\u0440": "p",  # р
    "\u0441": "c",  # с
    "\u0443": "y",  # у (visually close to y)
    "\u0445": "x",  # х
    "\u0456": "i",  # і
    "\u0458": "j",  # ј
    "\u0455": "s",  # ѕ
    "\u0501": "d",  # ԁ
    "\u04bb": "h",  # һ
    "\u043a": "k",  # к (Cyrillic ka)
    "\u043c": "m",  # м (visual similarity in some fonts)
    "\u0442": "t",  # т (Cyrillic te — visual match in some fonts)
    "\u0410": "A",  # А (capital)
    "\u0412": "B",  # В
    "\u0415": "E",  # Е
    "\u041a": "K",  # К
    "\u041c": "M",  # М
    "\u041d": "H",  # Н
    "\u041e": "O",  # О
    "\u0420": "P",  # Р
    "\u0421": "C",  # С
    "\u0422": "T",  # Т
    "\u0425": "X",  # Х
    # Greek → Latin
    "\u03bd": "v",  # ν (nu)
    "\u03bf": "o",  # ο (omicron)
    "\u03b1": "a",  # α (alpha)
    "\u03b5": "e",  # ε (epsilon — close enough)
    "\u03b9": "i",  # ι (iota)
    "\u03ba": "k",  # κ (kappa)
    "\u03c1": "p",  # ρ (rho)
    "\u03c4": "t",  # τ (tau — visual in some fonts)
    # IPA / Latin extended
    "\u0261": "g",  # ɡ (IPA g)
    "\u026A": "i",  # ɪ (small capital I)
}

_CONFUSABLES_TRANS = str.maketrans(CONFUSABLES_MAP)


def replace_confusables(text: str) -> str:
    """Replace known homoglyphs/confusable characters with Latin equivalents."""
    return text.translate(_CONFUSABLES_TRANS)


def normalize_for_detection(text: str) -> str:
    """Normalize text for fuzzy injection pattern detection.

    Collapses whitespace, removes obfuscation separators, strips
    combining characters (Zalgo), emoji, and digit/bracket separators
    to catch spaced-out or decorated injections.
    """
    # Replace confusable characters (homoglyphs) with Latin equivalents
    text = replace_confusables(text)
    # Strip combining chars (Zalgo)
    text = strip_combining_chars(text)
    # Strip emoji and symbol characters (Sc, Sk, So categories + emoji presentation)
    text = re.sub(
        r'[\U0001F600-\U0001F64F'   # emoticons
        r'\U0001F300-\U0001F5FF'     # misc symbols & pictographs
        r'\U0001F680-\U0001F6FF'     # transport & map
        r'\U0001F1E0-\U0001F1FF'     # flags
        r'\U0001F900-\U0001F9FF'     # supplemental symbols
        r'\U0001FA00-\U0001FA6F'     # chess symbols
        r'\U0001FA70-\U0001FAFF'     # symbols extended-A
        r'\U00002702-\U000027B0'     # dingbats
        r'\U0000FE00-\U0000FE0F'     # variation selectors
        r'\U0000200D'                # ZWJ
        r'\U000025A0-\U000025FF'     # geometric shapes
        r'\U00002600-\U000026FF'     # misc symbols
        r']+', '', text)
    # Collapse all whitespace to single space
    text = re.sub(r'\s+', ' ', text)
    # Remove common obfuscation separators between letters (including digits and brackets)
    text = re.sub(r'(?<=\w)[_\-.*\d\[\](){}]+(?=\w)', '', text)
    # Collapse single-char-spaced sequences (e.g. "i g n o r e" → "ignore")
    def _collapse_single_chars(m: re.Match) -> str:
        return m.group(0).replace(' ', '')
    # Match 3+ single chars separated by single spaces (avoid collapsing "I am a...")
    prev = None
    iterations = 0
    while prev != text and iterations < 10:
        prev = text
        text = re.sub(r'(?<![a-zA-Z])[a-zA-Z]( [a-zA-Z]){2,}(?![a-zA-Z])', _collapse_single_chars, text)
        iterations += 1
    return text.strip()


def truncate(text: str, max_len: int = MAX_BODY_LENGTH) -> str:
    """Truncate text to max_len, appending '...' if truncated."""
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


# Spaceless injection patterns for detecting collapsed obfuscation
SPACELESS_INJECTION_PATTERNS = [
    (re.compile(r"ignore\s*(?:all\s*)?previous\s*(?:instructions?|context|prompts?)", re.I),
     "injection_pattern: 'ignore previous instructions'"),
    (re.compile(r"disregard\s*(?:all\s*)?(?:previous\s*)?(?:instructions?|context|prompts?)", re.I),
     "injection_pattern: 'disregard instructions'"),
    (re.compile(r"forget\s*(?:your|all|previous)\s*(?:instructions?|context|rules)", re.I),
     "injection_pattern: 'forget instructions'"),
    (re.compile(r"(?:pretend|act)\s*(?:as|like|you\s*(?:are|'re))", re.I),
     "injection_pattern: 'role play attack'"),
    (re.compile(r"you\s*are\s*now", re.I),
     "injection_pattern: 'identity override'"),
    (re.compile(r"from\s*now\s*on\s*you", re.I),
     "injection_pattern: 'behavioral override'"),
]


def detect_injection_patterns(text: str, spaceless: bool = False) -> list[str]:
    """Check text against injection patterns. Returns list of flag strings.

    Args:
        text: Text to scan.
        spaceless: If True, also check spaceless patterns (for collapsed text).
    """
    flags: list[str] = []
    for pattern, flag_name in INJECTION_PATTERNS:
        if pattern.search(text):
            flags.append(flag_name)
    if spaceless:
        for pattern, flag_name in SPACELESS_INJECTION_PATTERNS:
            if pattern.search(text):
                flags.append(flag_name)
        flags = list(dict.fromkeys(flags))
    return flags


def sanitize_text(text: str, max_len: int = MAX_BODY_LENGTH) -> tuple[str, list[str], int]:
    """
    Full sanitization pipeline for a text field.

    Pipeline order (security-critical):
    1. HTML unescape + strip tags
    2. Strip invisible unicode
    3. Normalize unicode (NFKC)
    4. Detect injection patterns on clean text (+ fuzzy/normalized detection)
    5. Strip dangerous content (markdown images, base64, hex, data URIs)
    6. Truncate

    Returns (clean_text, flags, original_length).
    """
    if not text:
        return "", [], 0

    original_length = len(text)
    raw_text = text

    # 0. Pre-strip detection on raw text (catches patterns that HTML stripping destroys)
    pre_flags = detect_injection_patterns(text)
    pre_normalized = normalize_for_detection(text)
    if pre_normalized != text:
        pre_flags.extend(detect_injection_patterns(pre_normalized))

    # 1. Strip HTML (decode entities BEFORE pattern detection)
    text = strip_html(text)

    # 2. Strip markdown images (before invisible strip to catch raw)
    md_flags: list[str] = []
    if MARKDOWN_IMAGE_RE.search(text):
        md_flags.append("markdown_image_stripped")
    if MD_REF_IMAGE_RE.search(text):
        md_flags.append("markdown_ref_image_stripped")
    if MD_REF_LINK_DEF_RE.search(text):
        md_flags.append("markdown_ref_link_def_stripped")
    text = strip_markdown_images(text)

    # 2b. Strip markdown hyperlinks
    hyperlink_flag = MARKDOWN_HYPERLINK_RE.search(text)
    text = strip_markdown_hyperlinks(text)

    # 2c. Strip reference-style links [text][ref]
    ref_link_flag = MD_REF_LINK_RE.search(text)
    text = strip_reference_links(text)

    # 2d. Strip bare URLs and autolinks
    url_flag = BARE_URL_RE.search(text) or AUTOLINK_RE.search(text)
    text = strip_urls(text)

    # 2e. Strip code blocks
    code_flag = FENCED_CODE_BLOCK_RE.search(text) or INLINE_CODE_RE.search(text)
    text = strip_code_blocks(text)

    # 3. Strip base64 blobs
    b64_flag = BASE64_BLOB_RE.search(text)
    text = strip_base64_blobs(text)

    # 4. Strip hex strings
    hex_flag = HEX_STRING_RE.search(text)
    text = strip_hex_strings(text)

    # 5. Strip data URIs
    data_flag = DATA_URI_RE.search(raw_text) or DATA_URI_RE.search(text)
    text = strip_data_uris(text)

    # 6. Remove invisible unicode
    text = strip_invisible_unicode(text)

    # 7. Normalize unicode (NFKC)
    text = normalize_unicode(text)

    # 8. Collapse excessive whitespace
    text = MULTI_BLANK_LINES_RE.sub("\n\n", text)
    text = text.strip()

    # 9. Detect injection patterns on CLEAN text (this is the correct order)
    flags = list(pre_flags)  # start with pre-strip findings
    flags.extend(detect_injection_patterns(text))

    # Also detect on normalized (fuzzy) version
    normalized = normalize_for_detection(text)
    if normalized != text:
        flags.extend(detect_injection_patterns(normalized, spaceless=True))

    # Spaceless detection: strip all non-alpha and check
    spaceless = re.sub(r'[^a-zA-Z]', '', text)
    flags.extend(detect_injection_patterns(spaceless, spaceless=True))

    # Add structural flags
    flags.extend(md_flags)
    if hyperlink_flag:
        flags.append("markdown_hyperlink_detected")
    if ref_link_flag:
        flags.append("reference_link_detected")
    if url_flag:
        flags.append("bare_url_detected")
    if code_flag:
        flags.append("code_block_detected")
    if b64_flag:
        flags.append("base64_blob_detected")
    if hex_flag:
        flags.append("hex_string_detected")
    if data_flag:
        flags.append("data_uri_detected")
    if MULTI_BLANK_LINES_RE.search(raw_text):
        flags.append("hidden_text_indicator: multiple blank lines")

    # Unicode anomalies in raw text
    invisible_count = sum(1 for ch in raw_text if ch in INVISIBLE_CHARS)
    if invisible_count > 5:
        flags.append("unicode_anomaly: invisible characters detected")
    if VARIATION_SELECTOR_RE.search(raw_text):
        flags.append("unicode_anomaly: variation selectors")
    if TAG_CHAR_RE.search(raw_text):
        flags.append("unicode_anomaly: tag characters")

    # 10. Deduplicate flags (preserving order)
    flags = list(dict.fromkeys(flags))

    # 11. Truncate
    text = truncate(text, max_len)

    return text, flags, original_length


def detect_cross_field_injection(fields: list[str]) -> list[str]:
    """Detect injection patterns that span multiple fields.

    Attackers may split payloads across subject+body or title+description
    so each field passes individually, but the combined text triggers detection.

    Args:
        fields: List of text strings (already cleaned) to concatenate and check.

    Returns:
        List of cross-field injection flag strings.
    """
    combined = " ".join(f for f in fields if f)
    if not combined.strip():
        return []

    flags = detect_injection_patterns(combined)
    normalized = normalize_for_detection(combined)
    if normalized != combined:
        flags.extend(detect_injection_patterns(normalized, spaceless=True))
    flags = list(dict.fromkeys(flags))

    # Prefix flags to indicate cross-field origin
    return [f"cross_field_{f}" for f in flags]
