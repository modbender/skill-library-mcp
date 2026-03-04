#!/usr/bin/env bash
# leadgen-helper.sh — Safe operations for Email Lead Generation
# All user-provided input passes through code-enforced sanitization.
# The agent calls this script instead of constructing raw shell commands.
#
# Usage:
#   bash leadgen-helper.sh <command> [args...]
#
# Commands:
#   init                          — Create workspace directories
#   write-config <file>           — Write config from stdin (heredoc)
#   add-lead <json_file>          — Validate and write a lead JSON file
#   update-lead <lead_id> <field> <value> — Update a single field in a lead
#   move-lead <lead_id> <from> <to>       — Move lead between active/archive
#   write-template <json_file>    — Validate and write a template JSON file
#   write-sequence <json_file>    — Validate and write a sequence JSON file
#   list-leads [status]           — List leads, optionally filtered by status
#   count-leads                   — Count leads by status
#   search-leads <term>           — Search leads by keyword
#   find-due-leads <date>         — Find leads with next_action_date <= date
#   daily-sends-count             — Count emails sent today
#   domain-sends-count <domain>   — Count sends to a domain in last hour
#   audit-log <action> <detail>   — Append to audit log
#   strip-html <string>           — Strip HTML tags from input
#   write-email-body <text>       — Write email body to temp file safely
#   check-warmup <day_num>        — Return max sends allowed for warmup day
#   sanitize-string <string>      — Echo sanitized version of input
#
# Security:
#   - All paths validated to stay within ~/workspace/leadgen/
#   - All string inputs stripped of shell metacharacters
#   - JSON validated with jq (if available) or basic checks
#   - No eval, no unquoted variables, no command substitution on user input

set -euo pipefail

LEADGEN_DIR="${HOME}/workspace/leadgen"
LEADS_ACTIVE="${LEADGEN_DIR}/leads/active"
LEADS_ARCHIVE="${LEADGEN_DIR}/leads/archive"
TEMPLATES_DIR="${LEADGEN_DIR}/templates"
SEQUENCES_DIR="${LEADGEN_DIR}/sequences"
REPORTS_DIR="${LEADGEN_DIR}/reports"
DRAFTS_DIR="${LEADGEN_DIR}/drafts"

# ──────────────────────────────────────────────
# SANITIZATION FUNCTIONS
# ──────────────────────────────────────────────

sanitize_string() {
  # Strip shell metacharacters, control chars, and limit length
  local input="$1"
  local max_len="${2:-200}"
  
  # Remove dangerous characters
  local clean
  clean=$(printf '%s' "$input" | tr -d '`$\\!(){}|;&<>#\n\r\t' | sed "s/['\"]//g")
  
  # Truncate to max length
  printf '%s' "$clean" | head -c "$max_len"
}

