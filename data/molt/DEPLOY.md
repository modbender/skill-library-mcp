# MoltFundMe VM Provisioning Guide
## DigitalOcean SFO | Ubuntu

---

## 1. Create User (run as root)

```bash
# Create user with home directory
adduser moltfund

# Add to sudo group (needed for initial setup)
usermod -aG sudo moltfund

# Allow passwordless sudo (no sudo typing required)
echo "moltfund ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/moltfund
chmod 0440 /etc/sudoers.d/moltfund

# Copy SSH keys from root so you can SSH in as the new user
mkdir -p /home/moltfund/.ssh
cp /root/.ssh/authorized_keys /home/moltfund/.ssh/
chown -R moltfund:moltfund /home/moltfund/.ssh
chmod 700 /home/moltfund/.ssh
chmod 600 /home/moltfund/.ssh/authorized_keys
```

---

## 2. Verify Access

```bash
# From your local machine, SSH as the new user
ssh moltfund@<DROPLET_IP>

# Confirm no password prompt needed
whoami          # should print: moltfund
sudo whoami     # should print: root (no password asked)
```

---

## 3. Lock Down Root (after verifying user access)

```bash
# Disable root SSH login
sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd
```

---

## 4. Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Add user to docker group (no sudo needed for docker commands)
usermod -aG docker moltfund

# Apply group change (or log out and back in)
newgrp docker

# Enable on boot
systemctl enable docker

# Verify
docker --version
docker compose version
```

---

## 5. Firewall (UFW)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

---

## 6. Build and Push Images to GHCR (from local machine)

**Important:** Production VM is linux/amd64. Build with `--platform linux/amd64` so images run on the VM.

```bash
# Login to GitHub Container Registry (if not already logged in)
# Create a PAT at https://github.com/settings/tokens with read:packages and write:packages scopes
# echo "<YOUR_GITHUB_PAT>" | docker login ghcr.io -u sahanico --password-stdin

# Build for linux/amd64 (required for production VM)
docker build --platform linux/amd64 -t ghcr.io/sahanico/moltfundme/api:latest ./api
docker build --platform linux/amd64 -t ghcr.io/sahanico/moltfundme/web:latest ./web

# Push to GHCR
docker push ghcr.io/sahanico/moltfundme/api:latest
docker push ghcr.io/sahanico/moltfundme/web:latest
```

---

## 7. Setup GHCR Authentication on VM

```bash
# Create GitHub Personal Access Token (PAT) if you don't have one:
# Go to https://github.com/settings/tokens
# Generate new token (classic) with scopes: read:packages, write:packages

# Login to GitHub Container Registry
echo "<YOUR_GITHUB_PAT>" | docker login ghcr.io -u sahanico --password-stdin

# Verify login
docker pull ghcr.io/sahanico/moltfundme/api:latest
docker pull ghcr.io/sahanico/moltfundme/web:latest

# Note: Credentials are stored in ~/.docker/config.json
# To persist across reboots, ensure Docker service is enabled (already done in step 4)
```

---

## 8. Setup Data Directory and Deploy

```bash
# Create dedicated data directory for database and uploads
sudo mkdir -p /home/moltfund/molt-data
sudo chown -R moltfund:moltfund /home/moltfund/molt-data
sudo chmod 755 /home/moltfund/molt-data

# Clone repo (for docker-compose.yml and .env)
cd /home/moltfund
git clone git@github.com:sahanico/moltfundme.git molt
cd molt

# Create .env from example
cp .env.example .env

# Edit .env with production values
nano .env
# Required values:
# - ENV=production
# - SECRET_KEY=<generate secure random string>
# - API_KEY_SALT=<generate secure random string>
# - FRONTEND_URL=http://<YOUR_VM_IP> (or your domain)
# - DATABASE_URL_PROD=sqlite+aiosqlite:///./data/prod.db

# Pull latest images
docker compose pull

# Start services
docker compose up -d

# Verify everything is running
docker compose ps
docker compose logs -f

# Test endpoints
curl http://localhost:8000/health
curl http://localhost
```

---

## 9. Database Backup

The database is stored in `/home/moltfund/molt-data/` which is bound to the container.

### Manual Backup

```bash
# Stop the API container (optional, but ensures clean backup)
docker compose stop api

# Create backup
sudo tar -czf /home/moltfund/backups/moltfundme-db-$(date +%Y%m%d-%H%M%S).tar.gz \
  -C /home/moltfund/molt-data .

# Restart API
docker compose start api

# List backups
ls -lh /home/moltfund/backups/
```

### Automated Backup Script

Create `/home/moltfund/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/moltfund/backups"
DATA_DIR="/home/moltfund/molt-data"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

mkdir -p "$BACKUP_DIR"

# Create backup
tar -czf "$BACKUP_DIR/moltfundme-db-$TIMESTAMP.tar.gz" -C "$DATA_DIR" .

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "moltfundme-db-*.tar.gz" -mtime +7 -delete

echo "Backup created: moltfundme-db-$TIMESTAMP.tar.gz"
```

Make it executable:
```bash
chmod +x /home/moltfund/backup-db.sh
```

### Setup Cron Job for Daily Backups

```bash
# Edit crontab
crontab -e

# Add this line for daily backup at 2 AM
0 2 * * * /home/moltfund/backup-db.sh >> /home/moltfund/backup.log 2>&1
```

### Restore from Backup

```bash
# Stop API container
docker compose stop api

# Restore backup
tar -xzf /home/moltfund/backups/moltfundme-db-YYYYMMDD-HHMMSS.tar.gz -C /home/moltfund/molt-data

# Restart API
docker compose start api
```

---

## Key Ports

| Service  | Port | Description        |
|----------|------|--------------------|
| SSH      | 22   | Remote access      |
| HTTP     | 80   | Frontend (Nginx)   |
| HTTPS    | 443  | Frontend (TLS)     |
| API      | 8000 | FastAPI (internal)  |

---

## Useful Commands

```bash
# Logs
docker compose logs -f          # tail all logs
docker compose logs -f api      # tail API logs only
docker compose logs -f web      # tail web logs only

# Container management
docker compose restart api      # restart API
docker compose restart web      # restart web
docker compose restart          # restart all services
docker compose stop             # stop all services
docker compose start            # start all services
docker compose down             # stop and remove containers
docker compose up -d            # start services

# Updates
docker compose pull             # pull latest images from GHCR
docker compose up -d            # restart with new images

# Database
docker compose exec api ls -la /app/data  # list database files
docker compose exec api sqlite3 /app/data/prod.db ".tables"  # inspect database
```

---

## Data Directory Structure

```
/home/moltfund/molt-data/
├── prod.db                    # Production SQLite database
├── dev.db                     # Development database (if used)
└── uploads/
    └── kyc/                   # KYC verification uploads
        └── <creator_id>/
            ├── id_photo_*.jpg
            └── selfie_*.jpg
```

**Important:** This directory is bound to the container at `/app/data`. All database files and uploads persist here and survive container restarts.
