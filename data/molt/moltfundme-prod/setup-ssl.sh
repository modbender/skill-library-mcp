#!/bin/bash
# SSL Certificate Setup Script for MoltFundMe
# Run this after DNS is configured and pointing to your droplet

set -e

echo "🔒 Setting up SSL certificate for moltfundme.com"
echo ""

# Check if services are running
if ! docker compose ps | grep -q "moltfundme-nginx-proxy.*Up"; then
    echo "❌ Nginx proxy is not running. Starting services..."
    docker compose up -d nginx-proxy
    sleep 5
fi

# Check if HTTP-only config is active
if ! grep -q "location /.well-known/acme-challenge/" nginx-proxy.conf; then
    echo "⚠️  Switching to HTTP-only config for certificate acquisition..."
    cp nginx-proxy-http-only.conf nginx-proxy.conf
    docker compose restart nginx-proxy
    sleep 3
fi

# Prompt for email
read -p "Enter your email address for Let's Encrypt notifications: " EMAIL

echo ""
echo "📝 Requesting SSL certificate from Let's Encrypt..."
echo "   This may take 30-60 seconds..."
echo ""

# Request certificate
docker compose run --rm certbot certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive \
    -d moltfundme.com \
    -d www.moltfundme.com

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Certificate obtained successfully!"
    echo ""
    echo "🔐 Switching to SSL configuration..."
    
    # Switch to SSL config
    cp nginx-proxy-ssl.conf nginx-proxy.conf
    docker compose restart nginx-proxy
    
    echo ""
    echo "✅ SSL setup complete!"
    echo ""
    echo "🧪 Testing HTTPS..."
    sleep 3
    
    if curl -s -o /dev/null -w "%{http_code}" https://moltfundme.com | grep -q "200\|301\|302"; then
        echo "✅ HTTPS is working!"
    else
        echo "⚠️  HTTPS test returned non-200 status. Check logs: docker compose logs nginx-proxy"
    fi
    
    echo ""
    echo "🎉 Setup complete! Your site should now be accessible at:"
    echo "   https://moltfundme.com"
    echo "   https://www.moltfundme.com"
else
    echo ""
    echo "❌ Certificate acquisition failed!"
    echo ""
    echo "Common issues:"
    echo "  - DNS not fully propagated (wait 5-15 minutes)"
    echo "  - Port 80 not accessible from internet (check firewall)"
    echo "  - Domain not pointing to this server"
    echo ""
    echo "Check logs: docker compose logs certbot"
    exit 1
fi
