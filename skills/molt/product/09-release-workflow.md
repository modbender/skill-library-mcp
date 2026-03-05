# Release Workflow & Production Operations

> Living document. Covers the full cycle from dev changes to production deploy, maintenance, and rollback.

---

## Architecture Overview

```
Dev Machine                    GHCR                    Production VM
──────────                    ────                    ──────────────
code changes                                          /home/moltfund/molt-repo  (git clone, read-only)
    │                                                     ├── product/          (these docs)
    ▼                                                     ├── scripts/          (deploy, maintenance)
tests pass                                                └── moltfundme-prod/  (compose, nginx, .env)
    │
    ▼                                                 /home/moltfund/molt-data  (database, uploads)
build-and-push.sh v1.2.0                                  ├── prod.db
    │                                                     └── uploads/
    ├──► api:v1.2.0 + :latest ──────────────────────►
    └──► web:v1.2.0 + :latest ──────────────────────► docker compose pull + up -d
```

**Key principle:** Docker images carry the application code. The repo clone on the VM is only for configs, docs, and scripts — never for building.

---

## Prod VM File Layout

```
/home/moltfund/
├── molt-repo/                    # Git clone (read-only, configs/docs/scripts only)
│   ├── product/                  # Product docs, release notes
│   ├── scripts/                  # deploy-prod.sh, build-and-push.sh, prod-maintenance.sh
│   └── moltfundme-prod/          # Compose, nginx configs, .env.example
│       ├── docker-compose.yml
│       ├── nginx-proxy.conf
│       ├── nginx-proxy-ssl.conf
│       ├── .env                  # Production secrets (edit on VM, never commit)
│       └── .env.example
├── molt-data/                    # Persistent data (not in repo)
│   ├── prod.db                   # SQLite database
│   └── uploads/                  # Campaign images, KYC docs, agent avatars
└── backups/                      # Database backups
```

**Notes:**
- `molt-repo` is a shallow clone; `git pull` updates configs and docs only.
- `molt-data` and `backups` are created during setup; they are not in the repo.
- `.env` lives in `moltfundme-prod/` and is volume-mounted into containers.

---

## Release Checklist

### On Dev Machine

1. **Code is ready** — feature/fix is complete and tested locally
2. **Tests pass**
   ```bash
   cd api && pytest
   cd web && bun run test
   ```
3. **Build and push versioned images**
   ```bash
   ./scripts/build-and-push.sh v1.2.0
   ```
   This builds `linux/amd64` images, tags them as both `v1.2.0` and `latest`, pushes to GHCR, and creates a git tag.
4. **Update release notes** — Add entry to `product/release-feb2026.md` (or the current month's release file)
5. **Commit and push** — So the prod VM can pull the updated docs/configs
   ```bash
   git add -A && git commit -m "Release v1.2.0" && git push
   ```

### On Production VM

6. **Deploy**
   ```bash
   cd /home/moltfund/molt-repo
   ./scripts/deploy-prod.sh v1.2.0
   ```
   The script: pulls repo, sets `IMAGE_TAG`, backs up database, pulls images, restarts, verifies health.
7. **Verify** — Check the site manually, confirm the change is live

---

## Hotfix Process

For urgent production fixes:

1. Fix the code on dev
2. Build with the next patch version: `./scripts/build-and-push.sh v1.2.1`
3. Commit, push
4. SSH into VM, run `./scripts/deploy-prod.sh v1.2.1`

Skip the full test suite only if the fix is trivially verifiable. Always run at minimum the tests covering the affected code.

---

## Rollback

If a deploy breaks production:

1. SSH into the VM
2. Edit `.env` in the prod directory:
   ```bash
   cd /home/moltfund/molt-repo/moltfundme-prod
   # Change IMAGE_TAG to the last known good version
   sed -i 's/^IMAGE_TAG=.*/IMAGE_TAG=v1.1.0/' .env
   ```
3. Pull and restart:
   ```bash
   docker compose pull && docker compose up -d
   ```
4. Verify health, then investigate the issue on dev

Because every version is tagged in GHCR, rollback is instant — no rebuilding required.

---

## Data Maintenance

### Accessing the Database

The production SQLite database lives at `/home/moltfund/molt-data/prod.db`.

**Always back up before any maintenance:**
```bash
cp /home/moltfund/molt-data/prod.db /home/moltfund/backups/prod_$(date +%Y%m%d_%H%M%S).db
```

**Interactive access:**
```bash
sqlite3 /home/moltfund/molt-data/prod.db
```

### Common Maintenance Tasks

Use the maintenance script for common operations:
```bash
cd /home/moltfund/molt-repo
./scripts/prod-maintenance.sh backup          # Back up database
./scripts/prod-maintenance.sh logs api        # View API logs
./scripts/prod-maintenance.sh logs web        # View web logs
./scripts/prod-maintenance.sh status          # Container health status
./scripts/prod-maintenance.sh db-shell        # Open SQLite shell
```

### Updating Nginx Config

When nginx configs change (e.g., adding OG tag routing):
1. Pull the repo on the VM: `cd /home/moltfund/molt-repo && git pull`
2. Copy the updated config: `cp moltfundme-prod/nginx-proxy.conf /home/moltfund/molt-repo/moltfundme-prod/nginx-proxy.conf`
3. Reload nginx: `docker exec moltfundme-nginx-proxy nginx -s reload`

No image rebuild needed — nginx configs are volume-mounted.

---

## Environment Differences

| Aspect | Development (local) | Production (VM) |
|--------|-------------------|-----------------|
| **ENV** | `development` | `production` |
| **Docker images** | Built locally or from source | Pulled from GHCR with pinned version tag |
| **Database** | `./data/dev.db` | `/home/moltfund/molt-data/prod.db` |
| **Frontend URL** | `http://localhost:5173` | `https://moltfundme.com` |
| **SSL** | None | Let's Encrypt via Certbot |
| **Nginx proxy** | None (direct port access) | nginx-proxy with SSL termination |
| **Docker Compose** | Root `docker-compose.yml` | `moltfundme-prod/docker-compose.yml` |
| **Env config** | `.env` at repo root | `.env` in `moltfundme-prod/` on VM |
| **Repo** | Full clone, active development | Shallow clone, read-only (docs/scripts/configs) |

---

## Prod VM Setup (One-Time)

For initial setup or if recreating the VM:

1. **Clone the repo** (shallow, for configs/docs/scripts only):
   ```bash
   git clone --depth 1 https://github.com/sahanico/moltfundme.git /home/moltfund/molt-repo
   ```

2. **Create data directory:**
   ```bash
   mkdir -p /home/moltfund/molt-data
   mkdir -p /home/moltfund/backups
   ```

3. **Configure environment:**
   ```bash
   cd /home/moltfund/molt-repo/moltfundme-prod
   cp .env.example .env
   # Edit .env with real secrets and API keys
   ```

4. **Authenticate with GHCR:**
   ```bash
   docker login ghcr.io -u sahanico
   ```

5. **First deploy:**
   ```bash
   cd /home/moltfund/molt-repo
   ./scripts/deploy-prod.sh v1.0.0
   ```

6. **Set up SSL** (see `moltfundme-prod/setup-ssl.sh`)

---

## Version History

Track deployed versions here as a quick reference:

| Version | Date | Notes |
|---------|------|-------|
| (pre-versioning) | Feb 2026 | Initial launch, :latest only |
