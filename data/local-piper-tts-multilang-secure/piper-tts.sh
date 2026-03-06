#!/bin/bash
# Local Piper TTS wrapper — bundled with local-piper-tts-multilang-secure.
# Lives in ~/.openclaw/skills/local-piper-tts-multilang-secure/
# Usage: piper-tts.sh "Text to synthesize" [output.wav]
#
# Portable: uses only grep -Eq with literal UTF-8 characters (no -P / PCRE).
# Works on GNU grep (Linux) and BSD grep (macOS) alike.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_ACTIVATE="${SCRIPT_DIR}/venv/bin/activate"

TEXT="$1"
OUTPUT="${2:-${SCRIPT_DIR}/output.wav}"

if [ -z "$TEXT" ]; then
    echo "Usage: $0 \"Text to synthesize\" [output.wav]" >&2
    exit 1
fi

if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "Error: Piper venv not found at ${SCRIPT_DIR}/venv. Run setup() from the skill." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Helper: find the first installed .onnx model matching a language prefix.
# Usage: find_model "pl" → first pl_*.onnx, find_model "en" → first en_*.onnx
# ---------------------------------------------------------------------------
find_model() {
  local prefix="$1"
  local m
  m=$(ls "${SCRIPT_DIR}"/${prefix}_*.onnx 2>/dev/null | head -1)
  [ -n "$m" ] && echo "$m"
}

# ---------------------------------------------------------------------------
# Helper: test whether TEXT contains any character from a given set.
# Uses grep -Eq with literal UTF-8 — portable across GNU and BSD grep.
# ---------------------------------------------------------------------------
text_has() {
  printf '%s\n' "$TEXT" | grep -Eq "$1"
}

text_has_i() {
  printf '%s\n' "$TEXT" | grep -Eqi "$1"
}

