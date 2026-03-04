#!/usr/bin/env bash
#
# gmail-label-audit.sh — Audit a Gmail label and its sublabels, then optionally clean up
#
# Usage: gmail-label-audit.sh <label-name> [--cleanup] [account-email]
#
# Without --cleanup: reports message counts per label/sublabel and identifies
#                    single-label vs multi-label messages
# With --cleanup:    removes the target label(s) from single-label messages
#                    and leaves multi-label messages untouched
#
set -euo pipefail

usage() {
    echo "Usage: $0 <label-name> [--cleanup] [account-email]" >&2
    echo "" >&2
    echo "  label-name    The Gmail label to audit (e.g., 'Professional/Companies')" >&2
    echo "  --cleanup     Actually remove labels from single-label messages" >&2
    echo "  account       Gmail address (defaults to \$GMAIL_ACCOUNT)" >&2
    exit 1
}

# --- Parse arguments ---
LABEL=""
CLEANUP=false
ACCOUNT="${GMAIL_ACCOUNT:-}"

for arg in "$@"; do
    case "$arg" in
        --cleanup) CLEANUP=true ;;
        --help|-h) usage ;;
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

# --- System labels to ignore when determining "multi-label" ---
# These don't count as user-applied labels
SYSTEM_LABELS="INBOX|SENT|DRAFT|TRASH|SPAM|CHAT|STARRED|IMPORTANT|UNREAD|YELLOW_STAR|CATEGORY_PERSONAL|CATEGORY_SOCIAL|CATEGORY_PROMOTIONS|CATEGORY_UPDATES|CATEGORY_FORUMS"

# --- Step 1: Find all matching labels (target + sublabels) ---
echo "Auditing label: ${LABEL}"
echo "Account: ${ACCOUNT}"
echo ""

# Get all user labels, filter to target and sublabels
all_labels=$(gog gmail labels list --account "$ACCOUNT" --plain 2>/dev/null \
    | tail -n +2 \
    | cut -f2)

matching_labels=()
while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    # Match exact label or sublabels (label/*)
    if [[ "$name" == "$LABEL" || "$name" == "$LABEL/"* ]]; then
        matching_labels+=("$name")
    fi
done <<< "$all_labels"

if [[ ${#matching_labels[@]} -eq 0 ]]; then
    echo "No labels found matching '${LABEL}' or '${LABEL}/*'"
    exit 0
fi

echo "Labels in scope (${#matching_labels[@]}):"
for lbl in "${matching_labels[@]}"; do
    echo "  - ${lbl}"
done
echo ""

# --- Step 2: For each label, get messages and classify ---
total_messages=0
total_single_label=0
total_multi_label=0

# Associative arrays for per-label counts
declare -A label_total
declare -A label_single
declare -A label_multi

# Collect all message IDs and their labels across all matching labels
declare -A msg_labels_map    # message_id -> comma-separated labels from search
declare -A msg_source_label  # message_id -> which of our target labels it came from

for lbl in "${matching_labels[@]}"; do
    # Search for messages with this label
    results=$(gog gmail messages search "label:${lbl}" \
        --account "$ACCOUNT" \
        --max 500 \
        --plain 2>/dev/null | tail -n +2 || true)

    label_count=0
    single_count=0
    multi_count=0

    while IFS=$'\t' read -r id thread date from subject labels_str; do
        [[ -z "$id" ]] && continue

        label_count=$((label_count + 1))

        # Parse the LABELS column (comma-separated)
        # Filter out system labels to find user labels
        user_label_count=0
        IFS=',' read -ra msg_labels <<< "$labels_str"
        for ml in "${msg_labels[@]}"; do
            ml=$(echo "$ml" | xargs)  # trim whitespace
            # Skip system labels
            if ! echo "$ml" | grep -qE "^(${SYSTEM_LABELS})$"; then
                user_label_count=$((user_label_count + 1))
            fi
        done

        # Track for deduplication
        if [[ -z "${msg_labels_map[$id]+x}" ]]; then
            msg_labels_map[$id]="$labels_str"
            msg_source_label[$id]="$lbl"

            if [[ $user_label_count -le 1 ]]; then
                single_count=$((single_count + 1))
            else
                multi_count=$((multi_count + 1))
            fi
        fi
    done <<< "$results"

    label_total[$lbl]=$label_count
    label_single[$lbl]=$single_count
    label_multi[$lbl]=$multi_count

    total_messages=$((total_messages + label_count))
    total_single_label=$((total_single_label + single_count))
    total_multi_label=$((total_multi_label + multi_count))
done

# --- Step 3: Report ---
echo "=== Label Audit Report ==="
echo ""
printf "%-50s %8s %8s %8s\n" "LABEL" "TOTAL" "SINGLE" "MULTI"
printf "%-50s %8s %8s %8s\n" "-----" "-----" "------" "-----"

for lbl in "${matching_labels[@]}"; do
    t="${label_total[$lbl]:-0}"
    s="${label_single[$lbl]:-0}"
    m="${label_multi[$lbl]:-0}"
    printf "%-50s %8d %8d %8d\n" "$lbl" "$t" "$s" "$m"
done

echo ""
printf "%-50s %8d %8d %8d\n" "TOTAL (deduplicated)" "${#msg_labels_map[@]}" "$total_single_label" "$total_multi_label"
echo ""
echo "SINGLE = only this label (safe to clean up)"
echo "MULTI  = has other user labels (will be left alone)"
echo ""

# --- Step 4: Cleanup (if requested) ---
if [[ "$CLEANUP" == false ]]; then
    echo "Run with --cleanup to remove labels from single-label messages."
    exit 0
fi

if [[ $total_single_label -eq 0 ]]; then
    echo "No single-label messages to clean up."
    exit 0
fi

echo "=== Cleaning Up ==="
echo "Removing labels from ${total_single_label} single-label messages..."
echo "(Skipping ${total_multi_label} multi-label messages)"
echo ""

cleaned=0

for lbl in "${matching_labels[@]}"; do
    # Collect single-label message IDs for this label
    batch_ids=()

    results=$(gog gmail messages search "label:${lbl}" \
        --account "$ACCOUNT" \
        --max 500 \
        --plain 2>/dev/null | tail -n +2 || true)

    while IFS=$'\t' read -r id thread date from subject labels_str; do
        [[ -z "$id" ]] && continue

        # Re-check: only process single-user-label messages
        user_label_count=0
        IFS=',' read -ra msg_labels <<< "$labels_str"
        for ml in "${msg_labels[@]}"; do
            ml=$(echo "$ml" | xargs)
            if ! echo "$ml" | grep -qE "^(${SYSTEM_LABELS})$"; then
                user_label_count=$((user_label_count + 1))
            fi
        done

        if [[ $user_label_count -le 1 ]]; then
            batch_ids+=("$id")
        fi
    done <<< "$results"

    if [[ ${#batch_ids[@]} -eq 0 ]]; then
        continue
    fi

    echo "  ${lbl}: removing from ${#batch_ids[@]} messages..."

    # Process in batches of 100
    for ((i=0; i<${#batch_ids[@]}; i+=100)); do
        chunk=("${batch_ids[@]:i:100}")
        gog gmail batch modify "${chunk[@]}" \
            --account "$ACCOUNT" \
            --remove "$lbl" \
            --force 2>/dev/null || echo "    Warning: batch modify failed for some messages in ${lbl}"
    done

    cleaned=$((cleaned + ${#batch_ids[@]}))
done

echo ""
echo "=== Cleanup Complete ==="
echo "Cleaned: ${cleaned} messages (labels removed)"
echo "Skipped: ${total_multi_label} messages (multi-label, left alone)"
