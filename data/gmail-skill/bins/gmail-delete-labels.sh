#!/usr/bin/env bash
#
# gmail-delete-labels.sh — Delete a Gmail label and all sublabels via Gmail API
#
# Usage: gmail-delete-labels.sh <label-name> [--delete-messages] [account-email]
#
# This script performs a two-phase deletion:
# 1. Optional: Trash ALL messages with the target label (or sublabels)
# 2. Delete the label(s) via Gmail API (using gog OAuth credentials + Python)
#
# Requirements:
# - gog CLI (for listing labels and message operations)
# - python3 with google-auth and google-api-python-client
# - jq (for JSON parsing)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
    echo "Usage: $0 <label-name> [--delete-messages] [account-email]" >&2
    echo "" >&2
    echo "  label-name         The Gmail label to delete (e.g., 'Professional/OldCompany')" >&2
    echo "  --delete-messages  Also trash ALL messages with this label" >&2
    echo "  account            Gmail address (defaults to \$GMAIL_ACCOUNT)" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0 'Professional/OldCompany'                    # Delete labels only" >&2
    echo "  $0 'Professional/OldCompany' --delete-messages  # Trash ALL messages, then delete labels" >&2
    exit 1
}

# --- Parse arguments (check for --help first) ---
for arg in "$@"; do
    case "$arg" in
        --help|-h) usage ;;
    esac
done

# --- Check dependencies ---
if ! command -v gog &>/dev/null; then
    echo "Error: gog CLI not found. Install via: npm install -g gogcli" >&2
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 not found." >&2
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "Error: jq not found. Install via: brew install jq" >&2
    exit 1
fi

# Check Python dependencies
if ! python3 -c "from google.oauth2.credentials import Credentials; from googleapiclient.discovery import build" 2>/dev/null; then
    echo "Error: Missing Python packages. Install via:" >&2
    echo "  pip install google-auth google-api-python-client" >&2
    exit 1
fi

# --- Parse arguments ---
LABEL=""
DELETE_MESSAGES=false
ACCOUNT="${GMAIL_ACCOUNT:-}"

for arg in "$@"; do
    case "$arg" in
        --delete-messages) DELETE_MESSAGES=true ;;
        --help|-h) ;; # already handled above
        *)
            if [[ -z "$LABEL" ]]; then
                LABEL="$arg"
            elif [[ -z "$ACCOUNT" ]]; then
                ACCOUNT="$arg"
            fi
            ;;
    esac
done

if [[ -z "$LABEL" ]]; then
    echo "Error: No label specified." >&2
    usage
fi

if [[ -z "$ACCOUNT" ]]; then
    echo "Error: No Gmail account specified. Set GMAIL_ACCOUNT or pass as argument." >&2
    exit 1
fi

echo "=== Gmail Label Deletion ==="
echo "Label: ${LABEL}"
echo "Account: ${ACCOUNT}"
echo "Delete messages: ${DELETE_MESSAGES}"
echo ""

# --- Step 1: Find all matching labels (target + sublabels) ---
echo "[1/4] Finding matching labels..."

all_labels_tsv=$(gog gmail labels list --account "$ACCOUNT" --plain 2>/dev/null \
    | tail -n +2)

matching_labels=()
declare -A label_ids

while IFS=$'\t' read -r label_id label_name label_type; do
    [[ -z "$label_name" ]] && continue
    if [[ "$label_name" == "$LABEL" || "$label_name" == "$LABEL/"* ]]; then
        matching_labels+=("$label_name")
        label_ids["$label_name"]="$label_id"
    fi
done <<< "$all_labels_tsv"

