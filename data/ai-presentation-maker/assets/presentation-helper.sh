#!/usr/bin/env bash
# presentation-helper.sh — Safe operations for AI Presentation Maker
# All user-provided input passes through code-enforced sanitization.
#
# Usage:
#   bash presentation-helper.sh <command> [args...]
#
# Commands:
#   init                        — Create workspace directories
#   save-meta                   — Validate and save presentation JSON from stdin
#   save-deck <pres_id>        — Save markdown deck from stdin
#   get-meta <pres_id>         — Read presentation metadata
#   get-deck <pres_id>         — Read markdown deck
#   list                        — List all presentations
#   delete <pres_id>           — Delete a presentation (metadata + deck)
#   archive <pres_id>          — Move to archive
#   duplicate <pres_id>        — Copy presentation with new ID
#   export-pdf <pres_id>       — Export to PDF via pandoc
#   export-pptx <pres_id>      — Export to PPTX via python-pptx
#   sanitize-string <string>   — Echo sanitized version of input

set -euo pipefail

PRES_DIR="${HOME}/workspace/presentations"
DECKS_DIR="${PRES_DIR}/decks"
EXPORTS_DIR="${PRES_DIR}/exports"
ARCHIVE_DIR="${PRES_DIR}/archive"

# ──────────────────────────────────────────────
# SANITIZATION FUNCTIONS
# ──────────────────────────────────────────────

sanitize_string() {
  local input="$1"
  local max_len="${2:-200}"
  local clean
  clean=$(printf '%s' "$input" | tr -d '`$\\!(){}|;&<>#' | sed "s/['\"]//g")
  printf '%s' "$clean" | head -c "$max_len"
}

sanitize_filename() {
  local input="$1"
  local clean
  clean=$(printf '%s' "$input" | tr -cd 'a-zA-Z0-9_-' | head -c 50)
  printf '%s' "$clean"
}

validate_path() {
  local target="$1"
  local resolved
  resolved=$(realpath -m "$target" 2>/dev/null || echo "$target")
  if [[ "$resolved" != "${PRES_DIR}"* ]]; then
    echo "ERROR: Path traversal blocked — must be within ${PRES_DIR}" >&2
    return 1
  fi
  printf '%s' "$resolved"
}

validate_json() {
  local file="$1"
  if command -v jq &>/dev/null; then
    jq empty "$file" 2>/dev/null || { echo "ERROR: Invalid JSON in $file" >&2; return 1; }
  else
    local first last
    first=$(head -c 1 "$file")
    last=$(tail -c 2 "$file" | head -c 1)
    if [[ "$first" != "{" ]] || [[ "$last" != "}" ]]; then
      echo "ERROR: File does not appear to be valid JSON" >&2
      return 1
    fi
  fi
}

# ──────────────────────────────────────────────
# COMMANDS
# ──────────────────────────────────────────────

cmd_init() {
  mkdir -p "${DECKS_DIR}" "${EXPORTS_DIR}" "${ARCHIVE_DIR}"
  echo "✅ Workspace created at ${PRES_DIR}"
}

cmd_save_meta() {
  local tmp="/tmp/pres_meta_tmp.json"
  cat > "$tmp"
  
  validate_json "$tmp"
  
  local pres_id
  if command -v jq &>/dev/null; then
    pres_id=$(jq -r '.presentation_id // empty' "$tmp")
  else
    pres_id=$(grep -o '"presentation_id": *"[^"]*"' "$tmp" | head -1 | cut -d'"' -f4)
  fi
  
  [[ -z "$pres_id" ]] && { echo "ERROR: No presentation_id in JSON" >&2; rm -f "$tmp"; return 1; }
  
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  local target="${DECKS_DIR}/${safe_id}.json"
  
  validate_path "$target" >/dev/null
  
  cp "$tmp" "$target"
  rm -f "$tmp"
  echo "✅ Metadata saved: ${safe_id}.json"
}

cmd_save_deck() {
  local pres_id="$1"
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  local target="${DECKS_DIR}/${safe_id}.md"
  
  validate_path "$target" >/dev/null
  
  # Read markdown from stdin
  cat > "$target"
  
  if [[ -s "$target" ]]; then
    local slide_count
    slide_count=$(grep -c "^## " "$target" 2>/dev/null || echo 0)
    echo "✅ Deck saved: ${safe_id}.md (${slide_count} slides)"
  else
    echo "ERROR: Deck file is empty" >&2
    return 1
  fi
}

cmd_get_meta() {
  local pres_id="$1"
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  local target="${DECKS_DIR}/${safe_id}.json"
  
  validate_path "$target" >/dev/null
  [[ -f "$target" ]] || { echo "ERROR: Presentation not found: ${safe_id}" >&2; return 1; }
  
  cat "$target"
}

cmd_get_deck() {
  local pres_id="$1"
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  local target="${DECKS_DIR}/${safe_id}.md"
  
  validate_path "$target" >/dev/null
  [[ -f "$target" ]] || { echo "ERROR: Deck not found: ${safe_id}" >&2; return 1; }
  
  cat "$target"
}