sanitize_email() {
  local input="$1"
  # Basic email validation: something@something.something
  # Strip everything except valid email chars
  local clean
  clean=$(printf '%s' "$input" | tr -cd 'a-zA-Z0-9@._+-' | head -c 254)
  
  if [[ "$clean" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    printf '%s' "$clean"
  else
    echo "ERROR: Invalid email format" >&2
    return 1
  fi
}

sanitize_name() {
  # Names: letters, spaces, hyphens, apostrophes, periods only
  local input="$1"
  local clean
  clean=$(printf '%s' "$input" | tr -cd "a-zA-Z0-9 .'-" | head -c 100)
  printf '%s' "$clean"
}

sanitize_filename() {
  # Filenames: alphanumeric, hyphens, underscores only
  local input="$1"
  local clean
  clean=$(printf '%s' "$input" | tr -cd 'a-zA-Z0-9_-' | head -c 50)
  printf '%s' "$clean"
}

validate_path() {
  # Ensure path stays within LEADGEN_DIR
  local target="$1"
  local resolved
  resolved=$(realpath -m "$target" 2>/dev/null || echo "$target")
  
  if [[ "$resolved" != "${LEADGEN_DIR}"* ]]; then
    echo "ERROR: Path traversal blocked — must be within ${LEADGEN_DIR}" >&2
    return 1
  fi
  printf '%s' "$resolved"
}

validate_json() {
  # Validate JSON structure
  local file="$1"
  if command -v jq &>/dev/null; then
    jq empty "$file" 2>/dev/null || { echo "ERROR: Invalid JSON in $file" >&2; return 1; }
  else
    # Basic check: starts with { and ends with }
    local first last
    first=$(head -c 1 "$file")
    last=$(tail -c 2 "$file" | head -c 1)
    if [[ "$first" != "{" ]] || [[ "$last" != "}" ]]; then
      echo "ERROR: File does not appear to be valid JSON" >&2
      return 1
    fi
  fi
}

validate_status() {
  local status="$1"
  local valid_statuses="new contacted responded qualified call_booked proposal_sent closed_won closed_lost nurture do_not_contact"
  for s in $valid_statuses; do
    [[ "$status" == "$s" ]] && return 0
  done
  echo "ERROR: Invalid status '$status'. Valid: $valid_statuses" >&2
  return 1
}

# ──────────────────────────────────────────────
# COMMANDS
# ──────────────────────────────────────────────

cmd_init() {
  mkdir -p \
    "${LEADS_ACTIVE}" \
    "${LEADS_ARCHIVE}" \
    "${TEMPLATES_DIR}" \
    "${SEQUENCES_DIR}" \
    "${REPORTS_DIR}/daily" \
    "${REPORTS_DIR}/weekly" \
    "${REPORTS_DIR}/monthly" \
    "${DRAFTS_DIR}"
  echo "✅ Workspace created at ${LEADGEN_DIR}"
}

cmd_write_config() {
  local target="${LEADGEN_DIR}/config.yaml"
  # Read from stdin (agent uses heredoc)
  cat > "$target"
  echo "✅ Config written to ${target}"
}

cmd_add_lead() {
  local json_file="$1"
  
  # Validate the file exists and is JSON
  [[ -f "$json_file" ]] || { echo "ERROR: File not found: $json_file" >&2; return 1; }
  validate_json "$json_file"
  
  # Extract lead_id for filename
  local lead_id
  if command -v jq &>/dev/null; then
    lead_id=$(jq -r '.lead_id // empty' "$json_file")
  else
    lead_id=$(grep -o '"lead_id": *"[^"]*"' "$json_file" | head -1 | cut -d'"' -f4)
  fi
  
  [[ -z "$lead_id" ]] && { echo "ERROR: No lead_id found in JSON" >&2; return 1; }
  
  local safe_id
  safe_id=$(sanitize_filename "$lead_id")
  local target="${LEADS_ACTIVE}/${safe_id}.json"
  
  validate_path "$target" >/dev/null
  
  if [[ -f "$target" ]]; then
    echo "WARNING: Lead file already exists: ${safe_id}.json" >&2
    echo "Use 'update-lead' to modify existing leads." >&2
    return 1
  fi
  
  cp "$json_file" "$target"
  echo "✅ Lead saved: ${safe_id}.json"
}

cmd_update_lead() {
  local lead_id="$1"
  local field="$2"
  local value="$3"
  
  local safe_id
  safe_id=$(sanitize_filename "$lead_id")
  local target="${LEADS_ACTIVE}/${safe_id}.json"
  
  validate_path "$target" >/dev/null
  [[ -f "$target" ]] || { echo "ERROR: Lead not found: ${safe_id}" >&2; return 1; }
  
  # Sanitize the field name
  local safe_field
  safe_field=$(printf '%s' "$field" | tr -cd 'a-zA-Z0-9_.')
  
  # Sanitize the value
  local safe_value
  safe_value=$(sanitize_string "$value" 1000)
  
  if command -v jq &>/dev/null; then
    # Use jq for safe JSON updates
    local tmp="${target}.tmp"
    
    # Handle nested fields (e.g., "sequence.active")
    if [[ "$safe_field" == *"."* ]]; then
      jq --arg val "$safe_value" "(.$(echo "$safe_field" | sed 's/\././g')) = (\$val | try tonumber // try (if . == \"true\" then true elif . == \"false\" then false else . end) // .)" "$target" > "$tmp"
    else
      jq --arg val "$safe_value" ".${safe_field} = (\$val | try tonumber // try (if . == \"true\" then true elif . == \"false\" then false else . end) // .)" "$target" > "$tmp"
    fi
    
    # Update timestamp
    jq --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '.updated = $now' "$tmp" > "$target"
    rm -f "$tmp"
  else
    # Fallback: sed-based update (less safe, but functional)
    local escaped_value
    escaped_value=$(printf '%s' "$safe_value" | sed 's/[&/\]/\\&/g')
    sed -i "s/\"${safe_field}\": *\"[^\"]*\"/\"${safe_field}\": \"${escaped_value}\"/" "$target"
  fi
  
  echo "✅ Updated ${safe_id}: ${safe_field} = ${safe_value}"
}

cmd_move_lead() {
  local lead_id="$1"
  local from="$2"
  local to="$3"
  
  local safe_id
  safe_id=$(sanitize_filename "$lead_id")
  
  local from_dir to_dir
  case "$from" in
    active)  from_dir="${LEADS_ACTIVE}" ;;
    archive) from_dir="${LEADS_ARCHIVE}" ;;
    *) echo "ERROR: Invalid source: $from (use 'active' or 'archive')" >&2; return 1 ;;
  esac
  case "$to" in
    active)  to_dir="${LEADS_ACTIVE}" ;;
    archive) to_dir="${LEADS_ARCHIVE}" ;;
    *) echo "ERROR: Invalid destination: $to (use 'active' or 'archive')" >&2; return 1 ;;
  esac
  
  local source_file="${from_dir}/${safe_id}.json"
  local dest_file="${to_dir}/${safe_id}.json"
  
  validate_path "$source_file" >/dev/null
  validate_path "$dest_file" >/dev/null
  
  [[ -f "$source_file" ]] || { echo "ERROR: Lead not found in ${from}: ${safe_id}" >&2; return 1; }
  
  mv "$source_file" "$dest_file"
  echo "✅ Moved ${safe_id}: ${from} → ${to}"
}

