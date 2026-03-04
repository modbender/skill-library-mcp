#!/usr/bin/env bash
# DocSync — Code Analysis Module
# Extracts symbols (functions, classes, types, exports) from source files
# Uses tree-sitter when available, falls back to regex patterns

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Language detection ─────────────────────────────────────────────────────

detect_language() {
  local file="$1"
  local ext="${file##*.}"
  case "$ext" in
    ts|tsx)     echo "typescript" ;;
    js|jsx|mjs) echo "javascript" ;;
    py)         echo "python" ;;
    rs)         echo "rust" ;;
    go)         echo "go" ;;
    java)       echo "java" ;;
    c|h)        echo "c" ;;
    cpp|cc|cxx|hpp) echo "cpp" ;;
    rb)         echo "ruby" ;;
    php)        echo "php" ;;
    cs)         echo "c_sharp" ;;
    swift)      echo "swift" ;;
    kt|kts)     echo "kotlin" ;;
    *)          echo "unknown" ;;
  esac
}

is_source_file() {
  local lang
  lang=$(detect_language "$1")
  [[ "$lang" != "unknown" ]]
}

# ─── tree-sitter based extraction ──────────────────────────────────────────

has_tree_sitter() {
  command -v tree-sitter &>/dev/null
}

# Extract symbols using tree-sitter query patterns
ts_extract_symbols() {
  local file="$1"
  local lang
  lang=$(detect_language "$file")

  if ! has_tree_sitter; then
    return 1
  fi

  # tree-sitter parse outputs S-expressions — we extract key node types
  local ast
  ast=$(tree-sitter parse "$file" 2>/dev/null) || return 1

  local symbols=()

  # Extract function/method declarations
  while IFS= read -r line; do
    symbols+=("$line")
  done < <(echo "$ast" | grep -oP '(function_declaration|method_definition|function_definition|fn_item|func_declaration|method_declaration)\s+name:\s*\(identifier\)\s*\[.*?\]' 2>/dev/null || true)

  # Extract class/struct/interface declarations
  while IFS= read -r line; do
    symbols+=("$line")
  done < <(echo "$ast" | grep -oP '(class_declaration|struct_item|interface_declaration|type_declaration|class_definition)\s+name:\s*\(identifier\)\s*\[.*?\]' 2>/dev/null || true)

  printf '%s\n' "${symbols[@]}" 2>/dev/null || true
}

# ─── Regex-based fallback extraction ───────────────────────────────────────

regex_extract_symbols() {
  local file="$1"
  local lang
  lang=$(detect_language "$file")

  local symbols_file
  symbols_file=$(mktemp)

  case "$lang" in
    typescript|javascript)
      # Functions: export function name(, const name = (, function name(
      grep -nP '^\s*(export\s+)?(async\s+)?function\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      grep -nP '^\s*(export\s+)?(const|let|var)\s+\w+\s*=\s*(async\s+)?\(' "$file" >> "$symbols_file" 2>/dev/null || true
      # Classes: export class Name
      grep -nP '^\s*(export\s+)?(abstract\s+)?class\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Interfaces: export interface Name
      grep -nP '^\s*(export\s+)?interface\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Type aliases: export type Name
      grep -nP '^\s*(export\s+)?type\s+\w+\s*=' "$file" >> "$symbols_file" 2>/dev/null || true
      # Enums
      grep -nP '^\s*(export\s+)?enum\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      ;;

    python)
      # Functions: def name(
      grep -nP '^\s*(async\s+)?def\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Classes: class Name
      grep -nP '^\s*class\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      ;;

    rust)
      # Functions: pub fn name, fn name
      grep -nP '^\s*(pub(\(.*?\))?\s+)?(async\s+)?fn\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Structs: pub struct Name
      grep -nP '^\s*(pub(\(.*?\))?\s+)?struct\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Enums: pub enum Name
      grep -nP '^\s*(pub(\(.*?\))?\s+)?enum\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Traits: pub trait Name
      grep -nP '^\s*(pub(\(.*?\))?\s+)?trait\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Impl blocks
      grep -nP '^\s*impl(<.*?>)?\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      ;;

    go)
      # Functions: func Name(, func (r Receiver) Name(
      grep -nP '^\s*func\s+(\(.*?\)\s+)?\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Types: type Name struct/interface
      grep -nP '^\s*type\s+\w+\s+(struct|interface)' "$file" >> "$symbols_file" 2>/dev/null || true
      ;;

    java|kotlin)
      # Classes
      grep -nP '^\s*(public|private|protected)?\s*(static\s+)?(abstract\s+)?(class|interface|enum)\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Methods
      grep -nP '^\s*(public|private|protected)?\s*(static\s+)?(abstract\s+)?\w+\s+\w+\s*\(' "$file" >> "$symbols_file" 2>/dev/null || true
      ;;

    c|cpp)
      # Functions (heuristic: type name( at start of line)
      grep -nP '^\w[\w\s\*]+\s+\w+\s*\(' "$file" >> "$symbols_file" 2>/dev/null || true
      # Structs/classes
      grep -nP '^\s*(typedef\s+)?struct\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      grep -nP '^\s*class\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      ;;

    ruby)
      # Methods: def name
      grep -nP '^\s*def\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Classes/modules
      grep -nP '^\s*(class|module)\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      ;;

    php)
      # Functions/methods
      grep -nP '^\s*(public|private|protected)?\s*(static\s+)?function\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      # Classes
      grep -nP '^\s*(abstract\s+)?class\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      grep -nP '^\s*interface\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      ;;

    swift)
      grep -nP '^\s*(public|private|internal|open)?\s*(static\s+)?(func|class|struct|protocol|enum)\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      ;;

    c_sharp)
      grep -nP '^\s*(public|private|protected|internal)?\s*(static\s+)?(abstract\s+)?(class|interface|struct|enum)\s+\w+' "$file" >> "$symbols_file" 2>/dev/null || true
      grep -nP '^\s*(public|private|protected|internal)?\s*(static\s+)?(async\s+)?\w+\s+\w+\s*\(' "$file" >> "$symbols_file" 2>/dev/null || true
      ;;
  esac

  cat "$symbols_file"
  rm -f "$symbols_file"
}