cmd_list() {
  if [[ ! -d "$DECKS_DIR" ]] || [[ -z "$(ls -A "$DECKS_DIR"/*.json 2>/dev/null)" ]]; then
    echo "No presentations found."
    return 0
  fi
  
  for f in "${DECKS_DIR}"/*.json; do
    [[ -f "$f" ]] || continue
    
    local name created slide_count angle
    if command -v jq &>/dev/null; then
      name=$(jq -r '.name // "Untitled"' "$f")
      created=$(jq -r '.created // "Unknown"' "$f")
      angle=$(jq -r '.angle.title // "No angle"' "$f")
      slide_count=$(jq -r '.slides | length // 0' "$f")
    else
      name=$(grep -o '"name": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
      created=$(grep -o '"created": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
      angle=$(grep -o '"title": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
      slide_count="?"
    fi
    
    local pres_id
    pres_id=$(basename "$f" .json)
    printf '%-12s %-30s %-25s %s slides  %s\n' "$pres_id" "${name:0:29}" "${angle:0:24}" "$slide_count" "${created:0:10}"
  done
}

cmd_delete() {
  local pres_id="$1"
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  
  local meta="${DECKS_DIR}/${safe_id}.json"
  local deck="${DECKS_DIR}/${safe_id}.md"
  
  validate_path "$meta" >/dev/null
  validate_path "$deck" >/dev/null
  
  local deleted=0
  [[ -f "$meta" ]] && { rm -f "$meta"; deleted=$((deleted + 1)); }
  [[ -f "$deck" ]] && { rm -f "$deck"; deleted=$((deleted + 1)); }
  
  # Also remove exports
  rm -f "${EXPORTS_DIR}/${safe_id}".*  2>/dev/null
  
  if [[ $deleted -gt 0 ]]; then
    echo "✅ Deleted: ${safe_id} (${deleted} files)"
  else
    echo "ERROR: Presentation not found: ${safe_id}" >&2
    return 1
  fi
}

cmd_archive() {
  local pres_id="$1"
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  
  local meta_src="${DECKS_DIR}/${safe_id}.json"
  local deck_src="${DECKS_DIR}/${safe_id}.md"
  
  validate_path "$meta_src" >/dev/null
  
  local moved=0
  [[ -f "$meta_src" ]] && { mv "$meta_src" "${ARCHIVE_DIR}/"; moved=$((moved + 1)); }
  [[ -f "$deck_src" ]] && { mv "$deck_src" "${ARCHIVE_DIR}/"; moved=$((moved + 1)); }
  
  if [[ $moved -gt 0 ]]; then
    echo "✅ Archived: ${safe_id}"
  else
    echo "ERROR: Presentation not found: ${safe_id}" >&2
    return 1
  fi
}

cmd_duplicate() {
  local pres_id="$1"
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  
  local meta_src="${DECKS_DIR}/${safe_id}.json"
  local deck_src="${DECKS_DIR}/${safe_id}.md"
  
  [[ -f "$meta_src" ]] || { echo "ERROR: Presentation not found: ${safe_id}" >&2; return 1; }
  
  # Generate new ID
  local new_id
  new_id="pres_$(head -c 4 /dev/urandom | od -An -tx1 | tr -d ' ')"
  local safe_new_id
  safe_new_id=$(sanitize_filename "$new_id")
  
  local meta_dst="${DECKS_DIR}/${safe_new_id}.json"
  local deck_dst="${DECKS_DIR}/${safe_new_id}.md"
  
  # Copy metadata with new ID
  if command -v jq &>/dev/null; then
    jq --arg id "$safe_new_id" --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      '.presentation_id = $id | .created = $now | .updated = $now | .name = .name + " (copy)"' \
      "$meta_src" > "$meta_dst"
  else
    sed "s/\"presentation_id\": *\"[^\"]*\"/\"presentation_id\": \"${safe_new_id}\"/" "$meta_src" > "$meta_dst"
  fi
  
  # Copy deck
  [[ -f "$deck_src" ]] && cp "$deck_src" "$deck_dst"
  
  echo "✅ Duplicated: ${safe_id} → ${safe_new_id}"
  echo "New ID: ${safe_new_id}"
}

cmd_export_pdf() {
  local pres_id="$1"
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  local deck="${DECKS_DIR}/${safe_id}.md"
  local output="${EXPORTS_DIR}/${safe_id}.pdf"
  
  validate_path "$deck" >/dev/null
  [[ -f "$deck" ]] || { echo "ERROR: Deck not found: ${safe_id}" >&2; return 1; }
  
  command -v pandoc &>/dev/null || { echo "ERROR: pandoc not installed. Install with your package manager." >&2; return 1; }
  
  pandoc "$deck" -o "$output" --pdf-engine=xelatex 2>/dev/null || \
  pandoc "$deck" -o "$output" 2>/dev/null || \
  { echo "ERROR: PDF export failed. Try: pandoc $deck -o $output" >&2; return 1; }
  
  echo "✅ PDF exported: ${output}"
}

cmd_export_pptx() {
  local pres_id="$1"
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  local deck="${DECKS_DIR}/${safe_id}.md"
  local meta="${DECKS_DIR}/${safe_id}.json"
  local output="${EXPORTS_DIR}/${safe_id}.pptx"
  
  validate_path "$deck" >/dev/null
  [[ -f "$deck" ]] || { echo "ERROR: Deck not found: ${safe_id}" >&2; return 1; }
  
  python3 -c "import pptx" 2>/dev/null || { echo "ERROR: python-pptx not installed. Install with: pip install python-pptx" >&2; return 1; }
  
  # Generate PPTX using the export script
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  
  local export_script="${script_dir}/../references/export-pptx.py"
  [[ -f "$export_script" ]] || export_script="${script_dir}/export-pptx.py"
  
  if [[ -f "$export_script" ]]; then
    python3 "$export_script" "$deck" "$output" "$meta"
  else
    echo "ERROR: export-pptx.py not found" >&2
    return 1
  fi
  
  echo "✅ PPTX exported: ${output}"
}

cmd_export_html() {
  local pres_id="$1"
  local theme="${2:-gradient}"
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  local deck="${DECKS_DIR}/${safe_id}.md"
  local meta="${DECKS_DIR}/${safe_id}.json"
  local output="${EXPORTS_DIR}/${safe_id}.html"
  
  validate_path "$deck" >/dev/null
  [[ -f "$deck" ]] || { echo "ERROR: Deck not found: ${safe_id}" >&2; return 1; }
  
  which python3 &>/dev/null || { echo "ERROR: python3 not found" >&2; return 1; }
  
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  
  local export_script="${script_dir}/../references/export-html-slides.py"
  [[ -f "$export_script" ]] || export_script="${script_dir}/export-html-slides.py"
  
  if [[ -f "$export_script" ]]; then
    local meta_arg=""
    [[ -f "$meta" ]] && meta_arg="$meta"
    python3 "$export_script" "$deck" "$output" $meta_arg --theme "$theme"
  else
    echo "ERROR: export-html-slides.py not found" >&2
    return 1
  fi
}

cmd_export_gamma() {
  local pres_id="$1"
  local safe_id
  safe_id=$(sanitize_filename "$pres_id")
  local deck="${DECKS_DIR}/${safe_id}.md"
  local output="${EXPORTS_DIR}/${safe_id}_gamma.md"
  
  validate_path "$deck" >/dev/null
  [[ -f "$deck" ]] || { echo "ERROR: Deck not found: ${safe_id}" >&2; return 1; }
  
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  
  local export_script="${script_dir}/../references/export-gamma.sh"
  [[ -f "$export_script" ]] || export_script="${script_dir}/export-gamma.sh"
  
  if [[ -f "$export_script" ]]; then
    bash "$export_script" "$deck" "$output"
  else
    echo "ERROR: export-gamma.sh not found" >&2
    return 1
  fi
}

cmd_sanitize_string() {
  sanitize_string "$1" "${2:-200}"
}

# ──────────────────────────────────────────────
# MAIN DISPATCH
# ──────────────────────────────────────────────

case "${1:-}" in
  init)             cmd_init ;;
  save-meta)        cmd_save_meta ;;
  save-deck)        cmd_save_deck "${2:?ERROR: pres_id required}" ;;
  get-meta)         cmd_get_meta "${2:?ERROR: pres_id required}" ;;
  get-deck)         cmd_get_deck "${2:?ERROR: pres_id required}" ;;
  list)             cmd_list ;;
  delete)           cmd_delete "${2:?ERROR: pres_id required}" ;;
  archive)          cmd_archive "${2:?ERROR: pres_id required}" ;;
  duplicate)        cmd_duplicate "${2:?ERROR: pres_id required}" ;;
  export-pdf)       cmd_export_pdf "${2:?ERROR: pres_id required}" ;;
  export-pptx)      cmd_export_pptx "${2:?ERROR: pres_id required}" ;;
  export-html)      cmd_export_html "${2:?ERROR: pres_id required}" "${3:-gradient}" ;;
  export-gamma)     cmd_export_gamma "${2:?ERROR: pres_id required}" ;;
  sanitize-string)  cmd_sanitize_string "${2:?ERROR: string required}" "${3:-200}" ;;
  *)
    echo "presentation-helper.sh — Safe operations for AI Presentation Maker"
    echo ""
    echo "Commands:"
    echo "  init                        Create workspace"
    echo "  save-meta                   Save presentation JSON from stdin"
    echo "  save-deck <pres_id>         Save markdown deck from stdin"
    echo "  get-meta <pres_id>          Read presentation metadata"
    echo "  get-deck <pres_id>          Read markdown deck"
    echo "  list                        List all presentations"
    echo "  delete <pres_id>            Delete presentation"
    echo "  archive <pres_id>           Move to archive"
    echo "  duplicate <pres_id>         Copy with new ID"
    echo "  export-pdf <pres_id>        Export to PDF"
    echo "  export-pptx <pres_id>       Export to PPTX"
    echo "  export-html <pres_id> [theme]  Export to HTML slides (dark/light/gradient)"
    echo "  export-gamma <pres_id>      Export for Gamma.app import"
    echo "  sanitize-string <str> [max] Sanitize input"
    ;;
esac
