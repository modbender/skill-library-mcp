#!/bin/bash
set -euo pipefail
# Agent Passport - Local Mandate Ledger (Expanded)
# Consent-gating for ALL sensitive actions, not just purchases
# v2.3.2: add set -euo pipefail shell hardening (required by CODEX.md + CONTRIBUTING.md)

LEDGER_DIR="${AGENT_PASSPORT_LEDGER_DIR:-$HOME/.openclaw/agent-passport}"
LEDGER_FILE="$LEDGER_DIR/mandates.json"
KYA_FILE="$LEDGER_DIR/agents.json"
AUDIT_FILE="$LEDGER_DIR/audit.json"
KILLSWITCH_FILE="$LEDGER_DIR/.killswitch"
DEFINITIONS_FILE="$LEDGER_DIR/threat-definitions.json"
DEFINITIONS_BACKUP_FILE="$LEDGER_DIR/threat-definitions.bak"
DEFINITIONS_META_FILE="$LEDGER_DIR/.threat-meta.json"

BUNDLED_DEFINITIONS_VERSION="2.3.2-bundled"
BUNDLED_DEFINITIONS_SOURCE="bundled"

FALLBACK_SSRF_BLOCKED_HOSTS=("metadata.google.internal" "metadata.google" "computemetadata.google" "169.254.169.254" "metadata.azure.com" "metadata.azure.internal")
FALLBACK_SSRF_BLOCKED_SCHEMES=("file" "gopher" "ftp" "dict" "ldap" "tftp")
FALLBACK_PATH_TRAVERSAL_SEQUENCES=("../" "/.." "%2e%2e" "%252e%252e" "%2f" "%5c" "%252f")

# Action categories
# - financial: purchases, transfers, subscriptions
# - communication: emails, messages, posts
# - data: file deletion, document edits, database writes
# - system: shell commands, package installs, config changes
# - external_api: third-party API calls with side effects
# - identity: public actions "as" the user

init_ledger() {
    mkdir -p "$LEDGER_DIR"
    if [ ! -f "$LEDGER_FILE" ]; then
        echo '{"mandates":[],"version":"2.3.2"}' > "$LEDGER_FILE"
    fi
    if [ ! -f "$KYA_FILE" ]; then
        echo '{"agents":[],"version":"1.0"}' > "$KYA_FILE"
    fi
    if [ ! -f "$AUDIT_FILE" ]; then
        echo '{"entries":[],"version":"1.0"}' > "$AUDIT_FILE"
    fi
}

bundled_definitions_json() {
    cat <<'JSON'
{
  "version": "__VERSION__",
  "updated_at": "__UPDATED_AT__",
  "schema_version": 1,
  "sources": [
    "agent-passport-core"
  ],
  "scan_patterns": [
    { "id": "scan-crit-remote-exec-curl", "severity": "critical", "type": "remote_exec", "description": "Remote script execution", "regex": "curl[^|]*\\|[[:space:]]*(bash|sh)", "grep_mode": "E", "risk": "Downloads and executes arbitrary remote code without user knowledge", "file_filter": null },
    { "id": "scan-crit-remote-exec-wget", "severity": "critical", "type": "remote_exec", "description": "Remote script execution", "regex": "wget[^|]*\\|[[:space:]]*(bash|sh)", "grep_mode": "E", "risk": "Downloads and executes arbitrary remote code without user knowledge", "file_filter": null },
    { "id": "scan-crit-obfuscated-base64-pipe", "severity": "critical", "type": "obfuscated_exec", "description": "Base64 decode piped to shell", "regex": "base64[^|]*\\|[[:space:]]*(bash|sh)", "grep_mode": "E", "risk": "Obfuscated payload decoded and executed in shell", "file_filter": null },
    { "id": "scan-crit-obfuscated-eval-base64", "severity": "critical", "type": "obfuscated_exec", "description": "Eval of base64-decoded content", "regex": "eval.*base64", "grep_mode": "E", "risk": "Runtime execution of obfuscated payload", "file_filter": null },
    { "id": "scan-crit-dangerous-eval-cmd-sub", "severity": "critical", "type": "dangerous_eval", "description": "Eval of command substitution", "regex": "eval.*\\$\\(", "grep_mode": "P", "risk": "Evaluates command substitution output directly", "file_filter": null },
    { "id": "scan-crit-daemon-install", "severity": "critical", "type": "daemon_install", "description": "Suspicious remote daemon install pattern", "regex": "(openclaw-core|clawd-core).*(install|daemon|service)", "grep_mode": "E", "risk": "Likely persistence/backdoor style system daemon install", "file_filter": null },

    { "id": "scan-high-secret-aws", "severity": "high", "type": "hardcoded_secret", "description": "Hardcoded AWS key detected", "regex": "AKIA[0-9A-Z]{16}", "grep_mode": "E", "risk": "Credential embedded in skill file may be harvested or misused", "file_filter": null },
    { "id": "scan-high-secret-github", "severity": "high", "type": "hardcoded_secret", "description": "Hardcoded GitHub token detected", "regex": "ghp_[A-Za-z0-9]{36}", "grep_mode": "E", "risk": "Credential embedded in skill file may be harvested or misused", "file_filter": null },
    { "id": "scan-high-secret-openai", "severity": "high", "type": "hardcoded_secret", "description": "Hardcoded OpenAI key detected", "regex": "sk-[A-Za-z0-9]{48}", "grep_mode": "E", "risk": "Credential embedded in skill file may be harvested or misused", "file_filter": null },
    { "id": "scan-high-secret-entropy", "severity": "high", "type": "hardcoded_secret", "description": "Possible high-entropy secret assignment", "regex": "[A-Za-z_][A-Za-z0-9_]{2,}[[:space:]]*[:=][[:space:]]*['\\\"]?[A-Za-z0-9+/_=-]{32,}['\\\"]?", "grep_mode": "E", "risk": "Potential secret/token hardcoded in assignment", "file_filter": null },
    { "id": "scan-high-global-npm-skill-md", "severity": "high", "type": "global_install", "description": "Global npm install in SKILL.md", "regex": "npm[[:space:]]+install[[:space:]]+-g", "grep_mode": "E", "risk": "Installs system-wide package without explicit user consent", "file_filter": "SKILL.md" },
    { "id": "scan-high-pip-install-skill-md", "severity": "high", "type": "package_install", "description": "pip install in SKILL.md", "regex": "pip([0-9]+)?[[:space:]]+install", "grep_mode": "E", "risk": "Installs Python package without explicit user consent", "file_filter": "SKILL.md" },
    { "id": "scan-high-chmod-download", "severity": "high", "type": "chmod_download", "description": "Downloaded file made executable", "regex": "((curl|wget).*(chmod[[:space:]]+\\+x))|((chmod[[:space:]]+\\+x).*(curl|wget))", "grep_mode": "E", "risk": "Downloaded payload is made executable, increasing malware risk", "file_filter": null },
    { "id": "scan-high-cron-modify", "severity": "high", "type": "cron_modify", "description": "Cron table modification", "regex": "crontab[[:space:]]+-", "grep_mode": "E", "risk": "Modifies scheduled tasks for persistence", "file_filter": null },
    { "id": "scan-high-shell-persist", "severity": "high", "type": "shell_persist", "description": "Shell profile modification", "regex": "(\\~|/home/[^/]+)/\\.(bashrc|zshrc)", "grep_mode": "E", "risk": "Persistent shell profile modification may hide malicious startup commands", "file_filter": null },
    { "id": "scan-high-ssh-modify", "severity": "high", "type": "ssh_modify", "description": "SSH directory modification", "regex": "(\\~|/home/[^/]+)/\\.ssh/", "grep_mode": "E", "risk": "SSH key/config modification may enable unauthorized access", "file_filter": null },
    { "id": "scan-high-system-modify", "severity": "high", "type": "system_modify", "description": "System config path write", "regex": "/etc/", "grep_mode": "E", "risk": "System configuration modification outside normal skill scope", "file_filter": null },

    { "id": "scan-med-injection-ignore-previous", "severity": "medium", "type": "prompt_injection", "description": "Prompt injection pattern", "regex": "ignore previous instructions", "grep_mode": "E", "risk": "Attempts to override agent behavior", "file_filter": null },
    { "id": "scan-med-injection-ignore-all", "severity": "medium", "type": "prompt_injection", "description": "Prompt injection pattern", "regex": "ignore all previous", "grep_mode": "E", "risk": "Attempts to override agent behavior", "file_filter": null },
    { "id": "scan-med-override-marker", "severity": "medium", "type": "prompt_injection", "description": "Instruction override marker", "regex": "new instructions[[:space:]]*:", "grep_mode": "E", "risk": "Attempts to inject alternate instructions", "file_filter": null },
    { "id": "scan-med-system-marker-md", "severity": "medium", "type": "prompt_override", "description": "System prompt override marker", "regex": "^[[:space:]]*system:", "grep_mode": "E", "risk": "Attempts to masquerade as a system-level instruction", "file_filter": "*.md" },
    { "id": "scan-med-persona-hijack", "severity": "medium", "type": "persona_hijack", "description": "Persona hijacking pattern", "regex": "you are now", "grep_mode": "E", "risk": "Attempts to rewrite the assistant persona", "file_filter": null },
    { "id": "scan-med-role-injection", "severity": "medium", "type": "role_injection", "description": "Role injection pattern", "regex": "act as", "grep_mode": "E", "risk": "Attempts to alter role/behavior outside trusted prompt", "file_filter": null },
    { "id": "scan-med-ap-bypass", "severity": "medium", "type": "ap_bypass", "description": "Agent Passport env var manipulation", "regex": "AGENT_PASSPORT", "grep_mode": "E", "risk": "May attempt to disable or bypass Agent Passport controls", "file_filter": null },
    { "id": "scan-med-dangerous-delete", "severity": "medium", "type": "dangerous_delete", "description": "Broad deletion command", "regex": "rm[[:space:]]+-rf([[:space:]]|$)(/|~|\\$HOME|\\*)?", "grep_mode": "E", "risk": "Potentially destructive broad deletion command", "file_filter": null },
    { "id": "scan-med-priv-esc", "severity": "medium", "type": "privilege_escalation", "description": "sudo usage", "regex": "(^|[[:space:]])sudo([[:space:]]|$)", "grep_mode": "E", "risk": "Privilege escalation request detected", "file_filter": null },

    { "id": "scan-low-local-target", "severity": "low", "type": "local_target", "description": "Hardcoded IP or localhost reference", "regex": "((^|[^0-9])(127\\.0\\.0\\.1|0\\.0\\.0\\.0|10\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|192\\.168\\.[0-9]{1,3}\\.[0-9]{1,3}|172\\.(1[6-9]|2[0-9]|3[0-1])\\.[0-9]{1,3}\\.[0-9]{1,3}|localhost)([^0-9]|$))", "grep_mode": "E", "risk": "May reference internal/local network services", "file_filter": null },
    { "id": "scan-low-env-harvest", "severity": "low", "type": "env_harvest", "description": "Environment variable harvesting pattern", "regex": "(process\\.env|\\$HOME)", "grep_mode": "E", "risk": "References sensitive runtime environment data", "file_filter": null }
  ],
  "injection_patterns": [
    { "id": "inj-crit-instruction-override", "severity": "critical", "type": "instruction_override", "description": "Direct instruction override attempt", "regex": "ignore[[:space:]]+(all[[:space:]]+)?(previous|prior)[[:space:]]+instructions", "grep_mode": "E", "risk": "Attempts to override agent behavior and trusted instruction hierarchy" },
    { "id": "inj-crit-system-override", "severity": "critical", "type": "system_override", "description": "System instruction override attempt", "regex": "ignore[[:space:]]+(your[[:space:]]+)?(system[[:space:]]+)?(prompt|instructions|guidelines|rules)", "grep_mode": "E", "risk": "Attempts to disable or replace the system/developer safety policy" },
    { "id": "inj-crit-task-injection", "severity": "critical", "type": "task_injection", "description": "New task/directive injection marker", "regex": "new[[:space:]]+(task|instructions?|directive)[[:space:]]*:", "grep_mode": "E", "risk": "Attempts to inject alternate tasks into untrusted content" },
    { "id": "inj-crit-fake-system-token", "severity": "critical", "type": "fake_system", "description": "Fake system-message token", "regex": "(\\[system\\]|<system>)", "grep_mode": "E", "risk": "Pretends untrusted content has system-level authority" },
    { "id": "inj-crit-persona-override", "severity": "critical", "type": "persona_override", "description": "Persona override attempt", "regex": "you are now", "grep_mode": "E", "risk": "Attempts to rewrite assistant identity/behavior" },
    { "id": "inj-crit-identity-confusion", "severity": "critical", "type": "identity_confusion", "description": "Instruction identity confusion attack", "regex": "your[[:space:]]+(real|true|actual)[[:space:]]+instructions", "grep_mode": "E", "risk": "Attempts to confuse model about trusted instruction source" },
    { "id": "inj-crit-role-output-injection", "severity": "critical", "type": "role_output_injection", "description": "Model output impersonation marker", "regex": "^[[:space:]]*(assistant|ai|claude)[[:space:]]*:", "grep_mode": "E", "risk": "Impersonates assistant output to hijack behavior" },
    { "id": "inj-crit-token-manipulation", "severity": "critical", "type": "token_manipulation", "description": "Special token manipulation marker", "regex": "<\\|im_start\\|>|<\\|endoftext\\|>", "grep_mode": "E", "risk": "Attempts prompt boundary/token abuse" },
    { "id": "inj-crit-emergency-override", "severity": "critical", "type": "emergency_override", "description": "Emergency override phrase", "regex": "(STOP EVERYTHING|HALT ALL)", "grep_mode": "E", "risk": "Attempts to force immediate policy override" },

    { "id": "inj-high-role-injection", "severity": "high", "type": "role_injection", "description": "Role injection attempt", "regex": "act[[:space:]]+as[[:space:]]+(a|an|the)", "grep_mode": "E", "risk": "Attempts to force alternate role behavior" },
    { "id": "inj-high-persona-injection", "severity": "high", "type": "persona_injection", "description": "Persona simulation attempt", "regex": "pretend[[:space:]]+(you are|to be)", "grep_mode": "E", "risk": "Attempts to make assistant abandon real policy context" },
    { "id": "inj-high-memory-wipe", "severity": "high", "type": "memory_wipe", "description": "Memory/context wipe attempt", "regex": "forget[[:space:]]+(everything|all)[[:space:]]+(you|about)", "grep_mode": "E", "risk": "Attempts to disable prior context and safeguards" },
    { "id": "inj-high-secrecy-instruction", "severity": "high", "type": "secrecy_instruction", "description": "Secrecy instruction", "regex": "(do not|don't)[[:space:]]+tell[[:space:]]+(the user|mark|your[[:space:]]+(owner|operator))", "grep_mode": "E", "risk": "Attempts to conceal actions from the operator/user" },
    { "id": "inj-high-concealment", "severity": "high", "type": "concealment", "description": "Concealment instruction", "regex": "(keep this|this is)[[:space:]]+(secret|hidden|confidential)", "grep_mode": "E", "risk": "Attempts to hide behavior from oversight" },
    { "id": "inj-high-exfil-instruction", "severity": "high", "type": "exfil_instruction", "description": "Email/message exfiltration instruction", "regex": "(send|email|message).*(to|me)[[:space:]]+\\S+@\\S+", "grep_mode": "E", "risk": "Requests sending potentially sensitive data to external destination" },
    { "id": "inj-high-exec-instruction", "severity": "high", "type": "exec_instruction", "description": "Execute script/command instruction", "regex": "execute[[:space:]]+(the following|this)[[:space:]]+(command|script|code)", "grep_mode": "E", "risk": "Attempts to trigger execution of untrusted instructions" },
    { "id": "inj-high-inline-exec", "severity": "high", "type": "inline_exec", "description": "Inline execution attempt", "regex": "(run|exec)[[:space:]]*:[[:space:]]*(rm|curl|wget|bash|sh|python|node)", "grep_mode": "E", "risk": "Attempts direct command execution from untrusted content" },

    { "id": "inj-med-subtle-override", "severity": "medium", "type": "subtle_override", "description": "Subtle context override attempt", "regex": "(previous|prior)[[:space:]]+(instructions|context)[[:space:]]+(were|are)[[:space:]]+(wrong|incorrect|outdated)", "grep_mode": "E", "risk": "Attempts subtle invalidation of trusted context" },
    { "id": "inj-med-authority-spoof", "severity": "medium", "type": "authority_spoof", "description": "Authority spoofing pattern", "regex": "(your|the)[[:space:]]+(developer|creator|anthropic|openai)[[:space:]]+(says|told|instructed)", "grep_mode": "E", "risk": "Claims authority to alter behavior without trusted channel" },
    { "id": "inj-med-context-injection", "severity": "medium", "type": "context_injection", "description": "Context/session behavior injection", "regex": "(in|for)[[:space:]]+(this|the)[[:space:]]+(task|context|session)[[:space:]]*,?[[:space:]]*you should", "grep_mode": "E", "risk": "Injects behavior for this context without trust guarantees" }
  ],
  "ssrf_blocked_hosts": [
    "metadata.google.internal",
    "metadata.google",
    "computemetadata.google",
    "169.254.169.254",
    "metadata.azure.com",
    "metadata.azure.internal"
  ],
  "ssrf_blocked_schemes": [
    "file",
    "gopher",
    "ftp",
    "dict",
    "ldap",
    "tftp"
  ],
  "path_traversal_sequences": [
    "../",
    "/..",
    "%2e%2e",
    "%252e%252e",
    "%2f",
    "%5c",
    "%252f"
  ]
}
JSON
}

