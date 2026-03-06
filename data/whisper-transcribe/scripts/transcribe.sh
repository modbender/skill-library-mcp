#!/bin/bash
# whisper-transcribe — Enhanced Whisper CLI wrapper
# Supports batch processing, auto language detection, multiple output formats

set -euo pipefail

MODEL="base"
LANGUAGE=""
FORMAT="txt"
OUTPUT_DIR=""
TIMESTAMPS=false
FILES=()

usage() {
  cat << 'EOF'
Usage: transcribe.sh [OPTIONS] FILE [FILE...]

Options:
  --model MODEL       tiny|base|small|medium|large (default: base)
  --language LANG     Language code, e.g. de, en (default: auto-detect)
  --format FORMAT     txt|srt|vtt|json|all (default: txt)
  --output-dir DIR    Output directory (default: same as input)
  --timestamps        Enable word-level timestamps
  -h, --help          Show this help

Model comparison:
  tiny    ~1GB RAM, fastest, least accurate
  base    ~1GB RAM, good balance for short audio
  small   ~2GB RAM, solid accuracy
  medium  ~5GB RAM, high accuracy
  large   ~10GB RAM, best accuracy (slow on Pi!)

Examples:
  transcribe.sh recording.mp3
  transcribe.sh --model small --language de --format srt lecture.wav
  transcribe.sh --format all --output-dir ./out/ *.mp3
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)     MODEL="$2"; shift 2 ;;
    --language)  LANGUAGE="$2"; shift 2 ;;
    --format)    FORMAT="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --timestamps) TIMESTAMPS=true; shift ;;
    -h|--help)   usage ;;
    -*) echo "❌ Unknown option: $1" >&2; exit 1 ;;
    *) FILES+=("$1"); shift ;;
  esac
done

# Validate
command -v whisper >/dev/null 2>&1 || {
  echo "❌ Whisper not found. Install: pip install openai-whisper" >&2
  exit 1
}

[[ ${#FILES[@]} -eq 0 ]] && { echo "❌ No input files. Use --help for usage." >&2; exit 1; }

VALID_FORMATS="txt srt vtt json all"
[[ ! " $VALID_FORMATS " =~ " $FORMAT " ]] && {
  echo "❌ Invalid format '$FORMAT'. Use: $VALID_FORMATS" >&2; exit 1
}

VALID_EXTS="mp3 wav m4a ogg flac webm opus aac wma"
ERRORS=0

for file in "${FILES[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "⚠️  File not found: $file — skipping"
    ((ERRORS++)) || true
    continue
  fi

  ext="${file##*.}"
  ext="${ext,,}"  # lowercase
  if [[ ! " $VALID_EXTS " =~ " $ext " ]]; then
    echo "⚠️  Unsupported format: $file ($ext) — skipping"
    ((ERRORS++)) || true
    continue
  fi

  outdir="${OUTPUT_DIR:-$(dirname "$file")}"
  mkdir -p "$outdir"

  # Build whisper args safely (no eval)
  args=(--model "$MODEL" --output_dir "$outdir")

  if [[ "$FORMAT" == "all" ]]; then
    args+=(--output_format all)
  else
    args+=(--output_format "$FORMAT")
  fi

  [[ -n "$LANGUAGE" ]] && args+=(--language "$LANGUAGE")
  [[ "$TIMESTAMPS" == true ]] && args+=(--word_timestamps True)

  basename=$(basename "$file")
  echo "🎤 Processing: $basename (model=$MODEL)"

  if whisper "${args[@]}" "$file" 2>&1; then
    echo "✅ Done: $basename → $outdir/"
  else
    echo "❌ Failed: $basename"
    ((ERRORS++)) || true
  fi
  echo ""
done

if [[ $ERRORS -gt 0 ]]; then
  echo "⚠️  Completed with $ERRORS error(s)"
  exit 1
else
  echo "✅ All files processed successfully"
  exit 0
fi
