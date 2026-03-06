# SSL Troubleshooting Guide

## Diagnostic Commands

```bash
# Full connection test with chain
openssl s_client -connect example.com:443 -servername example.com

# Check certificate dates
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates

# View full certificate details
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -text -noout

# Test specific TLS version
openssl s_client -connect example.com:443 -tls1_2
openssl s_client -connect example.com:443 -tls1_3

# Check what ciphers are supported
nmap --script ssl-enum-ciphers -p 443 example.com
```

## Problem: Certificate Chain Incomplete

**Symptoms:**
- Works in Chrome but fails in curl/wget
- "unable to verify the first certificate"
- Some clients show warning, others don't

**Diagnosis:**
```bash
openssl s_client -connect example.com:443
# Look for "Verify return code: 21 (unable to verify)"
```

**Fix:**
Include the intermediate certificate in your config. For Let's Encrypt, use `fullchain.pem` not just `cert.pem`.

## Problem: Certificate Expired

**Symptoms:**
- Browser shows "Your connection is not private"
- `NET::ERR_CERT_DATE_INVALID`

**Diagnosis:**
```bash
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates
```

**Fix:**
```bash
# Force renewal
certbot renew --force-renewal

# Or for specific domain
certbot certonly --nginx -d example.com --force-renewal
```

## Problem: Hostname Mismatch

**Symptoms:**
- "SSL_ERROR_BAD_CERT_DOMAIN"
- "The certificate is not valid for the requested resource"

**Diagnosis:**
```bash
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -subject -ext subjectAltName
```

**Fix:**
Get a new certificate that includes all required domains:
```bash
certbot certonly --nginx -d example.com -d www.example.com -d api.example.com
```

## Problem: Mixed Content

**Symptoms:**
- Page loads but some resources blocked
- Console shows "Mixed Content" warnings
- Padlock icon shows warning

**Fix:**
1. Find HTTP resources: Check browser DevTools → Console
2. Change URLs to HTTPS or use protocol-relative (`//example.com/resource`)
3. Add upgrade header: `Content-Security-Policy: upgrade-insecure-requests`

## Problem: Renewal Failing

**Diagnosis:**
```bash
certbot renew --dry-run
cat /var/log/letsencrypt/letsencrypt.log
```

**Common causes:**
- Port 80 blocked (needed for HTTP-01 challenge)
- DNS not pointing to server (for DNS-01)
- Old certbot version
- Server config syntax error

## Problem: Permission Denied

**Symptoms:**
- Web server can't read certificate files
- "permission denied" in server logs

**Fix:**
```bash
# Let's Encrypt default perms are usually fine
# But if needed:
chmod 644 /etc/letsencrypt/live/example.com/fullchain.pem
chmod 600 /etc/letsencrypt/live/example.com/privkey.pem
chown root:ssl-cert /etc/letsencrypt/live/example.com/privkey.pem
```