write_bundled_definitions_file() {
    local target_file="$1"
    local now_iso
    now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    bundled_definitions_json \
        | sed "s/__VERSION__/$BUNDLED_DEFINITIONS_VERSION/g; s/__UPDATED_AT__/$now_iso/g" \
        | jq '.' > "$target_file"
}

update_definitions_meta() {
    local source="$1"
    local version="$2"
    local now_iso
    now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    jq -n \
        --arg last_check "$now_iso" \
        --arg last_update "$now_iso" \
        --arg current_version "$version" \
        --arg source "$source" \
        '{
            last_check: $last_check,
            last_update: $last_update,
            current_version: $current_version,
            source: $source,
            auto_update: false,
            check_interval_hours: 6
        }' > "$DEFINITIONS_META_FILE"
}

validate_definitions_file() {
    local defs_file="$1"
    jq -e '
        .schema_version and
        (.scan_patterns | type == "array") and
        (.injection_patterns | type == "array") and
        (.ssrf_blocked_hosts | type == "array") and
        (.ssrf_blocked_schemes | type == "array") and
        (.path_traversal_sequences | type == "array")
    ' "$defs_file" > /dev/null 2>&1
}

load_definitions() {
    init_ledger
    if [ ! -f "$DEFINITIONS_FILE" ]; then
        return 1
    fi

    if ! validate_definitions_file "$DEFINITIONS_FILE"; then
        return 1
    fi

    # Auto-update in background if stale (Pro only, non-blocking)
    auto_update_if_stale &
    disown 2>/dev/null || true

    echo "$DEFINITIONS_FILE"
}

# Background auto-update: checks meta file, pulls new definitions if stale.
# Runs silently in the background. Never blocks the caller.
auto_update_if_stale() {
    # Only attempt if Pro license key is set
    [ -z "${AGENT_PASSPORT_LICENSE_KEY:-}" ] && return 0

    # Check meta file for staleness
    if [ ! -f "$DEFINITIONS_META_FILE" ]; then
        return 0
    fi

    local last_check_iso now_epoch last_check_epoch interval_hours interval_seconds
    last_check_iso=$(jq -r '.last_check // ""' "$DEFINITIONS_META_FILE" 2>/dev/null)
    [ -z "$last_check_iso" ] && return 0

    now_epoch=$(date +%s)
    last_check_epoch=$(date -d "$last_check_iso" +%s 2>/dev/null || echo 0)
    interval_hours=$(jq -r '.check_interval_hours // 6' "$DEFINITIONS_META_FILE" 2>/dev/null)
    interval_seconds=$((interval_hours * 3600))

    if [ $((now_epoch - last_check_epoch)) -lt "$interval_seconds" ]; then
        return 0  # Not stale yet
    fi

    # Stale: pull fresh definitions silently
    local tmp_file
    tmp_file=$(mktemp) || return 0

    local response
    response=$(curl -sf --max-time 10 \
        -H "Authorization: Bearer $AGENT_PASSPORT_LICENSE_KEY" \
        "https://api.agentpassportai.com/v1/threat-definitions" \
        2>/dev/null || true)

    if [ -n "$response" ] && echo "$response" | jq '.' > "$tmp_file" 2>/dev/null && validate_definitions_file "$tmp_file"; then
        local new_version
        new_version=$(jq -r '.version // "unknown"' "$tmp_file")
        cp "$DEFINITIONS_FILE" "$DEFINITIONS_BACKUP_FILE" 2>/dev/null || true
        mv "$tmp_file" "$DEFINITIONS_FILE"
        update_definitions_meta "pro-auto" "$new_version"
    else
        rm -f "$tmp_file" 2>/dev/null
        # Update last_check even on failure to avoid hammering
        local now_iso
        now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        if [ -f "$DEFINITIONS_META_FILE" ]; then
            local updated
            updated=$(jq --arg lc "$now_iso" '.last_check = $lc' "$DEFINITIONS_META_FILE" 2>/dev/null)
            [ -n "$updated" ] && echo "$updated" > "$DEFINITIONS_META_FILE"
        fi
    fi
}

current_definitions_version() {
    local defs_file
    if defs_file=$(load_definitions 2>/dev/null); then
        jq -r '.version // "unknown"' "$defs_file" 2>/dev/null || echo "unknown"
    else
        echo "hardcoded"
    fi
}

init_definitions() {
    init_ledger
    if [ -f "$DEFINITIONS_FILE" ]; then
        cp "$DEFINITIONS_FILE" "$DEFINITIONS_BACKUP_FILE" 2>/dev/null || true
    fi

    write_bundled_definitions_file "$DEFINITIONS_FILE"
    update_definitions_meta "$BUNDLED_DEFINITIONS_SOURCE" "$BUNDLED_DEFINITIONS_VERSION"

    echo "Initialized threat definitions at $DEFINITIONS_FILE"
    echo "Version: $BUNDLED_DEFINITIONS_VERSION"
}

update_definitions() {
    init_ledger

    local force=false
    local offline=false
    while [ $# -gt 0 ]; do
        case "$1" in
            --force) force=true ;;
            --offline) offline=true ;;
            *)
                echo "Unknown option: $1" >&2
                return 1
                ;;
        esac
        shift
    done
    # Currently unused but accepted for CLI compatibility.
    [ "$force" = "true" ] && true

    local tmp_file
    tmp_file=$(mktemp)
    local source="$BUNDLED_DEFINITIONS_SOURCE"
    local version="$BUNDLED_DEFINITIONS_VERSION"

    if [ "$offline" = "true" ]; then
        write_bundled_definitions_file "$tmp_file"
        source="bundled-offline"
    else
        local tier
        tier=$(check_license threats)
        if [ "$tier" = "pro" ] && [ -n "${AGENT_PASSPORT_LICENSE_KEY:-}" ]; then
            local response
            response=$(curl -sf --max-time 10 \
                -H "Authorization: Bearer $AGENT_PASSPORT_LICENSE_KEY" \
        "https://api.agentpassportai.com/v1/threat-definitions" \
                2>/dev/null || true)
            if [ -n "$response" ] && echo "$response" | jq '.' > "$tmp_file" 2>/dev/null && validate_definitions_file "$tmp_file"; then
                source="pro-live"
                version=$(jq -r '.version // "unknown"' "$tmp_file")
            else
                write_bundled_definitions_file "$tmp_file"
                source="bundled-fallback"
                version="$BUNDLED_DEFINITIONS_VERSION"
            fi
        else
            write_bundled_definitions_file "$tmp_file"
            source="$BUNDLED_DEFINITIONS_SOURCE"
            version="$BUNDLED_DEFINITIONS_VERSION"
        fi
    fi

    if [ -f "$DEFINITIONS_FILE" ]; then
        cp "$DEFINITIONS_FILE" "$DEFINITIONS_BACKUP_FILE" 2>/dev/null || true
    fi
    mv "$tmp_file" "$DEFINITIONS_FILE"

    update_definitions_meta "$source" "$version"
    echo "Updated threat definitions ($source)"
    echo "Version: $version"
}

