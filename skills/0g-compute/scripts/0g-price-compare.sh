#!/bin/bash
# 0G vs OpenRouter Price Comparison
# No API keys required — uses public endpoints only.
set -e

OG_DATA=$(mktemp)
OR_DATA=$(mktemp)
trap 'rm -f "$OG_DATA" "$OR_DATA"' EXIT

echo -e "\033[1m0G vs OpenRouter Price Comparison\033[0m"
echo ""

# 1. 0G token price (CoinGecko ID: zero-gravity)
echo -e "\033[2mFetching 0G token price...\033[0m"
OG_USD=$(curl -sf 'https://api.coingecko.com/api/v3/simple/price?ids=zero-gravity&vs_currencies=usd' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['zero-gravity']['usd'])" 2>/dev/null || echo "")

if [ -z "$OG_USD" ]; then
    OG_USD="${OG_TOKEN_PRICE_USD:-}"
    if [ -z "$OG_USD" ]; then
        echo -e "\033[0;31m✗ Could not fetch 0G price. Set OG_TOKEN_PRICE_USD env var.\033[0m"
        exit 1
    fi
fi
echo -e "  0G = \033[0;32m\$${OG_USD}\033[0m"

# 2. 0G providers
echo -e "\033[2mFetching 0G providers...\033[0m"
0g-compute-cli inference list-providers 2>&1 | sed 's/\x1b\[[0-9;]*m//g' > "$OG_DATA"

# 3. OpenRouter models
echo -e "\033[2mFetching OpenRouter models...\033[0m"
curl -sf 'https://openrouter.ai/api/v1/models' > "$OR_DATA"
echo ""

# 4. Compare
python3 - "$OG_DATA" "$OR_DATA" "$OG_USD" << 'PYEOF'
import sys, json, re

og_file, or_file, og_usd = sys.argv[1], sys.argv[2], float(sys.argv[3])

# Parse 0G CLI two-column table: "│ Label │ Value │"
with open(og_file) as f:
    raw = f.read()

providers = []
cur = {}
for line in raw.split('\n'):
    parts = [p.strip() for p in line.split('│') if p.strip()]
    if len(parts) != 2:
        continue
    label, value = parts[0], parts[1]
    
    if re.match(r'Provider \d+', label):
        if cur.get('model'):
            providers.append(cur)
        cur = {'addr': value.strip()}
    elif label == 'Model':
        cur['model'] = value.strip()
    elif 'Input Price Per Token' in label:
        cur['in_price'] = float(value.strip())
    elif 'Output Price Per Token' in label:
        cur['out_price'] = float(value.strip())
    elif 'Price Per Image' in label:
        cur['img_price'] = float(value.strip())
        cur['in_price'] = 0
        cur['out_price'] = 0
    elif label == 'Verifiability':
        cur['tee'] = value.strip()

if cur.get('model'):
    providers.append(cur)

# Parse OpenRouter
with open(or_file) as f:
    or_data = json.load(f)

or_map = {}
for m in or_data.get('data', []):
    mid = m['id'].lower()
    p = m.get('pricing', {})
    or_map[mid] = {
        'id': m['id'],
        'in': float(p.get('prompt', '0')),
        'out': float(p.get('completion', '0')),
    }

def match_or(model):
    ml = model.lower()
    if ml in or_map: return or_map[ml]
    base = ml.split('/')[-1] if '/' in ml else ml
    base_clean = re.sub(r'[-_](fp\d+|int\d+|awq|gptq)$', '', base)
    for k, v in or_map.items():
        kb = re.sub(r'[-_](fp\d+|int\d+|awq|gptq)$', '', k.split('/')[-1])
        if base_clean == kb: return v
    for k, v in or_map.items():
        kb = k.split('/')[-1]
        if base_clean in kb or kb in base_clean: return v
    return None

G = '\033[0;32m'; R = '\033[0;31m'; D = '\033[2m'; N = '\033[0m'; Y = '\033[1;33m'

print(f"{'Model':<38} {'0G $/1M in':>12} {'0G $/1M out':>13} {'OR $/1M in':>12} {'OR $/1M out':>13} {'Savings':>9}")
print('─' * 103)

for p in providers:
    m = p.get('model', '?')
    inp = p.get('in_price', 0)
    out = p.get('out_price', 0)
    
    og_in = inp * og_usd * 1_000_000
    og_out = out * og_usd * 1_000_000
    
    orr = match_or(m)
    if orr:
        or_in = orr['in'] * 1_000_000
        or_out = orr['out'] * 1_000_000
        total_og = og_in + og_out
        total_or = or_in + or_out
        if total_or > 0:
            sav = ((total_or - total_og) / total_or) * 100
            sc = G if sav > 0 else R
            sav_s = f"{sc}{sav:+.1f}%{N}"
        else:
            sav_s = "N/A"
        print(f"{m:<38} ${og_in:>10.4f} ${og_out:>10.4f} ${or_in:>10.4f} ${or_out:>10.4f}  {sav_s}")
        print(f"{D}{'':38} matched: {orr['id']}{N}")
    else:
        print(f"{m:<38} ${og_in:>10.4f} ${og_out:>10.4f}  {Y}{'no match':>24}{N}")

print()
print(f"{D}0G = ${og_usd} USD | All prices USD/1M tokens | + savings = 0G cheaper{N}")
PYEOF
