#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Model Switchboard v3.0 — Production-Grade Model Configuration
# Never crashes the gateway. Always validates. Always backs up.
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
BACKUP_DIR="$HOME/.openclaw/model-backups"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VALIDATE="$SKILL_DIR/scripts/validate.py"
REDUNDANCY="$SKILL_DIR/scripts/redundancy.py"
MAX_BACKUPS="${SWITCHBOARD_MAX_BACKUPS:-30}"

# Ensure backup/log directory exists early
mkdir -p "$BACKUP_DIR" 2>/dev/null
chmod 700 "$BACKUP_DIR" 2>/dev/null

# ── Colors & Output ────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}ℹ${NC}  $1"; }
log_ok()      { echo -e "${GREEN}✅${NC} $1"; }
log_warn()    { echo -e "${YELLOW}⚠️${NC}  $1"; }
log_error()   { echo -e "${RED}❌${NC} $1"; }
log_header()  { echo -e "\n${CYAN}${BOLD}$1${NC}"; }
log_dim()     { echo -e "${DIM}$1${NC}"; }

# ── Pre-flight Checks ─────────────────────────────────────────
check_config_exists() {
    if [ ! -f "$OPENCLAW_CONFIG" ]; then
        log_error "Config not found: $OPENCLAW_CONFIG"
        log_info "Run 'openclaw onboard' to create initial config"
        exit 1
    fi
}

check_cli_available() {
    if ! command -v openclaw &>/dev/null; then
        log_error "openclaw CLI not found in PATH"
        log_info "Install: npm install -g openclaw"
        return 1
    fi
    return 0
}

check_python() {
    if ! command -v python3 &>/dev/null; then
        log_error "Python 3 required but not found"
        exit 1
    fi
}

# ── Validation ─────────────────────────────────────────────────
run_validation() {
    local cmd="$1"
    shift
    python3 "$VALIDATE" "$cmd" "$@" 2>>"$BACKUP_DIR/switchboard-stderr.log"
}

validate_model_for_role() {
    local model="$1"
    local role="$2"

    # FAIL-CLOSED: any parse/validation failure = reject
    # This is a safety tool. We never allow through on error.

    # Step 1: Format validation
    local ref_result ref_exit
    ref_result=$(run_validation ref "$model" 2>/dev/null) || ref_exit=$?
    if [ -z "$ref_result" ]; then
        log_error "Format validation failed (validator returned no output)"
        return 1
    fi

    local ref_valid
    ref_valid=$(echo "$ref_result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('valid', False))" 2>/dev/null) || ref_valid=""

    if [ "$ref_valid" != "True" ]; then
        local ref_msg
        ref_msg=$(echo "$ref_result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message', 'Invalid format'))" 2>/dev/null) || ref_msg="Validation parse error"
        log_error "Format error: $ref_msg"
        return 1
    fi

    # Step 2: Role compatibility
    local role_result role_exit
    role_result=$(run_validation role "$model" "$role" 2>/dev/null) || role_exit=$?
    if [ -z "$role_result" ]; then
        log_error "Role validation failed (empty response from validator)"
        return 1
    fi

    local role_valid
    role_valid=$(echo "$role_result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('valid', False))" 2>/dev/null) || role_valid=""

    # FAIL-CLOSED: anything other than explicit "True" is a rejection
    if [ "$role_valid" != "True" ]; then
        local role_msg
        role_msg=$(echo "$role_result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message', 'Incompatible or validation error'))" 2>/dev/null) || role_msg="Role validation failed"
        log_error "Role validation failed: $role_msg"
        return 1
    fi

    # Warnings (valid but not in registry — still allowed)
    local role_msg
    role_msg=$(echo "$role_result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message', ''))" 2>/dev/null) || role_msg=""
    if echo "$role_msg" | grep -qi "caution\|warning\|not in registry"; then
        log_warn "$role_msg"
    fi

    return 0
}