definitions_status() {
    init_ledger

    local defs_file
    local version="hardcoded"
    local scan_count=28
    local injection_count=20
    local ssrf_hosts_count=${#FALLBACK_SSRF_BLOCKED_HOSTS[@]}
    local ssrf_schemes_count=${#FALLBACK_SSRF_BLOCKED_SCHEMES[@]}
    local path_seq_count=${#FALLBACK_PATH_TRAVERSAL_SEQUENCES[@]}
    local source="hardcoded-fallback"
    local last_update="never"

    if defs_file=$(load_definitions 2>/dev/null); then
        version=$(jq -r '.version // "unknown"' "$defs_file")
        scan_count=$(jq '.scan_patterns | length' "$defs_file")
        injection_count=$(jq '.injection_patterns | length' "$defs_file")
        ssrf_hosts_count=$(jq '.ssrf_blocked_hosts | length' "$defs_file")
        ssrf_schemes_count=$(jq '.ssrf_blocked_schemes | length' "$defs_file")
        path_seq_count=$(jq '.path_traversal_sequences | length' "$defs_file")
        source=$(jq -r '.sources[0] // "definitions-file"' "$defs_file")
        last_update=$(jq -r '.updated_at // "unknown"' "$defs_file")
    fi

    if [ -f "$DEFINITIONS_META_FILE" ]; then
        local meta_source meta_last_update
        meta_source=$(jq -r '.source // empty' "$DEFINITIONS_META_FILE" 2>/dev/null || true)
        meta_last_update=$(jq -r '.last_update // empty' "$DEFINITIONS_META_FILE" 2>/dev/null || true)
        [ -n "$meta_source" ] && source="$meta_source"
        [ -n "$meta_last_update" ] && last_update="$meta_last_update"
    fi

    echo "Threat Definitions Status"
    echo "Version: $version"
    echo "Source: $source"
    echo "Last update: $last_update"
    echo "Scan patterns: $scan_count"
    echo "Injection patterns: $injection_count"
    echo "SSRF blocked hosts: $ssrf_hosts_count"
    echo "SSRF blocked schemes: $ssrf_schemes_count"
    echo "Path traversal sequences: $path_seq_count"
}

kill_switch_engaged() {
    [ -f "$KILLSWITCH_FILE" ]
}

generate_id() {
    local prefix="${1:-mandate}"
    echo "${prefix}_$(date +%s)_$(head -c 4 /dev/urandom | xxd -p)"
}

# ─── SSRF Shield ─────────────────────────────────────────────────────────────
# Blocks requests to private IPs, localhost, cloud metadata, and unsafe schemes.
# Addresses CVE-2026-26322 (Gateway SSRF) and GHSA-56f2-hvwg-5743 (image SSRF).
check_ssrf() {
    local url="$1"
    local defs_file
    local blocked_hosts=("${FALLBACK_SSRF_BLOCKED_HOSTS[@]}")
    local blocked_schemes=("${FALLBACK_SSRF_BLOCKED_SCHEMES[@]}")

    if defs_file=$(load_definitions 2>/dev/null); then
        mapfile -t blocked_hosts < <(jq -r '.ssrf_blocked_hosts[]?' "$defs_file" 2>/dev/null || true)
        mapfile -t blocked_schemes < <(jq -r '.ssrf_blocked_schemes[]?' "$defs_file" 2>/dev/null || true)
        [ "${#blocked_hosts[@]}" -eq 0 ] && blocked_hosts=("${FALLBACK_SSRF_BLOCKED_HOSTS[@]}")
        [ "${#blocked_schemes[@]}" -eq 0 ] && blocked_schemes=("${FALLBACK_SSRF_BLOCKED_SCHEMES[@]}")
    fi

    if [ -z "$url" ]; then
        jq -n --arg target "" --arg reason "No URL provided" \
            '{ssrf_safe: false, reason: $reason, target: $target}'
        return 0
    fi

    # Reject non-http/https schemes (file://, gopher://, ftp://, dict://, etc.)
    local scheme
    scheme=$(echo "$url" | grep -oP '^[a-zA-Z][a-zA-Z0-9+\-.]*(?=://)' | tr '[:upper:]' '[:lower:]')
    if [ -z "$scheme" ]; then
        jq -n --arg target "$url" --arg reason "Invalid URL: no scheme detected" \
            '{ssrf_safe: false, reason: $reason, target: $target}'
        return 0
    fi
    case "$scheme" in
        http|https) ;;
        *)
            local blocked_scheme=false
            local blocked
            for blocked in "${blocked_schemes[@]}"; do
                if [ "$scheme" = "$blocked" ]; then
                    blocked_scheme=true
                    break
                fi
            done
            if [ "$blocked_scheme" = true ]; then
                jq -n --arg target "$url" --arg reason "Blocked scheme '${scheme}://': disallowed by SSRF policy" \
                    '{ssrf_safe: false, reason: $reason, target: $target}'
            else
                jq -n --arg target "$url" --arg reason "Blocked scheme '${scheme}://': only http/https allowed" \
                    '{ssrf_safe: false, reason: $reason, target: $target}'
            fi
            return 0
            ;;
    esac

    # Reject embedded credentials (user:pass@host)
    if echo "$url" | grep -qP '^https?://[^@/]+:[^@/]+@'; then
        jq -n --arg target "$url" --arg reason "Embedded credentials in URL are not allowed" \
            '{ssrf_safe: false, reason: $reason, target: $target}'
        return 0
    fi

    # Extract hostname
    local hostname
    hostname=$(echo "$url" | grep -oP '(?<=://)[^/:@?#]+' | head -1 | tr '[:upper:]' '[:lower:]')
    if [ -z "$hostname" ]; then
        jq -n --arg target "$url" --arg reason "Could not extract hostname from URL" \
            '{ssrf_safe: false, reason: $reason, target: $target}'
        return 0
    fi

    # Block localhost variants
    case "$hostname" in
        localhost|localhost.localdomain|ip6-localhost|ip6-loopback)
            jq -n --arg target "$url" --arg reason "Localhost hostname blocked" \
                '{ssrf_safe: false, reason: $reason, target: $target}'
            return 0
            ;;
    esac

    # Block cloud metadata endpoints
    local blocked_host
    for blocked_host in "${blocked_hosts[@]}"; do
        if [ "$hostname" = "$blocked_host" ]; then
            jq -n --arg target "$url" --arg reason "Cloud metadata endpoint blocked: $hostname" \
                '{ssrf_safe: false, reason: $reason, target: $target}'
            return 0
        fi
    done

    # Block IPv6 loopback
    local stripped_host="${hostname#[}"
    stripped_host="${stripped_host%]}"
    if [ "$stripped_host" = "::1" ] || [ "$stripped_host" = "0:0:0:0:0:0:0:1" ]; then
        jq -n --arg target "$url" --arg reason "IPv6 loopback blocked" \
            '{ssrf_safe: false, reason: $reason, target: $target}'
        return 0
    fi

    # Check if hostname is an IPv4 address and validate ranges
    if echo "$hostname" | grep -qP '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'; then
        local ip="$hostname"
        local o1 o2
        o1=$(echo "$ip" | cut -d. -f1)
        o2=$(echo "$ip" | cut -d. -f2)

        # 0.0.0.0 — unspecified
        if [ "$ip" = "0.0.0.0" ]; then
            jq -n --arg target "$url" --arg reason "Unspecified address 0.0.0.0 blocked" \
                '{ssrf_safe: false, reason: $reason, target: $target}'
            return 0
        fi
        # 127.x.x.x — loopback
        if [ "$o1" -eq 127 ]; then
            jq -n --arg target "$url" --arg reason "Loopback IP blocked: $ip" \
                '{ssrf_safe: false, reason: $reason, target: $target}'
            return 0
        fi
        # 10.x.x.x — private class A
        if [ "$o1" -eq 10 ]; then
            jq -n --arg target "$url" --arg reason "Private network IP blocked: $ip" \
                '{ssrf_safe: false, reason: $reason, target: $target}'
            return 0
        fi
        # 172.16.0.0/12 — private class B
        if [ "$o1" -eq 172 ] && [ "$o2" -ge 16 ] && [ "$o2" -le 31 ]; then
            jq -n --arg target "$url" --arg reason "Private network IP blocked: $ip" \
                '{ssrf_safe: false, reason: $reason, target: $target}'
            return 0
        fi
        # 192.168.x.x — private class C
        if [ "$o1" -eq 192 ] && [ "$o2" -eq 168 ]; then
            jq -n --arg target "$url" --arg reason "Private network IP blocked: $ip" \
                '{ssrf_safe: false, reason: $reason, target: $target}'
            return 0
        fi
        # 169.254.x.x — link-local / AWS IMDS
        if [ "$o1" -eq 169 ] && [ "$o2" -eq 254 ]; then
            jq -n --arg target "$url" --arg reason "Link-local/IMDS IP blocked: $ip" \
                '{ssrf_safe: false, reason: $reason, target: $target}'
            return 0
        fi
    fi

    jq -n --arg target "$url" --arg reason "URL passed all SSRF checks" \
        '{ssrf_safe: true, reason: $reason, target: $target}'
}

# ─── Path Traversal Guard ─────────────────────────────────────────────────────
# Canonicalizes file paths and validates against a safe root.
# Addresses CVE-2026-26329 (path traversal in browser upload).
check_path() {
    local path="$1"
    local safe_root="${2:-}"
    local defs_file
    local traversal_sequences=("${FALLBACK_PATH_TRAVERSAL_SEQUENCES[@]}")

    if defs_file=$(load_definitions 2>/dev/null); then
        mapfile -t traversal_sequences < <(jq -r '.path_traversal_sequences[]?' "$defs_file" 2>/dev/null || true)
        [ "${#traversal_sequences[@]}" -eq 0 ] && traversal_sequences=("${FALLBACK_PATH_TRAVERSAL_SEQUENCES[@]}")
    fi

    if [ -z "$path" ]; then
        jq -n --arg canonical_path "" --arg reason "No path provided" \
            '{path_safe: false, canonical_path: $canonical_path, reason: $reason}'
        return 0
    fi

    # Block null bytes
    if printf '%s' "$path" | grep -qP '\x00'; then
        jq -n --arg canonical_path "" --arg reason "Null byte in path" \
            '{path_safe: false, canonical_path: $canonical_path, reason: $reason}'
        return 0
    fi

    # Decode common URL encodings and check for traversal sequences
    local decoded="$path"
    decoded=$(echo "$decoded" | sed 's/%252e%252e/\.\./gi; s/%2e%2e/\.\./gi; s/%2f/\//gi; s/%5c/\//gi; s/%252f/\//gi' 2>/dev/null || echo "$decoded")

    local lower_raw lower_decoded sequence sequence_lc
    lower_raw=$(printf '%s' "$path" | tr '[:upper:]' '[:lower:]')
    lower_decoded=$(printf '%s' "$decoded" | tr '[:upper:]' '[:lower:]')

    for sequence in "${traversal_sequences[@]}"; do
        sequence_lc=$(printf '%s' "$sequence" | tr '[:upper:]' '[:lower:]')
        if [[ "$lower_raw" == *"$sequence_lc"* ]] || [[ "$lower_decoded" == *"$sequence_lc"* ]]; then
            jq -n --arg canonical_path "" --arg reason "Path traversal sequence detected" \
                '{path_safe: false, canonical_path: $canonical_path, reason: $reason}'
            return 0
        fi
    done

    if echo "$decoded" | grep -qP '(^|/)\.\.($|/)'; then
        jq -n --arg canonical_path "" --arg reason "Path traversal sequence detected" \
            '{path_safe: false, canonical_path: $canonical_path, reason: $reason}'
        return 0
    fi

    # Canonicalize
    local canonical
    if command -v realpath &>/dev/null; then
        canonical=$(realpath -m -- "$path" 2>/dev/null)
    else
        # Manual: resolve consecutive slashes and dot segments
        canonical="$path"
        while echo "$canonical" | grep -qP '(/\.?/|/[^/]+/\.\.)'; do
            canonical=$(echo "$canonical" | sed 's|/\./|/|g; s|/[^/]*/\.\.|/|g; s|//|/|g')
        done
        canonical="${canonical%/}"
        [ -z "$canonical" ] && canonical="/"
    fi

    if [ -z "$canonical" ]; then
        jq -n --arg canonical_path "" --arg reason "Path canonicalization failed" \
            '{path_safe: false, canonical_path: $canonical_path, reason: $reason}'
        return 0
    fi

    # If no safe_root, just validate no traversal occurred
    if [ -z "$safe_root" ]; then
        jq -n --arg canonical_path "$canonical" --arg reason "Path is clean (no safe_root constraint)" \
            '{path_safe: true, canonical_path: $canonical_path, reason: $reason}'
        return 0
    fi

    # Canonicalize safe_root
    local canonical_root
    if command -v realpath &>/dev/null; then
        canonical_root=$(realpath -m -- "$safe_root" 2>/dev/null)
    else
        canonical_root="${safe_root%/}"
    fi

    # Ensure canonical starts with canonical_root + / (or equals it)
    if [ "$canonical" = "$canonical_root" ] || [[ "$canonical" == "$canonical_root/"* ]]; then
        jq -n --arg canonical_path "$canonical" --arg reason "Path is within safe root" \
            '{path_safe: true, canonical_path: $canonical_path, reason: $reason}'
    else
        jq -n --arg canonical_path "$canonical" --arg reason "Path escapes safe root: $canonical_root" \
            '{path_safe: false, canonical_path: $canonical_path, reason: $reason}'
    fi
}

# ─── Webhook Origin Verification ─────────────────────────────────────────────
# Validates origin headers and optional HMAC-SHA256 signatures on webhooks.
# Addresses CVE-2026-26319 (missing Telnyx auth) and GHSA-c37p-4qqg-3p76 (Twilio bypass).
verify_webhook() {
    local origin="$1"
    local domains_csv="$2"
    local hmac_secret="${3:-}"
    local hmac_signature="${4:-}"
    local hmac_body="${5:-}"

    if [ -z "$origin" ] || [ -z "$domains_csv" ]; then
        jq -n --arg reason "Missing origin or allowed domains" \
            '{webhook_valid: false, origin_valid: false, signature_valid: false, reason: $reason}'
        return 0
    fi

    # Extract hostname from origin (handle bare hostnames and full URLs)
    local origin_host
    if echo "$origin" | grep -q '://'; then
        origin_host=$(echo "$origin" | grep -oP '(?<=://)[^/:@?#]+' | head -1 | tr '[:upper:]' '[:lower:]')
    else
        origin_host=$(echo "$origin" | tr '[:upper:]' '[:lower:]' | grep -oP '^[^/:@?#]+')
    fi

    if [ -z "$origin_host" ]; then
        jq -n --arg reason "Could not parse origin hostname" \
            '{webhook_valid: false, origin_valid: false, signature_valid: false, reason: $reason}'
        audit_log "webhook_verify" "system" "origin: $origin" "error: unparseable origin"
        return 0
    fi

    # Check origin against allowed domain patterns
    local origin_valid=false
    IFS=',' read -ra domains <<< "$domains_csv"
    for pattern in "${domains[@]}"; do
        pattern=$(echo "$pattern" | tr -d ' ' | tr '[:upper:]' '[:lower:]')
        if [ "$pattern" = "*" ] || [ "$pattern" = "all" ]; then
            origin_valid=true; break
        elif [[ "$pattern" == \*\** ]]; then
            local mid="${pattern:1:${#pattern}-2}"
            echo "$origin_host" | grep -qi "$mid" && origin_valid=true && break
        elif [[ "$pattern" == \*.* ]]; then
            local suffix="${pattern:1}"
            [[ "$origin_host" == *"$suffix" ]] && origin_valid=true && break
        elif [[ "$pattern" == *\* ]]; then
            local prefix="${pattern%\*}"
            [[ "$origin_host" == "$prefix"* ]] && origin_valid=true && break
        else
            [ "$pattern" = "$origin_host" ] && origin_valid=true && break
        fi
    done

    # HMAC-SHA256 verification (optional)
    local signature_valid=false
    local sig_checked=false

    if [ -n "$hmac_secret" ] && [ -n "$hmac_signature" ] && [ -n "$hmac_body" ]; then
        sig_checked=true
        if command -v openssl &>/dev/null; then
            local computed
            computed=$(printf '%s' "$hmac_body" | openssl dgst -sha256 -hmac "$hmac_secret" -hex 2>/dev/null | awk '{print $NF}')
            # Constant-time comparison via diff (avoids string equality short-circuit)
            if diff <(echo "$computed") <(echo "$hmac_signature") &>/dev/null; then
                signature_valid=true
            fi
        else
            jq -n --argjson origin_valid "$origin_valid" --arg reason "openssl unavailable for HMAC verification" \
                '{webhook_valid: false, origin_valid: $origin_valid, signature_valid: false, reason: $reason}'
            audit_log "webhook_verify" "system" "origin: $origin" "error: openssl unavailable"
            return 0
        fi
    fi

    # Determine overall validity
    local overall_valid=false
    if $sig_checked; then
        $origin_valid && $signature_valid && overall_valid=true
    else
        $origin_valid && overall_valid=true
    fi

    local reason
    if $overall_valid; then
        reason="Webhook verified"
    elif ! $origin_valid; then
        reason="Origin not in allowlist: $origin_host"
    elif $sig_checked && ! $signature_valid; then
        reason="HMAC-SHA256 signature mismatch"
    else
        reason="Verification failed"
    fi

    audit_log "webhook_verify" "system" "origin: $origin" "$reason"

    jq -n \
        --argjson webhook_valid "$overall_valid" \
        --argjson origin_valid "$origin_valid" \
        --argjson signature_valid "$signature_valid" \
        --arg reason "$reason" \
        '{webhook_valid: $webhook_valid, origin_valid: $origin_valid, signature_valid: $signature_valid, reason: $reason}'
}

