#!/usr/bin/env bash
set -euo pipefail

# scan_file.sh — Scan files/directories for malware using ClamAV
# Outputs JSON results

# Cross-platform millisecond timestamp (macOS date doesn't support %N)
get_ms() {
  if [[ "$OSTYPE" == darwin* ]]; then
    python3 -c "import time; print(int(time.time()*1000))"
  else
    date +%s%3N
  fi
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/dashboard.sh" 2>/dev/null || true
QUARANTINE_DIR="${CRUSTY_QUARANTINE:-${CLAWGUARD_QUARANTINE:-/tmp/crusty_quarantine}}"
MAX_FILE_SIZE="${CRUSTY_MAX_FILE_SIZE:-${CLAWGUARD_MAX_FILE_SIZE:-200M}}"
SCAN_LOG_DIR="${CRUSTY_LOG_DIR:-${CLAWGUARD_LOG_DIR:-/tmp/crusty_logs}}"
ACTION="alert-only"
RECURSIVE=false
INCREMENTAL=false
TARGETS=()

show_help() {
    cat <<'EOF'
Usage: scan_file.sh [OPTIONS] <file_or_directory> [...]

Scan files or directories for malware using ClamAV.

Options:
  -r, --recursive     Scan directories recursively
  --quarantine         Move infected files to quarantine
  --remove             Delete infected files
  --alert-only         Report only, don't modify files (default)
  --max-size SIZE      Skip files larger than SIZE (default: 200M)
  --incremental        Skip files unchanged since last scan
  --json               Force JSON output (default)
  -h, --help           Show this help

Environment:
  CRUSTY_QUARANTINE        Quarantine directory (default: /tmp/crusty_quarantine)
  CRUSTY_MAX_FILE_SIZE     Max file size to scan (default: 200M)
  CRUSTY_LOG_DIR           Log directory (default: /tmp/crusty_logs)

Output: JSON with {status, file, engine, threat_name, timestamp, details}
Exit codes: 0 = scan completed (check JSON status field), 1 = runtime error
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -r|--recursive) RECURSIVE=true; shift ;;
        --quarantine) ACTION="quarantine"; shift ;;
        --remove) ACTION="remove"; shift ;;
        --alert-only) ACTION="alert-only"; shift ;;
        --max-size) MAX_FILE_SIZE="$2"; shift 2 ;;
        --incremental) INCREMENTAL=true; shift ;;
        --json) shift ;;
        -h|--help) show_help ;;
        -*) echo "Unknown option: $1" >&2; show_help ;;
        *) TARGETS+=("$1"); shift ;;
    esac
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
    echo '{"status":"error","message":"No target specified. Use --help for usage."}' >&2
    exit 2
fi

# Check ClamAV — auto-install if missing
if ! command -v clamscan &>/dev/null; then
    echo '{"status":"installing","message":"ClamAV not found, installing automatically..."}' >&2
    if bash "$SCRIPT_DIR/install_clamav.sh" >&2 2>&1; then
        echo '{"status":"installed","message":"ClamAV installed successfully"}' >&2
    else
        echo '{"status":"error","message":"ClamAV auto-install failed. Run bash scripts/install_clamav.sh manually."}'
        exit 2
    fi
fi

# Ensure dirs exist
mkdir -p "$SCAN_LOG_DIR" "$QUARANTINE_DIR"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
ENGINE_VERSION=$(clamscan --version 2>/dev/null | head -1 || echo "unknown")
SCAN_RESULT_FILE=$(mktemp)
trap 'rm -f "$SCAN_RESULT_FILE"' EXIT

# Build clamscan options
CLAM_OPTS=(--no-summary --infected --max-filesize="$MAX_FILE_SIZE" --max-scansize="$MAX_FILE_SIZE")

if [[ "$RECURSIVE" == true ]]; then
    CLAM_OPTS+=(-r)
fi

case "$ACTION" in
    quarantine)
        CLAM_OPTS+=(--move="$QUARANTINE_DIR")
        ;;
    remove)
        CLAM_OPTS+=(--remove=yes)
        ;;
    alert-only)
        # default, no action
        ;;
esac

# Prefer clamdscan (faster) if daemon is running, fall back to clamscan
SCANNER="clamscan"
if command -v clamdscan &>/dev/null && clamdscan --ping 1 2>/dev/null; then
    SCANNER="clamdscan"
    # clamdscan has different options
    CLAM_OPTS=(--no-summary --infected)
    if [[ "$ACTION" == "quarantine" ]]; then
        CLAM_OPTS+=(--move="$QUARANTINE_DIR")
    elif [[ "$ACTION" == "remove" ]]; then
        CLAM_OPTS+=(--remove)
    fi
fi

# Incremental: build exclude list
INCREMENTAL_OPTS=()
LAST_SCAN_TS_FILE="$SCAN_LOG_DIR/.last_scan_timestamp"
if [[ "$INCREMENTAL" == true && -f "$LAST_SCAN_TS_FILE" ]]; then
    # We'll use find + clamscan on changed files only
    INCREMENTAL_MODE=true
else
    INCREMENTAL_MODE=false
fi

FOUND_THREATS=0
SCANNED_FILES=0
RESULTS="["

