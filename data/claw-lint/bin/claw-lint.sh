#!/usr/bin/env bash
set -euo pipefail

FORMAT="text"          # text|json
MODE="summary"         # summary|full
STRICT=0               # 0|1 (strict increases weights for critical findings)
INCLUDE_SELF=0         # 0|1
MAX_BYTES=2000000      # hash files up to this size (full/json-full)
SCAN_MAX_BYTES=1048576 # scan text files up to this size
MIN_SCORE=0            # filter results
SORT_BY="score"        # score|name
SKILL_ONLY=""
declare -a ROOTS=()

NO_IGNORE=0
declare -a IGNORE_GLOBS=(
  ".git/*" "*/.git/*"
  "node_modules/*" "*/node_modules/*"
  "venv/*" "*/venv/*"
  "__pycache__/*" "*/__pycache__/*"
  "dist/*" "*/dist/*"
  "build/*" "*/build/*"
  ".clawhub/*" "*/.clawhub/*"
)

usage() {
  cat <<'USAGE'
claw-lint — local OpenClaw skill audit (no execution)

Usage:
  claw-lint [--root DIR]... [--skill NAME]
           [--summary|--full]
           [--format text|json]
           [--strict]
           [--max-bytes N]
           [--scan-max-bytes N]
           [--min-score N]
           [--sort score|name]
           [--include-self]
           [--ignore GLOB]...
           [--no-ignore]

Defaults:
  --root $HOME/.openclaw/workspace/skills
  --root $HOME/.openclaw/skills
  --summary
  --format text
USAGE
}

err() { echo "Error: $*" >&2; exit 2; }
need_bin() { command -v "$1" >/dev/null 2>&1 || err "Missing required binary: $1"; }
is_int() { [[ "${1:-}" =~ ^[0-9]+$ ]]; }
b64() { printf '%s' "$1" | base64 | tr -d '\n'; }

human_bytes() {
  local n="${1:-0}"
  if command -v numfmt >/dev/null 2>&1; then
    numfmt --to=iec --suffix=B "$n" 2>/dev/null || printf "%sB" "$n"
  else
    printf "%sB" "$n"
  fi
}

