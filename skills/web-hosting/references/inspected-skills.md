# Inspected Upstream Skills

Directly inspected from ClawHub:

- `github-api` latest `1.0.3`
- `vercel` latest `1.0.1`
- `netlify` latest `1.0.0`
- `domain-dns-ops` latest `1.0.0`
- `api-gateway` latest `1.0.29`

## Relevant Capability Notes

- `github-api` requires `MATON_API_KEY` and managed OAuth connection for GitHub API actions.
- `vercel` skill documents deploy/link/domain/env/status CLI workflows.
- `netlify` skill documents create/link/init/deploy workflows and CI/CD setup.
- `domain-dns-ops` is environment-specific (documented around a specific manager repo and operator context).
- `api-gateway` requires `MATON_API_KEY` plus active per-app connections; 400 indicates missing app connection and 401 indicates invalid/missing key.
- Inspected `api-gateway` listing explicitly includes Netlify routing references.
- DigitalOcean/AWS are not explicitly listed as native app names in the inspected `api-gateway` service index, so VPS provisioning via gateway is conditional.

## Naming Note

- User-provided `/netlifly` should be interpreted as `/netlify`.
