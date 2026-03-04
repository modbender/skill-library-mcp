#!/usr/bin/env bash
set -euo pipefail

# Invoice Generator — create professional invoices from CLI inputs
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Defaults
CLIENT="" CLIENT_EMAIL="" FROM="Shelly Labs"
DATE=$(date +%Y-%m-%d) DUE="" INVOICE_NUMBER=""
TAX=0 CURRENCY="USD" FORMAT="md" OUTPUT=""
ITEMS=()

usage() {
  echo "Usage: $0 --client NAME --item 'Desc|Qty|Rate' [options]"
  echo "See SKILL.md for full docs."
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --client) CLIENT="$2"; shift 2;;
    --email) CLIENT_EMAIL="$2"; shift 2;;
    --from) FROM="$2"; shift 2;;
    --date) DATE="$2"; shift 2;;
    --due) DUE="$2"; shift 2;;
    --invoice-number) INVOICE_NUMBER="$2"; shift 2;;
    --item) ITEMS+=("$2"); shift 2;;
    --tax) TAX="$2"; shift 2;;
    --currency) CURRENCY="$2"; shift 2;;
    --format) FORMAT="$2"; shift 2;;
    --output) OUTPUT="$2"; shift 2;;
    -h|--help) usage;;
    *) echo "Unknown: $1"; usage;;
  esac
done

[[ -z "$CLIENT" ]] && { echo "Error: --client required"; exit 1; }
[[ ${#ITEMS[@]} -eq 0 ]] && { echo "Error: at least one --item required"; exit 1; }
[[ -z "$DUE" ]] && DUE=$(date -v+30d +%Y-%m-%d 2>/dev/null || date -d "+30 days" +%Y-%m-%d 2>/dev/null || echo "N/A")
[[ -z "$INVOICE_NUMBER" ]] && INVOICE_NUMBER="INV-$(date +%s)"

# Calculate
SUBTOTAL=0
ITEM_LINES=()
ITEM_ROWS_HTML=""
ITEM_ROWS_MD=""

for item in "${ITEMS[@]}"; do
  IFS='|' read -r desc qty rate <<< "$item"
  amount=$(echo "$qty * $rate" | bc)
  SUBTOTAL=$(echo "$SUBTOTAL + $amount" | bc)
  amt_fmt=$(printf "%.2f" "$amount")
  rate_fmt=$(printf "%.2f" "$rate")
  ITEM_ROWS_HTML+="      <tr><td>${desc}</td><td>${qty}</td><td>${rate_fmt}</td><td>${amt_fmt}</td></tr>\n"
  ITEM_ROWS_MD+="| ${desc} | ${qty} | ${rate_fmt} | ${amt_fmt} |\n"
done

TAX_AMOUNT=$(printf "%.2f" "$(echo "$SUBTOTAL * $TAX / 100" | bc -l)")
TOTAL=$(printf "%.2f" "$(echo "$SUBTOTAL + $TAX_AMOUNT" | bc -l)")
SUBTOTAL=$(printf "%.2f" "$SUBTOTAL")

out() {
  if [[ -n "$OUTPUT" ]]; then echo -e "$1" > "$OUTPUT"; echo "Written to $OUTPUT"
  else echo -e "$1"; fi
}

if [[ "$FORMAT" == "html" ]]; then
  TPL=$(cat "$SCRIPT_DIR/template.html")
  TPL="${TPL//\{\{INVOICE_NUMBER\}\}/$INVOICE_NUMBER}"
  TPL="${TPL//\{\{DATE\}\}/$DATE}"
  TPL="${TPL//\{\{DUE_DATE\}\}/$DUE}"
  TPL="${TPL//\{\{FROM\}\}/$FROM}"
  TPL="${TPL//\{\{CLIENT\}\}/$CLIENT}"
  TPL="${TPL//\{\{CLIENT_EMAIL\}\}/$CLIENT_EMAIL}"
  TPL="${TPL//\{\{CURRENCY\}\}/$CURRENCY}"
  TPL="${TPL//\{\{SUBTOTAL\}\}/$SUBTOTAL}"
  TPL="${TPL//\{\{TAX_RATE\}\}/$TAX}"
  TPL="${TPL//\{\{TAX_AMOUNT\}\}/$TAX_AMOUNT}"
  TPL="${TPL//\{\{TOTAL\}\}/$TOTAL}"
  ROWS=$(echo -e "$ITEM_ROWS_HTML")
  TPL="${TPL//\{\{ITEMS_ROWS\}\}/$ROWS}"
  out "$TPL"
else
  MD="# Invoice ${INVOICE_NUMBER}\n\n"
  MD+="**From:** ${FROM}  \n**To:** ${CLIENT}"
  [[ -n "$CLIENT_EMAIL" ]] && MD+=" (${CLIENT_EMAIL})"
  MD+="\n\n**Date:** ${DATE}  \n**Due:** ${DUE}\n\n"
  MD+="| Description | Qty | Rate | Amount |\n|---|---|---|---|\n"
  MD+="$(echo -e "$ITEM_ROWS_MD")\n"
  MD+="| | | **Subtotal** | **${CURRENCY} ${SUBTOTAL}** |\n"
  MD+="| | | **Tax (${TAX}%)** | **${CURRENCY} ${TAX_AMOUNT}** |\n"
  MD+="| | | **Total** | **${CURRENCY} ${TOTAL}** |\n"
  out "$MD"
fi
