# CDN Security Hardening

## SSL/TLS Configuration

### Minimum Requirements
- TLS 1.2+ only (disable TLS 1.0, 1.1)
- Disable weak ciphers (RC4, 3DES, CBC mode ciphers)
- Enable HSTS: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- Use modern certificate (RSA 2048+ or ECDSA)

### Certificate Management
- Monitor expiration dates (alert at 30, 14, 7 days)
- Automate renewal via ACME/Let's Encrypt
- Verify propagation to all edge nodes after renewal

## Origin Protection

### Hide Origin IP
- Never expose origin server IP in DNS
- Use CDN's origin shield feature
- Configure firewall to only accept CDN IPs

### Authenticated Origin Pulls
```
# Cloudflare: Authenticated Origin Pulls
# Origin verifies requests come from Cloudflare using client cert

# CloudFront: Custom header
# Add secret header in CloudFront, validate at origin
X-Origin-Verify: your-secret-token
```

### Origin Firewall Rules
```bash
# Only allow CDN IPs (example for Cloudflare)
# Get current IPs: https://www.cloudflare.com/ips/
iptables -A INPUT -p tcp --dport 443 -s 103.21.244.0/22 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j DROP
```

## DDoS & Rate Limiting

### Rate Limiting Rules
| Endpoint | Threshold | Action |
|----------|-----------|--------|
| `/login` | 5 req/min per IP | Challenge/block |
| `/api/*` | 100 req/min per IP | Throttle |
| `/signup` | 3 req/min per IP | Challenge |
| General | 1000 req/min per IP | Log, then block |

### Bot Management
- Allow legitimate bots (Googlebot, Bingbot) via user-agent + IP verification
- Challenge suspicious patterns (headless browsers, rapid requests)
- Block known bad bot signatures

## WAF Configuration

### OWASP Core Rule Set
Enable these rule categories:
- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)
- Local File Inclusion (LFI)
- Remote Code Execution (RCE)
- Protocol violations

### Custom Rules
```
# Block requests with suspicious patterns
if (request.uri contains "wp-admin" and not client.ip in whitelist) {
  block
}

# Require specific headers for API
if (request.uri starts_with "/api/" and not request.headers["X-API-Key"]) {
  return 403
}
```

## Security Headers

Add these via CDN edge:
```
# Content Security Policy
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'

# Prevent clickjacking
X-Frame-Options: DENY

# Prevent MIME sniffing
X-Content-Type-Options: nosniff

# Referrer policy
Referrer-Policy: strict-origin-when-cross-origin

# Permissions policy
Permissions-Policy: geolocation=(), microphone=()
```

## Cache Security

### Prevent Cache Poisoning
- Normalize cache keys (strip tracking params)
- Validate `Vary` headers
- Never cache based on user-controllable headers without validation

### Sensitive Data
- **NEVER cache:** Auth responses, tokens, user-specific data
- Use `Cache-Control: no-store` for sensitive endpoints
- Audit cache keys regularly
