# Deployment Patterns

## Platform Comparison

| Platform | Best for | Gotchas |
|----------|----------|---------|
| Vercel | Next.js, serverless | Cold starts; limited to 10s (Hobby) or 60s (Pro) for functions |
| Netlify | Static + serverless | Functions timeout at 10s (free) / 26s (paid) |
| Cloudflare Pages | Static + Workers | Workers have no Node APIs; use `node-compat` flag |
| VPS (Docker) | Full control, long-running | You manage SSL, updates, scaling |
| Railway/Render | Docker apps | Sleep after inactivity on free tier |

## Common Deploy Issues

- **Build fails locally works** — Check Node version matches; use `.nvmrc` or `engines` in package.json
- **Environment variables missing** — Platform dashboards don't auto-sync; redeploy after adding vars
- **Static export breaks API routes** — `next export` is static only; use Vercel/custom server for API routes
- **Trailing slashes** — Configure consistently; `/about` vs `/about/` causes duplicate content/redirects

## DNS Setup

1. **Add A record** — Point `@` to platform IP (or use CNAME for subdomains)
2. **Add CNAME for www** — Point `www` to apex or platform domain
3. **Wait for propagation** — Up to 48h but usually minutes; check with `dig` or online tools
4. **SSL auto-provisions** — Most platforms handle Let's Encrypt; may take a few minutes after DNS resolves

## Deployment Checklist

- [ ] Environment variables set in platform dashboard
- [ ] Build command correct (`npm run build`, not `npm start`)
- [ ] Output directory correct (`out`, `.next`, `dist`)
- [ ] Domain DNS configured and propagated
- [ ] HTTPS working (check certificate valid)
- [ ] 404 page configured
- [ ] Redirects for old URLs if migrating
