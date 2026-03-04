#!/usr/bin/env bash
#
# gmail-delete-old-messages.sh — Delete messages older than a specific date from a label
#
# Usage: gmail-delete-old-messages.sh <label-name> <date> [account-email]
#
# This script deletes all messages older than the specified date from a label
# and all its sublabels. Date format: MM/DD/YYYY
#
# Requirements:
# - gog CLI (for listing labels)
# - python3 with google-auth and google-api-python-client
#
set -euo pipefail

usage() {
    echo "Usage: $0 <label-name> <date> [account-email]" >&2
    echo "" >&2
    echo "  label-name    The Gmail label (e.g., 'Personal/Archive')" >&2
    echo "  date          Delete messages older than this date (MM/DD/YYYY)" >&2
    echo "  account       Gmail address (defaults to \$GMAIL_ACCOUNT)" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0 'Personal/Archive' '01/01/2020'        # Delete messages before Jan 1, 2020" >&2
    echo "  $0 'Personal/Old' '12/31/2019' user@gmail.com" >&2
    exit 1
}

# --- Parse arguments ---
for arg in "$@"; do
    case "$arg" in
        --help|-h) usage ;;
    esac
done

if ! command -v gog &>/dev/null; then
    echo "Error: gog CLI not found. Install via: npm install -g gogcli" >&2
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 not found." >&2
    exit 1
fi

if ! python3 -c "from google.oauth2.credentials import Credentials; from googleapiclient.discovery import build" 2>/dev/null; then
    echo "Error: Missing Python packages. Install via:" >&2
    echo "  pip install google-auth google-api-python-client" >&2
    exit 1
fi

LABEL=""
DATE=""
ACCOUNT="${GMAIL_ACCOUNT:-}"

for arg in "$@"; do
    case "$arg" in
        --help|-h) ;; # already handled
        *)
            if [[ -z "$LABEL" ]]; then
                LABEL="$arg"
            elif [[ -z "$DATE" ]]; then
                DATE="$arg"
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

if [[ -z "$DATE" ]]; then
    echo "Error: No date specified." >&2
    usage
fi

if [[ -z "$ACCOUNT" ]]; then
    echo "Error: No Gmail account specified. Set GMAIL_ACCOUNT or pass as argument." >&2
    exit 1
fi

# Validate date format
if ! [[ "$DATE" =~ ^[0-9]{2}/[0-9]{2}/[0-9]{4}$ ]]; then
    echo "Error: Invalid date format. Use MM/DD/YYYY" >&2
    exit 1
fi

echo "=== Delete Old Messages ==="
echo "Label: ${LABEL}"
echo "Delete messages before: ${DATE}"
echo "Account: ${ACCOUNT}"
echo ""

# --- Step 1: Find matching labels ---
echo "[1/4] Finding matching labels..."

all_labels_tsv=$(gog gmail labels list --account "$ACCOUNT" --plain 2>/dev/null | tail -n +2)

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
    echo "  - ${lbl}"
done
echo ""

# --- Step 2: Convert date to Gmail search format (YYYY/MM/DD) ---
echo "[2/4] Converting date format..."
IFS='/' read -r month day year <<< "$DATE"
GMAIL_DATE="${year}/${month}/${day}"
echo "Gmail search format: before:${GMAIL_DATE}"
echo ""

# --- Step 3: Search and delete old messages ---
echo "[3/4] Finding and deleting old messages..."

# Check for full-scope token first (enables permanent delete)
FULL_SCOPE_TOKEN="${HOME}/.gmail-skill/full-scope-token.json"
CAN_DELETE=false

# Export gog token as fallback
TOKEN_FILE=$(mktemp)
rm "$TOKEN_FILE"  # gog auth tokens export needs the file to NOT exist
trap "rm -f '$TOKEN_FILE'" EXIT

if [[ -f "$FULL_SCOPE_TOKEN" ]]; then
    cp "$FULL_SCOPE_TOKEN" "$TOKEN_FILE"
    CAN_DELETE=true
    echo "Using full-scope token (permanent delete enabled)"
