#!/usr/bin/env bash
# Pre-migration audit — Check DNS, MX, SPF, DKIM, DMARC for Microsoft 365 readiness
# Usage: pre-migration-audit.sh <domain>

set -euo pipefail

DOMAIN="${1:?Usage: pre-migration-audit.sh <domain>}"

echo "=========================================="
echo "Pre-Migration DNS Audit: $DOMAIN"
echo "Microsoft 365 Readiness Check"
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

echo "--- Current DKIM (checking Microsoft selectors) ---"
for sel in selector1 selector2; do
  result=$(dig CNAME "${sel}._domainkey.$DOMAIN" +short 2>/dev/null)
  if [ -n "$result" ]; then
    echo "  $sel._domainkey: $result"
  else
    echo "  $sel._domainkey: Not configured"
  fi
done
echo ""

echo "--- Autodiscover ---"
dig CNAME "autodiscover.$DOMAIN" +short 2>/dev/null || echo "No autodiscover CNAME"
echo ""

echo "--- Microsoft 365 Tenant Check ---"
# Extract potential tenant name from domain
TENANT_GUESS=$(echo "$DOMAIN" | sed 's/\./-/g')
echo "Checking potential tenant: $TENANT_GUESS.mail.protection.outlook.com"
dig A "$TENANT_GUESS.mail.protection.outlook.com" +short 2>/dev/null || echo "Tenant MX not resolvable (normal if not configured yet)"
echo ""

echo "--- Assessment ---"
MX=$(dig MX "$DOMAIN" +short 2>/dev/null)
if echo "$MX" | grep -qi "outlook\|microsoft\|protection.outlook"; then
  echo "✅ MX already points to Microsoft 365"
elif echo "$MX" | grep -qi "google\|gmail\|aspmx"; then
  echo "⚠️  MX points to Google — migration source confirmed"
else
  echo "ℹ️  MX points to: $(echo "$MX" | head -1 | awk '{print $2}')"
fi

SPF=$(dig TXT "$DOMAIN" +short 2>/dev/null | grep -i "spf" || true)
if echo "$SPF" | grep -qi "protection.outlook.com"; then
  echo "✅ SPF includes Microsoft 365"
elif echo "$SPF" | grep -qi "google"; then
  echo "⚠️  SPF includes Google — will need update during cutover"
else
  echo "ℹ️  Current SPF: $SPF"
fi

AUTODISCOVER=$(dig CNAME "autodiscover.$DOMAIN" +short 2>/dev/null)
if echo "$AUTODISCOVER" | grep -qi "outlook.com"; then
  echo "✅ Autodiscover points to Microsoft"
elif echo "$AUTODISCOVER" | grep -qi "google"; then
  echo "⚠️  Autodiscover points to Google — needs update"
else
  echo "ℹ️  Autodiscover: $AUTODISCOVER"
fi

echo ""
echo "--- Microsoft 365 Readiness Checklist ---"
echo "Before migration:"
echo "  [ ] Verify Microsoft 365 tenant and domain ownership"
echo "  [ ] Assign Exchange Online licenses to all users"
echo "  [ ] Create service account for Google Workspace API access"
echo "  [ ] Test mail flow to [user]@$TENANT_GUESS.mail.onmicrosoft.com"
echo ""
echo "DNS changes needed during cutover:"
echo "  [ ] Update MX: $TENANT_GUESS.mail.protection.outlook.com"
echo "  [ ] Update SPF: v=spf1 include:spf.protection.outlook.com ~all"
echo "  [ ] Update Autodiscover: autodiscover.outlook.com"
echo "  [ ] Configure DKIM in Microsoft 365 Defender"
echo ""
echo "Done. Review output and plan DNS changes accordingly."