# ── Backup Engine ──────────────────────────────────────────────
backup_config() {
    mkdir -p "$BACKUP_DIR"
    chmod 700 "$BACKUP_DIR"
    local ts
    ts=$(date +%Y%m%d-%H%M%S)-$$
    local backup_file="$BACKUP_DIR/openclaw-$ts.json"

    # Validate source is valid JSON before backing up
    if ! SWITCHBOARD_CONFIG="$OPENCLAW_CONFIG" python3 -c "import json,os; json.load(open(os.environ['SWITCHBOARD_CONFIG']))" 2>/dev/null; then
        log_warn "Current config is not valid JSON — backing up anyway for recovery"
    fi

    cp "$OPENCLAW_CONFIG" "$backup_file"
    chmod 600 "$backup_file"
    log_ok "Config backed up: ${DIM}$backup_file${NC}"

    # Prune old backups (keep MAX_BACKUPS) with lockfile to prevent races
    local LOCKFILE="$BACKUP_DIR/.switchboard.lock"
    (
        flock -n 9 || { log_warn "Backup lock held — skipping prune"; return; }
        local count
        count=$(ls -1 "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | wc -l | tr -d ' ')
        if [ "$count" -gt "$MAX_BACKUPS" ]; then
            ls -t "$BACKUP_DIR"/openclaw-*.json | tail -n +"$((MAX_BACKUPS + 1))" | xargs rm -f 2>/dev/null || true
            log_dim "Pruned old backups (keeping last $MAX_BACKUPS)"
        fi
    ) 9>"$LOCKFILE"

    echo "$backup_file"
}

# ── Status ─────────────────────────────────────────────────────
show_status() {
    check_config_exists
    check_python

    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║         ${BOLD}🔀 MODEL SWITCHBOARD — STATUS${NC}${CYAN}                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Try CLI first, fall back to direct config read
    if check_cli_available 2>/dev/null; then
        local cli_output
        cli_output=$(openclaw models status 2>&1) || true
        if [ -n "$cli_output" ] && ! echo "$cli_output" | grep -qi "error\|cannot find module"; then
            echo "$cli_output"
            echo ""
        else
            log_warn "CLI unavailable — reading config directly"
            echo ""
            _show_status_from_config
        fi
    else
        _show_status_from_config
    fi

    # Show validation issues
    local issues
    issues=$(run_validation config 2>&1) || true
    local issue_count
    issue_count=$(echo "$issues" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('issues',[])))" 2>/dev/null || echo "0")

    if [ "$issue_count" -gt "0" ]; then
        log_header "⚠️  Config Issues"
        echo "$issues" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i in data.get('issues', []):
    level = '🔴' if i['level'] == 'error' else '🟡'
    print(f'  {level} [{i[\"field\"]}] {i[\"message\"]}')
" 2>/dev/null
        echo ""
    fi

    # Backup info
    local backup_count=0
    if [ -d "$BACKUP_DIR" ]; then
        backup_count=$(ls -1 "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | wc -l | tr -d ' ')
    fi
    local latest_backup="none"
    if [ "$backup_count" -gt 0 ]; then
        latest_backup=$(ls -t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | head -1 | xargs basename 2>/dev/null)
    fi

    echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  Backups: ${GREEN}${BOLD}$backup_count${NC} ${DIM}(latest: $latest_backup)${NC}"
    echo -e "  Config:  ${DIM}$OPENCLAW_CONFIG${NC}"
    echo ""
}

_show_status_from_config() {
    SWITCHBOARD_CONFIG="$OPENCLAW_CONFIG" python3 -c "
import json, sys, os
try:
    with open(os.environ['SWITCHBOARD_CONFIG']) as f:
        cfg = json.load(f)
except Exception as e:
    print(f'  Error reading config: {e}')
    sys.exit(0)

agents = cfg.get('agents', {}).get('defaults', {})
model = agents.get('model', {})
image = agents.get('imageModel', {})

# Primary
if isinstance(model, str):
    print(f'  \033[1mPrimary LLM:\033[0m      \033[34m{model}\033[0m')
elif isinstance(model, dict):
    p = model.get('primary', '(not set)')
    print(f'  \033[1mPrimary LLM:\033[0m      \033[34m{p}\033[0m')
    fb = model.get('fallbacks', [])
    if fb:
        print(f'  \033[1mFallbacks:\033[0m        \033[33m{\" → \".join(fb)}\033[0m')
    else:
        print(f'  \033[1mFallbacks:\033[0m        \033[2m(none)\033[0m')
else:
    print(f'  \033[1mPrimary LLM:\033[0m      \033[31m(not set)\033[0m')

# Image
if isinstance(image, str):
    print(f'  \033[1mImage Model:\033[0m      \033[35m{image}\033[0m')
elif isinstance(image, dict):
    ip = image.get('primary', '(not set)')
    print(f'  \033[1mImage Model:\033[0m      \033[35m{ip}\033[0m')
    ifb = image.get('fallbacks', [])
    if ifb:
        print(f'  \033[1mImage Fallbacks:\033[0m  \033[33m{\" → \".join(ifb)}\033[0m')
else:
    print(f'  \033[1mImage Model:\033[0m      \033[2m(not set)\033[0m')

# Allowlist
models_list = agents.get('models', {})
if models_list:
    print(f'  \033[1mAllowlist:\033[0m        {len(models_list)} models')
    for m, v in models_list.items():
        alias = v.get('alias', '') if isinstance(v, dict) else ''
        suffix = f' ({alias})' if alias else ''
        print(f'    • {m}{suffix}')
" 2>/dev/null || log_error "Could not parse config"
}

# ── Set Primary Model ──────────────────────────────────────────
set_primary() {
    local model="$1"
    check_config_exists

    log_header "Setting Primary LLM"
    log_info "Model: $model"

    # Validate
    validate_model_for_role "$model" "primary" || return 1

    # Dry run
    log_info "Dry run:"
    run_validation dry-run set-primary "$model" primary 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k, v in d.get('current', {}).items():
    print(f'  \033[31m- {k}: {v}\033[0m')
for k, v in d.get('proposed', {}).items():
    print(f'  \033[32m+ {k}: {v}\033[0m')
" 2>/dev/null

    # Backup (capture exact path for rollback)
    local this_backup
    this_backup=$(backup_config 2>/dev/null | tail -1)

    # Apply
    if check_cli_available 2>/dev/null; then
        if openclaw models set "$model" 2>&1; then
            log_ok "Primary model set to: ${BOLD}$model${NC}"
            _verify_health
        else
            log_error "CLI command failed. Restoring from this operation's backup..."
            if [ -n "$this_backup" ] && [ -f "$this_backup" ]; then
                restore_backup "$this_backup"
            else
                restore_backup "latest"
            fi
        fi
    else
        log_error "openclaw CLI not available — cannot apply change safely"
        log_info "Run manually: openclaw models set $model"
        return 1
    fi
}

# ── Set Image Model ────────────────────────────────────────────
set_image() {
    local model="$1"
    check_config_exists

    log_header "Setting Image Model"
    log_info "Model: $model"

    validate_model_for_role "$model" "image" || return 1

    # Dry run
    log_info "Dry run:"
    run_validation dry-run set-image "$model" image 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k, v in d.get('current', {}).items():
    print(f'  \033[31m- {k}: {v}\033[0m')
for k, v in d.get('proposed', {}).items():
    print(f'  \033[32m+ {k}: {v}\033[0m')
" 2>/dev/null

    local this_backup
    this_backup=$(backup_config 2>/dev/null | tail -1)

    if check_cli_available 2>/dev/null; then
        if openclaw models set-image "$model" 2>&1; then
            log_ok "Image model set to: ${BOLD}$model${NC}"
            _verify_health
        else
            log_error "CLI command failed. Restoring from this operation's backup..."
            if [ -n "$this_backup" ] && [ -f "$this_backup" ]; then
                restore_backup "$this_backup"
            else
                restore_backup "latest"
            fi
        fi
    else
        log_error "openclaw CLI not available"
        return 1
    fi
}

# ── Fallback Management ───────────────────────────────────────
add_fallback() {
    local model="$1"
    check_config_exists

    log_header "Adding LLM Fallback"
    validate_model_for_role "$model" "fallback" || return 1
    local this_backup
    this_backup=$(backup_config 2>/dev/null | tail -1)

    if check_cli_available 2>/dev/null; then
        if openclaw models fallbacks add "$model" 2>&1; then
            log_ok "Fallback added: ${BOLD}$model${NC}"
            _verify_health
        else
            log_error "Failed to add fallback. Restoring..."
            [ -n "$this_backup" ] && [ -f "$this_backup" ] && restore_backup "$this_backup"
        fi
    else
        log_error "openclaw CLI not available"
        return 1
    fi
}

remove_fallback() {
    local model="$1"
    check_config_exists
    local this_backup
    this_backup=$(backup_config 2>/dev/null | tail -1)

    if check_cli_available 2>/dev/null; then
        if openclaw models fallbacks remove "$model" 2>&1; then
            log_ok "Fallback removed: $model"
            _verify_health
        else
            log_error "Failed to remove fallback. Restoring..."
            [ -n "$this_backup" ] && [ -f "$this_backup" ] && restore_backup "$this_backup"
        fi
    else
        log_error "openclaw CLI not available"
        return 1
    fi
}

add_image_fallback() {
    local model="$1"
    check_config_exists

    log_header "Adding Image Fallback"
    validate_model_for_role "$model" "image" || return 1
    local this_backup
    this_backup=$(backup_config 2>/dev/null | tail -1)

    if check_cli_available 2>/dev/null; then
        if openclaw models image-fallbacks add "$model" 2>&1; then
            log_ok "Image fallback added: ${BOLD}$model${NC}"
            _verify_health
        else
            log_error "Failed to add image fallback. Restoring..."
            [ -n "$this_backup" ] && [ -f "$this_backup" ] && restore_backup "$this_backup"
        fi
    else
        log_error "openclaw CLI not available"
        return 1
    fi
}

remove_image_fallback() {
    local model="$1"
    check_config_exists
    local this_backup
    this_backup=$(backup_config 2>/dev/null | tail -1)

    if check_cli_available 2>/dev/null; then
        if openclaw models image-fallbacks remove "$model" 2>&1; then
            log_ok "Image fallback removed: $model"
            _verify_health
        else
            log_error "Failed to remove image fallback. Restoring..."
            [ -n "$this_backup" ] && [ -f "$this_backup" ] && restore_backup "$this_backup"
        fi
    else
        log_error "openclaw CLI not available"
        return 1
    fi
}

# ── Health Check ───────────────────────────────────────────────
_verify_health() {
    log_info "Verifying gateway health..."
    sleep 2
    if check_cli_available 2>/dev/null; then
        if openclaw status &>/dev/null; then
            log_ok "Gateway is healthy!"
        else
            log_warn "Gateway may need restart: openclaw gateway restart"
        fi
    fi
}

check_health() {
    log_header "Gateway Health Check"

    if ! check_cli_available 2>/dev/null; then
        log_error "openclaw CLI not available"
        return 1
    fi

    # Gateway status
    if openclaw status &>/dev/null; then
        log_ok "Gateway: running"
    else
        log_error "Gateway: not responding"
    fi

    # Provider auth
    log_info "Provider auth status:"
    if openclaw models status --plain 2>/dev/null; then
        log_ok "Models: configured"
    else
        log_warn "Cannot query model status"
    fi
}

# ── Discovery ──────────────────────────────────────────────────
discover_models() {
    log_header "Model Discovery"

    if check_cli_available 2>/dev/null; then
        log_info "Querying available models..."
        openclaw models list --all 2>&1 || {
            log_warn "CLI discovery failed — showing registry models"
            _show_registry_models
        }
    else
        log_warn "CLI unavailable — showing registry models"
        _show_registry_models
    fi
}

_show_registry_models() {
    SWITCHBOARD_REGISTRY="$SKILL_DIR/model-registry.json" python3 -c "
import json, os
with open(os.environ['SWITCHBOARD_REGISTRY']) as f:
    reg = json.load(f)
for mid, m in sorted(reg.get('models', {}).items()):
    if m.get('blocked'):
        continue
    caps = ', '.join(m.get('capabilities', []))
    cost = m.get('costTier', '?')
    print(f'  {mid:<40} [{cost}] {caps}')
" 2>/dev/null
}

# ── Recommendations ────────────────────────────────────────────
recommend() {
    log_header "Model Recommendations"
    check_python

    run_validation recommend 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for role_id, info in data.items():
    print(f'\n  \033[1m{info[\"role\"]}\033[0m')
    for c in info.get('candidates', []):
        auth = '\033[32m✓\033[0m' if c['hasAuth'] else '\033[31m✗\033[0m'
        print(f'    {auth} {c[\"model\"]:<40} [{c[\"costTier\"]}]')
    if not info.get('candidates'):
        print('    \033[2m(no compatible models found)\033[0m')
" 2>/dev/null || log_error "Recommendation engine failed"
}

# ── Dry Run ────────────────────────────────────────────────────
dry_run() {
    local action="${1:?Usage: switchboard.sh dry-run <action> <model>}"
    local model="${2:?Usage: switchboard.sh dry-run <action> <model>}"

    log_header "Dry Run — $action $model"
    check_python

    # Validate first
    local role="primary"
    case "$action" in
        set-primary)     role="primary" ;;
        set-image)       role="image" ;;
        add-fallback)    role="fallback" ;;
        add-image-fallback) role="image" ;;
    esac

    validate_model_for_role "$model" "$role" || return 1

    # Show diff
    run_validation dry-run "$action" "$model" "$role" 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
