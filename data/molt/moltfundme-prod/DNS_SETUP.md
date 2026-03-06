# Squarespace DNS Configuration Guide

## Overview

You need to configure DNS records on Squarespace to point `moltfundme.com` and `www.moltfundme.com` to your DigitalOcean droplet.

**Your Droplet IP:** `167.172.123.197`

## Step-by-Step Instructions

### 1. Access Squarespace DNS Settings

1. Log in to your Squarespace account
2. Go to **Settings** → **Domains**
3. Click on **moltfundme.com** (or your domain)
4. Click on **DNS Settings** or **Advanced DNS**

### 2. Add A Records

You need to add **two A records**:

#### A Record 1: Root Domain
- **Type:** A
- **Host:** `@` (or leave blank/empty, represents the root domain)
- **Points to:** `167.172.123.197`
- **TTL:** 3600 (or default)

#### A Record 2: WWW Subdomain
- **Type:** A
- **Host:** `www`
- **Points to:** `167.172.123.197`
- **TTL:** 3600 (or default)

### 3. Remove Conflicting Records (if any)

If there are existing A records pointing to other IPs (like Squarespace's hosting), you may need to:
- **Delete** or **update** them to point to `167.172.123.197`
- Or ensure your new records have **higher priority**

### 4. Verify DNS Propagation

After saving the DNS records, wait 5-15 minutes for DNS propagation, then verify:

```bash
# Check root domain
dig moltfundme.com +short
# Should return: 167.172.123.197

# Check www subdomain
dig www.moltfundme.com +short
# Should return: 167.172.123.197
```

Or use online tools:
- https://dnschecker.org/#A/moltfundme.com
- https://www.whatsmydns.net/#A/moltfundme.com

### 5. Test HTTP Access

Once DNS propagates, test that your domain resolves:

```bash
curl -I http://moltfundme.com
curl -I http://www.moltfundme.com
```

Both should return HTTP responses from your Nginx server.

## Troubleshooting

### DNS Not Propagating
- Wait up to 48 hours (usually 5-15 minutes)
- Clear your local DNS cache: `sudo systemd-resolve --flush-caches` (Linux) or `sudo dscacheutil -flushcache` (macOS)
- Check from multiple locations using online DNS checkers

### Domain Still Points to Squarespace
- Ensure you're editing DNS records, not just website settings
- Look for "Advanced DNS" or "DNS Records" section
- Some Squarespace plans may require you to disconnect the domain from Squarespace hosting first

### SSL Certificate Fails
- Ensure DNS is fully propagated before requesting certificates
- Verify both `moltfundme.com` and `www.moltfundme.com` resolve correctly
- Check that port 80 is accessible from the internet (firewall allows it)

## After DNS is Configured

Once DNS is working:
1. Wait for DNS propagation (5-15 minutes)
2. Run the SSL certificate acquisition command (see `DEPLOYMENT_NOTES.md`)
3. Switch to SSL config
4. Test HTTPS access
