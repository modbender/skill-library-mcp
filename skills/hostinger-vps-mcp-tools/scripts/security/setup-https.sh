#!/bin/bash
# Setup HTTPS with Let's Encrypt + Nginx Reverse Proxy
# Usage: ./setup-https.sh DOMAIN EMAIL [KODA_PORT]
# Run as root

set -e

DOMAIN="${1:?Usage: $0 DOMAIN EMAIL [KODA_PORT]}"
EMAIL="${2:?Usage: $0 DOMAIN EMAIL [KODA_PORT]}"
KODA_PORT="${3:-18789}"

echo "🔒 Setting up HTTPS with Let's Encrypt"
echo "======================================="
echo "Domain: $DOMAIN"
echo "Email:  $EMAIL"
echo ""

# Install Nginx and Certbot
echo "[1/4] Installing Nginx and Certbot..."
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx

# Configure Nginx
echo "[2/4] Configuring Nginx..."
cat > /etc/nginx/sites-available/koda << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:$KODA_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
EOF

ln -sf /etc/nginx/sites-available/koda /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Open port 80 and 443
echo "[3/4] Configuring firewall..."
ufw allow 80/tcp
ufw allow 443/tcp

# Get SSL certificate
echo "[4/4] Obtaining SSL certificate..."
certbot --nginx -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive --redirect

# Setup auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "✅ HTTPS configured!"
echo ""
echo "Access Koda at: https://$DOMAIN"
echo ""
echo "SSL certificate will auto-renew."
echo ""
echo "Optional: Remove direct port access"
echo "  ufw delete allow $KODA_PORT/tcp"