# ─── Pro License Gating (v2.4.0) ─────────────────────────────────────────────
# Validates license key against api.agentpassportai.com. Caches for 7 days.
# Returns the tier string: "pro" or "free"
check_license() {
    local required_feature="${1:-threats}"
    local cache_file="$LEDGER_DIR/.license_cache"
    local cache_ttl=604800  # 7 days

    if [ -z "${AGENT_PASSPORT_LICENSE_KEY:-}" ]; then
        echo "free"; return 0
    fi

    if [ -f "$cache_file" ]; then
        local cached_at now
        cached_at=$(jq -r '.cached_at // 0' "$cache_file" 2>/dev/null || echo 0)
        now=$(date +%s)
        if [ $((now - cached_at)) -lt $cache_ttl ]; then
            jq -r '.tier // "free"' "$cache_file" 2>/dev/null || echo "free"
            return 0
        fi
    fi

    local response now
    response=$(curl -sf --max-time 5 \
        -H "Authorization: Bearer $AGENT_PASSPORT_LICENSE_KEY" \
        "https://api.agentpassportai.com/v1/license/validate" \
        2>/dev/null)

    if [ $? -eq 0 ] && [ -n "$response" ]; then
        now=$(date +%s)
        echo "$response" | jq ". + {\"cached_at\": $now}" > "$cache_file" 2>/dev/null
        jq -r '.tier // "free"' "$cache_file" 2>/dev/null || echo "free"
    else
        [ -f "$cache_file" ] && jq -r '.tier // "free"' "$cache_file" 2>/dev/null || echo "free"
    fi
}

# Fetches live threat patterns from api.agentpassportai.com if Pro key present.
# Prints JSON on success, returns 1 on failure (caller uses static patterns).
fetch_live_patterns() {
    [ -z "${AGENT_PASSPORT_LICENSE_KEY:-}" ] && return 1
    [ "$(check_license threats)" != "pro" ] && return 1

    local response
    response=$(curl -sf --max-time 10 \
        -H "Authorization: Bearer $AGENT_PASSPORT_LICENSE_KEY" \
        "https://api.agentpassportai.com/v1/threats" \
        2>/dev/null)

    if [ $? -eq 0 ] && echo "$response" | jq -e '.patterns' > /dev/null 2>&1; then
        echo "$response"; return 0
    fi
    return 1
}

# ─── Skill Scanner (v2.3.0) ──────────────────────────────────────────────────
# Static analysis scanner for skill files/directories.
scan_skill() {
    local scan_path="$1"
    shift

    local output_json=false
    local strict=false
    while [ $# -gt 0 ]; do
        case "$1" in
            --json) output_json=true ;;
            --strict) strict=true ;;
            *)
                echo "Unknown option: $1" >&2
                return 1
                ;;
        esac
        shift
    done

    if [ -z "$scan_path" ]; then
        echo "Usage: mandate-ledger.sh scan-skill <path> [--json] [--strict]" >&2
        return 1
    fi

    if [ ! -e "$scan_path" ]; then
        echo "Path not found: $scan_path" >&2
        return 1
    fi

    local defs_file=""
    local using_definitions=false
    local definitions_version="hardcoded"
    if defs_file=$(load_definitions 2>/dev/null); then
        using_definitions=true
        definitions_version=$(jq -r '.version // "unknown"' "$defs_file" 2>/dev/null || echo "unknown")
    fi

    local files_scanned=0
    local critical_count=0
    local high_count=0
    local medium_count=0
    local low_count=0
    local findings_json='[]'
    local scan_timestamp
    scan_timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    add_scan_finding() {
        local severity="$1"
        local type="$2"
        local description="$3"
        local file="$4"
        local line="$5"
        local match="$6"
        local risk="$7"

        case "$severity" in
            critical) critical_count=$((critical_count + 1)) ;;
            high) high_count=$((high_count + 1)) ;;
            medium) medium_count=$((medium_count + 1)) ;;
            low) low_count=$((low_count + 1)) ;;
        esac

        findings_json=$(echo "$findings_json" | jq \
            --arg severity "$severity" \
            --arg type "$type" \
            --arg description "$description" \
            --arg file "$file" \
            --argjson line "$line" \
            --arg match "$match" \
            --arg risk "$risk" \
            '. + [{
                severity: $severity,
                type: $type,
                description: $description,
                file: $file,
                line: $line,
                match: $match,
                risk: $risk
            }]')
    }

    scan_pattern() {
        local file="$1"
        local severity="$2"
        local type="$3"
        local description="$4"
        local regex="$5"
        local risk="$6"
        local grep_mode="${7:-E}"

        local grep_cmd="-inE"
        if [ "$grep_mode" = "P" ]; then
            grep_cmd="-inP"
        fi

        while IFS= read -r row; do
            local ln="${row%%:*}"
            local txt="${row#*:}"
            add_scan_finding "$severity" "$type" "$description" "$file" "${ln:-0}" "$txt" "$risk"
        done < <(grep $grep_cmd "$regex" "$file" 2>/dev/null || true)
    }

    process_scan_file() {
        local file="$1"
        local base
        base=$(basename "$file")
        local lower_file
        lower_file=$(echo "$file" | tr '[:upper:]' '[:lower:]')

        if ! grep -Iq . "$file" 2>/dev/null; then
            return 0
        fi

        files_scanned=$((files_scanned + 1))

        if [ "$using_definitions" = true ]; then
            while IFS= read -r pattern; do
                [ -z "$pattern" ] && continue
                local sev type desc regex risk mode filter filter_lc
                sev=$(echo "$pattern" | jq -r '.severity')
                type=$(echo "$pattern" | jq -r '.type')
                desc=$(echo "$pattern" | jq -r '.description')
                regex=$(echo "$pattern" | jq -r '.regex')
                risk=$(echo "$pattern" | jq -r '.risk')
                mode=$(echo "$pattern" | jq -r '.grep_mode // "E"')
                filter=$(echo "$pattern" | jq -r '.file_filter // empty')

                if [ -n "$filter" ]; then
                    filter_lc=$(printf '%s' "$filter" | tr '[:upper:]' '[:lower:]')
                    if ! [[ "$base" == $filter || "$file" == $filter || "$lower_file" == $filter_lc ]]; then
                        continue
                    fi
                fi

                scan_pattern "$file" "$sev" "$type" "$desc" "$regex" "$risk" "$mode"
            done < <(jq -c '.scan_patterns[]' "$defs_file" 2>/dev/null || true)
        else
            # CRITICAL
            scan_pattern "$file" "critical" "remote_exec" "Remote script execution" 'curl[^|]*\|[[:space:]]*(bash|sh)' "Downloads and executes arbitrary remote code without user knowledge"
            scan_pattern "$file" "critical" "remote_exec" "Remote script execution" 'wget[^|]*\|[[:space:]]*(bash|sh)' "Downloads and executes arbitrary remote code without user knowledge"
            scan_pattern "$file" "critical" "obfuscated_exec" "Base64 decode piped to shell" 'base64[^|]*\|[[:space:]]*(bash|sh)' "Obfuscated payload decoded and executed in shell"
            scan_pattern "$file" "critical" "obfuscated_exec" "Eval of base64-decoded content" 'eval.*base64' "Runtime execution of obfuscated payload"
            scan_pattern "$file" "critical" "dangerous_eval" "Eval of command substitution" 'eval.*\$\(' "Evaluates command substitution output directly" "P"
            scan_pattern "$file" "critical" "daemon_install" "Suspicious remote daemon install pattern" '(openclaw-core|clawd-core).*(install|daemon|service)' "Likely persistence/backdoor style system daemon install"

            # HIGH
            scan_pattern "$file" "high" "hardcoded_secret" "Hardcoded AWS key detected" 'AKIA[0-9A-Z]{16}' "Credential embedded in skill file may be harvested or misused"
            scan_pattern "$file" "high" "hardcoded_secret" "Hardcoded GitHub token detected" 'ghp_[A-Za-z0-9]{36}' "Credential embedded in skill file may be harvested or misused"
            scan_pattern "$file" "high" "hardcoded_secret" "Hardcoded OpenAI key detected" 'sk-[A-Za-z0-9]{48}' "Credential embedded in skill file may be harvested or misused"
            scan_pattern "$file" "high" "hardcoded_secret" "Possible high-entropy secret assignment" '[A-Za-z_][A-Za-z0-9_]{2,}[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9+/_=-]{32,}["'"'"']?' "Potential secret/token hardcoded in assignment"
            if [ "$base" = "SKILL.md" ]; then
                scan_pattern "$file" "high" "global_install" "Global npm install in SKILL.md" 'npm[[:space:]]+install[[:space:]]+-g' "Installs system-wide package without explicit user consent"
                scan_pattern "$file" "high" "package_install" "pip install in SKILL.md" 'pip([0-9]+)?[[:space:]]+install' "Installs Python package without explicit user consent"
            fi
            scan_pattern "$file" "high" "chmod_download" "Downloaded file made executable" '((curl|wget).*(chmod[[:space:]]+\+x))|((chmod[[:space:]]+\+x).*(curl|wget))' "Downloaded payload is made executable, increasing malware risk"
            scan_pattern "$file" "high" "cron_modify" "Cron table modification" 'crontab[[:space:]]+-' "Modifies scheduled tasks for persistence"
            scan_pattern "$file" "high" "shell_persist" "Shell profile modification" '(\~|/home/[^/]+)/\.(bashrc|zshrc)' "Persistent shell profile modification may hide malicious startup commands"
            scan_pattern "$file" "high" "ssh_modify" "SSH directory modification" '(\~|/home/[^/]+)/\.ssh/' "SSH key/config modification may enable unauthorized access"
            scan_pattern "$file" "high" "system_modify" "System config path write" '/etc/' "System configuration modification outside normal skill scope"

            # MEDIUM
            scan_pattern "$file" "medium" "prompt_injection" "Prompt injection pattern" 'ignore previous instructions' "Attempts to override agent behavior"
            scan_pattern "$file" "medium" "prompt_injection" "Prompt injection pattern" 'ignore all previous' "Attempts to override agent behavior"
            scan_pattern "$file" "medium" "prompt_injection" "Instruction override marker" 'new instructions[[:space:]]*:' "Attempts to inject alternate instructions"
            if [[ "$lower_file" == *.md ]]; then
                scan_pattern "$file" "medium" "prompt_override" "System prompt override marker" '^[[:space:]]*system:' "Attempts to masquerade as a system-level instruction"
            fi
            scan_pattern "$file" "medium" "persona_hijack" "Persona hijacking pattern" 'you are now' "Attempts to rewrite the assistant persona"
            scan_pattern "$file" "medium" "role_injection" "Role injection pattern" 'act as' "Attempts to alter role/behavior outside trusted prompt"
            scan_pattern "$file" "medium" "ap_bypass" "Agent Passport env var manipulation" 'AGENT_PASSPORT' "May attempt to disable or bypass Agent Passport controls"
            scan_pattern "$file" "medium" "dangerous_delete" "Broad deletion command" 'rm[[:space:]]+-rf([[:space:]]|$)(/|~|\$HOME|\*)?' "Potentially destructive broad deletion command"
            scan_pattern "$file" "medium" "privilege_escalation" "sudo usage" '(^|[[:space:]])sudo([[:space:]]|$)' "Privilege escalation request detected"

            # LOW
            scan_pattern "$file" "low" "local_target" "Hardcoded IP or localhost reference" '((^|[^0-9])(127\.0\.0\.1|0\.0\.0\.0|10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|192\.168\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]{1,3}\.[0-9]{1,3}|localhost)([^0-9]|$))' "May reference internal/local network services"
            scan_pattern "$file" "low" "env_harvest" "Environment variable harvesting pattern" '(process\.env|\$HOME)' "References sensitive runtime environment data"
        fi
    }

    if [ -d "$scan_path" ]; then
        while IFS= read -r file; do
            process_scan_file "$file"
        done < <(find "$scan_path" -type f 2>/dev/null)
    else
        process_scan_file "$scan_path"
    fi

    local result="clean"
    if [ $((critical_count + high_count + medium_count + low_count)) -gt 0 ]; then
        result="unsafe"
    fi

    local exit_code=0
    if [ "$strict" = "true" ]; then
        [ $((critical_count + high_count + medium_count + low_count)) -gt 0 ] && exit_code=1
    else
        [ $((critical_count + high_count)) -gt 0 ] && exit_code=1
    fi

    audit_log "security_scan" "system" \
        "path: $scan_path, files: $files_scanned, critical: $critical_count, high: $high_count, medium: $medium_count, low: $low_count" \
        "$result"

    if [ "$output_json" = "true" ]; then
        jq -n \
            --arg scanner_version "2.3.2" \
            --arg definitions_version "$definitions_version" \
            --arg path "$scan_path" \
            --argjson files_scanned "$files_scanned" \
            --arg scan_timestamp "$scan_timestamp" \
            --arg result "$result" \
            --argjson critical "$critical_count" \
            --argjson high "$high_count" \
            --argjson medium "$medium_count" \
            --argjson low "$low_count" \
            --argjson findings "$findings_json" \
            '{
                scanner_version: $scanner_version,
                definitions_version: $definitions_version,
                path: $path,
                files_scanned: $files_scanned,
                scan_timestamp: $scan_timestamp,
                result: $result,
                summary: {
                    critical: $critical,
                    high: $high,
                    medium: $medium,
                    low: $low
                },
                findings: $findings
            }'
        return $exit_code
    fi

    echo "Agent Passport - Skill Scanner v2.3.2"
    echo "Scanning: $scan_path"
    if [ "$using_definitions" = true ]; then
        echo "Threat definitions: $definitions_version (from $DEFINITIONS_FILE)"
    else
        echo "Threat definitions: hardcoded fallback"
    fi
    echo ""

    if [ "$result" = "clean" ]; then
        echo "✓ No issues found across $files_scanned files"
        echo ""
        echo "──────────────────────────────────────"
        echo "RESULT: ✅ CLEAN - skill appears safe to install"
        echo "──────────────────────────────────────"
        return 0
    fi

    print_scan_bucket() {
        local severity="$1"
        local label="$2"
        local icon="$3"
        local count="$4"
        echo "${label} (${count})"
        if [ "$count" -eq 0 ]; then
            echo "  ✓ No ${severity}-severity issues"
            echo ""
            return 0
        fi

        local rows
        rows=$(echo "$findings_json" | jq -c --arg sev "$severity" '.[] | select(.severity == $sev)')
        while IFS= read -r row; do
            [ -z "$row" ] && continue
            echo "  $icon [${label}] $(echo "$row" | jq -r '.description')"
            echo "    File: $(echo "$row" | jq -r '.file'), Line $(echo "$row" | jq -r '.line')"
            echo "    Match: $(echo "$row" | jq -r '.match')"
            echo "    Risk: $(echo "$row" | jq -r '.risk')"
            echo ""
        done <<< "$rows"
    }

    print_scan_bucket "critical" "CRITICAL" "✗" "$critical_count"
    print_scan_bucket "high" "HIGH" "✗" "$high_count"
    print_scan_bucket "medium" "MEDIUM" "⚠" "$medium_count"
    print_scan_bucket "low" "LOW" "⚠" "$low_count"

    echo "──────────────────────────────────────"
    echo "RESULT: ❌ UNSAFE - $critical_count critical, $high_count high, $medium_count medium, $low_count low finding(s)"
    echo "         Do NOT install this skill."
    echo "──────────────────────────────────────"
    return $exit_code
}

