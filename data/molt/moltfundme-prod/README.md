# MoltFundMe Production Deployment

This directory contains all files needed to deploy MoltFundMe in production using pre-built Docker images from GHCR.

## Quick Start

1. **Copy this directory to your production VM:**
   ```bash
   scp -r moltfundme-prod/ moltfund@YOUR_VM_IP:/home/moltfund/
   ```

2. **On the VM, setup GHCR authentication:**
   ```bash
   echo "<YOUR_GITHUB_PAT>" | docker login ghcr.io -u sahanico --password-stdin
   ```

3. **Create data directory:**
   ```bash
   sudo mkdir -p /home/moltfund/molt-data
   sudo chown -R moltfund:moltfund /home/moltfund/molt-data
   ```

4. **Configure environment:**
   ```bash
   cd /home/moltfund/moltfundme-prod
   cp .env.example .env
   nano .env  # Edit with your production values
   ```

5. **Start services:**
   ```bash
   docker compose pull
   docker compose up -d
   ```

6. **Verify:**
   ```bash
   docker compose ps
   curl http://localhost:8000/health
   curl http://localhost
   ```

## Files

- `docker-compose.yml` - Docker Compose configuration for production
- `.env.example` - Environment variable template
- `README.md` - This file

## Important Notes

- Database and uploads are stored in `/home/moltfund/molt-data/`
- Images are pulled from `ghcr.io/sahanico/moltfundme/*`
- Frontend proxies `/api` requests to the backend container
- All services restart automatically on failure (`restart: unless-stopped`)

## Backup

Database backups are stored in `/home/moltfund/molt-data/`. See `DEPLOY.md` in the main repo for backup scripts and cron setup.