else
    gog auth tokens export "$ACCOUNT" --out "$TOKEN_FILE" 2>/dev/null || true
    echo "Using gog token (trash only — run gmail-auth-full-scope.sh for permanent delete)"
fi

GOG_CREDS_DIR="${HOME}/Library/Application Support/gogcli"
if [[ ! -f "$GOG_CREDS_DIR/credentials.json" ]]; then
    GOG_CREDS_DIR="${HOME}/.config/gogcli"
fi

if [[ ! -f "$GOG_CREDS_DIR/credentials.json" ]]; then
    echo "Error: Cannot find gog credentials." >&2
    exit 1
fi

# Build search queries for each label (include label IDs for API filtering)
SEARCH_QUERIES="["
first=true
for lbl in "${matching_labels[@]}"; do
    if [[ "$first" == true ]]; then
        first=false
    else
        SEARCH_QUERIES+=","
    fi
    SEARCH_QUERIES+="{\"label\":\"${lbl}\",\"label_id\":\"${label_ids[$lbl]}\",\"before\":\"${GMAIL_DATE}\"}"
done
SEARCH_QUERIES+="]"

# Run Python to search and delete
result=$(python3 - "$TOKEN_FILE" "$GOG_CREDS_DIR/credentials.json" "$SEARCH_QUERIES" "$CAN_DELETE" << 'PYEOF'
import json, sys
from datetime import datetime

token_file = sys.argv[1]
creds_file = sys.argv[2]
queries_json = sys.argv[3]
can_delete = sys.argv[4] == "true"

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
queries = json.loads(queries_json)

import time

total_trashed = 0
total_failed = 0

# Loop until no more messages found (Gmail index is eventually consistent)
pass_num = 0
while True:
    pass_num += 1
    all_msg_ids = set()

    for query in queries:
        label = query["label"]
        label_id = query["label_id"]
        before_date = query["before"]

        if pass_num == 1:
            print(f"  Searching: {label} ({label_id}) before {before_date}")

        search_query = f"before:{before_date}"
        try:
            results = service.users().messages().list(
                userId="me",
                labelIds=[label_id],
                q=search_query,
                maxResults=500
            ).execute()

            messages = results.get("messages", [])
            for msg in messages:
                all_msg_ids.add(msg["id"])

            while "nextPageToken" in results:
                results = service.users().messages().list(
                    userId="me",
                    labelIds=[label_id],
                    q=search_query,
                    maxResults=500,
                    pageToken=results["nextPageToken"]
                ).execute()
                messages = results.get("messages", [])
                for msg in messages:
                    all_msg_ids.add(msg["id"])

        except Exception as e:
            print(f"    Error searching: {e}")

    if not all_msg_ids:
        break

    action = "deleting" if can_delete else "trashing"
    print(f"  Pass {pass_num}: found {len(all_msg_ids)} messages, {action}...")

    for msg_id in all_msg_ids:
        try:
            if can_delete:
                service.users().messages().delete(userId="me", id=msg_id).execute()
            else:
                service.users().messages().trash(userId="me", id=msg_id).execute()
            total_trashed += 1
            if total_trashed % 50 == 0:
                print(f"    Processed {total_trashed} so far...")
        except Exception as e:
            total_failed += 1

    # Brief pause for Gmail index to update
    time.sleep(2)

action = "DELETED" if can_delete else "TRASHED"
print(f"\n{action}={total_trashed}")
print(f"FAILED={total_failed}")
PYEOF
)

echo "$result"

# Parse counts (key is DELETED or TRASHED depending on scope)
deleted_count=$(echo "$result" | grep -E "^(DELETED|TRASHED)=" | cut -d= -f2)
failed_count=$(echo "$result" | grep "^FAILED=" | cut -d= -f2)

echo ""
echo "=== Summary ==="
if [[ "$CAN_DELETE" == "true" ]]; then
    echo "Messages permanently deleted: ${deleted_count:-0}"
else
    echo "Messages trashed: ${deleted_count:-0} (auto-deleted after 30 days)"
fi
if [[ "${failed_count:-0}" -gt 0 ]]; then
    echo "Messages failed: $failed_count"
fi
echo ""

echo "Done!"
