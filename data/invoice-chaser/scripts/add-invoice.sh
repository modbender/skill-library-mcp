#!/bin/bash
# invoice-chaser/scripts/add-invoice.sh — Add a new invoice to the tracking system

set -euo pipefail

CHASER_DIR="${CHASER_DIR:-$HOME/.config/invoice-chaser}"
INVOICES_FILE="$CHASER_DIR/invoices.json"
CONFIG_FILE="$CHASER_DIR/config.json"

# --- HELPERS ---
function usage() {
  echo "Usage: $0 --number <inv_num> --client <name> --email <addr> --amount <num> [options]"
  echo ""
  echo "Adds a new invoice to the tracking system."
  echo ""
  echo "Required arguments:"
  echo "  --number      string    Invoice number (unique ID)"
  echo "  --client      string    Client's name"
  echo "  --email       string    Client's billing email address"
  echo "  --amount      float     Invoice total amount"
  echo ""
  echo "Optional arguments:"
  echo "  --date        string    Invoice date (YYYY-MM-DD, default: today)"
  echo "  --due         string    Due date (YYYY-MM-DD, default: net terms from config)"
  echo "  --net         integer   Payment terms in days (e.g., 30)"
  echo "  --project     string    Project name or description"
  echo "  --notes       string    Internal notes about the invoice"
  echo "  --test                    Add a test invoice with pre-filled data"
  echo "  -h, --help                Show this help message"
  exit 1
}

# --- ARGUMENT PARSING ---
INV_NUMBER=""
CLIENT_NAME=""
CLIENT_EMAIL=""
AMOUNT=0
INV_DATE=$(date +%Y-%m-%d)
DUE_DATE=""
NET_TERMS=""
PROJECT=""
NOTES=""

# Test mode flag
if [[ " $* " == *" --test "* ]]; then
  echo "🧪 Adding a test invoice..."
  INV_NUMBER="TEST-$(date +%s)"
  CLIENT_NAME="Test Client Inc."
  CLIENT_EMAIL="test@example.com"
  AMOUNT="1250.50"
  PROJECT="Test Project"
  NOTES="This is a test invoice created by add-invoice.sh --test"
else
  while [[ $# -gt 0 ]]; do
    case $1 in
      --number) INV_NUMBER="$2"; shift 2 ;;
      --client) CLIENT_NAME="$2"; shift 2 ;;
      --email) CLIENT_EMAIL="$2"; shift 2 ;;
      --amount) AMOUNT="$2"; shift 2 ;;
      --date) INV_DATE="$2"; shift 2 ;;
      --due) DUE_DATE="$2"; shift 2 ;;
      --net) NET_TERMS="$2"; shift 2 ;;
      --project) PROJECT="$2"; shift 2 ;;
      --notes) NOTES="$2"; shift 2 ;;
      -h|--help) usage ;;
      *) echo "Unknown option: $1"; usage ;;
    esac
  done
fi


# --- VALIDATION ---
if [[ -z "$INV_NUMBER" || -z "$CLIENT_NAME" || -z "$CLIENT_EMAIL" || "$AMOUNT" == "0" ]]; then
  echo "Error: Missing required arguments."
  usage
fi

if ! command -v jq &> /dev/null; then
    echo "Error: 'jq' is not installed. Please install it to continue."
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found at $CONFIG_FILE"
    echo "Run setup.sh first."
    exit 1
fi

if [ ! -f "$INVOICES_FILE" ]; then
    echo "Error: Invoices file not found at $INVOICES_FILE"
    echo "Run setup.sh first."
    exit 1
fi

# Check if invoice number already exists
if jq -e ".invoices[\"$INV_NUMBER\"]" "$INVOICES_FILE" > /dev/null; then
  echo "Error: Invoice number '$INV_NUMBER' already exists."
  exit 1
fi

# --- DATE CALCULATION ---
if [[ -z "$DUE_DATE" ]]; then
  if [[ -z "$NET_TERMS" ]]; then
    NET_TERMS=$(jq -r '.business.default_payment_terms' "$CONFIG_FILE" | sed 's/net-//')
  fi
  # Simple date addition; for production, a more robust date tool might be needed
  DUE_DATE=$(date -j -v+${NET_TERMS}d -f "%Y-%m-%d" "$INV_DATE" "+%Y-%m-%d")
fi

# --- CREATE INVOICE OBJECT ---
invoice_json=$(jq -n \
  --arg number "$INV_NUMBER" \
  --arg client "$CLIENT_NAME" \
  --arg email "$CLIENT_EMAIL" \
  --arg amount "$AMOUNT" \
  --arg date "$INV_DATE" \
  --arg due "$DUE_DATE" \
  --arg project "$PROJECT" \
  --arg notes "$NOTES" \
  '{
    "client_name": $client,
    "client_email": $email,
    "amount": ($amount | tonumber),
    "date": $date,
    "due_date": $due,
    "project": $project,
    "status": "sent",
    "last_chase_stage": null,
    "last_chase_date": null,
    "payment_date": null,
    "is_paused": false,
    "pause_until": null,
    "notes": [$notes],
    "history": [
      {
        "timestamp": "\(now | strftime("%Y-%m-%dT%H:%M:%SZ"))",
        "action": "created",
        "details": "Invoice added to tracking system."
      }
    ]
  }')

# --- SAVE TO FILE ---
temp_file=$(mktemp)
jq ".invoices[\"$INV_NUMBER\"] = $invoice_json" "$INVOICES_FILE" > "$temp_file" && mv "$temp_file" "$INVOICES_FILE"

# --- CONFIRMATION ---
echo "✅ Invoice '$INV_NUMBER' added successfully."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Client:   $CLIENT_NAME"
echo "  Amount:   \$${AMOUNT}"
echo "  Date:     $INV_DATE"
echo "  Due:      $DUE_DATE"
echo "  Status:   sent"
echo ""
echo "The chase cycle will pick this up on its next run."