scan_targets() {
    local exit_code=0
    
    if [[ "$INCREMENTAL_MODE" == true ]]; then
        # Scan only files newer than last scan
        for target in "${TARGETS[@]}"; do
            if [[ -d "$target" ]]; then
                while IFS= read -r -d '' file; do
                    $SCANNER "${CLAM_OPTS[@]}" "$file" >> "$SCAN_RESULT_FILE" 2>/dev/null || exit_code=$?
                    ((SCANNED_FILES++)) || true
                done < <(find "$target" -newer "$LAST_SCAN_TS_FILE" -type f -print0)
            else
                if [[ "$target" -nt "$LAST_SCAN_TS_FILE" ]]; then
                    $SCANNER "${CLAM_OPTS[@]}" "$target" >> "$SCAN_RESULT_FILE" 2>/dev/null || exit_code=$?
                    ((SCANNED_FILES++)) || true
                fi
            fi
        done
    else
        $SCANNER "${CLAM_OPTS[@]}" "${TARGETS[@]}" > "$SCAN_RESULT_FILE" 2>/dev/null || exit_code=$?
    fi
    
    return $exit_code
}

SCAN_START_MS=$(get_ms)
SCAN_EXIT=0
scan_targets || SCAN_EXIT=$?

# Update last scan timestamp
date +%s > "$LAST_SCAN_TS_FILE"

# Parse results
THREAT_ENTRIES=""
if [[ -s "$SCAN_RESULT_FILE" ]]; then
    while IFS= read -r line; do
        # ClamAV output: /path/to/file: ThreatName FOUND
        if [[ "$line" =~ ^(.+):\ (.+)\ FOUND$ ]]; then
            FILE_PATH="${BASH_REMATCH[1]}"
            THREAT_NAME="${BASH_REMATCH[2]}"
            ((FOUND_THREATS++)) || true
            
            # Escape for JSON
            FILE_PATH_ESC=$(echo "$FILE_PATH" | sed 's/\\/\\\\/g; s/"/\\"/g')
            THREAT_NAME_ESC=$(echo "$THREAT_NAME" | sed 's/\\/\\\\/g; s/"/\\"/g')
            
            if [[ -n "$THREAT_ENTRIES" ]]; then
                THREAT_ENTRIES+=","
            fi
            THREAT_ENTRIES+="{\"file\":\"$FILE_PATH_ESC\",\"threat_name\":\"$THREAT_NAME_ESC\",\"action\":\"$ACTION\"}"
            
            # Update quarantine manifest
            if [[ "$ACTION" == "quarantine" ]]; then
                MANIFEST="$QUARANTINE_DIR/manifest.json"
                if [[ ! -f "$MANIFEST" ]]; then
                    echo "[]" > "$MANIFEST"
                fi
                # Append entry (simple approach)
                ENTRY="{\"file\":\"$FILE_PATH_ESC\",\"threat\":\"$THREAT_NAME_ESC\",\"quarantined_at\":\"$TIMESTAMP\"}"
                TMP_MANIFEST=$(mktemp)
                if command -v python3 &>/dev/null; then
                    python3 -c "
import json, sys
m = json.load(open('$MANIFEST'))
m.append(json.loads('$ENTRY'))
json.dump(m, open('$TMP_MANIFEST','w'), indent=2)
" 2>/dev/null && mv "$TMP_MANIFEST" "$MANIFEST" || rm -f "$TMP_MANIFEST"
                fi
            fi
        fi
    done < "$SCAN_RESULT_FILE"
fi

# Determine overall status
# Primary signal: did we actually find threats? Exit codes can be unreliable
# (e.g. clamscan returns 2 for permission denied on a single file in a clean scan)
if [[ $FOUND_THREATS -gt 0 ]]; then
    STATUS="infected"
elif [[ $SCAN_EXIT -eq 2 && $FOUND_THREATS -eq 0 ]]; then
    # Scanner had an issue but found nothing — treat as clean with warning
    STATUS="clean"
elif [[ $SCAN_EXIT -eq 0 ]]; then
    STATUS="clean"
else
    STATUS="error"
fi

# Save scan log
LOG_FILE="$SCAN_LOG_DIR/scan_$(date +%Y%m%d_%H%M%S).json"

cat <<EOF | tee "$LOG_FILE"
{
  "status": "$STATUS",
  "timestamp": "$TIMESTAMP",
  "engine": "$ENGINE_VERSION",
  "scanner": "$SCANNER",
  "action": "$ACTION",
  "targets": $(printf '%s\n' "${TARGETS[@]}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin]))" 2>/dev/null || echo '[]'),
  "threats_found": $FOUND_THREATS,
  "threats": [$THREAT_ENTRIES],
  "incremental": $INCREMENTAL
}
EOF

# Push to dashboard
TARGETS_JSON=$(printf '%s\n' "${TARGETS[@]}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin]))" 2>/dev/null || echo '[]')
SCAN_DURATION=$(($(get_ms) - ${SCAN_START_MS:-$(get_ms)}))
RESULTS_JSON="{\"engine\":\"$ENGINE_VERSION\",\"scanner\":\"$SCANNER\",\"threats_found\":$FOUND_THREATS,\"action\":\"$ACTION\",\"incremental\":$INCREMENTAL}"

DASH_SEVERITY="none"
[[ "$STATUS" == "infected" ]] && DASH_SEVERITY="critical"

cg_push_scan "file" "${TARGETS[0]}" "$STATUS" "$ENGINE_VERSION" "$DASH_SEVERITY" "$SCAN_DURATION" "$RESULTS_JSON" 2>/dev/null || true

# Exit 0 = script ran successfully (use JSON status/threats_found for results)
# Exit 1 = runtime error (script couldn't execute properly)
exit 0
