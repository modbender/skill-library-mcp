#!/bin/bash
# Install Docker and Docker Compose
# Run as root

set -e

echo "🐳 Installing Docker"
echo "===================="

# Remove old versions
echo "[1/4] Removing old Docker versions..."
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install Docker using official script
echo "[2/4] Installing Docker..."
curl -fsSL https://get.docker.com | sh

# Install Docker Compose plugin
echo "[3/4] Installing Docker Compose..."
apt-get install -y docker-compose-plugin

# Add koda user to docker group
echo "[4/4] Adding 'koda' user to docker group..."
usermod -aG docker koda

# Enable Docker service
systemctl enable docker
systemctl start docker

# Verify installation
echo ""
echo "✅ Docker installation complete!"
echo ""
docker --version
docker compose version
echo ""
echo "Next: Run 04-deploy-koda.sh to deploy Koda"
