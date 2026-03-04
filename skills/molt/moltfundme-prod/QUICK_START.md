# Quick Start Guide

## Current Status

✅ **Infrastructure Ready**: All configuration files are in place  
✅ **GHCR Authenticated**: Docker can pull images from GitHub Container Registry  
✅ **Environment Configured**: `.env` file with production values  
✅ **Nginx Proxy Ready**: Reverse proxy with SSL support configured  
✅ **Certbot Ready**: Automated SSL certificate renewal configured  

⚠️ **Action Required**: Docker images need to be rebuilt for `linux/amd64` architecture

## Next Steps

### 1. Rebuild Docker Images (from your local machine or CI/CD)

The current images are built for ARM64, but your VM is x86_64. Rebuild and push:

```bash
# Build for amd64 platform
docker buildx build --platform linux/amd64 \
  -t ghcr.io/sahanico/moltfundme/api:latest \
  --push ./api

docker buildx build --platform linux/amd64 \
  --build-arg VITE_API_URL=https://moltfundme.com/api \
  -t ghcr.io/sahanico/moltfundme/web:latest \
  --push ./web
```

### 2. Configure DNS on Squarespace

See `DNS_SETUP.md` for detailed instructions. You need to add two A records:
- `@` → `167.172.123.197`
- `www` → `167.172.123.197`

### 3. Pull Images and Start Services

```bash
cd /home/moltfund/moltfundme-prod
docker compose pull
docker compose up -d
```

### 4. Obtain SSL Certificate

Wait 5-15 minutes for DNS to propagate, then run:

```bash
cd /home/moltfund/moltfundme-prod
./setup-ssl.sh
```

Or manually:

```bash
docker compose run --rm certbot certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d moltfundme.com \
  -d www.moltfundme.com

# Switch to SSL config
cp nginx-proxy-ssl.conf nginx-proxy.conf
docker compose restart nginx-proxy
```

### 5. Verify Everything Works

```bash
# Check container status
docker compose ps

# Test endpoints
curl https://moltfundme.com/api/health
curl https://moltfundme.com
```

## File Structure

```
/home/moltfund/moltfundme-prod/
├── docker-compose.yml          # Main compose file with all services
├── .env                        # Production environment variables
├── nginx-proxy.conf            # Current Nginx config (HTTP-only initially)
├── nginx-proxy-http-only.conf # HTTP-only config for cert acquisition
├── nginx-proxy-ssl.conf        # Full SSL config (use after cert obtained)
├── setup-ssl.sh                # Automated SSL setup script
├── DNS_SETUP.md                # Squarespace DNS configuration guide
├── DEPLOYMENT_NOTES.md         # Detailed deployment notes
└── QUICK_START.md             # This file
```

## Useful Commands

```bash
# View logs
docker compose logs -f
docker compose logs -f api
docker compose logs -f nginx-proxy

# Restart services
docker compose restart
docker compose restart api
docker compose restart nginx-proxy

# Update and redeploy
docker compose pull
docker compose up -d

# Check SSL certificate expiry
docker compose exec certbot certbot certificates
```

## Troubleshooting

### Images won't pull
- **Issue**: "no matching manifest for linux/amd64"
- **Solution**: Rebuild images for amd64 platform (see step 1)

### SSL certificate fails
- **Issue**: "Failed to obtain certificate"
- **Solution**: 
  - Wait for DNS propagation (5-15 minutes)
  - Verify DNS: `dig moltfundme.com +short` should return `167.172.123.197`
  - Check firewall allows port 80

### Services won't start
- Check logs: `docker compose logs`
- Verify `.env` file exists and has correct values
- Ensure data directory exists: `ls -la /home/moltfund/molt-data`