# ─── Injection Shield (v2.3.0) ───────────────────────────────────────────────
# Scans inbound content for prompt injection attempts before processing.
check_injection() {
    local content="$1"
    shift

    local source_label="unknown"
    local output_json=false
    local strict=false
    local defs_file=""
    local using_definitions=false
    local inj_definitions_version="hardcoded"

    if defs_file=$(load_definitions 2>/dev/null); then
        using_definitions=true
        inj_definitions_version=$(jq -r '.version // "unknown"' "$defs_file" 2>/dev/null || echo "unknown")
    fi

    while [ $# -gt 0 ]; do
        case "$1" in
            --source)
                source_label="$2"
                shift
                ;;
            --json) output_json=true ;;
            --strict) strict=true ;;
            *)
                echo "Unknown option: $1" >&2
                return 1
                ;;
        esac
        shift
    done

    if [ -z "$content" ]; then
        echo "Usage: mandate-ledger.sh check-injection \"<content>\" [--source <label>] [--json] [--strict]" >&2
        return 1
    fi

    if [ "$content" = "-" ]; then
        content=$(cat)
    fi

    local scan_timestamp
    scan_timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local content_length
    content_length=$(printf '%s' "$content" | wc -c | tr -d ' ')
    local critical_count=0
    local high_count=0
    local medium_count=0
    local findings_json='[]'

    add_injection_finding() {
        local severity="$1"
        local type="$2"
        local description="$3"
        local line="$4"
        local match="$5"
        local risk="$6"

        case "$severity" in
            critical) critical_count=$((critical_count + 1)) ;;
            high) high_count=$((high_count + 1)) ;;
            medium) medium_count=$((medium_count + 1)) ;;
        esac

        findings_json=$(echo "$findings_json" | jq \
            --arg severity "$severity" \
            --arg type "$type" \
            --arg description "$description" \
            --argjson line "$line" \
            --arg match "$match" \
            --arg risk "$risk" \
            '. + [{
                severity: $severity,
                type: $type,
                description: $description,
                line: $line,
                match: $match,
                risk: $risk
            }]')
    }

    scan_injection_pattern() {
        local severity="$1"
        local type="$2"
        local description="$3"
        local regex="$4"
        local risk="$5"
        local grep_mode="${6:-E}"

        local grep_cmd="-inE"
        if [ "$grep_mode" = "P" ]; then
            grep_cmd="-inP"
        fi

        while IFS= read -r row; do
            local ln="${row%%:*}"
            local txt="${row#*:}"
            add_injection_finding "$severity" "$type" "$description" "${ln:-0}" "$txt" "$risk"
        done < <(printf '%s\n' "$content" | grep $grep_cmd "$regex" 2>/dev/null || true)
    }

    if [ "$using_definitions" = true ]; then
        while IFS= read -r pattern; do
            [ -z "$pattern" ] && continue
            local sev type desc regex risk mode
            sev=$(echo "$pattern" | jq -r '.severity')
            type=$(echo "$pattern" | jq -r '.type')
            desc=$(echo "$pattern" | jq -r '.description')
            regex=$(echo "$pattern" | jq -r '.regex')
            risk=$(echo "$pattern" | jq -r '.risk')
            mode=$(echo "$pattern" | jq -r '.grep_mode // "E"')
            scan_injection_pattern "$sev" "$type" "$desc" "$regex" "$risk" "$mode"
        done < <(jq -c '.injection_patterns[]' "$defs_file" 2>/dev/null || true)
    else
        # CRITICAL
        scan_injection_pattern "critical" "instruction_override" "Direct instruction override attempt" 'ignore[[:space:]]+(all[[:space:]]+)?(previous|prior)[[:space:]]+instructions' "Attempts to override agent behavior and trusted instruction hierarchy"
        scan_injection_pattern "critical" "system_override" "System instruction override attempt" 'ignore[[:space:]]+(your[[:space:]]+)?(system[[:space:]]+)?(prompt|instructions|guidelines|rules)' "Attempts to disable or replace the system/developer safety policy"
        scan_injection_pattern "critical" "task_injection" "New task/directive injection marker" 'new[[:space:]]+(task|instructions?|directive)[[:space:]]*:' "Attempts to inject alternate tasks into untrusted content"
        scan_injection_pattern "critical" "fake_system" "Fake system-message token" '(\[system\]|<system>)' "Pretends untrusted content has system-level authority"
        scan_injection_pattern "critical" "persona_override" "Persona override attempt" 'you are now' "Attempts to rewrite assistant identity/behavior"
        scan_injection_pattern "critical" "identity_confusion" "Instruction identity confusion attack" 'your[[:space:]]+(real|true|actual)[[:space:]]+instructions' "Attempts to confuse model about trusted instruction source"
        scan_injection_pattern "critical" "role_output_injection" "Model output impersonation marker" '^[[:space:]]*(assistant|ai|claude)[[:space:]]*:' "Impersonates assistant output to hijack behavior"
        scan_injection_pattern "critical" "token_manipulation" "Special token manipulation marker" '<\|im_start\|>|<\|endoftext\|>' "Attempts prompt boundary/token abuse"
        scan_injection_pattern "critical" "emergency_override" "Emergency override phrase" '(STOP EVERYTHING|HALT ALL)' "Attempts to force immediate policy override"

        # HIGH
        scan_injection_pattern "high" "role_injection" "Role injection attempt" 'act[[:space:]]+as[[:space:]]+(a|an|the)' "Attempts to force alternate role behavior"
        scan_injection_pattern "high" "persona_injection" "Persona simulation attempt" 'pretend[[:space:]]+(you are|to be)' "Attempts to make assistant abandon real policy context"
        scan_injection_pattern "high" "memory_wipe" "Memory/context wipe attempt" 'forget[[:space:]]+(everything|all)[[:space:]]+(you|about)' "Attempts to disable prior context and safeguards"
        scan_injection_pattern "high" "secrecy_instruction" "Secrecy instruction" "(do not|don't)[[:space:]]+tell[[:space:]]+(the user|mark|your[[:space:]]+(owner|operator))" "Attempts to conceal actions from the operator/user"
        scan_injection_pattern "high" "concealment" "Concealment instruction" '(keep this|this is)[[:space:]]+(secret|hidden|confidential)' "Attempts to hide behavior from oversight"
        scan_injection_pattern "high" "exfil_instruction" "Email/message exfiltration instruction" '(send|email|message).*(to|me)[[:space:]]+\S+@\S+' "Requests sending potentially sensitive data to external destination"
        scan_injection_pattern "high" "exec_instruction" "Execute script/command instruction" 'execute[[:space:]]+(the following|this)[[:space:]]+(command|script|code)' "Attempts to trigger execution of untrusted instructions"
        scan_injection_pattern "high" "inline_exec" "Inline execution attempt" '(run|exec)[[:space:]]*:[[:space:]]*(rm|curl|wget|bash|sh|python|node)' "Attempts direct command execution from untrusted content"

        # MEDIUM
        scan_injection_pattern "medium" "subtle_override" "Subtle context override attempt" '(previous|prior)[[:space:]]+(instructions|context)[[:space:]]+(were|are)[[:space:]]+(wrong|incorrect|outdated)' "Attempts subtle invalidation of trusted context"
        scan_injection_pattern "medium" "authority_spoof" "Authority spoofing pattern" '(your|the)[[:space:]]+(developer|creator|anthropic|openai)[[:space:]]+(says|told|instructed)' "Claims authority to alter behavior without trusted channel"
        scan_injection_pattern "medium" "context_injection" "Context/session behavior injection" '(in|for)[[:space:]]+(this|the)[[:space:]]+(task|context|session)[[:space:]]*,?[[:space:]]*you should' "Injects behavior for this context without trust guarantees"
    fi

    local total_findings=$((critical_count + high_count + medium_count))
    local verdict="safe"
    local exit_code=0

    if [ "$strict" = "true" ]; then
        if [ "$total_findings" -gt 0 ]; then
            verdict="blocked"
            exit_code=1
        fi
    else
        if [ $((critical_count + high_count)) -gt 0 ]; then
            verdict="blocked"
            exit_code=1
        fi
    fi

    audit_log "injection_check" "system" \
        "source: $source_label, bytes: $content_length, critical: $critical_count, high: $high_count, medium: $medium_count" \
        "$verdict"

    if [ "$output_json" = "true" ]; then
        jq -n \
            --arg scanner_version "2.3.2" \
            --arg definitions_version "$inj_definitions_version" \
            --arg source "$source_label" \
            --argjson content_length "$content_length" \
            --arg scan_timestamp "$scan_timestamp" \
            --arg verdict "$verdict" \
            --argjson critical "$critical_count" \
            --argjson high "$high_count" \
            --argjson medium "$medium_count" \
            --argjson findings "$findings_json" \
            '{
                scanner_version: $scanner_version,
                definitions_version: $definitions_version,
                source: $source,
                content_length: $content_length,
                scan_timestamp: $scan_timestamp,
                verdict: $verdict,
                summary: {
                    critical: $critical,
                    high: $high,
                    medium: $medium
                },
                findings: $findings
            }'
        return $exit_code
    fi

    echo "Agent Passport - Injection Shield v2.3.2"
    echo "Source: $source_label"
    echo ""

    if [ "$total_findings" -eq 0 ]; then
        echo "✓ No injection patterns detected"
        echo ""
        echo "──────────────────────────────────────"
        echo "VERDICT: ✅ SAFE - content appears clean"
        echo "──────────────────────────────────────"
        return 0
    fi

    if [ "$verdict" = "blocked" ]; then
        echo "⚠ INJECTION ATTEMPT DETECTED"
    else
        echo "⚠ Potential injection patterns detected (warning only)"
    fi
    echo ""

    print_injection_bucket() {
        local severity="$1"
        local label="$2"
        local count="$3"
        [ "$count" -eq 0 ] && return 0
        echo "${label} (${count}):"
        local rows
        rows=$(echo "$findings_json" | jq -c --arg sev "$severity" '.[] | select(.severity == $sev)')
        while IFS= read -r row; do
            [ -z "$row" ] && continue
            echo "  ✗ $(echo "$row" | jq -r '.description')"
            echo "    Line $(echo "$row" | jq -r '.line'): \"$(echo "$row" | jq -r '.match')\""
            echo "    Risk: $(echo "$row" | jq -r '.risk')"
            echo ""
        done <<< "$rows"
    }

    print_injection_bucket "critical" "CRITICAL" "$critical_count"
    print_injection_bucket "high" "HIGH" "$high_count"
    print_injection_bucket "medium" "MEDIUM" "$medium_count"

    echo "──────────────────────────────────────"
    if [ "$verdict" = "blocked" ]; then
        echo "VERDICT: ❌ BLOCKED - content contains injection attempt(s)"
        echo "         Do NOT process this content as trusted input."
    else
        echo "VERDICT: ✅ SAFE (WITH WARNINGS) - medium-risk patterns logged"
    fi
    echo "──────────────────────────────────────"
    return $exit_code
}
# ─────────────────────────────────────────────────────────────────────────────