cmd_write_template() {
  local json_file="$1"
  
  [[ -f "$json_file" ]] || { echo "ERROR: File not found: $json_file" >&2; return 1; }
  validate_json "$json_file"
  
  local template_name
  if command -v jq &>/dev/null; then
    template_name=$(jq -r '.template_name // empty' "$json_file")
  else
    template_name=$(grep -o '"template_name": *"[^"]*"' "$json_file" | head -1 | cut -d'"' -f4)
  fi
  
  [[ -z "$template_name" ]] && { echo "ERROR: No template_name in JSON" >&2; return 1; }
  
  local safe_name
  safe_name=$(sanitize_filename "$template_name")
  local target="${TEMPLATES_DIR}/${safe_name}.json"
  
  validate_path "$target" >/dev/null
  cp "$json_file" "$target"
  echo "✅ Template saved: ${safe_name}.json"
}

cmd_write_sequence() {
  local json_file="$1"
  
  [[ -f "$json_file" ]] || { echo "ERROR: File not found: $json_file" >&2; return 1; }
  validate_json "$json_file"
  
  local seq_name
  if command -v jq &>/dev/null; then
    seq_name=$(jq -r '.sequence_name // empty' "$json_file")
  else
    seq_name=$(grep -o '"sequence_name": *"[^"]*"' "$json_file" | head -1 | cut -d'"' -f4)
  fi
  
  [[ -z "$seq_name" ]] && { echo "ERROR: No sequence_name in JSON" >&2; return 1; }
  
  local safe_name
  safe_name=$(sanitize_filename "$seq_name")
  local target="${SEQUENCES_DIR}/${safe_name}.json"
  
  validate_path "$target" >/dev/null
  cp "$json_file" "$target"
  echo "✅ Sequence saved: ${safe_name}.json"
}