# args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) shift; [[ $# -gt 0 ]] || err "--root needs a value"; ROOTS+=("$1"); shift ;;
    --skill) shift; [[ $# -gt 0 ]] || err "--skill needs a value"; SKILL_ONLY="$1"; shift ;;
    --format) shift; [[ $# -gt 0 ]] || err "--format needs a value"; FORMAT="$1"; shift ;;
    --summary) MODE="summary"; shift ;;
    --full) MODE="full"; shift ;;
    --strict) STRICT=1; shift ;;
    --include-self) INCLUDE_SELF=1; shift ;;
    --max-bytes) shift; [[ $# -gt 0 ]] || err "--max-bytes needs a value"; MAX_BYTES="$1"; shift ;;
    --scan-max-bytes) shift; [[ $# -gt 0 ]] || err "--scan-max-bytes needs a value"; SCAN_MAX_BYTES="$1"; shift ;;
    --min-score) shift; [[ $# -gt 0 ]] || err "--min-score needs a value"; MIN_SCORE="$1"; shift ;;
    --sort) shift; [[ $# -gt 0 ]] || err "--sort needs a value"; SORT_BY="$1"; shift ;;
    --ignore) shift; [[ $# -gt 0 ]] || err "--ignore needs a value"; IGNORE_GLOBS+=("$1"); shift ;;
    --no-ignore) NO_IGNORE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) err "Unknown arg: $1" ;;
  esac
done

need_bin bash
need_bin find
need_bin sha256sum
need_bin grep
need_bin awk
need_bin sort
need_bin stat
need_bin base64
need_bin tr
need_bin readlink
need_bin mktemp

[[ "$FORMAT" == "text" || "$FORMAT" == "json" ]] || err "Invalid --format: $FORMAT"
[[ "$MODE" == "summary" || "$MODE" == "full" ]] || err "Invalid --mode: $MODE"
[[ "$SORT_BY" == "score" || "$SORT_BY" == "name" ]] || err "Invalid --sort: $SORT_BY"
is_int "$MAX_BYTES" || err "--max-bytes must be an integer"
is_int "$SCAN_MAX_BYTES" || err "--scan-max-bytes must be an integer"
is_int "$MIN_SCORE" || err "--min-score must be an integer"

if [[ ${#ROOTS[@]} -eq 0 ]]; then
  ROOTS=("$HOME/.openclaw/workspace/skills" "$HOME/.openclaw/skills")
fi

SELF_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

is_ignored() {
  [[ $NO_IGNORE -eq 1 ]] && return 1
  local rel="$1"
  local g
  for g in "${IGNORE_GLOBS[@]}"; do
    case "$rel" in
      $g) return 0 ;;
    esac
  done
  return 1
}

# discover skills: root/<skill>/SKILL.md (workspace precedence by root order)
declare -A SKILL_DIR_BY_NAME=()
for root in "${ROOTS[@]}"; do
  [[ -d "$root" ]] || continue
  while IFS= read -r -d '' md; do
    dir="$(dirname "$md")"
    [[ $INCLUDE_SELF -eq 1 || "$dir" != "$SELF_ROOT" ]] || continue
    name="$(basename "$dir")"
    [[ -z "$SKILL_ONLY" || "$name" == "$SKILL_ONLY" ]] || continue
    [[ -n "${SKILL_DIR_BY_NAME[$name]+x}" ]] && continue
    SKILL_DIR_BY_NAME["$name"]="$dir"
  done < <(find "$root" -mindepth 2 -maxdepth 2 -name 'SKILL.md' -print0 2>/dev/null || true)
done
mapfile -t SKILL_NAMES < <(printf '%s\n' "${!SKILL_DIR_BY_NAME[@]}" | LC_ALL=C sort)

is_text_like() {
  local p="$1"
  case "$p" in
    *.md|*.txt|*.json|*.yml|*.yaml|*.sh|*.bash|*.py|*.js|*.ts|*.toml|*.ini|*.env) return 0 ;;
  esac
  head -c 2 -- "$p" 2>/dev/null | grep -q '^#!' && return 0
  return 1
}

w() {
  local base="$1"
  local strict_bonus="$2"
  if [[ $STRICT -eq 1 ]]; then echo $((base + strict_bonus)); else echo "$base"; fi
}

# safe nameref mutator (no circular refs)
add_flag() {
  local flags_name="$1"
  local score_name="$2"
  local flag="$3"
  local weight="$4"

  local -n flags_ref="$flags_name"
  local -n score_ref="$score_name"

  # If flag already exists, don't add weight again.
  local existing
  for existing in "${flags_ref[@]}"; do
    if [[ "$existing" == "$flag" ]]; then
      return 0
    fi
  done

  : "${score_ref:=0}"
  flags_ref+=("$flag")
  score_ref=$((score_ref + weight))
}

scan_text_file() {
  local f="$1"

  grep -Eqi '(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|BEGIN (RSA|OPENSSH) PRIVATE KEY|xox[baprs]-[0-9A-Za-z-]{10,})' -- "$f" \
    && add_flag "$2" "$3" "hardcoded_secrets" "$(w 90 10)" || true

  grep -Eqi '(\bcrontab\b|/etc/cron\.|systemd|launchctl|schtasks\.exe|~/.ssh/authorized_keys)' -- "$f" \
    && add_flag "$2" "$3" "persistence_or_system_tampering" "$(w 60 20)" || true

  grep -Eqi '(\bcurl\b|\bwget\b).*\\|.*(\bbash\b|\bsh\b|\bpython\b|\bnode\b)' -- "$f" \
    && add_flag "$2" "$3" "pipes_remote_to_shell" "$(w 45 25)" || true

  grep -Eqi '\b(curl|wget)\b' -- "$f" \
    && add_flag "$2" "$3" "downloads_remote_content" 12 || true

  grep -Eqi '(/dev/tcp/|\bnc\b|\bnetcat\b)' -- "$f" \
    && add_flag "$2" "$3" "raw_socket_or_netcat" 25 || true

  grep -Eqi '(\bssh\b|\bscp\b|\bsftp\b)' -- "$f" \
    && add_flag "$2" "$3" "uses_ssh_or_scp" 15 || true

  grep -Eqi '(\beval\b|bash\s+-c|sh\s+-c|python\s+-c|node\s+-e)' -- "$f" \
    && add_flag "$2" "$3" "exec_one_liners_or_eval" 20 || true

  grep -Eqi '(\bbase64\b.*-d|\bopenssl\b.*\benc\b|\bxxd\b.*-r)' -- "$f" \
    && add_flag "$2" "$3" "decodes_or_decrypts_payloads" 20 || true

  grep -Eqi '\bsudo\b' -- "$f" \
    && add_flag "$2" "$3" "mentions_sudo" 5 || true

  grep -Eqi '(rm\s+-rf\b|mkfs\.|dd\s+if=)' -- "$f" \
    && add_flag "$2" "$3" "destructive_commands" "$(w 35 15)" || true
}

audit_one_text_summary_tsv() {
  local name="$1"
  local dir="$2"

  local score=0
  local flags=()
  local file_count=0
  local total_bytes=0

  [[ -d "$dir/bin" ]] && find "$dir/bin" -type f -perm -111 2>/dev/null | grep -q . && add_flag flags score "has_executables" 2 || true
  find "$dir" -type l 2>/dev/null | grep -q . && add_flag flags score "contains_symlinks" 3 || true
  [[ -d "$dir/venv" ]] && add_flag flags score "bundles_venv" 2 || true
  [[ -d "$dir/node_modules" ]] && add_flag flags score "bundles_node_modules" 2 || true

  while IFS= read -r -d '' rel; do
    is_ignored "$rel" && continue
    local full="$dir/$rel"
    local bytes
    bytes="$(stat -c '%s' -- "$full" 2>/dev/null || echo 0)"
    file_count=$((file_count + 1))
    total_bytes=$((total_bytes + bytes))
    if [[ "$bytes" -le "$SCAN_MAX_BYTES" ]] && is_text_like "$full"; then
      scan_text_file "$full" flags score
    fi
  done < <(cd "$dir" && find . -type f -printf '%P\0' | LC_ALL=C sort -z 2>/dev/null || true)

  if [[ ${#flags[@]} -gt 0 ]]; then
    mapfile -t flags < <(printf '%s\n' "${flags[@]}" | LC_ALL=C sort -u)
  fi
  (( score > 100 )) && score=100
  (( score < MIN_SCORE )) && return 0

  local flags_csv="(none)"
  [[ ${#flags[@]} -gt 0 ]] && flags_csv="$(IFS=, ; echo "${flags[*]}")"
  printf "%s\t%s\t%s\t%s\t%s\n" "$score" "$name" "$flags_csv" "$file_count" "$total_bytes"
}

emit_json_records() {
  local want_inventory="$1"  # 0|1

  for name in "${SKILL_NAMES[@]}"; do
    local dir="${SKILL_DIR_BY_NAME[$name]}"

    local score=0
    local flags=()
    local file_count=0
    local total_bytes=0
    local skipped_hashes=0

    [[ -d "$dir/bin" ]] && find "$dir/bin" -type f -perm -111 2>/dev/null | grep -q . && add_flag flags score "has_executables" 2 || true
    find "$dir" -type l 2>/dev/null | grep -q . && add_flag flags score "contains_symlinks" 3 || true
    [[ -d "$dir/venv" ]] && add_flag flags score "bundles_venv" 2 || true
    [[ -d "$dir/node_modules" ]] && add_flag flags score "bundles_node_modules" 2 || true

    while IFS= read -r -d '' rel; do
      is_ignored "$rel" && continue
      local full="$dir/$rel"
      local bytes
      bytes="$(stat -c '%s' -- "$full" 2>/dev/null || echo 0)"
      file_count=$((file_count + 1))
      total_bytes=$((total_bytes + bytes))
      if [[ "$bytes" -le "$SCAN_MAX_BYTES" ]] && is_text_like "$full"; then
        scan_text_file "$full" flags score
      fi
    done < <(cd "$dir" && find . -type f -printf '%P\0' | LC_ALL=C sort -z 2>/dev/null || true)

    if [[ ${#flags[@]} -gt 0 ]]; then
      mapfile -t flags < <(printf '%s\n' "${flags[@]}" | LC_ALL=C sort -u)
    fi
    (( score > 100 )) && score=100
    (( score < MIN_SCORE )) && continue

    local flags_joined
    flags_joined="$(IFS=, ; echo "${flags[*]-}")"

    printf "SKILL\t%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$(b64 "$name")" "$(b64 "$dir")" "$score" "$(b64 "$flags_joined")" "$file_count" "$total_bytes"

    [[ "$want_inventory" -eq 1 ]] || continue

    while IFS= read -r -d '' rel; do
      is_ignored "$rel" && continue
      local full="$dir/$rel"
      local bytes mode sha skipped
      bytes="$(stat -c '%s' -- "$full" 2>/dev/null || echo 0)"
      mode="$(stat -c '%a' -- "$full" 2>/dev/null || echo '???')"
      sha=""
      skipped=0
      if [[ "$bytes" -le "$MAX_BYTES" ]]; then
        sha="$(sha256sum -- "$full" | awk '{print $1}')"
      else
        skipped=1
        skipped_hashes=$((skipped_hashes + 1))
      fi
      printf "FILE\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$(b64 "$name")" "$(b64 "$rel")" "$sha" "$bytes" "$mode" "$skipped"
    done < <(cd "$dir" && find . -type f -printf '%P\0' | LC_ALL=C sort -z 2>/dev/null || true)

    while IFS= read -r -d '' rel; do
      is_ignored "$rel" && continue
      local target
      target="$(readlink -- "$dir/$rel" 2>/dev/null || echo '')"
      printf "SYMLINK\t%s\t%s\t%s\n" "$(b64 "$name")" "$(b64 "$rel")" "$(b64 "$target")"
    done < <(cd "$dir" && find . -type l -printf '%P\0' | LC_ALL=C sort -z 2>/dev/null || true)
  done
}

run_text_summary() {
  local tmp
  tmp="$(mktemp)"
  for n in "${SKILL_NAMES[@]}"; do
    audit_one_text_summary_tsv "$n" "${SKILL_DIR_BY_NAME[$n]}" >>"$tmp"
  done

  if [[ "$SORT_BY" == "score" ]]; then
    LC_ALL=C sort -t$'\t' -k1,1nr -k2,2 "$tmp" -o "$tmp"
  else
    LC_ALL=C sort -t$'\t' -k2,2 "$tmp" -o "$tmp"
  fi

  printf "%-5s  %-26s  %-7s  %-10s  %s\n" "SCORE" "SKILL" "FILES" "SIZE" "FLAGS"
  printf "%-5s  %-26s  %-7s  %-10s  %s\n" "-----" "-----" "-----" "----" "-----"

  while IFS=$'\t' read -r score name flags files bytes; do
    printf "%-5s  %-26s  %-7s  %-10s  %s\n" \
      "$score" "$name" "$files" "$(human_bytes "$bytes")" "$flags"
  done <"$tmp"

  rm -f "$tmp"
}

run_text_full() {
  # Simple full mode: per-skill header + inventory hashes (can be large).
  for name in "${SKILL_NAMES[@]}"; do
    local dir="${SKILL_DIR_BY_NAME[$name]}"
    echo "== $name =="
    echo "path: $dir"
    echo "(use --format json --full for structured inventory)"
    echo
  done
}

run_json() {
  need_bin python3

  tmp="$(mktemp)"
  for n in "${SKILL_NAMES[@]}"; do
    audit_one_text_summary_tsv "$n" "${SKILL_DIR_BY_NAME[$n]}" >>"$tmp"
  done

  python3 - "$tmp" <<'PY'
import sys, json
tmp_path = sys.argv[1]
skills = []
with open(tmp_path, 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        score, name, flags, files_s, bytes_s = line.split("\t")
        skills.append({
            "name": name,
            "risk_score": int(score),
            "flags": [] if flags == "(none)" else flags.split(","),
            "summary": {"files": int(files_s), "bytes": int(bytes_s)},
        })
print(json.dumps({"skills": skills}, indent=2))
PY

  rm -f "$tmp"
}

main() {
  if [[ "$FORMAT" == "json" ]]; then
    run_json
    exit 0
  fi

  if [[ "$MODE" == "summary" ]]; then
    run_text_summary
  else
    run_text_full
  fi
}

main "$@"
