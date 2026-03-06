#!/usr/bin/env bash
# Pre-migration audit — Check DNS, MX, SPF, DKIM, DMARC for a domain
# Usage: pre-migration-audit.sh <domain>

set -euo pipefail

DOMAIN="${1:?Usage: pre-migration-audit.sh <domain>}"

echo "=========================================="
echo "Pre-Migration DNS Audit: $DOMAIN"
echo "=========================================="
echo ""

echo "--- Current MX Records ---"
dig MX "$DOMAIN" +short 2>/dev/null || echo "(dig not available, try: nslookup -type=MX $DOMAIN)"
echo ""

echo "--- Current SPF ---"
dig TXT "$DOMAIN" +short 2>/dev/null | grep -i "spf" || echo "No SPF record found"
echo ""

echo "--- Current DMARC ---"
dig TXT "_dmarc.$DOMAIN" +short 2>/dev/null || echo "No DMARC record found"
echo ""

echo "--- Current DKIM (common selectors) ---"
for sel in google default selector1 selector2 s1 s2; do
  result=$(dig TXT "${sel}._domainkey.$DOMAIN" +short 2>/dev/null)
  if [ -n "$result" ]; then
    echo "  $sel._domainkey: $result"
  fi
done
echo ""

echo "--- Autodiscover ---"
dig CNAME "autodiscover.$DOMAIN" +short 2>/dev/null || echo "No autodiscover CNAME"
echo ""

echo "--- Assessment ---"
MX=$(dig MX "$DOMAIN" +short 2>/dev/null)
if echo "$MX" | grep -qi "google\|gmail\|aspmx"; then
  echo "✅ MX already points to Google"
elif echo "$MX" | grep -qi "outlook\|microsoft\|protection.outlook"; then
  echo "⚠️  MX points to Microsoft — needs cutover"
else
  echo "ℹ️  MX points to: $(echo "$MX" | head -1)"
fi

SPF=$(dig TXT "$DOMAIN" +short 2>/dev/null | grep -i "spf" || true)
if echo "$SPF" | grep -qi "google"; then
  echo "✅ SPF includes Google"
else
  echo "⚠️  SPF does not include Google — needs update"
fi

echo ""
echo "Done. Review output and plan DNS changes accordingly."
