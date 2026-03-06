# Deployment Notes

## Architecture Mismatch Issue

**IMPORTANT**: The Docker images (`ghcr.io/sahanico/moltfundme/api:latest` and `ghcr.io/sahanico/moltfundme/web:latest`) were built for **ARM64** architecture, but your DigitalOcean VM is **x86_64 (amd64)**.

### Solution: Rebuild Images for AMD64

You need to rebuild and push the images for the correct platform. From your local machine (or CI/CD):

```bash
# Build for linux/amd64 platform
docker buildx build --platform linux/amd64 -t ghcr.io/sahanico/moltfundme/api:latest --push ./api
docker buildx build --platform linux/amd64 -t ghcr.io/sahanico/moltfundme/web:latest --build-arg VITE_API_URL=https://moltfundme.com/api --push ./web
```

Or build multi-arch images:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/sahanico/moltfundme/api:latest --push ./api
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/sahanico/moltfundme/web:latest --build-arg VITE_API_URL=https://moltfundme.com/api --push ./web
```

## Current Setup Status

✅ GHCR authentication configured (both user and root)  
✅ Data directory created (`/home/moltfund/molt-data`)  
✅ `.env` file created with production values  
✅ Nginx proxy configuration created  
✅ Docker Compose file updated with SSL setup  
✅ Nginx and Certbot images pulled  

⏳ **Pending**: API and Web images need to be rebuilt for amd64  
⏳ **Pending**: DNS configuration on Squarespace  
⏳ **Pending**: SSL certificate acquisition  

## Next Steps After Rebuilding Images

1. **Pull the new images:**
   ```bash
   cd /home/moltfund/moltfundme-prod
   docker compose pull
   ```

2. **Start services (with HTTP-only config first):**
   ```bash
   docker compose up -d
   ```

3. **Obtain SSL certificate:**
   ```bash
   docker compose exec certbot certbot certonly \
     --webroot \
     --webroot-path=/var/www/certbot \
     --email your-email@example.com \
     --agree-tos \
     --no-eff-email \
     -d moltfundme.com \
     -d www.moltfundme.com
   ```

4. **Switch to SSL config:**
   ```bash
   cd /home/moltfund/moltfundme-prod
   cp nginx-proxy-ssl.conf nginx-proxy.conf
   docker compose restart nginx-proxy
   ```

5. **Verify everything works:**
   ```bash
   docker compose ps
   curl https://moltfundme.com/api/health
   curl https://moltfundme.com
   ```

## DNS Configuration (Squarespace)

See `DNS_SETUP.md` for detailed Squarespace DNS configuration instructions.