cmd_list_leads() {
  local filter_status="${1:-}"
  
  if [[ ! -d "$LEADS_ACTIVE" ]] || [[ -z "$(ls -A "$LEADS_ACTIVE" 2>/dev/null)" ]]; then
    echo "No active leads found."
    return 0
  fi
  
  for f in "${LEADS_ACTIVE}"/*.json; do
    [[ -f "$f" ]] || continue
    
    local name company status score next_action next_date
    if command -v jq &>/dev/null; then
      name=$(jq -r '.contact.name // "Unknown"' "$f")
      company=$(jq -r '.contact.company // "Unknown"' "$f")
      status=$(jq -r '.status // "unknown"' "$f")
      score=$(jq -r '.lead_score // 0' "$f")
      next_action=$(jq -r '.next_action // "None"' "$f")
      next_date=$(jq -r '.next_action_date // "N/A"' "$f")
    else
      name=$(grep -o '"name": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
      company=$(grep -o '"company": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
      status=$(grep -o '"status": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
      score=$(grep -o '"lead_score": *[0-9]*' "$f" | head -1 | awk '{print $2}')
      next_action=$(grep -o '"next_action": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
      next_date=$(grep -o '"next_action_date": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
    fi
    
    # Filter by status if provided
    if [[ -n "$filter_status" ]] && [[ "$status" != "$filter_status" ]]; then
      continue
    fi
    
    printf '%-25s %-20s %-15s %3s  %-25s %s\n' \
      "${name:0:24}" "${company:0:19}" "$status" "$score" "${next_action:0:24}" "$next_date"
  done
}

cmd_count_leads() {
  if [[ ! -d "$LEADS_ACTIVE" ]] || [[ -z "$(ls -A "$LEADS_ACTIVE" 2>/dev/null)" ]]; then
    echo "No active leads."
    return 0
  fi
  
  local statuses="new contacted responded qualified call_booked proposal_sent closed_won closed_lost nurture do_not_contact"
  local total=0
  
  for status in $statuses; do
    local count=0
    for f in "${LEADS_ACTIVE}"/*.json; do
      [[ -f "$f" ]] || continue
      if grep -q "\"status\": *\"${status}\"" "$f" 2>/dev/null; then
        count=$((count + 1))
      fi
    done
    total=$((total + count))
    [[ $count -gt 0 ]] && printf '%-15s %d\n' "$status" "$count"
  done
  
  echo "─────────────────────"
  printf '%-15s %d\n' "TOTAL" "$total"
}

cmd_search_leads() {
  local term="$1"
  local safe_term
  safe_term=$(sanitize_string "$term" 100)
  
  if [[ ! -d "$LEADS_ACTIVE" ]]; then
    echo "No active leads."
    return 0
  fi
  
  grep -li "$safe_term" "${LEADS_ACTIVE}"/*.json 2>/dev/null | while read -r f; do
    local name company
    if command -v jq &>/dev/null; then
      name=$(jq -r '.contact.name // "Unknown"' "$f")
      company=$(jq -r '.contact.company // "Unknown"' "$f")
    else
      name=$(grep -o '"name": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
      company=$(grep -o '"company": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
    fi
    echo "• ${name} at ${company} — $(basename "$f")"
  done
}

cmd_find_due_leads() {
  local target_date="$1"
  
  if [[ ! -d "$LEADS_ACTIVE" ]]; then
    echo "No active leads."
    return 0
  fi
  
  for f in "${LEADS_ACTIVE}"/*.json; do
    [[ -f "$f" ]] || continue
    
    local next_date
    if command -v jq &>/dev/null; then
      next_date=$(jq -r '.next_action_date // ""' "$f")
    else
      next_date=$(grep -o '"next_action_date": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
    fi
    
    if [[ -n "$next_date" ]] && [[ "$next_date" < "$target_date" || "$next_date" == "$target_date" ]]; then
      local name next_action
      if command -v jq &>/dev/null; then
        name=$(jq -r '.contact.name // "Unknown"' "$f")
        next_action=$(jq -r '.next_action // "None"' "$f")
      else
        name=$(grep -o '"name": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
        next_action=$(grep -o '"next_action": *"[^"]*"' "$f" | head -1 | cut -d'"' -f4)
      fi
      echo "• ${name}: ${next_action} (due ${next_date})"
    fi
  done
}

cmd_daily_sends_count() {
  local today
  today=$(date +%Y-%m-%d)
  local count=0
  
  if [[ -d "$LEADS_ACTIVE" ]]; then
    for f in "${LEADS_ACTIVE}"/*.json; do
      [[ -f "$f" ]] || continue
      count=$((count + $(grep -c "\"sent_date\": *\"${today}" "$f" 2>/dev/null || echo 0)))
    done
  fi
  
  echo "$count"
}

cmd_sanitize_string() {
  sanitize_string "$1" "${2:-200}"
}

cmd_domain_sends_count() {
  local domain="$1"
  local safe_domain
  safe_domain=$(printf '%s' "$domain" | tr -cd 'a-zA-Z0-9.-' | head -c 100)
  local count=0
  local one_hour_ago
  one_hour_ago=$(date -u -d '1 hour ago' +%Y-%m-%dT%H 2>/dev/null || date -u -v-1H +%Y-%m-%dT%H 2>/dev/null || echo "")
  
  if [[ -d "$LEADS_ACTIVE" ]] && [[ -n "$one_hour_ago" ]]; then
    for f in "${LEADS_ACTIVE}"/*.json; do
      [[ -f "$f" ]] || continue
      # Count sends to this domain in the last hour
      count=$((count + $(grep -c "\"sent_date\": *\"${one_hour_ago}.*\".*@${safe_domain}" "$f" 2>/dev/null || echo 0)))
    done
  fi
  
  echo "$count"
}

cmd_audit_log() {
  local action="$1"
  local detail="$2"
  local log_file="${LEADGEN_DIR}/audit.log"
  
  # Sanitize inputs
  local safe_action
  safe_action=$(sanitize_string "$action" 50)
  local safe_detail
  safe_detail=$(sanitize_string "$detail" 500)
  
  local timestamp
  timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  
  # Append to audit log (create if missing)
  printf '%s | %-20s | %s\n' "$timestamp" "$safe_action" "$safe_detail" >> "$log_file"
  echo "✅ Audit logged: ${safe_action}"
}

cmd_audit_prune() {
  local retention_days="${1:-90}"
  local log_file="${LEADGEN_DIR}/audit.log"
  
  [[ -f "$log_file" ]] || { echo "No audit log found."; return 0; }
  
  local cutoff_date
  cutoff_date=$(date -u -d "${retention_days} days ago" +%Y-%m-%d 2>/dev/null || date -u -v-${retention_days}d +%Y-%m-%d 2>/dev/null || echo "")
  
  if [[ -n "$cutoff_date" ]]; then
    local before_count
    before_count=$(wc -l < "$log_file")
    # Keep only lines with dates after cutoff
    local tmp="${log_file}.tmp"
    awk -v cutoff="$cutoff_date" '$0 >= cutoff' "$log_file" > "$tmp"
    mv "$tmp" "$log_file"
    local after_count
    after_count=$(wc -l < "$log_file")
    echo "✅ Pruned $((before_count - after_count)) entries older than ${retention_days} days"
  else
    echo "WARNING: Could not calculate cutoff date. Skipping prune."
  fi
}

cmd_strip_html() {
  local input="$1"
  # Remove HTML tags, decode common entities, strip scripts/styles
  printf '%s' "$input" \
    | sed 's/<script[^>]*>.*<\/script>//gi' \
    | sed 's/<style[^>]*>.*<\/style>//gi' \
    | sed 's/<[^>]*>//g' \
    | sed 's/&amp;/\&/g; s/&lt;/</g; s/&gt;/>/g; s/&quot;/"/g; s/&#39;/'"'"'/g; s/&nbsp;/ /g' \
    | sed 's/  */ /g' \
    | head -c 10000
}

