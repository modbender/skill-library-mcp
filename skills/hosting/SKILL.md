---
name: Hosting
description: Choose and manage web hosting services for websites and apps without server administration.
metadata: {"clawdbot":{"emoji":"🌍","os":["linux","darwin","win32"]}}
---

# Web Hosting Guidance

## Choosing the Right Type
- Static sites (HTML, CSS, JS only): Use Vercel, Netlify, Cloudflare Pages, GitHub Pages — free tier often enough, no server management
- Dynamic sites with backend: Platform hosting (Railway, Render, Fly.io) handles servers without manual management
- WordPress or PHP: Managed WordPress hosts (WP Engine, Kinsta) or traditional shared hosting
- E-commerce: Shopify or platform-specific hosting — payment security is not worth DIY risk
- Don't recommend VPS to someone uncomfortable with terminal — managed hosting exists for a reason

## Shared Hosting Reality
- "Unlimited" bandwidth and storage always have fair use limits — read the terms
- Performance depends on neighbors — bad neighbors slow your site
- SSH access may be limited or unavailable — verify before assuming
- Cron jobs and background processes often restricted
- Fine for small sites and blogs — not for growing businesses

## Platform Hosting (Vercel, Netlify, Railway, etc.)
- Free tiers have limits — check build minutes, bandwidth, function invocations
- Serverless functions have cold start latency — first request after idle is slow
- Vendor lock-in varies — static files portable, platform-specific features less so
- Preview deployments per branch are invaluable for review workflows
- Environment variables configured in dashboard — never commit secrets to repo

## Database Considerations
- Most platform hosts don't include databases — need separate provider (PlanetScale, Supabase, Neon)
- Database location should match app location — cross-region latency hurts performance
- Connection pooling often required for serverless — direct connections exhaust limits
- Backups may or may not be included — verify and test restore process

## Domain and DNS
- Hosting provider often offers DNS — but separating them gives flexibility
- Point nameservers to host: simpler setup, less control
- Point A/CNAME records: more control, slightly more complex
- SSL certificates usually automatic with modern hosts — verify HTTPS works after setup

## Email Separation
- Web hosting and email hosting are different services — can use different providers
- Don't rely on free email with web hosting — often limited and unreliable
- Google Workspace, Zoho, or dedicated email providers are more reliable
- MX records for email don't affect web hosting

## Backups
- Managed hosts usually include backups — verify frequency and retention
- Download periodic backups locally — host backups don't help if host goes away
- Know the restore process before you need it
- Database backups separate from file backups — need both

## Cost Awareness
- Monthly vs yearly billing — annual often 20-40% cheaper but commits you
- Traffic spikes can trigger overage fees — understand the billing model
- Free tiers often enough for side projects — don't overpay for unused capacity
- Compare total cost including add-ons — base price rarely tells the whole story

## Migration Readiness
- Keep content in portable formats — avoid excessive platform-specific features
- Document how the current setup works — needed when moving
- Export data regularly — don't assume you can always access it
- DNS propagation takes up to 48 hours — plan migrations with overlap

## Common Mistakes
- Choosing by price alone — support quality matters when things break
- Not testing staging before production — preview environments prevent disasters
- Ignoring geographic location — hosting in US for European users adds latency
- Assuming backups exist — verify and test before you need them
- Overcomplicating for small sites — a blog doesn't need Kubernetes
