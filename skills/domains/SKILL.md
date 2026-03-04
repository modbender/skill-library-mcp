---
name: Domains
description: Register, manage, and protect domain names with practical DNS and security guidance.
metadata: {"clawdbot":{"emoji":"🌐","os":["linux","darwin","win32"]}}
---

# Domain Management Rules

## Before Registration
- Check availability on the registrar directly — WHOIS lookups from third parties can trigger front-running (someone registers it before you)
- Search for the domain name + "scam" or "controversy" — previous owners leave reputation baggage
- Verify trademark conflicts before investing in branding — legal disputes are expensive

## Choosing Extensions
- .com still has highest trust for general audiences — alternatives work but require more brand building
- Country TLDs (.co.uk, .de) rank better in local search — use them for geo-targeted businesses
- New TLDs (.io, .ai, .dev) work for tech audiences but confuse mainstream users
- Premium domains have recurring premium renewal fees, not just higher initial cost — check yearly price

## Registration Practices
- Enable auto-renewal immediately — domains lost to expiration get scooped by squatters within hours
- Buy WHOIS privacy — public registration data leads to endless spam and social engineering attempts
- Register for multiple years if the domain is important — shows search engines you're serious
- Use a dedicated email for registrar accounts — losing access to that email means losing the domain

## DNS Fundamentals
- DNS changes take 24-48 hours to fully propagate — plan migrations accordingly
- TTL (Time To Live) should be lowered before migrations, raised after — low TTL during normal operation wastes resources
- A records point to IP addresses, CNAME points to another domain — never CNAME the root domain
- MX records for email are separate from web hosting — moving hosts doesn't require changing email if MX stays

## Security
- Enable registrar lock (clientTransferProhibited) — prevents unauthorized transfers
- DNSSEC adds cryptographic verification — worth enabling but breaks if misconfigured
- Two-factor on registrar account is mandatory — domain hijacking is common attack vector
- Authorization/EPP code is the password for transfers — treat it like a credential

## Transfers
- 60-day lock after registration or previous transfer — plan ahead, can't transfer immediately
- Transfers extend registration by one year — not wasted money
- Unlock domain and get auth code before initiating — missing either blocks the transfer
- Some TLDs have special transfer rules — .uk, .de, and others differ from standard process

## Expiration
- Grace period (usually 30 days) allows renewal at normal price — but risky, site goes down
- Redemption period costs 10-20x normal renewal — expensive mistake
- After redemption, domain goes to auction or open registration — you've lost it
- Expired domains with backlinks get bought by spammers — protect your brand's domains even if unused

## Multi-Domain Strategy
- Register common misspellings and redirect — typosquatters will otherwise profit from your traffic
- Consider .com + main country TLD at minimum — others only if brand is valuable
- Subdomains are free and instant — don't buy domains for every project, use subdomains for experiments
- Consolidate domains at one registrar — easier management, less credential sprawl

## Common Mistakes
- Registering through web host instead of dedicated registrar — harder to move later, often more expensive
- Letting domains expire assuming no one cares — competitors and squatters monitor expirations
- Using registrar's free email forwarding for critical accounts — tied to domain renewal, single point of failure
- Not documenting which domains exist where — large organizations lose track and lose domains