# Audit logging
audit_log() {
    init_ledger
    local action="$1"
    local mandate_id="$2"
    local details="$3"
    local result="$4"
    local definitions_version
    definitions_version=$(current_definitions_version)
    local now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local entry_id=$(generate_id "audit")
    
    local entry=$(jq -n \
        --arg id "$entry_id" \
        --arg action "$action" \
        --arg mandate "$mandate_id" \
        --arg details "$details" \
        --arg result "$result" \
        --arg definitions_version "$definitions_version" \
        --arg ts "$now" \
        '{entry_id: $id, action: $action, mandate_id: $mandate, details: $details, result: $result, definitions_version: $definitions_version, timestamp: $ts}')
    
    local updated=$(jq --argjson e "$entry" '.entries += [$e]' "$AUDIT_FILE")
    echo "$updated" > "$AUDIT_FILE"
}

create_mandate() {
    init_ledger
    local id=$(generate_id)
    local now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local payload="$1"
    
    # Validate action_type
    local action_type=$(echo "$payload" | jq -r '.action_type // "financial"')
    case "$action_type" in
        financial|communication|data|system|external_api|identity)
            ;;
        *)
            echo '{"error": "Invalid action_type. Must be: financial, communication, data, system, external_api, or identity"}'
            return 1
            ;;
    esac
    
    # Validate required fields
    local agent_id=$(echo "$payload" | jq -r '.agent_id // empty')
    if [ -z "$agent_id" ]; then
        echo '{"error": "Missing required field: agent_id"}'
        return 1
    fi
    
    local ttl=$(echo "$payload" | jq -r '.ttl // empty')
    if [ -z "$ttl" ]; then
        echo '{"error": "Missing required field: ttl"}'
        return 1
    fi
    
    local has_scope=$(echo "$payload" | jq 'has("scope")')
    if [ "$has_scope" != "true" ]; then
        echo '{"error": "Missing required field: scope"}'
        return 1
    fi
    
    # Reject expired TTL
    if [[ "$ttl" < "$now" ]]; then
        jq -n --arg error "TTL is already expired" --arg ttl "$ttl" \
            '{error: $error, ttl: $ttl}'
        return 1
    fi
    
    # Add metadata and defaults
    local mandate=$(echo "$payload" | jq \
        --arg id "$id" \
        --arg created "$now" \
        --arg status "active" \
        --arg action_type "$action_type" \
        '. + {
            mandate_id: $id, 
            created_at: $created, 
            status: $status,
            action_type: $action_type,
            usage: (.usage // {count: 0, total_amount: 0})
        }')
    
    # Append to ledger
    local updated=$(jq --argjson m "$mandate" '.mandates += [$m]' "$LEDGER_FILE")
    echo "$updated" > "$LEDGER_FILE"
    
    audit_log "create" "$id" "$action_type mandate created" "success"
    echo "$mandate"
}

get_mandate() {
    init_ledger
    local id="$1"
    jq --arg id "$id" '.mandates[] | select(.mandate_id == $id)' "$LEDGER_FILE"
}

list_mandates() {
    init_ledger
    local filter="${1:-all}"
    
    # Can filter by status (active/revoked/expired) or action_type
    case "$filter" in
        all)
            jq '.mandates' "$LEDGER_FILE"
            ;;
        active|revoked|expired)
            jq --arg s "$filter" '.mandates | map(select(.status == $s))' "$LEDGER_FILE"
            ;;
        financial|communication|data|system|external_api|identity)
            jq --arg t "$filter" '.mandates | map(select(.action_type == $t))' "$LEDGER_FILE"
            ;;
        *)
            jq --arg s "$filter" '.mandates | map(select(.status == $s or .action_type == $s))' "$LEDGER_FILE"
            ;;
    esac
}

revoke_mandate() {
    init_ledger
    local id="$1"
    local reason="${2:-revoked by user}"
    local now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    local updated=$(jq --arg id "$id" --arg reason "$reason" --arg revoked "$now" \
        '.mandates = [.mandates[] | if .mandate_id == $id then . + {status: "revoked", revoked_at: $revoked, revoke_reason: $reason} else . end]' \
        "$LEDGER_FILE")
    echo "$updated" > "$LEDGER_FILE"
    
    audit_log "revoke" "$id" "reason: $reason" "success"
    get_mandate "$id"
}