if [[ ${#matching_labels[@]} -eq 0 ]]; then
    echo "No labels found matching '${LABEL}' or '${LABEL}/*'"
    exit 0
fi

echo "Found ${#matching_labels[@]} label(s):"
for lbl in "${matching_labels[@]}"; do
    echo "  - ${lbl} (${label_ids[$lbl]})"
done
echo ""

# --- Step 2: Optionally trash ALL messages ---
if [[ "$DELETE_MESSAGES" == true ]]; then
    echo "[2/4] Trashing ALL messages with these labels..."

    total_deleted=0

    for lbl in "${matching_labels[@]}"; do
        echo "  Processing label: ${lbl}"

        messages=$(gog gmail messages search "label:\"${lbl}\"" \
            --account "$ACCOUNT" \
            --max 500 \
            --json 2>/dev/null || echo "{\"messages\":null}" || true) || {
            echo "    ERROR: Failed to fetch messages for label: ${lbl}" >&2
            continue
        }

        if [[ -z "$messages" ]]; then
            messages="{\"messages\":null}"
        fi

        # Extract message IDs safely - handle the case where messages is null
        msg_ids_file=$(mktemp)
        echo "$messages" | jq -r '.messages[]? | .id' 2>/dev/null > "$msg_ids_file" || true

        count=$(grep -c . "$msg_ids_file" 2>/dev/null || true)
        count=${count:-0}
        if [[ "$count" -gt 0 ]]; then
            # Batch move messages to trash in groups of 100
            batch_ids=()
            while IFS= read -r msg_id; do
                [[ -z "$msg_id" ]] && continue
                batch_ids+=("$msg_id")
                
                if [[ ${#batch_ids[@]} -ge 100 ]]; then
                    gog gmail batch modify "${batch_ids[@]}" \
                        --account "$ACCOUNT" \
                        --add="TRASH" 2>/dev/null || true
                    batch_ids=()
                fi
                total_deleted=$((total_deleted + 1))
            done < "$msg_ids_file"
            
            # Process remaining messages
            if [[ ${#batch_ids[@]} -gt 0 ]]; then
                gog gmail batch modify "${batch_ids[@]}" \
                    --account "$ACCOUNT" \
                    --add="TRASH" 2>/dev/null || true
            fi
            
            echo "    Trashed $count message(s)"
        else
            echo "    No messages to trash"
        fi
        
        rm -f "$msg_ids_file"
    done

    echo ""
    echo "Total messages trashed: $total_deleted"
    echo ""
else
    echo "[2/4] Skipping message deletion (--delete-messages not specified)"
    echo ""
fi

# --- Step 3: Delete the labels via Gmail API (Python) ---
echo "[3/4] Deleting labels via Gmail API..."

# Export gog token temporarily
TOKEN_FILE=$(mktemp)
rm "$TOKEN_FILE"  # gog auth tokens export needs the file to NOT exist
trap "rm -f '$TOKEN_FILE'" EXIT

gog auth tokens export "$ACCOUNT" --out "$TOKEN_FILE" 2>/dev/null || true

# Read gog client credentials
GOG_CREDS_DIR="${HOME}/Library/Application Support/gogcli"
if [[ ! -f "$GOG_CREDS_DIR/credentials.json" ]]; then
    # Try Linux path
    GOG_CREDS_DIR="${HOME}/.config/gogcli"
fi

if [[ ! -f "$GOG_CREDS_DIR/credentials.json" ]]; then
    echo "Error: Cannot find gog credentials. Expected at:" >&2
    echo "  ~/Library/Application Support/gogcli/credentials.json (macOS)" >&2
    echo "  ~/.config/gogcli/credentials.json (Linux)" >&2
    exit 1
fi

# Build label ID list for Python (children first, parent last)
LABEL_IDS_JSON="["
first=true
# Sort: longer names (deeper children) first
IFS=$'\n' sorted_labels=($(for lbl in "${matching_labels[@]}"; do echo "$lbl"; done | awk '{print length, $0}' | sort -rn | cut -d' ' -f2-))
for lbl in "${sorted_labels[@]}"; do
    if [[ "$first" == true ]]; then
        first=false
    else
        LABEL_IDS_JSON+=","
    fi
    LABEL_IDS_JSON+="{\"id\":\"${label_ids[$lbl]}\",\"name\":\"$lbl\"}"
done
LABEL_IDS_JSON+="]"

# Run Python to delete labels
result=$(python3 - "$TOKEN_FILE" "$GOG_CREDS_DIR/credentials.json" "$LABEL_IDS_JSON" << 'PYEOF'
import json, sys

token_file = sys.argv[1]
creds_file = sys.argv[2]
labels_json = sys.argv[3]

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open(creds_file) as f:
    client = json.load(f)
with open(token_file) as f:
    token = json.load(f)

creds = Credentials(
    token=None,
    refresh_token=token["refresh_token"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=client["client_id"],
    client_secret=client["client_secret"],
)

service = build("gmail", "v1", credentials=creds)
labels = json.loads(labels_json)

deleted = 0
failed = 0
for label in labels:
    try:
        service.users().labels().delete(userId="me", id=label["id"]).execute()
        print(f"  Deleted: {label['name']}")
        deleted += 1
    except Exception as e:
        print(f"  FAILED: {label['name']} -- {e}")
        failed += 1

print(f"\nDELETED={deleted}")
print(f"FAILED={failed}")
PYEOF
)

echo "$result"

# Parse counts from Python output
deleted_count=$(echo "$result" | grep "^DELETED=" | cut -d= -f2)
failed_count=$(echo "$result" | grep "^FAILED=" | cut -d= -f2)

echo ""
echo "=== Summary ==="
echo "Labels deleted: ${deleted_count:-0}/${#matching_labels[@]}"
if [[ "$DELETE_MESSAGES" == true ]]; then
    echo "Messages trashed: $total_deleted"
fi
if [[ "${failed_count:-0}" -gt 0 ]]; then
    echo "Labels failed: $failed_count"
fi
echo ""

# Note: With gmail.modify scope, we cannot permanently delete messages.
# Trashed messages will be auto-deleted by Gmail after 30 days.
# To empty trash immediately, do it manually in Gmail.

echo "Done!"
