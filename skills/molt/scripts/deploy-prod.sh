#!/bin/bash
# Deploy MoltFundMe to production VM.
# Run from the repo clone on the VM: /home/moltfund/molt-repo/scripts/deploy-prod.sh
#
# Usage:
#   ./scripts/deploy-prod.sh v1.0.0    # Deploy a specific version
#   ./scripts/deploy-prod.sh            # Deploy whatever IMAGE_TAG is set in .env (or :latest)
set -e

REPO_DIR="/home/moltfund/molt-repo"
PROD_DIR="/home/moltfund/molt-repo/moltfundme-prod"
DATA_DIR="/home/moltfund/molt-data"
BACKUP_DIR="/home/moltfund/backups"
VERSION="${1:-}"

echo "==========================================="
echo " MoltFundMe Production Deploy"
echo "==========================================="
echo ""

# Step 1: Pull latest repo (docs, scripts, configs)
echo "[1/6] Updating repo..."
cd "$REPO_DIR"
git pull --ff-only
echo ""

# Step 2: Set version if provided
if [ -n "$VERSION" ]; then
    if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Version must be in format vX.Y.Z (e.g. v1.0.0)"
        exit 1
    fi
    echo "[2/6] Setting IMAGE_TAG=${VERSION} in .env..."
    cd "$PROD_DIR"
    if grep -q "^IMAGE_TAG=" .env; then
        sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=${VERSION}/" .env
    else
        echo "IMAGE_TAG=${VERSION}" >> .env
    fi
else
    echo "[2/6] No version specified — using IMAGE_TAG from .env (or :latest)"
    cd "$PROD_DIR"
fi
echo ""

# Step 3: Back up database before deploy
echo "[3/6] Backing up database..."
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ -f "$DATA_DIR/prod.db" ]; then
    cp "$DATA_DIR/prod.db" "$BACKUP_DIR/prod_${TIMESTAMP}.db"
    echo "  Backed up to $BACKUP_DIR/prod_${TIMESTAMP}.db"
else
    echo "  No database file found at $DATA_DIR/prod.db — skipping backup"
fi
echo ""

# Step 4: Pull new images
echo "[4/6] Pulling Docker images..."
cd "$PROD_DIR"
docker compose pull
echo ""

# Step 5: Restart services
echo "[5/6] Restarting services..."
docker compose up -d
echo ""

# Step 6: Verify health
echo "[6/6] Verifying health..."
echo "  Waiting 15s for services to start..."
sleep 15

API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
if [ "$API_STATUS" = "200" ]; then
    echo "  API: healthy (200)"
else
    echo "  API: UNHEALTHY (status: $API_STATUS)"
    echo "  Check logs: docker compose -f $PROD_DIR/docker-compose.yml logs api"
fi

WEB_STATUS=$(docker exec moltfundme-web wget --quiet --tries=1 --spider http://localhost/ 2>&1 && echo "200" || echo "000")
if [ "$WEB_STATUS" = "200" ]; then
    echo "  Web: healthy"
else
    echo "  Web: UNHEALTHY"
    echo "  Check logs: docker compose -f $PROD_DIR/docker-compose.yml logs web"
fi

echo ""
echo "==========================================="
DEPLOYED_TAG=$(grep "^IMAGE_TAG=" "$PROD_DIR/.env" 2>/dev/null | cut -d= -f2)
echo " Deployed: ${DEPLOYED_TAG:-latest}"
echo " Time: $(date)"
echo "==========================================="

# Clean up old backups (keep last 7)
find "$BACKUP_DIR" -name "prod_*.db" -mtime +7 -delete 2>/dev/null || true
