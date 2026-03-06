# MUKI Quick Reference

## Common Use Cases

### 1. Single Target Assessment
```bash
muki-fingerprint -u https://target.com -o result.json
```

### 2. Batch Scanning
```bash
# Create target list
cat > targets.txt << 'EOF'
https://target1.com
https://target2.com
192.168.1.10
192.168.1.11
EOF

# Scan all
muki-fingerprint -l targets.txt -o batch_results.json
```

### 3. Anonymous Scanning (via Tor)
```bash
# Ensure Tor is running on port 9050
muki-fingerprint -u https://target.com -p socks5://127.0.0.1:9050
```

### 4. Stealth / Low Impact
```bash
# Passive only, no active probes
muki-fingerprint -u https://target.com --no-active --no-dir

# Reduce threads
muki-fingerprint -u https://target.com -t 5
```

### 5. Comprehensive Assessment
```bash
# Full scan with increased threads
muki-fingerprint -u https://target.com -t 50 -o full_report.xlsx
```

## Output Processing

### JSON Analysis
```bash
# Extract fingerprints
cat results.json | jq '.fingerprints[] | {service: .service, version: .version}'

# Find sensitive paths
cat results.json | jq '.sensitive_paths[] | select(.status == 200)'

# Count findings by severity
cat results.json | jq '[.sensitive_data[].type] | group_by(.) | map({type: .[0], count: length})'
```

### Excel Export
Results exported as .xlsx include:
- Summary sheet with statistics
- Assets sheet with all targets
- Fingerprints sheet with identified services
- Paths sheet with accessible endpoints
- Data sheet with extracted sensitive information

## Fingerprint Categories

### Web Technologies
- Frameworks: React, Angular, Vue, Django, Spring, Laravel
- Servers: Apache, Nginx, IIS, Tomcat, Jetty
- CMS: WordPress, Drupal, Joomla, Magento
- WAF: Cloudflare, ModSecurity, AWS WAF, Imperva

### Databases
- MySQL, PostgreSQL, MongoDB, Redis, Elasticsearch
- Oracle, MSSQL, SQLite

### Infrastructure
- Docker, Kubernetes, VMWare
- AWS, Azure, GCP services
- CDN: Cloudflare, Akamai, Fastly

## Sensitive Path Patterns

### Admin Panels
```
/admin
/manage
/manager
/system
/console
/dashboard
/phpmyadmin
```

### Configuration
```
/.env
/config.php
/web.config
/settings.py
```

### Version Control
```
/.git
/.svn
/.hg
/.bzr
```

### Backup Files
```
/backup.sql
/database.tar.gz
/www.zip
/site.bak
```

### API Endpoints
```
/api/v1
/swagger
/actuator
/graphql
```

## Rule Categories

### 疑似漏洞 (Vulnerability Indicators)
- ID parameters (potential SQL injection)
- JSON ID parameters
- Redirect parameters (open redirect)

### 指纹信息 (Fingerprinting)
- URL redirect parameters
- Sensitive admin paths
- Technology indicators

### 敏感信息 (Sensitive Data)
- Password patterns
- Account credentials
- Database connection strings (JDBC)

### 基础信息 (Personal Information)
- Email addresses
- Chinese ID numbers
- Phone numbers
- Bank card numbers
- License plates

## Performance Tuning

### Memory Usage
- Default: ~500MB for 1000 targets
- Reduce with: `-t 10` and batch scanning

### Network Bandwidth
- Active scanning: ~50KB per target
- Passive scanning: ~10KB per target

### Scan Speed
- Default threads (20): ~50 targets/minute
- Max threads (100): ~200 targets/minute
- Tor proxy: ~10 targets/minute

## Integration Examples

### With Nmap
```bash
# Port scan first, then fingerprint
nmap -p- target.com -oG - | awk '/Up$/ {print $2}' > targets.txt
muki-fingerprint -l targets.txt
```

### With Nuclei
```bash
# Use MUKI to find targets, Nuclei for CVEs
muki-fingerprint -l targets.txt -o muki.json
cat muki.json | jq -r '.fingerprints[] | select(.service == "WordPress") | .target' | nuclei -t cves/
```

### With Metasploit
```bash
# Import services to Metasploit
muki-fingerprint -l targets.txt -o muki.json
cat muki.json | jq -r '.fingerprints[] | "\(.target) \(.service) \(.version)"' >> msf_targets.txt
```

## Troubleshooting

### "Connection refused"
- Check if target is reachable: `curl -I https://target.com`
- Verify proxy settings

### "Out of memory"
- Reduce thread count: `-t 10`
- Process targets in smaller batches

### False positives
- Manually verify findings
- Check context of extracted data
- Review Rules.yml for pattern specificity

### Slow scan
- Increase threads: `-t 50`
- Disable passive fingerprinting if not needed: `-x`
- Check network latency to target
