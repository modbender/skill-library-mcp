#!/usr/bin/env bash
set -euo pipefail

STORE_RAW=0
if [[ "${1:-}" == "--store-raw" ]]; then
  STORE_RAW=1
fi

CRED_FILE="${GUMROAD_CREDENTIALS_FILE:-$HOME/.config/gumroad/credentials.json}"
if [[ ! -f "$CRED_FILE" ]]; then
  echo "Credentials file not found: $CRED_FILE" >&2
  exit 1
fi

TOKEN="$(python3 - <<'PY' "$CRED_FILE"
import json,sys
p=sys.argv[1]
with open(p,'r',encoding='utf-8') as f:
    data=json.load(f)
print(data.get('access_token') or data.get('token') or '')
PY
)"

if [[ -z "$TOKEN" ]]; then
  echo "No access token found in $CRED_FILE (expected access_token or token)" >&2
  exit 1
fi

API="https://api.gumroad.com/v2"
TODAY="$(date +%F)"
OUT_DIR="memory/metrics/gumroad"
mkdir -p "$OUT_DIR"

SALES_JSON="$(curl -sS --get "$API/sales" --data-urlencode "access_token=$TOKEN")"
PRODUCTS_JSON="$(curl -sS --get "$API/products" --data-urlencode "access_token=$TOKEN")"

SUMMARY_PATH="$OUT_DIR/$TODAY-summary.json"

python3 - <<'PY' "$SALES_JSON" "$PRODUCTS_JSON" "$TODAY" "$SUMMARY_PATH"
import json,sys
sales_raw=json.loads(sys.argv[1] or '{}')
products_raw=json.loads(sys.argv[2] or '{}')
today=sys.argv[3]
out_path=sys.argv[4]

sales=sales_raw.get('sales') or []
products=products_raw.get('products') or []

revenue_cents=0
for s in sales:
    # Gumroad sales payload may include price in cents (as number or string)
    v=s.get('price',0)
    try:
        revenue_cents += int(v)
    except Exception:
        pass

summary={
    'date': today,
    'sales_count': len(sales),
    'products_count': len(products),
    'revenue_cents': revenue_cents,
    'revenue_usd': round(revenue_cents/100,2),
}

with open(out_path,'w',encoding='utf-8') as f:
    json.dump(summary,f,indent=2)

print(json.dumps(summary,indent=2))
PY

if [[ "$STORE_RAW" -eq 1 ]]; then
  SALES_RAW_PATH="$OUT_DIR/$TODAY-raw-sales-redacted.json"
  PRODUCTS_RAW_PATH="$OUT_DIR/$TODAY-raw-products.json"

  python3 - <<'PY' "$SALES_JSON" "$SALES_RAW_PATH"
import json,sys
payload=json.loads(sys.argv[1] or '{}')
out_path=sys.argv[2]
for s in payload.get('sales',[]) or []:
    for key in ('email','full_name','name','buyer_email'):
        if key in s:
            s.pop(key,None)
with open(out_path,'w',encoding='utf-8') as f:
    json.dump(payload,f,indent=2)
PY

  printf '%s\n' "$PRODUCTS_JSON" > "$PRODUCTS_RAW_PATH"
  echo "Raw files written (redacted sales):"
  echo "- $SALES_RAW_PATH"
  echo "- $PRODUCTS_RAW_PATH"
fi