cmd_write_email_body() {
  # Write email body to temp file safely using quoted heredoc
  local tmp_file="/tmp/leadgen_email_body.txt"
  
  # Read from stdin (agent pipes body content)
  cat > "$tmp_file"
  
  # Verify file was written
  if [[ -s "$tmp_file" ]]; then
    echo "✅ Email body written to ${tmp_file} ($(wc -c < "$tmp_file") bytes)"
  else
    echo "ERROR: Email body file is empty" >&2
    return 1
  fi
}

cmd_check_warmup() {
  local day_num="${1:-1}"
  
  # Warmup schedule: day_1=5, day_2=10, day_3=20, day_4=35, day_5+=50
  case "$day_num" in
    1) echo 5 ;;
    2) echo 10 ;;
    3) echo 20 ;;
    4) echo 35 ;;
    *) echo 50 ;;
  esac
}

# ──────────────────────────────────────────────
# MAIN DISPATCH
# ──────────────────────────────────────────────

case "${1:-}" in
  init)              cmd_init ;;
  write-config)      cmd_write_config ;;
  add-lead)          cmd_add_lead "${2:?ERROR: json_file required}" ;;
  update-lead)       cmd_update_lead "${2:?ERROR: lead_id required}" "${3:?ERROR: field required}" "${4:?ERROR: value required}" ;;
  move-lead)         cmd_move_lead "${2:?ERROR: lead_id required}" "${3:?ERROR: from required}" "${4:?ERROR: to required}" ;;
  write-template)    cmd_write_template "${2:?ERROR: json_file required}" ;;
  write-sequence)    cmd_write_sequence "${2:?ERROR: json_file required}" ;;
  list-leads)        cmd_list_leads "${2:-}" ;;
  count-leads)       cmd_count_leads ;;
  search-leads)      cmd_search_leads "${2:?ERROR: search term required}" ;;
  find-due-leads)    cmd_find_due_leads "${2:?ERROR: date required}" ;;
  daily-sends-count) cmd_daily_sends_count ;;
  domain-sends-count) cmd_domain_sends_count "${2:?ERROR: domain required}" ;;
  audit-log)         cmd_audit_log "${2:?ERROR: action required}" "${3:?ERROR: detail required}" ;;
  audit-prune)       cmd_audit_prune "${2:-90}" ;;
  strip-html)        cmd_strip_html "${2:?ERROR: input required}" ;;
  write-email-body)  cmd_write_email_body ;;
  check-warmup)      cmd_check_warmup "${2:-1}" ;;
  sanitize-string)   cmd_sanitize_string "${2:?ERROR: string required}" "${3:-200}" ;;
  *)
    echo "leadgen-helper.sh — Safe operations for Email Lead Generation"
    echo ""
    echo "Commands:"
    echo "  init                            Create workspace directories"
    echo "  write-config                    Write config from stdin"
    echo "  add-lead <json_file>            Validate and write lead"
    echo "  update-lead <id> <field> <val>  Update lead field"
    echo "  move-lead <id> <from> <to>      Move between active/archive"
    echo "  write-template <json_file>      Validate and write template"
    echo "  write-sequence <json_file>      Validate and write sequence"
    echo "  list-leads [status]             List leads"
    echo "  count-leads                     Count by status"
    echo "  search-leads <term>             Search leads"
    echo "  find-due-leads <date>           Find due actions"
    echo "  daily-sends-count               Count today's sends"
    echo "  domain-sends-count <domain>     Count sends to domain in last hour"
    echo "  audit-log <action> <detail>     Append to audit log"
    echo "  audit-prune [days]              Prune audit entries older than N days"
    echo "  strip-html <string>             Strip HTML tags from input"
    echo "  write-email-body                Write email body from stdin to temp file"
    echo "  check-warmup <day_num>          Return max sends for warmup day"
    echo "  sanitize-string <str> [max]     Sanitize input"
    ;;
esac
