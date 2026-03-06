#!/bin/bash
# Windfall Server Setup Script
# Run on a fresh Ubuntu 24.04 server

set -e

echo "=== Windfall Server Setup ==="

# Install Node.js 22 LTS
if ! command -v node &> /dev/null; then
  echo "Installing Node.js 22..."
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
  apt-get install -y nodejs
fi

echo "Node.js $(node -v)"
echo "npm $(npm -v)"

# Install build tools for better-sqlite3
apt-get install -y build-essential python3

# Create app directory
mkdir -p /opt/windfall
echo "App directory: /opt/windfall"

# Install certbot for SSL
apt-get install -y certbot

# Install nginx
apt-get install -y nginx

echo "=== Setup complete ==="
echo "Next: upload app files to /opt/windfall and run 'npm install && npm run build'"
