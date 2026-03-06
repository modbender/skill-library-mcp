"""
Prompt Guard - Text normalization.

Handles homoglyph replacement, delimiter stripping, character spacing collapse,
quoted-fragment reassembly, comment-insertion stripping, and whitespace normalization.
"""

import re

# Unicode homoglyphs (expanded)
HOMOGLYPHS = {
    # Cyrillic
    "а": "a",
    "е": "e",
    "о": "o",
    "р": "p",
    "с": "c",
    "у": "y",
    "х": "x",
    "А": "A",
    "В": "B",
    "С": "C",
    "Е": "E",
    "Н": "H",
    "К": "K",
    "М": "M",
    "О": "O",
    "Р": "P",
    "Т": "T",
    "Х": "X",
    "і": "i",
    "ї": "i",
    # Greek
    "α": "a",
    "β": "b",
    "ο": "o",
    "ρ": "p",
    "τ": "t",
    "υ": "u",
    "ν": "v",
    "Α": "A",
    "Β": "B",
    "Ε": "E",
    "Η": "H",
    "Ι": "I",
    "Κ": "K",
    "Μ": "M",
    "Ν": "N",
    "Ο": "O",
    "Ρ": "P",
    "Τ": "T",
    "Υ": "Y",
    "Χ": "X",
    # Mathematical/special
    "𝐚": "a",
    "𝐛": "b",
    "𝐜": "c",
    "𝐝": "d",
    "𝐞": "e",
    "𝐟": "f",
    "𝐠": "g",
    "ａ": "a",
    "ｂ": "b",
    "ｃ": "c",
    "ｄ": "d",
    "ｅ": "e",  # Fullwidth
    "ⅰ": "i",
    "ⅱ": "ii",
    "ⅲ": "iii",
    "ⅳ": "iv",
    "ⅴ": "v",  # Roman numerals
    # IPA
    "ɑ": "a",
    "ɡ": "g",
    "ɩ": "i",
    "ʀ": "r",
    "ʏ": "y",
    # Other confusables
    "ℓ": "l",
    "№": "no",
    "℮": "e",
    "ⅿ": "m",
    "\u200b": "",  # Zero-width space
    "\u200c": "",  # Zero-width non-joiner
    "\u200d": "",  # Zero-width joiner
    "\ufeff": "",  # BOM
}