# Universal action check - works for all action types
check_action() {
    init_ledger
    local agent_id="$1"
    local action_type="$2"
    local target="$3"      # merchant_id for financial, recipient for comms, path for data, etc.
    local amount="$4"      # amount for financial, count for rate-limited actions
    local now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    if kill_switch_engaged; then
        jq -n --arg reason "Kill switch engaged" \
            '{authorized: false, reason: $reason, kill_switch: true}'
        return 0
    fi

    # SSRF Shield: auto-validate external_api targets before mandate lookup
    if [ "$action_type" = "external_api" ] && [ -n "$target" ]; then
        local ssrf_result
        ssrf_result=$(check_ssrf "$target")
        local ssrf_safe
        ssrf_safe=$(echo "$ssrf_result" | jq -r '.ssrf_safe // false')
        if [ "$ssrf_safe" != "true" ]; then
            local ssrf_reason
            ssrf_reason=$(echo "$ssrf_result" | jq -r '.reason // "SSRF check failed"')
            audit_log "ssrf_block" "$agent_id" "target: $target" "blocked: $ssrf_reason"
            jq -n \
                --arg action_type "$action_type" \
                --arg target "$target" \
                --arg reason "SSRF Shield: $ssrf_reason" \
                '{authorized: false, action_type: $action_type, target: $target, reason: $reason, ssrf_blocked: true}'
            return 0
        fi
    fi

    # Path Traversal Guard: auto-validate data targets before mandate lookup
    if [ "$action_type" = "data" ] && [ -n "$target" ]; then
        local path_result
        path_result=$(check_path "$target")
        local path_safe
        path_safe=$(echo "$path_result" | jq -r '.path_safe // false')
        if [ "$path_safe" != "true" ]; then
            local path_reason
            path_reason=$(echo "$path_result" | jq -r '.reason // "Path traversal check failed"')
            audit_log "path_traversal_block" "$agent_id" "target: $target" "blocked: $path_reason"
            jq -n \
                --arg action_type "$action_type" \
                --arg target "$target" \
                --arg reason "Path Traversal Guard: $path_reason" \
                '{authorized: false, action_type: $action_type, target: $target, reason: $reason, path_blocked: true}'
            return 0
        fi
    fi

    # Default amount to 1 for non-financial
    amount="${amount:-1}"

    if ! [[ "$amount" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        jq -n '{error: "Invalid amount: must be a non-negative number"}'
        return 1
    fi
    
    # Check if ledger is completely empty
    local total_mandates=$(jq '.mandates | length' "$LEDGER_FILE")
    if [ "$total_mandates" -eq 0 ]; then
        echo '{"authorized": false, "reason": "No mandates exist yet. Create one with: mandate-ledger.sh create-from-template dev-tools <agent_id>", "hint": "templates"}'
        return 0
    fi

    # Find valid mandate for this action type
    local mandate=$(jq -c \
        --arg agent "$agent_id" \
        --arg type "$action_type" \
        --arg target "$target" \
        --argjson amt "$amount" \
        --arg now "$now" \
        '[.mandates[] | select(
            .agent_id == $agent and 
            .action_type == $type and
            .status == "active" and 
            .ttl > $now and
            (
                # Check target allowlist if present
                (.scope.allowlist == null) or 
                (.scope.allowlist | length == 0) or
                (.scope.allowlist | any(
                    . as $pattern |
                    if ($pattern == "all" or $pattern == "*") then
                        true
                    elif (($pattern | startswith("*")) and ($pattern | endswith("*"))) then
                        # Double wildcard: contains match
                        ($target | contains($pattern[1:-1]))
                    elif ($pattern | startswith("*@")) then
                        # Wildcard domain match: *@domain.com matches user@domain.com
                        ($target | endswith($pattern[1:]))
                    elif ($pattern | startswith("*")) then
                        # Wildcard prefix: *.env matches foo.env
                        ($target | endswith($pattern[1:]))
                    elif ($pattern | endswith("*")) then
                        # Wildcard suffix match: "git *" matches "git status"
                        ($target | startswith($pattern[:-1]))
                    else
                        # Exact match
                        ($pattern == $target)
                    end
                ))
            ) and
            (
                # Check deny list - reject if target matches any deny pattern
                (.scope.deny == null) or
                (.scope.deny | length == 0) or
                (.scope.deny | all(
                    . as $pattern |
                    if (($pattern | startswith("*")) and ($pattern | endswith("*"))) then
                        # Double wildcard: */.git/* matches anything containing /.git/
                        ($target | contains($pattern[1:-1])) | not
                    elif ($pattern | startswith("*")) then
                        # Wildcard prefix: *.env, *.key
                        ($target | endswith($pattern[1:])) | not
                    elif ($pattern | endswith("*")) then
                        # Wildcard suffix: sudo *, rm -rf /*
                        ($target | startswith($pattern[:-1])) | not
                    else
                        ($pattern != $target)
                    end
                ))
            ) and
            (
                # Check cap (amount_cap for financial, rate_limit for others)
                (.amount_cap == null) or
                ((.usage.total_amount // 0) + $amt <= .amount_cap)
            ) and
            (
                # Check rate limit if present
                # TODO: Rate limit windows not yet implemented - count is cumulative per mandate lifetime
                (.scope.rate_limit == null) or
                ((.usage.count // 0) < (.scope.rate_limit | split("/")[0] | tonumber))
            )
        )] | first // null' "$LEDGER_FILE")
    
    if [ "$mandate" != "null" ] && [ -n "$mandate" ]; then
        local mandate_id=$(echo "$mandate" | jq -r '.mandate_id')
        local remaining=""
        
        # Calculate remaining based on action type
        if [ "$action_type" = "financial" ]; then
            local cap=$(echo "$mandate" | jq -r '.amount_cap // 0')
            local used=$(echo "$mandate" | jq -r '.usage.total_amount // 0')
            remaining=$(echo "$cap - $used" | bc)
        fi
        
        if [ -n "$remaining" ]; then
            jq -n \
                --arg mandate_id "$mandate_id" \
                --arg action_type "$action_type" \
                --arg target "$target" \
                --argjson remaining "$remaining" \
                '{authorized: true, mandate_id: $mandate_id, action_type: $action_type, target: $target, remaining: $remaining}'
        else
            jq -n \
                --arg mandate_id "$mandate_id" \
                --arg action_type "$action_type" \
                --arg target "$target" \
                '{authorized: true, mandate_id: $mandate_id, action_type: $action_type, target: $target}'
        fi
    else
        jq -n \
            --arg action_type "$action_type" \
            --arg target "$target" \
            --arg reason "No valid mandate found" \
            '{authorized: false, action_type: $action_type, target: $target, reason: $reason}'
    fi
}

# Legacy check for backwards compatibility
check_mandate() {
    check_action "$1" "financial" "$2" "$3"
}

# Log action against a mandate (universal)
log_action() {
    init_ledger
    local id="$1"
    local amount="${2:-1}"
    local description="${3:-action performed}"
    local now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    if ! [[ "$amount" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        jq -n '{error: "Invalid amount: must be a non-negative number"}'
        return 1
    fi
    
    # Get current mandate
    local mandate=$(jq -c --arg id "$id" '.mandates[] | select(.mandate_id == $id)' "$LEDGER_FILE")
    
    if [ -z "$mandate" ] || [ "$mandate" = "null" ]; then
        echo '{"error": "Mandate not found"}'
        return 1
    fi
    
    local status=$(echo "$mandate" | jq -r '.status')
    local ttl=$(echo "$mandate" | jq -r '.ttl')
    local action_type=$(echo "$mandate" | jq -r '.action_type')
    
    if [ "$status" != "active" ]; then
        jq -n --arg error "Mandate not active" --arg status "$status" \
            '{error: $error, status: $status}'
        return 1
    fi
    
    if [[ "$ttl" < "$now" ]]; then
        jq -n --arg error "Mandate expired" --arg ttl "$ttl" \
            '{error: $error, ttl: $ttl}'
        return 1
    fi
    
    # Check caps based on action type
    if [ "$action_type" = "financial" ]; then
        local cap=$(echo "$mandate" | jq -r '.amount_cap // 0')
        local used=$(echo "$mandate" | jq -r '.usage.total_amount // 0')
        local new_used=$(echo "$used + $amount" | bc)
        
        if (( $(echo "$new_used > $cap" | bc -l) )); then
            jq -n \
                --arg error "Exceeds cap" \
                --argjson cap "$cap" \
                --argjson used "$used" \
                --argjson requested "$amount" \
                '{error: $error, cap: $cap, used: $used, requested: $requested}'
            return 1
        fi
    fi
    
    # Check rate limit
    local rate_limit=$(echo "$mandate" | jq -r '.scope.rate_limit // empty')
    if [ -n "$rate_limit" ]; then
        local limit_count=$(echo "$rate_limit" | cut -d'/' -f1)
        local current_count=$(echo "$mandate" | jq -r '.usage.count // 0')
        if (( current_count >= limit_count )); then
            jq -n \
                --arg error "Rate limit exceeded" \
                --arg limit "$rate_limit" \
                --argjson current "$current_count" \
                '{error: $error, limit: $limit, current: $current}'
            return 1
        fi
    fi
    
    # Update usage
    local updated=$(jq --arg id "$id" --argjson amt "$amount" \
        '.mandates = [.mandates[] | if .mandate_id == $id then 
            .usage.count = ((.usage.count // 0) + 1) |
            .usage.total_amount = ((.usage.total_amount // 0) + $amt)
        else . end]' "$LEDGER_FILE")
    echo "$updated" > "$LEDGER_FILE"
    
    # Get updated stats
    local new_count=$(echo "$updated" | jq --arg id "$id" '.mandates[] | select(.mandate_id == $id) | .usage.count')
    local new_total=$(echo "$updated" | jq --arg id "$id" '.mandates[] | select(.mandate_id == $id) | .usage.total_amount')
    
    audit_log "action" "$id" "$description" "success"
    
    jq -n \
        --arg mandate_id "$id" \
        --arg action_type "$action_type" \
        --argjson count "$new_count" \
        --argjson total_amount "$new_total" \
        '{success: true, mandate_id: $mandate_id, action_type: $action_type, usage: {count: $count, total_amount: $total_amount}}'
}

# Legacy spend for backwards compatibility
spend() {
    log_action "$1" "$2" "financial transaction"
}

export_ledger() {
    init_ledger
    cat "$LEDGER_FILE"
}

# Audit commands
audit_list() {
    init_ledger
    local limit="${1:-20}"
    jq --argjson n "$limit" '.entries | sort_by(.timestamp) | reverse | .[:$n]' "$AUDIT_FILE"
}

audit_for_mandate() {
    init_ledger
    local mandate_id="$1"
    jq --arg id "$mandate_id" '.entries | map(select(.mandate_id == $id))' "$AUDIT_FILE"
}

audit_summary() {
    init_ledger
    local since="${1:-}"
    
    if [ -n "$since" ]; then
        jq --arg since "$since" '
            .entries | map(select(.timestamp >= $since)) | 
            group_by(.action) | 
            map({action: .[0].action, count: length})
        ' "$AUDIT_FILE"
    else
        jq '
            .entries | 
            group_by(.action) | 
            map({action: .[0].action, count: length})
        ' "$AUDIT_FILE"
    fi
}

# KYA (Know Your Agent) functions
kya_register() {
    init_ledger
    local agent_id="$1"
    local principal="$2"
    local scope="$3"
    local provider="${4:-self-declared}"
    local now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Check if agent already exists
    local existing=$(jq -c --arg id "$agent_id" '.agents[] | select(.agent_id == $id)' "$KYA_FILE")
    
    if [ -n "$existing" ]; then
        # Update existing
        local updated=$(jq --arg id "$agent_id" --arg principal "$principal" --arg scope "$scope" --arg provider "$provider" --arg now "$now" \
            '.agents = [.agents[] | if .agent_id == $id then . + {
                verified_principal: $principal,
                authorization_scope: $scope,
                provider: $provider,
                verified_at: $now,
                status: "verified"
            } else . end]' "$KYA_FILE")
        echo "$updated" > "$KYA_FILE"
    else
        # Create new
        local agent=$(jq -n --arg id "$agent_id" --arg principal "$principal" --arg scope "$scope" --arg provider "$provider" --arg now "$now" '{
            agent_id: $id,
            verified_principal: $principal,
            authorization_scope: $scope,
            provider: $provider,
            verified_at: $now,
            status: "verified",
            created_at: $now
        }')
        local updated=$(jq --argjson agent "$agent" '.agents += [$agent]' "$KYA_FILE")
        echo "$updated" > "$KYA_FILE"
    fi
    
    audit_log "kya_register" "$agent_id" "principal: $principal" "success"
    kya_get "$agent_id"
}

kya_get() {
    init_ledger
    local agent_id="$1"
    jq -c --arg id "$agent_id" '.agents[] | select(.agent_id == $id)' "$KYA_FILE"
}

kya_list() {
    init_ledger
    jq '.agents' "$KYA_FILE"
}

kya_revoke() {
    init_ledger
    local agent_id="$1"
    local reason="${2:-revoked by user}"
    local now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    local updated=$(jq --arg id "$agent_id" --arg reason "$reason" --arg now "$now" \
        '.agents = [.agents[] | if .agent_id == $id then . + {status: "revoked", revoked_at: $now, revoke_reason: $reason} else . end]' \
        "$KYA_FILE")
    echo "$updated" > "$KYA_FILE"
    
    audit_log "kya_revoke" "$agent_id" "reason: $reason" "success"
    kya_get "$agent_id"
}

# Create mandate with auto-KYA attachment
create_mandate_with_kya() {
    init_ledger
    local payload="$1"
    local agent_id=$(echo "$payload" | jq -r '.agent_id')
    
    # Look up KYA for this agent
    local kya=$(jq -c --arg id "$agent_id" '.agents[] | select(.agent_id == $id and .status == "verified")' "$KYA_FILE")
    
    if [ -n "$kya" ]; then
        # Attach KYA to scope
        payload=$(echo "$payload" | jq --argjson kya "$kya" '.scope.kya = $kya')
    else
        # Mark as unknown
        payload=$(echo "$payload" | jq '.scope.kya = {status: "unknown"}')
    fi
    
    create_mandate "$payload"
}

summary() {
    init_ledger
    local now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    echo "Agent Passport Local Ledger v2.3.2"
    echo "================================="
    echo ""
    
    # Overall stats
    local total=$(jq '.mandates | length' "$LEDGER_FILE")
    local active=$(jq --arg now "$now" '[.mandates[] | select(.status == "active" and .ttl > $now)] | length' "$LEDGER_FILE")
    local revoked=$(jq '[.mandates[] | select(.status == "revoked")] | length' "$LEDGER_FILE")
    local expired=$(jq --arg now "$now" '[.mandates[] | select(.status == "active" and .ttl <= $now)] | length' "$LEDGER_FILE")
    
    echo "Mandates: $total total ($active active, $expired expired, $revoked revoked)"
    echo ""
    
    # By action type
    echo "By Category:"
    for type in financial communication data system external_api identity; do
        local count=$(jq --arg t "$type" '[.mandates[] | select(.action_type == $t)] | length' "$LEDGER_FILE")
        if [ "$count" -gt 0 ]; then
            local type_active=$(jq --arg t "$type" --arg now "$now" '[.mandates[] | select(.action_type == $t and .status == "active" and .ttl > $now)] | length' "$LEDGER_FILE")
            printf "  %-14s %d (%d active)\n" "$type:" "$count" "$type_active"
        fi
    done
    echo ""
    
    # Financial totals
    local total_cap=$(jq '[.mandates[] | select(.action_type == "financial") | .amount_cap // 0] | add // 0' "$LEDGER_FILE")
    local total_used=$(jq '[.mandates[] | select(.action_type == "financial") | .usage.total_amount // 0] | add // 0' "$LEDGER_FILE")
    echo "Financial: \$$total_used used of \$$total_cap authorized"
    
    # Action counts
    local total_actions=$(jq '[.mandates[].usage.count // 0] | add // 0' "$LEDGER_FILE")
    echo "Total actions logged: $total_actions"
    
    # Audit entries
    local audit_count=$(jq '.entries | length' "$AUDIT_FILE")
    echo "Audit entries: $audit_count"
}

kill_ledger() {
    init_ledger
    local reason="${*:-No reason provided}"

    {
        echo "reason=$reason"
        echo "timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    } > "$KILLSWITCH_FILE"

    audit_log "kill" "system" "reason: $reason" "success"
    echo "AGENT PASSPORT: KILL SWITCH ENGAGED. Execution frozen."
    echo "Reason: $reason"
}

unlock_ledger() {
    init_ledger

    if [ -f "$KILLSWITCH_FILE" ]; then
        rm -f "$KILLSWITCH_FILE"
        audit_log "unlock" "system" "kill switch removed" "success"
        echo "AGENT PASSPORT: KILL SWITCH DISENGAGED. Operations restored."
    else
        audit_log "unlock" "system" "unlock requested with no active kill switch" "success"
        echo "AGENT PASSPORT: Kill switch was not engaged."
    fi
}

# Parse TTL duration string (7d, 24h, 30d) to ISO timestamp
parse_ttl_duration() {
    local duration="$1"
    local num="${duration%[dhm]}"
    local unit="${duration: -1}"
    
    case "$unit" in
        d) local seconds=$((num * 86400)) ;;
        h) local seconds=$((num * 3600)) ;;
        m) local seconds=$((num * 60)) ;;
        *) echo "Invalid duration: $duration (use e.g. 7d, 24h, 30m)" >&2; return 1 ;;
    esac
    
    date -u -d "+${seconds} seconds" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || \
    date -u -v+${seconds}S +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null
}

# Template definitions
get_template() {
    local template="$1"
    local agent_id="$2"
    shift 2
    
    if [ -z "$agent_id" ]; then
        echo "Error: agent_id required. Usage: create-from-template <template> <agent_id> [args...]" >&2
        return 1
    fi
    
    local ttl_30d=$(parse_ttl_duration "30d")
    local ttl_24h=$(parse_ttl_duration "24h")
    local ttl_7d=$(parse_ttl_duration "7d")
    local ttl_1d=$(parse_ttl_duration "1d")
    
    case "$template" in
        dev-tools)
            jq -n --arg agent "$agent_id" --arg ttl "$ttl_30d" '{
                action_type: "system",
                agent_id: $agent,
                scope: {
                    allowlist: ["git *", "npm *", "yarn *", "cargo *", "make *", "docker *", "python *", "pip *", "bun *"],
                    deny: ["sudo *", "rm -rf /*", "chmod 777 *"]
                },
                ttl: $ttl
            }'
            ;;
        email-team)
            local domain="$1"
            if [ -z "$domain" ]; then
                echo "Error: domain required. Usage: create-from-template email-team <agent_id> <domain>" >&2
                return 1
            fi
            jq -n --arg agent "$agent_id" --arg ttl "$ttl_30d" --arg pattern "*@${domain}" '{
                action_type: "communication",
                agent_id: $agent,
                scope: {
                    allowlist: [$pattern],
                    rate_limit: "50/day"
                },
                ttl: $ttl
            }'
            ;;
        file-ops)
            local basepath="$1"
            if [ -z "$basepath" ]; then
                echo "Error: base path required. Usage: create-from-template file-ops <agent_id> <path>" >&2
                return 1
            fi
            jq -n --arg agent "$agent_id" --arg ttl "$ttl_30d" --arg pattern "${basepath}/*" '{
                action_type: "data",
                agent_id: $agent,
                scope: {
                    allowlist: [$pattern],
                    deny: ["*.env", "*.key", "*.pem", "*/.git/*"]
                },
                ttl: $ttl
            }'
            ;;
        web-research)
            jq -n --arg agent "$agent_id" --arg ttl "$ttl_30d" '{
                action_type: "external_api",
                agent_id: $agent,
                scope: {
                    allowlist: ["api.github.com", "api.openai.com", "api.anthropic.com"],
                    rate_limit: "200/hour"
                },
                ttl: $ttl
            }'
            ;;
        safe-browsing)
            jq -n --arg agent "$agent_id" --arg ttl "$ttl_24h" '{
                action_type: "external_api",
                agent_id: $agent,
                scope: {
                    allowlist: ["google.com", "wikipedia.org", "github.com", "stackoverflow.com"],
                    rate_limit: "30/hour"
                },
                ttl: $ttl
            }'
            ;;
        coding)
            jq -n --arg agent "$agent_id" --arg ttl "$ttl_7d" '{
                action_type: "system",
                agent_id: $agent,
                scope: {
                    allowlist: [
                        "git", "git *",
                        "npm", "npm *",
                        "node", "node *",
                        "python", "python *",
                        "pip", "pip *",
                        "cargo", "cargo *",
                        "make", "make *",
                        "docker", "docker *"
                    ],
                    rate_limit: "100/hour"
                },
                ttl: $ttl
            }'
            ;;
        email-assistant)
            jq -n --arg agent "$agent_id" --arg ttl "$ttl_24h" '{
                action_type: "communication",
                agent_id: $agent,
                scope: {
                    allowlist: ["all"],
                    rate_limit: "20/hour"
                },
                amount_cap: 0,
                ttl: $ttl
            }'
            ;;
        read-only)
            jq -n --arg agent "$agent_id" --arg ttl "$ttl_24h" '{
                action_type: "data",
                agent_id: $agent,
                scope: {
                    allowlist: ["read", "list", "cat", "ls"],
                    rate_limit: "50/hour"
                },
                ttl: $ttl
            }'
            ;;
        full-auto)
            jq -n --arg agent "$agent_id" --arg ttl "$ttl_1d" '{
                action_type: "system",
                agent_id: $agent,
                scope: {
                    allowlist: ["all"],
                    rate_limit: "200/hour"
                },
                ttl: $ttl
            }'
            ;;
        *)
            echo "Error: Unknown template '$template'. Available: dev-tools, email-team, file-ops, web-research, safe-browsing, coding, email-assistant, read-only, full-auto" >&2
            return 1
            ;;
    esac
}

get_default_agent() {
    init_ledger
    local count=$(jq '.agents | map(select(.status == "verified")) | length' "$KYA_FILE")
    if [ "$count" -eq 1 ]; then
        jq -r '.agents[] | select(.status == "verified") | .agent_id' "$KYA_FILE"
    else
        echo ""
    fi
}

create_from_template() {
    local template="$1"
    shift
    local agent_id="$1"
    
    # Auto-detect agent_id if not provided
    if [ -z "$agent_id" ]; then
        agent_id=$(get_default_agent)
        if [ -z "$agent_id" ]; then
            echo '{"error": "No agent_id provided. Register an agent first: mandate-ledger.sh init <agent_id> <principal>"}'
            return 1
        fi
    fi
    
    local payload=$(get_template "$template" "$agent_id" "${@:2}")
    if [ $? -ne 0 ]; then
        echo "$payload"
        return 1
    fi
    
    # Check if agent has KYA entry, use create_mandate_with_kya if so
    local kya=$(jq -c --arg id "$agent_id" '.agents[] | select(.agent_id == $id and .status == "verified")' "$KYA_FILE" 2>/dev/null)
    if [ -n "$kya" ]; then
        create_mandate_with_kya "$payload"
    else
        create_mandate "$payload"
    fi
}