print()
if d.get('wouldChange'):
    print('  \033[1mChanges:\033[0m')
    for k, v in d.get('current', {}).items():
        print(f'    \033[31m- {k}: {json.dumps(v)}\033[0m')
    for k, v in d.get('proposed', {}).items():
        print(f'    \033[32m+ {k}: {json.dumps(v)}\033[0m')
else:
    print('  \033[2mNo changes — already set to this value\033[0m')
print()
print('  \033[2mThis is a dry run. No changes were made.\033[0m')
" 2>/dev/null
}

# ── Export / Import ────────────────────────────────────────────
export_config() {
    check_config_exists
    check_python

    local output="${1:-model-config-export.json}"

    SWITCHBOARD_CONFIG="$OPENCLAW_CONFIG" SWITCHBOARD_EXPORT="$output" python3 -c "
import json, os, datetime
config_path = os.environ['SWITCHBOARD_CONFIG']
export_path = os.environ['SWITCHBOARD_EXPORT']
with open(config_path) as f:
    cfg = json.load(f)
agents = cfg.get('agents', {}).get('defaults', {})
export_data = {
    'version': '1.0',
    'exportedAt': datetime.datetime.now().isoformat(),
    'model': agents.get('model', {}),
    'imageModel': agents.get('imageModel', {}),
    'models': agents.get('models', {}),
}
with open(export_path, 'w') as f:
    json.dump(export_data, f, indent=2)
print(f'Exported to: {export_path}')
" 2>/dev/null

    log_ok "Model config exported to: $output"
}