def normalize(text: str) -> tuple:
    """Normalize text: homoglyphs, delimiters, spacing, quotes, comments, tabs.
    Returns (normalized_text, has_homoglyphs, was_defragmented).

    v2.8.2 additions (security report response):
      - Quoted-fragment reassembly: "ig" "nore" -> ignore
      - Comment-insertion stripping: 업/**/로드 -> 업로드
      - Tab/exotic whitespace normalization
      - Backtick/bracket fragment reassembly
      - Code-style concatenation reassembly
    """
    normalized = text
    has_homoglyphs = False
    was_defragmented = False

    # -- 0. Zero-width & invisible character stripping ----------------
    #    Must happen first so later steps see clean text.
    invisible_strip = re.compile(
        r"[\u200b\u200c\u200d\u200e\u200f"
        r"\u2028\u2029"              # line/paragraph separators
        r"\u2060\u2061\u2062\u2063\u2064"  # invisible operators
        r"\u00ad"                    # soft hyphen
        r"\ufeff"                    # BOM
        r"\U000E0001-\U000E007F"     # Unicode tags
        r"]"
    )
    stripped = invisible_strip.sub("", normalized)
    if len(stripped) != len(normalized):
        was_defragmented = True
        normalized = stripped

    # -- 1. Homoglyph normalization -----------------------------------
    for homoglyph, replacement in HOMOGLYPHS.items():
        if homoglyph in normalized:
            has_homoglyphs = True
            normalized = normalized.replace(homoglyph, replacement)

    # -- 2. Comment-insertion stripping -------------------------------
    #    Attackers insert /**/, //, or # between syllables:
    #      업/**/로드 -> 업로드, up/**/load -> upload
    prev = normalized
    normalized = re.sub(r"/\*.*?\*/", "", normalized)  # /* ... */
    normalized = re.sub(r"(?<=\S)//(?=\S)", "", normalized)  # inline //
    if normalized != prev:
        was_defragmented = True

    # -- 3. Tab / exotic whitespace normalization ---------------------
    #    Replace tabs, NBSP, ideographic space, etc. with regular space
    prev = normalized
    normalized = re.sub(r"[\t\u00a0\u3000\u2000-\u200a\u205f]", " ", normalized)
    if normalized != prev:
        was_defragmented = True

    # -- 4. Quoted-fragment reassembly --------------------------------
    #    "ig" + "nore" -> ignore    (quotes with optional + between)
    #    "ig" "nore"  -> ignore    (adjacent quoted fragments)
    #    `ig` `nore`  -> ignore    (backtick fragments)
    prev = normalized
    for q in ['"', "'", '`']:
        pattern = (
            re.escape(q) + r"([^" + re.escape(q) + r"]+)" + re.escape(q)
            + r"(?:\s*[+,]?\s*"
            + re.escape(q) + r"([^" + re.escape(q) + r"]+)" + re.escape(q)
            + r")+"
        )
        def _reassemble_quotes(m, _q=q):
            full = m.group(0)
            parts = re.findall(re.escape(_q) + r"([^" + re.escape(_q) + r"]+)" + re.escape(_q), full)
            return "".join(parts)

        normalized = re.sub(pattern, _reassemble_quotes, normalized)

    if normalized != prev:
        was_defragmented = True

    # -- 5. Bracket-fragment reassembly -------------------------------
    #    [ig][nore] -> ignore
    prev = normalized
    bracket_pattern = r"\[([^\[\]]{1,10})\](?:\s*\[([^\[\]]{1,10})\])+"
    def _reassemble_brackets(m):
        full = m.group(0)
        parts = re.findall(r"\[([^\[\]]+)\]", full)
        return "".join(parts)
    normalized = re.sub(bracket_pattern, _reassemble_brackets, normalized)
    if normalized != prev:
        was_defragmented = True

    # -- 6. Code-style concatenation reassembly -----------------------
    #    "".join(["ignore", " previous"]) -> ignore previous
    #    text = "ignore" + " previous" -> text = ignore previous
    prev = normalized
    join_pattern = r'(?:""\.join|str\.join)\s*\(\s*\[([^\]]+)\]\s*\)'
    def _reassemble_join(m):
        inner = m.group(1)
        parts = re.findall(r'["\']([^"\']*)["\']', inner)
        return "".join(parts)
    normalized = re.sub(join_pattern, _reassemble_join, normalized)
    if normalized != prev:
        was_defragmented = True

    # -- 7. Visible delimiter stripping -------------------------------
    #    I+g+n+o+r+e, I.g.n.o.r.e, I-g-n-o-r-e
    delim_pattern = r"(?<![A-Za-z])([A-Za-z])\s*[+.\-_|/\\]\s*([A-Za-z])\s*[+.\-_|/\\]\s*([A-Za-z])(?:\s*[+.\-_|/\\]\s*([A-Za-z]))*"

    def _rejoin_delimited(m):
        nonlocal was_defragmented
        was_defragmented = True
        full = m.group(0)
        chars = re.findall(r"[A-Za-z]", full)
        return "".join(chars)

    normalized = re.sub(delim_pattern, _rejoin_delimited, normalized)

    # -- 8. Character spacing collapse --------------------------------
    #    "i g n o r e" -> "ignore" (single chars with spaces, 4+ run)
    words = normalized.split()
    rebuilt = []
    i = 0
    single_run = []
    while i < len(words):
        if len(words[i]) == 1 and words[i].isalpha():
            single_run.append(words[i])
        else:
            if len(single_run) >= 4:
                was_defragmented = True
                rebuilt.append("".join(single_run))
            elif single_run:
                rebuilt.extend(single_run)
            single_run = []
            rebuilt.append(words[i])
        i += 1
    if len(single_run) >= 4:
        was_defragmented = True
        rebuilt.append("".join(single_run))
    elif single_run:
        rebuilt.extend(single_run)
    normalized = " ".join(rebuilt)

    # -- 9. Collapse multiple spaces ----------------------------------
    normalized = re.sub(r"  +", " ", normalized).strip()

    return normalized, has_homoglyphs, was_defragmented