# ─── Unified extraction ────────────────────────────────────────────────────

extract_symbols() {
  local file="$1"

  if ! is_source_file "$file"; then
    return 0
  fi

  # Try tree-sitter first, fall back to regex
  if has_tree_sitter; then
    ts_extract_symbols "$file" 2>/dev/null || regex_extract_symbols "$file"
  else
    regex_extract_symbols "$file"
  fi
}

# Parse extracted symbols into a structured format (tab-separated)
# Output: TYPE\tNAME\tLINE\tFILE
parse_symbols() {
  local file="$1"
  local lang
  lang=$(detect_language "$file")

  extract_symbols "$file" | while IFS= read -r line; do
    local lineno name type
    lineno=$(echo "$line" | grep -oP '^\d+' || echo "0")

    case "$lang" in
      typescript|javascript)
        if echo "$line" | grep -qP 'function\s+'; then
          name=$(echo "$line" | grep -oP 'function\s+\K\w+')
          type="function"
        elif echo "$line" | grep -qP 'class\s+'; then
          name=$(echo "$line" | grep -oP 'class\s+\K\w+')
          type="class"
        elif echo "$line" | grep -qP 'interface\s+'; then
          name=$(echo "$line" | grep -oP 'interface\s+\K\w+')
          type="interface"
        elif echo "$line" | grep -qP 'type\s+\w+\s*='; then
          name=$(echo "$line" | grep -oP 'type\s+\K\w+')
          type="type"
        elif echo "$line" | grep -qP 'enum\s+'; then
          name=$(echo "$line" | grep -oP 'enum\s+\K\w+')
          type="enum"
        elif echo "$line" | grep -qP '(const|let|var)\s+\w+\s*='; then
          name=$(echo "$line" | grep -oP '(const|let|var)\s+\K\w+')
          type="function"
        else
          continue
        fi
        ;;
      python)
        if echo "$line" | grep -qP 'def\s+'; then
          name=$(echo "$line" | grep -oP 'def\s+\K\w+')
          type="function"
        elif echo "$line" | grep -qP 'class\s+'; then
          name=$(echo "$line" | grep -oP 'class\s+\K\w+')
          type="class"
        else
          continue
        fi
        ;;
      *)
        # Generic extraction
        if echo "$line" | grep -qiP '(function|func|fn|def|method)\s+'; then
          name=$(echo "$line" | grep -oP '(function|func|fn|def|method)\s+\K\w+')
          type="function"
        elif echo "$line" | grep -qiP '(class|struct|interface|trait|protocol|module)\s+'; then
          name=$(echo "$line" | grep -oP '(class|struct|interface|trait|protocol|module)\s+\K\w+')
          type="class"
        elif echo "$line" | grep -qiP '(enum)\s+'; then
          name=$(echo "$line" | grep -oP '(enum)\s+\K\w+')
          type="enum"
        elif echo "$line" | grep -qiP 'type\s+\w+'; then
          name=$(echo "$line" | grep -oP 'type\s+\K\w+')
          type="type"
        else
          continue
        fi
        ;;
    esac

    if [[ -n "${name:-}" ]]; then
      echo -e "${type}\t${name}\t${lineno}\t${file}"
    fi
  done
}

# Analyze a directory recursively
analyze_directory() {
  local dir="$1"
  local exclude_patterns=("node_modules" "dist" "build" ".git" "__pycache__" "vendor" ".venv" "target")

  local find_excludes=""
  for pat in "${exclude_patterns[@]}"; do
    find_excludes="$find_excludes -not -path '*/$pat/*'"
  done

  eval "find '$dir' -type f $find_excludes" 2>/dev/null | while IFS= read -r file; do
    if is_source_file "$file"; then
      parse_symbols "$file"
    fi
  done
}

# Get a summary of symbols in a file
summarize_file() {
  local file="$1"
  local functions=0
  local classes=0
  local types=0
  local enums=0

  while IFS=$'\t' read -r type name lineno filepath; do
    case "$type" in
      function) ((functions++)) || true ;;
      class)    ((classes++)) || true ;;
      type|interface) ((types++)) || true ;;
      enum)     ((enums++)) || true ;;
    esac
  done < <(parse_symbols "$file")

  echo "functions=$functions classes=$classes types=$types enums=$enums"
}