import_config() {
    local input="${1:?Usage: switchboard.sh import <file>}"
    check_config_exists
    check_python

    if [ ! -f "$input" ]; then
        log_error "File not found: $input"
        return 1
    fi

    log_header "Importing Model Config"
    log_info "Source: $input"

    # Validate import file
    SWITCHBOARD_IMPORT_FILE="$input" SWITCHBOARD_CONFIG="$OPENCLAW_CONFIG" python3 -c "
import json, sys, os
import_file = os.environ['SWITCHBOARD_IMPORT_FILE']
with open(import_file) as f:
    data = json.load(f)
if 'model' not in data and 'imageModel' not in data:
    print('ERROR: Invalid export file — missing model configuration')
    sys.exit(1)
print(f'  Version: {data.get(\"version\", \"unknown\")}')
print(f'  Exported: {data.get(\"exportedAt\", \"unknown\")}')
model = data.get('model', {})
if isinstance(model, dict):
    print(f'  Primary: {model.get(\"primary\", \"(not set)\")}')
    print(f'  Fallbacks: {len(model.get(\"fallbacks\", []))}')
image = data.get('imageModel', {})
if isinstance(image, dict):
    print(f'  Image: {image.get(\"primary\", \"(not set)\")}')
models = data.get('models', {})
print(f'  Allowlist: {len(models)} models')
" 2>/dev/null || { log_error "Invalid import file"; return 1; }

    # Validate all model assignments in import before applying
    log_info "Validating imported model assignments..."
    local import_valid=true

    # Extract and validate primary model
    local imp_primary
    imp_primary=$(SWITCHBOARD_IMPORT_FILE="$input" python3 -c "
import json, os
with open(os.environ['SWITCHBOARD_IMPORT_FILE']) as f:
    d = json.load(f)
m = d.get('model', {})
print(m.get('primary', '') if isinstance(m, dict) else (m if isinstance(m, str) else ''))
" 2>/dev/null)
    if [ -n "$imp_primary" ]; then
        if ! validate_model_for_role "$imp_primary" "primary"; then
            log_error "Import blocked: primary model '$imp_primary' failed validation"
            import_valid=false
        fi
    fi

    # Extract and validate image model
    local imp_image
    imp_image=$(SWITCHBOARD_IMPORT_FILE="$input" python3 -c "
import json, os
with open(os.environ['SWITCHBOARD_IMPORT_FILE']) as f:
    d = json.load(f)
m = d.get('imageModel', {})
print(m.get('primary', '') if isinstance(m, dict) else (m if isinstance(m, str) else ''))
" 2>/dev/null)
    if [ -n "$imp_image" ]; then
        if ! validate_model_for_role "$imp_image" "image"; then
            log_error "Import blocked: image model '$imp_image' failed validation"
            import_valid=false
        fi
    fi

    if [ "$import_valid" != "true" ]; then
        log_error "Import aborted — one or more model assignments failed validation"
        return 1
    fi

    backup_config > /dev/null
    log_info "Applying imported config..."

    SWITCHBOARD_IMPORT_FILE="$input" SWITCHBOARD_CONFIG="$OPENCLAW_CONFIG" SWITCHBOARD_VALIDATE="$VALIDATE" python3 -c "
import json, os, sys, tempfile
config_path = os.environ['SWITCHBOARD_CONFIG']
import_file = os.environ['SWITCHBOARD_IMPORT_FILE']

with open(config_path) as f:
    cfg = json.load(f)
with open(import_file) as f:
    imp = json.load(f)

if 'agents' not in cfg:
    cfg['agents'] = {}
if 'defaults' not in cfg['agents']:
    cfg['agents']['defaults'] = {}

if 'model' in imp:
    cfg['agents']['defaults']['model'] = imp['model']
if 'imageModel' in imp:
    cfg['agents']['defaults']['imageModel'] = imp['imageModel']
if 'models' in imp:
    cfg['agents']['defaults']['models'] = imp['models']

# Atomic write: temp file → validate JSON + schema → rename
fd, tmp = tempfile.mkstemp(suffix='.json', dir=os.path.dirname(config_path))
with os.fdopen(fd, 'w') as f:
    json.dump(cfg, f, indent=2)
# Validate the temp file is valid JSON
with open(tmp) as vf:
    validated = json.load(vf)
# Schema validation before committing
sys.path.insert(0, os.path.dirname(os.path.realpath(os.environ['SWITCHBOARD_VALIDATE'])))
try:
    from validate import validate_config_schema
    issues = validate_config_schema(validated)
    errors = [i for i in issues if i['level'] == 'error']
    if errors:
        os.unlink(tmp)
        for e in errors:
            print('VALIDATION ERROR: ' + e['message'], file=sys.stderr)
        print('VALIDATION_FAILED')
        sys.exit(1)
except ImportError:
    pass  # validate.py not importable, skip schema check
os.rename(tmp, config_path)
os.chmod(config_path, 0o600)
print('OK')
" 2>/dev/null || { log_error "Import failed — config unchanged"; return 1; }

    log_ok "Model config imported successfully"
    log_info "Restart gateway: openclaw gateway restart"
}

# ── Backup Management ─────────────────────────────────────────
list_backups() {
    log_header "Config Backups"
    echo ""

    if ! ls "$BACKUP_DIR"/openclaw-*.json &>/dev/null 2>&1; then
        log_warn "No backups found in $BACKUP_DIR"
        return
    fi

    local count
    count=$(ls -1 "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | wc -l | tr -d ' ')
    echo -e "  ${BOLD}Total: $count backups${NC} ${DIM}(max retention: $MAX_BACKUPS)${NC}"
    echo ""

    ls -lht "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | head -20 | while IFS= read -r line; do
        echo "  $line"
    done

    if [ "$count" -gt 20 ]; then
        echo -e "\n  ${DIM}... and $((count - 20)) more${NC}"
    fi
}

restore_backup() {
    local target="$1"

    if [ "$target" = "latest" ]; then
        target=$(ls -t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | head -1)
        if [ -z "$target" ]; then
            log_error "No backups found!"
            return 1
        fi
    fi

    # Resolve path
    if [ ! -f "$target" ]; then
        if [ -f "$BACKUP_DIR/$target" ]; then
            target="$BACKUP_DIR/$target"
        else
            log_error "Backup not found: $target"
            log_info "Run: $0 list-backups"
            return 1
        fi
    fi

    # Validate backup is valid JSON
    if ! SWITCHBOARD_TARGET="$target" python3 -c "import json,os; json.load(open(os.environ['SWITCHBOARD_TARGET']))" 2>/dev/null; then
        log_error "Backup file is not valid JSON: $target"
        return 1
    fi

    log_header "Restoring Config"
    log_info "From: $target"

    # Save current broken config for forensics
    mkdir -p "$BACKUP_DIR"
    cp "$OPENCLAW_CONFIG" "$BACKUP_DIR/pre-restore-$(date +%Y%m%d-%H%M%S).json" 2>/dev/null || true

    # Atomic restore
    local tmp
    tmp=$(mktemp "${OPENCLAW_CONFIG}.tmp.XXXXXX")
    cp "$target" "$tmp"
    mv "$tmp" "$OPENCLAW_CONFIG"
    chmod 600 "$OPENCLAW_CONFIG"

    log_ok "Config restored from: $(basename "$target")"
    log_info "Restart gateway: ${BOLD}openclaw gateway restart${NC}"
}

# ── Redundancy Engine ──────────────────────────────────────────
redundancy_report() {
    check_python
    log_header "Redundancy Assessment"
    python3 "$REDUNDANCY" report "${1:-3}" 2>/dev/null || log_error "Redundancy engine failed"
}

redundancy_deploy() {
    local min_depth="${1:-3}"
    check_config_exists
    check_python

    log_header "Generating ${min_depth}-Deep Redundant Config"

    local deploy_json
    deploy_json=$(python3 "$REDUNDANCY" deploy "$min_depth" 2>/dev/null)

    if [ -z "$deploy_json" ]; then
        log_error "Redundancy engine produced no output"
        return 1
    fi

    # Check for error
    if echo "$deploy_json" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if 'error' not in d else 1)" 2>/dev/null; then
        log_info "Preview of generated config:"
        echo "$deploy_json" | python3 -m json.tool 2>/dev/null
        echo ""
        log_info "To apply this config, run:"
        echo "  switchboard.sh redundancy-apply $min_depth"
    else
        local err_msg
        err_msg=$(echo "$deploy_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('error','Unknown error'))" 2>/dev/null)
        log_error "$err_msg"
        return 1
    fi
}

redundancy_apply() {
    local min_depth="${1:-3}"
    check_config_exists
    check_python

    log_header "Applying ${min_depth}-Deep Redundant Config"

    local deploy_json
    deploy_json=$(python3 "$REDUNDANCY" deploy "$min_depth" 2>/dev/null)

    if [ -z "$deploy_json" ] || echo "$deploy_json" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(1 if 'error' in d else 0)" 2>/dev/null; then
        log_error "Cannot generate valid redundant config"
        return 1
    fi

    # Backup first
    local this_backup
    this_backup=$(backup_config 2>/dev/null | tail -1)

    # Merge into existing config using atomic write
    SWITCHBOARD_CONFIG="$OPENCLAW_CONFIG" SWITCHBOARD_DEPLOY="$deploy_json" python3 -c "
import json, os, tempfile

config_path = os.environ['SWITCHBOARD_CONFIG']
deploy_data = json.loads(os.environ['SWITCHBOARD_DEPLOY'])

with open(config_path) as f:
    cfg = json.load(f)

# Deep merge: only update agents.defaults model fields
if 'agents' not in cfg:
    cfg['agents'] = {}
if 'defaults' not in cfg['agents']:
    cfg['agents']['defaults'] = {}

deploy_defaults = deploy_data.get('agents', {}).get('defaults', {})

if 'model' in deploy_defaults:
    cfg['agents']['defaults']['model'] = deploy_defaults['model']
if 'imageModel' in deploy_defaults:
    cfg['agents']['defaults']['imageModel'] = deploy_defaults['imageModel']
if 'models' in deploy_defaults:
    # Merge allowlist (don't overwrite existing entries)
    existing = cfg['agents']['defaults'].get('models', {}) or {}
    for k, v in deploy_defaults['models'].items():
        if k not in existing:
            existing[k] = v
    cfg['agents']['defaults']['models'] = existing

# Atomic write
fd, tmp = tempfile.mkstemp(suffix='.json', dir=os.path.dirname(config_path))
with os.fdopen(fd, 'w') as f:
    json.dump(cfg, f, indent=2)
json.load(open(tmp))  # Validate
os.rename(tmp, config_path)
os.chmod(config_path, 0o600)
print('OK')
" 2>/dev/null

    if [ $? -eq 0 ]; then
        log_ok "Redundant config applied successfully!"
        log_info "Run 'openclaw gateway restart' to activate"
        log_info "Run 'switchboard.sh status' to verify"

        # Show what was deployed
        python3 "$REDUNDANCY" report "$min_depth" 2>/dev/null
    else
        log_error "Failed to apply config. Restoring backup..."
        if [ -n "$this_backup" ] && [ -f "$this_backup" ]; then
            restore_backup "$this_backup"
        fi
        return 1
    fi
}

# ── Cron Model Validation ──────────────────────────────────
validate_cron_models() {
    check_python
    log_header "Validating Cron Job Models"
    run_validation validate-cron-models 2>&1 | python3 -c "
import sys, json
data = json.load(sys.stdin)
issues = data.get('issues', [])
if not issues:
    print('  ✅ All cron job models are valid')
else:
    for i in issues:
        level = '🔴' if i.get('level') == 'error' else '🟡'
        print(f'  {level} Job \"{i.get(\"job\", \"?\")}\" — {i.get(\"message\", \"unknown issue\")}')
print(f'\n  Total jobs checked: {data.get(\"totalJobs\", 0)}')
print(f'  Issues found: {len(issues)}')
" 2>/dev/null || log_error "Cron model validation failed"
}

# ── Canvas UI Data ─────────────────────────────────────────────
generate_ui_data() {
    check_python
    run_validation status 2>/dev/null
}

# ── Main Router ────────────────────────────────────────────────
show_help() {
    echo ""
    echo -e "${CYAN}${BOLD}🔀 Model Switchboard v3.0${NC}"
    echo -e "${DIM}Safe AI Model Configuration for OpenClaw${NC}"
    echo ""
    echo -e "${BOLD}USAGE${NC}"
    echo "  switchboard.sh <command> [args]"
    echo ""
    echo -e "${BOLD}MODEL ASSIGNMENT${NC}"
    echo "  status                    Show current model assignments"
    echo "  set-primary <model>       Set primary LLM"
    echo "  set-image <model>         Set image/vision model"
    echo "  add-fallback <model>      Add LLM fallback"
    echo "  remove-fallback <model>   Remove LLM fallback"
    echo "  add-image-fallback <m>    Add image model fallback"
    echo "  remove-image-fallback <m> Remove image model fallback"
    echo ""
    echo -e "${BOLD}DISCOVERY & RECOMMENDATIONS${NC}"
    echo "  discover                  List all available models"
    echo "  recommend                 Suggest optimal assignments"
    echo "  dry-run <action> <model>  Preview changes without applying"
    echo ""
    echo -e "${BOLD}BACKUP & RESTORE${NC}"
    echo "  backup                    Backup current config"
    echo "  list-backups              List available backups"
    echo "  restore <file|latest>     Restore from backup"
    echo ""
    echo -e "${BOLD}IMPORT / EXPORT${NC}"
    echo "  export [file]             Export model config as JSON"
    echo "  import <file>             Import model config from JSON"
    echo ""
    echo -e "${BOLD}REDUNDANCY${NC}"
    echo "  redundancy [depth]        Assess current redundancy (default: 3)"
    echo "  redundancy-deploy [depth] Preview redundant config"
    echo "  redundancy-apply [depth]  Apply redundant config to gateway"
    echo ""
    echo -e "${BOLD}DIAGNOSTICS${NC}"
    echo "  health                    Check gateway & provider status"
    echo "  validate <model> <role>   Test model-role compatibility"
    echo "  validate-cron-models      Validate models used in cron jobs"
    echo "  ui                        Generate Canvas UI data (JSON)"
    echo ""
    echo -e "${BOLD}MODEL FORMAT${NC}"
    echo "  provider/model-name       e.g., anthropic/claude-opus-4-6"
    echo ""
    echo -e "${BOLD}GETTING STARTED${NC}"
    echo "  setup                     First-time setup wizard"
    echo "  init                      Alias for setup"
    echo ""
    echo -e "${BOLD}EXAMPLES${NC}"
    echo "  switchboard.sh set-primary anthropic/claude-opus-4-6"
    echo "  switchboard.sh set-image google/gemini-3-pro-preview"
    echo "  switchboard.sh dry-run set-primary openai/gpt-5.2"
    echo "  switchboard.sh restore latest"
    echo ""
}

case "${1:-}" in
    setup|init)          [ -f "$SKILL_DIR/scripts/setup.sh" ] || { log_error "setup.sh not found"; exit 1; }; bash "$SKILL_DIR/scripts/setup.sh" ;;
    status)              show_status ;;
    set-primary)         set_primary "${2:?Model required. Usage: switchboard.sh set-primary provider/model}" ;;
    set-image)           set_image "${2:?Model required. Usage: switchboard.sh set-image provider/model}" ;;
    add-fallback)        add_fallback "${2:?Model required}" ;;
    remove-fallback)     remove_fallback "${2:?Model required}" ;;
    add-image-fallback)  add_image_fallback "${2:?Model required}" ;;
    remove-image-fallback) remove_image_fallback "${2:?Model required}" ;;
    discover)            discover_models ;;
    recommend)           recommend ;;
    dry-run)             dry_run "${2:-}" "${3:-}" ;;
    redundancy)          redundancy_report "${2:-3}" ;;
    redundancy-deploy)   redundancy_deploy "${2:-3}" ;;
    redundancy-apply)    redundancy_apply "${2:-3}" ;;
    health)              check_health ;;
    validate)            validate_model_for_role "${2:?Model required}" "${3:-primary}" ;;
    backup)              backup_config ;;
    list-backups)        list_backups ;;
    restore)             restore_backup "${2:?Target required. Use 'latest' or a filename}" ;;
    export)              export_config "${2:-model-config-export.json}" ;;
    import)              import_config "${2:?File required}" ;;
    validate-cron-models) validate_cron_models ;;
    ui)                  generate_ui_data ;;
    help|--help|-h)      show_help ;;
    *)                   show_help ;;
esac