# ---------------------------------------------------------------------------
# Voice model selection — no hardcoded filenames.
# Priority: PIPER_VOICE_MODEL env override > language heuristics > first EN > any model.
#
# To add a language: install the .onnx + .onnx.json pair and add a heuristic below.
# The detection is best-effort based on character/script analysis.
# For reliable language selection, pass the `voice` parameter explicitly.
# ---------------------------------------------------------------------------
detect_voice_model() {
  # 0) Explicit override always wins.
  if [ -n "${PIPER_VOICE_MODEL}" ] && [ -f "${PIPER_VOICE_MODEL}" ]; then
    echo "${PIPER_VOICE_MODEL}"
    return
  fi

  # --- Non-Latin scripts (unambiguous) ---
  # Using representative literal characters instead of \p{} property classes for portability.

  # Cyrillic — sample characters from the block: а-я, А-Я, and common extras
  # Ukrainian-specific: іїєґ
  if text_has '[абвгдежзийклмнопрстуфхцчшщъыьэюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯіїєґІЇЄҐёЁ]'; then
    if text_has '[іїєґІЇЄҐ]'; then
      local m; m=$(find_model "uk"); [ -n "$m" ] && echo "$m" && return
    fi
    local m; m=$(find_model "ru"); [ -n "$m" ] && echo "$m" && return
    m=$(find_model "bg"); [ -n "$m" ] && echo "$m" && return
    m=$(find_model "sr"); [ -n "$m" ] && echo "$m" && return
  fi

  # Greek — sample: α-ω, Α-Ω, accented vowels
  if text_has '[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩάέήίόύώ]'; then
    local m; m=$(find_model "el"); [ -n "$m" ] && echo "$m" && return
  fi

  # Arabic script — sample Arabic + Persian-specific letters
  if text_has '[ابتثجحخدذرزسشصضطظعغفقكلمنهويءآأؤإئ]'; then
    # Persian-specific: پچژگ
    if text_has '[پچژگ]'; then
      local m; m=$(find_model "fa"); [ -n "$m" ] && echo "$m" && return
    fi
    local m; m=$(find_model "ar"); [ -n "$m" ] && echo "$m" && return
  fi

  # Japanese — Hiragana (ぁ-ん) or Katakana (ァ-ヶ)
  if text_has '[ぁあいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんァアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン]'; then
    local m; m=$(find_model "ja"); [ -n "$m" ] && echo "$m" && return
  fi

  # Chinese — common CJK ideographs (sample set)
  if text_has '[的一是不了人我在有他这为之大来以个中上们到说时地也子就道会那要下看天出小么起你都把好过没多少我们它]'; then
    local m; m=$(find_model "zh"); [ -n "$m" ] && echo "$m" && return
  fi

  # Korean — Hangul syllables (sample set from common syllables)
  if text_has '[가나다라마바사아자차카타파하고노도로모보소오조초코토포호그는를이의에서한]'; then
    local m; m=$(find_model "ko"); [ -n "$m" ] && echo "$m" && return
  fi

  # Georgian — sample characters
  if text_has '[აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ]'; then
    local m; m=$(find_model "ka"); [ -n "$m" ] && echo "$m" && return
  fi

  # --- Latin-script languages (ordered from most to least distinctive characters) ---

  # Vietnamese — highly distinctive: ăơưđ
  if text_has_i '[ăơưđ]'; then
    local m; m=$(find_model "vi"); [ -n "$m" ] && echo "$m" && return
  fi

  # Polish — unique: ąćęłńśźż
  if text_has_i '[ąćęłńśźż]'; then
    local m; m=$(find_model "pl"); [ -n "$m" ] && echo "$m" && return
  fi

  # Romanian — unique: șț (with comma below, not cedilla)
  if text_has_i '[șț]'; then
    local m; m=$(find_model "ro"); [ -n "$m" ] && echo "$m" && return
  fi

  # Turkish — unique: ğışİ (dotless ı and dotted İ)
  if text_has '[ğışİ]'; then
    local m; m=$(find_model "tr"); [ -n "$m" ] && echo "$m" && return
  fi

  # Czech/Slovak — unique: ěščřžďťň (ů is Czech-only)
  if text_has_i '[ěščřžďťň]'; then
    if text_has_i '[ů]'; then
      local m; m=$(find_model "cs"); [ -n "$m" ] && echo "$m" && return
    fi
    local m; m=$(find_model "sk"); [ -n "$m" ] && echo "$m" && return
    m=$(find_model "cs"); [ -n "$m" ] && echo "$m" && return
  fi

  # Hungarian — unique: őű (double-acute accents)
  if text_has_i '[őű]'; then
    local m; m=$(find_model "hu"); [ -n "$m" ] && echo "$m" && return
  fi

  # Portuguese — ãõ combo is distinctive
  if text_has_i '[ãõ]'; then
    local m; m=$(find_model "pt"); [ -n "$m" ] && echo "$m" && return
  fi

  # Spanish — ñ and inverted punctuation
  if text_has_i '[ñ¿¡]'; then
    local m; m=$(find_model "es"); [ -n "$m" ] && echo "$m" && return
  fi

  # Catalan — unique: l·l (geminated L)
  if text_has 'l·l'; then
    local m; m=$(find_model "ca"); [ -n "$m" ] && echo "$m" && return
  fi

  # German — ß is unique to German; äöü overlap with others
  if text_has 'ß'; then
    local m; m=$(find_model "de"); [ -n "$m" ] && echo "$m" && return
  fi
  # äöü without ß — could be German, Finnish, Swedish, etc. Try German first.
  if text_has_i '[äöü]' && ! text_has_i '[åæø]'; then
    local m; m=$(find_model "de"); [ -n "$m" ] && echo "$m" && return
    m=$(find_model "fi"); [ -n "$m" ] && echo "$m" && return
  fi

  # Scandinavian — å, æ, ø
  if text_has_i '[åæø]'; then
    # Norwegian and Danish use æø, Swedish uses åäö
    if text_has_i '[æø]'; then
      local m; m=$(find_model "no"); [ -n "$m" ] && echo "$m" && return
      m=$(find_model "nb"); [ -n "$m" ] && echo "$m" && return
      m=$(find_model "da"); [ -n "$m" ] && echo "$m" && return
    fi
    local m; m=$(find_model "sv"); [ -n "$m" ] && echo "$m" && return
  fi

  # French — distinctive: œçèêëïî
  if text_has_i '[œçèêëïî]'; then
    local m; m=$(find_model "fr"); [ -n "$m" ] && echo "$m" && return
  fi

  # Italian — common accented endings: àèìòù (overlaps, so low priority)
  if text_has_i '[àèìòù]'; then
    local m; m=$(find_model "it"); [ -n "$m" ] && echo "$m" && return
  fi

  # Dutch — ij digraph is common but not unique; hard to detect reliably.
  # Will fall through to English or "any model" below.

  # --- Fallback: English keywords ---
  if text_has_i '\b(the|this|that|these|those|is|are|was|were|and|or|but|with|from|hello|alright|sure|you|we|they)\b'; then
    local m; m=$(find_model "en"); [ -n "$m" ] && echo "$m" && return
  fi

  # --- Default: first English model ---
  local m; m=$(find_model "en"); [ -n "$m" ] && echo "$m" && return

  # --- Last resort: any installed model ---
  ls "${SCRIPT_DIR}"/*.onnx 2>/dev/null | head -1
}

VOICE_MODEL_SELECTED="$(detect_voice_model)"

if [ -z "$VOICE_MODEL_SELECTED" ] || [ ! -f "$VOICE_MODEL_SELECTED" ]; then
    echo "Error: No voice model found in ${SCRIPT_DIR}. Download a .onnx model from https://github.com/rhasspy/piper/blob/master/VOICES.md" >&2
    exit 1
fi

# Activate venv and synthesize via stdin (text never touches a shell command string)
source "$VENV_ACTIVATE"
printf '%s\n' "$TEXT" | piper -m "$VOICE_MODEL_SELECTED" --output_file "$OUTPUT" --length-scale "${PIPER_LENGTH_SCALE:-1.0}"

if [ $? -eq 0 ]; then
    echo "$OUTPUT"
else
    echo "Error: Piper synthesis failed" >&2
    exit 1
fi
