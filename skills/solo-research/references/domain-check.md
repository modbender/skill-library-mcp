# /research — Domain & Naming Check Reference

Referenced by SKILL.md step 7.

## TLD Priority Tiers

Check in order, skip regionals except .us:

| Tier | TLDs | When to check |
|------|------|---------------|
| **Must** | `.com` | Always — SEO, credibility |
| **Core** | `.app`, `.dev`, `.io`, `.co` | All candidates — tech/startup standard |
| **Budget** | `.win`, `.xyz`, `.cc`, `.work`, `.club`, `.org` | All candidates — cheap alternatives ($4-12/yr) |
| **Premium** | `.ai` | Only if AI product — NOTE: $160/yr from March 2026 |
| **US only** | `.us` | Add-on if US-focused ($6.50/yr) |
| **Skip** | `.ru`, `.de`, `.uk`, `.fr`, `.jp`, etc. | Regional — skip unless targeting that market |
| **Skip** | `.net`, `.info`, `.biz`, `.mobi`, `.site`, `.online`, `.store`, `.shop` | Low trust / overpriced for the value |

## Step 1: whois + dig combo (most reliable)

```bash
# Check all TLD tiers at once
for name in candidate1 candidate2 candidate3; do
  for ext in com app dev io co win xyz cc work club org us; do
    domain="${name}.${ext}"
    # whois check
    match=$(whois "$domain" 2>/dev/null | grep -i "no match\|not found\|domain not found\|no data found" | head -1)
    if [ -n "$match" ]; then
      echo "AVAILABLE:  $domain"
    else
      # DNS fallback for ambiguous whois
      ns=$(dig +short "$domain" 2>/dev/null)
      if [ -z "$ns" ]; then
        echo "LIKELY FREE: $domain  (no DNS)"
      else
        echo "TAKEN:       $domain"
      fi
    fi
  done
  echo "---"
done
```

## Step 2: RDAP cross-check (for uncertain results)

```bash
# IMPORTANT: use -L to follow redirects (RDAP returns 302)
# 404 = available, 200 = registered
for name in candidate1 candidate2; do
  for ext in com app io; do
    code=$(curl -sL -o /dev/null -w "%{http_code}" "https://rdap.org/domain/${name}.${ext}")
    if [ "$code" = "404" ]; then r="AVAIL"; else r="taken"; fi
    printf "  %-25s %s\n" "${name}.${ext}" "$r"
  done
done
```

## Gotchas

- `.app`/`.dev` (Google Registry): whois shows TLD creation date 2015 even for unregistered domains — do NOT use creation date as indicator. Check Name Server and Registrar fields instead.
- `.ai`: $160/yr from March 2026. Only worth it for AI-branded products.
- `.win`: extremely cheap ($4-5/yr) — good for MVPs and redirects.
- RDAP rate limits after ~20 requests — prefer whois+dig combo for bulk checks.

**Summary:** whois checks availability → dig confirms no DNS → RDAP cross-checks uncertain cases.

## Trademark & Company Checks

- `"<name> trademark"` — basic conflict check
- `"site:trademarkia.com <name>"` — US trademarks
- `"site:opencorporates.com <name>"` — 240M+ companies worldwide
- `"<name> LLC OR Inc OR Corp"` — existing businesses