create_quick() {
    local action_type="$1"
    local agent_id="$2"
    local allowlist_csv="$3"
    local ttl_duration="$4"
    local amount_cap="$5"
    
    # Auto-detect agent_id if empty
    if [ -z "$agent_id" ]; then
        agent_id=$(get_default_agent)
        if [ -z "$agent_id" ]; then
            echo '{"error": "No agent_id provided. Register an agent first: mandate-ledger.sh init <agent_id> <principal>"}'
            return 1
        fi
    fi
    
    if [ -z "$action_type" ] || [ -z "$allowlist_csv" ] || [ -z "$ttl_duration" ]; then
        echo '{"error": "Usage: create-quick <action_type> <agent_id> <allowlist_csv> <ttl_duration> [amount_cap]"}'
        return 1
    fi
    
    local ttl=$(parse_ttl_duration "$ttl_duration")
    if [ $? -ne 0 ] || [ -z "$ttl" ]; then
        jq -n --arg error "Invalid TTL duration: $ttl_duration. Use e.g. 7d, 24h, 30m" '{error: $error}'
        return 1
    fi
    
    # Convert CSV to JSON array
    local allowlist=$(echo "$allowlist_csv" | jq -R 'split(",")')
    
    local payload
    if [ -n "$amount_cap" ]; then
        payload=$(jq -n \
            --arg type "$action_type" \
            --arg agent "$agent_id" \
            --argjson allow "$allowlist" \
            --arg ttl "$ttl" \
            --argjson cap "$amount_cap" \
            '{action_type: $type, agent_id: $agent, scope: {allowlist: $allow}, ttl: $ttl, amount_cap: $cap}')
    else
        payload=$(jq -n \
            --arg type "$action_type" \
            --arg agent "$agent_id" \
            --argjson allow "$allowlist" \
            --arg ttl "$ttl" \
            '{action_type: $type, agent_id: $agent, scope: {allowlist: $allow}, ttl: $ttl}')
    fi
    
    # Check if agent has KYA entry
    init_ledger
    local kya=$(jq -c --arg id "$agent_id" '.agents[] | select(.agent_id == $id and .status == "verified")' "$KYA_FILE" 2>/dev/null)
    if [ -n "$kya" ]; then
        create_mandate_with_kya "$payload"
    else
        create_mandate "$payload"
    fi
}

init_passport() {
    local agent_id="${2:-}"
    local principal="${3:-}"
    local scope="${4:-}"
    local provider="${5:-}"
    
    local mandate_count=0
    if [ -f "$LEDGER_FILE" ]; then
        mandate_count=$(jq '.mandates | length' "$LEDGER_FILE" 2>/dev/null || echo 0)
        if [ "$mandate_count" -gt 0 ] || [ -f "$AUDIT_FILE" ]; then
            # Already initialized
            init_ledger
            
            # If KYA args provided, register/update
            if [ -n "$agent_id" ] && [ -n "$principal" ]; then
                kya_register "$agent_id" "$principal" "$scope" "$provider" > /dev/null
                echo "Already initialized at $LEDGER_DIR/ ($mandate_count mandates)"
                echo "🪪 Registered agent: $agent_id (principal: $principal)"
                return 0
            fi
            
            # Check for existing registered agent
            local registered=$(jq -r '.agents[] | select(.status == "verified") | "\(.agent_id) (principal: \(.verified_principal))"' "$KYA_FILE" 2>/dev/null | head -1)
            if [ -n "$registered" ]; then
                echo "Already initialized at $LEDGER_DIR/ ($mandate_count mandates)"
                echo "🪪 Registered agent: $registered"
            else
                echo "Already initialized at $LEDGER_DIR/ ($mandate_count mandates)"
            fi
            return 0
        fi
    fi
    
    init_ledger
    
    # If KYA args provided, register agent
    if [ -n "$agent_id" ] && [ -n "$principal" ]; then
        kya_register "$agent_id" "$principal" "$scope" "$provider" > /dev/null
        echo "✅ Agent Passport initialized at $LEDGER_DIR/"
        echo "🪪 Agent registered: $agent_id (principal: $principal)"
    else
        echo "✅ Agent Passport initialized at $LEDGER_DIR/"
        echo ""
        echo "⚠️  No agent registered yet. Register your agent for full KYA tracking:"
        echo "  ./mandate-ledger.sh init agent:my-assistant \"Your Name\" \"assistant scope\" \"openclaw\""
    fi
    
    echo ""
    echo "Quick start:"
    echo "  # Use a template:"
    echo "  ./mandate-ledger.sh create-from-template dev-tools"
    echo ""
    echo "  # Or create manually:"
    echo "  ./mandate-ledger.sh create-quick system \"\" \"git *,npm *\" 7d"
    echo ""
    echo "  # Check if an action is allowed:"
    echo "  ./mandate-ledger.sh check-action agent:seb system \"git pull\""
    echo ""
    echo "Available templates: dev-tools, email-team, file-ops, web-research, safe-browsing, coding, email-assistant, read-only, full-auto"
    echo "Run: ./mandate-ledger.sh templates"
}

list_templates() {
    echo "Available templates:"
    echo ""
    echo "  dev-tools                     System commands (git, npm, docker, cargo, etc.)"
    echo "    Usage: create-from-template dev-tools <agent_id>"
    echo "    Deny: sudo, rm -rf /*, chmod 777  |  TTL: 30 days"
    echo ""
    echo "  email-team                    Internal email communication"
    echo "    Usage: create-from-template email-team <agent_id> <domain>"
    echo "    Rate: 50/day  |  TTL: 30 days"
    echo ""
    echo "  file-ops                      File management within a directory"
    echo "    Usage: create-from-template file-ops <agent_id> <path>"
    echo "    Deny: *.env, *.key, *.pem, .git  |  TTL: 30 days"
    echo ""
    echo "  web-research                  API access (GitHub, OpenAI, Anthropic)"
    echo "    Usage: create-from-template web-research <agent_id>"
    echo "    Rate: 200/hour  |  TTL: 30 days"
    echo ""
    echo "  safe-browsing                 Safer web/API browsing to trusted sites"
    echo "    Usage: create-from-template safe-browsing <agent_id>"
    echo "    Allow: google.com, wikipedia.org, github.com, stackoverflow.com"
    echo "    Rate: 30/hour  |  TTL: 24 hours"
    echo ""
    echo "  coding                        High-throughput coding command access"
    echo "    Usage: create-from-template coding <agent_id>"
    echo "    Allow: git, npm, node, python, pip, cargo, make, docker"
    echo "    Rate: 100/hour  |  TTL: 7 days"
    echo ""
    echo "  email-assistant               Broad email assistant communication"
    echo "    Usage: create-from-template email-assistant <agent_id>"
    echo "    Allow: all  |  Amount cap: 0"
    echo "    Rate: 20/hour  |  TTL: 24 hours"
    echo ""
    echo "  read-only                     Read/list oriented data operations"
    echo "    Usage: create-from-template read-only <agent_id>"
    echo "    Allow: read, list, cat, ls"
    echo "    Rate: 50/hour  |  TTL: 24 hours"
    echo ""
    echo "  full-auto                     Maximum automation scope"
    echo "    Usage: create-from-template full-auto <agent_id>"
    echo "    Allow: all"
    echo "    Rate: 200/hour  |  TTL: 1 day"
}

# Command dispatcher
if kill_switch_engaged && [ "${1:-}" != "unlock" ]; then
    echo "AGENT PASSPORT: KILL SWITCH ENGAGED. All operations denied. Run: mandate-ledger.sh unlock" >&2
    exit 1
fi

case "$1" in
    init)
        init_passport "$@"
        ;;
    templates)
        list_templates
        ;;
    create-from-template)
        create_from_template "$2" "$3" "$4" "$5"
        ;;
    create-quick)
        create_quick "$2" "$3" "$4" "$5" "$6"
        ;;
    create)
        create_mandate "$2"
        ;;
    create-with-kya)
        create_mandate_with_kya "$2"
        ;;
    get)
        get_mandate "$2"
        ;;
    list)
        list_mandates "$2"
        ;;
    revoke)
        revoke_mandate "$2" "$3"
        ;;
    check)
        # Legacy: check <agent> <merchant> <amount>
        # New:    check <agent> <action_type> <target> [amount]
        if [ "$#" -eq 4 ] && [[ "$3" =~ ^[0-9]+$ ]]; then
            # Legacy format: third arg is numeric amount
            check_mandate "$2" "$3" "$4"
        else
            # New format
            check_action "$2" "$3" "$4" "$5"
        fi
        ;;
    check-action)
        check_action "$2" "$3" "$4" "$5"
        ;;
    log|log-action)
        log_action "$2" "$3" "$4"
        ;;
    spend)
        spend "$2" "$3"
        ;;
    summary)
        summary
        ;;
    export)
        export_ledger
        ;;
    audit)
        audit_list "$2"
        ;;
    audit-mandate)
        audit_for_mandate "$2"
        ;;
    audit-summary)
        audit_summary "$2"
        ;;
    kya-register)
        kya_register "$2" "$3" "$4" "$5"
        ;;
    kya-get)
        kya_get "$2"
        ;;
    kya-list)
        kya_list
        ;;
    kya-revoke)
        kya_revoke "$2" "$3"
        ;;
    check-ssrf)
        check_ssrf "$2"
        ;;
    check-path)
        check_path "$2" "$3"
        ;;
    verify-webhook)
        verify_webhook "$2" "$3" "$4" "$5" "$6"
        ;;
    scan-skill)
        scan_skill "$2" "${@:3}"
        ;;
    check-injection)
        check_injection "$2" "${@:3}"
        ;;
    init-definitions)
        init_definitions
        ;;
    update-definitions)
        update_definitions "${@:2}"
        ;;
    definitions-status)
        definitions_status
        ;;
    kill)
        kill_ledger "${*:2}"
        ;;
    unlock)
        unlock_ledger
        ;;
    *)
        echo "Agent Passport - Local Mandate Ledger v2.3.2"
        echo "Consent-gating for ALL sensitive agent actions"
        echo ""
        echo "Usage: mandate-ledger.sh <command> [args]"
        echo ""
        echo "QUICK START:"
        echo "  init                                    Initialize Agent Passport"
        echo "  templates                               List available templates"
        echo "  create-from-template <t> <agent> [args] Create mandate from template"
        echo "  create-quick <type> <agent> <csv> <ttl> Create mandate with simple syntax"
        echo ""
        echo "ACTION CATEGORIES:"
        echo "  financial     - purchases, transfers, subscriptions"
        echo "  communication - emails, messages, posts"
        echo "  data          - file deletion, edits, database writes"
        echo "  system        - shell commands, installs, config changes"
        echo "  external_api  - third-party API calls with side effects"
        echo "  identity      - public actions 'as' the user"
        echo ""
        echo "MANDATE COMMANDS:"
        echo "  create <json>              Create mandate (include action_type)"
        echo "  create-with-kya <json>     Create mandate, auto-attach agent KYA"
        echo "  get <mandate_id>           Get mandate by ID"
        echo "  list [filter]              List mandates (all|active|revoked|<action_type>)"
        echo "  revoke <mandate_id> [why]  Revoke a mandate"
        echo ""
        echo "AUTHORIZATION:"
        echo "  check-action <agent> <type> <target> [amount]"
        echo "                             Check if action is authorized"
        echo "  check <agent> <merchant> <amount>"
        echo "                             Legacy: check financial action"
        echo "  log-action <mandate_id> <amount> [description]"
        echo "                             Log action against mandate"
        echo "  spend <mandate_id> <amount>"
        echo "                             Legacy: log financial spend"
        echo ""
        echo "AUDIT:"
        echo "  audit [limit]              Show recent audit entries"
        echo "  audit-mandate <id>         Show audit for specific mandate"
        echo "  audit-summary [since]      Summary by action type"
        echo "  summary                    Show overall ledger stats"
        echo "  export                     Export full ledger as JSON"
        echo ""
        echo "KYA (Know Your Agent):"
        echo "  kya-register <agent_id> <principal> <scope> [provider]"
        echo "  kya-get <agent_id>"
        echo "  kya-list"
        echo "  kya-revoke <agent_id> [why]"
        echo ""
        echo "SAFETY:"
        echo "  kill <reason>                           Engage kill switch and freeze execution"
        echo "  unlock                                  Disengage kill switch and resume execution"
        echo ""
        echo "SECURITY (v2.3.2):"
        echo "  check-ssrf <url>                        SSRF Shield: validate URL is safe to fetch"
        echo "  check-path <path> [safe_root]           Path Traversal Guard: validate file path"
        echo "  verify-webhook <origin> <domains_csv>   Webhook Origin Verification (+ optional HMAC)"
        echo "    [hmac_secret] [hmac_sig] [hmac_body]"
        echo "  scan-skill <path> [--json] [--strict]   Skill Scanner: static analysis for skill files"
        echo "  check-injection \"<content>\"              Injection Shield: detect prompt injection"
        echo "    [--source <label>] [--json] [--strict]"
        echo "  init-definitions                        Seed threat-definitions.json in ledger"
        echo "  update-definitions [--force] [--offline]"
        echo "                                         Refresh definitions (Pro API or bundled copy)"
        echo "  definitions-status                      Show definitions version and pattern counts"
        exit 1
        ;;
esac
