# PROJECTS.md — Schema & Update Guide

## When to Update PROJECTS.md

- **New project** started (repo created, first deployment)
- **Status change**: Prototype → Production, Active → Archived
- **Major changes**: URL, stack, server location
- **Project shutdown**: Move to Archived section

## Project Entry Schema

```markdown
## [Project Name]
- **URL:** https://example.com (or "Internal" if no public URL)
- **Stack:** Main technologies (e.g., "Next.js + TypeScript", "Node.js + Express", "Static HTML/CSS")
- **Repo:** github-user/repo-name
- **Server:** server-name (port/path)
- **Status:** Production ✅ | Prototype | Archived
- **Notes:** 1-2 sentence description (what it does, key features)
```

## Categories

### Active
Production services, live websites, actively maintained projects.

### Prototypes
Experimental, staging, proof-of-concept, not yet production-ready.

### Archived
Deprecated, shut down, or replaced projects. Include archive date and reason.

## What NOT to Include

- ❌ Detailed architecture → belongs in repo README
- ❌ Deployment commands → belongs in repo (deploy.sh)
- ❌ Event timeline → belongs in daily logs
- ❌ API keys/credentials → belongs in TOOLS.md
- ❌ Code examples → belongs in repo documentation

## Example

```markdown
# Active Projects

## lynk-site
- **URL:** https://lynk.run
- **Stack:** Static HTML/CSS/JS
- **Repo:** jpj069/lynk-site
- **Server:** lynk-prod /opt/lynk-site (nginx:8080)
- **Status:** Production ✅
- **Notes:** Main website with blog, 3-theme system, daily automated posts

## talkhub-platform
- **URL:** https://talk.lynk.run
- **Stack:** Node.js + Express
- **Repo:** jpj069/talkhub-platform
- **Server:** lynk-prod :3003
- **Status:** Production ✅
- **Notes:** Multi-channel communication (Phone/SMS/Email/WhatsApp)

# Prototypes

## gekko
- **URL:** https://gekko.one
- **Stack:** Next.js + shadcn/ui
- **Repo:** jpj069/gekko
- **Server:** lynk-prod :3000
- **Status:** Prototype
- **Notes:** Revenue OS with 90+ pages, HTTP basic auth

# Archived

## network-rampage
- **Archived:** Feb 16, 2026
- **Reason:** Dead 404 link, game project discontinued
- **Repo:** jpj069/network-rampage (deleted)
```
