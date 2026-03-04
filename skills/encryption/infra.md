# Infrastructure Encryption Patterns

## TLS Certificate Auto-Renewal

### Certbot with systemd timer
```bash
# /etc/systemd/system/certbot-renewal.timer
[Unit]
Description=Certbot renewal timer

[Timer]
OnCalendar=*-*-* 02:00:00
RandomizedDelaySec=3600
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# /etc/systemd/system/certbot-renewal.service
[Unit]
Description=Certbot renewal

[Service]
Type=oneshot
ExecStart=/usr/bin/certbot renew --quiet --deploy-hook "systemctl reload nginx"
```

### Monitor expiry (cron check)
```bash
#!/bin/bash
DOMAIN="example.com"
DAYS_WARN=14

EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | \
         openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt $DAYS_WARN ]; then
    echo "ALERT: $DOMAIN cert expires in $DAYS_LEFT days"
fi
```

## HashiCorp Vault Policies

### Least privilege service policy
```hcl
# policy: myapp-prod
path "secret/data/myapp/prod/*" {
  capabilities = ["read"]
}

path "database/creds/myapp-prod" {
  capabilities = ["read"]
}

# Deny everything else implicitly
```

### Create and assign policy
```bash
vault policy write myapp-prod myapp-prod.hcl
vault token create -policy=myapp-prod -period=24h
```

### Auto-unseal with AWS KMS
```hcl
# vault.hcl
seal "awskms" {
  region     = "eu-west-1"
  kms_key_id = "alias/vault-unseal"
}
```

## mTLS Between Services

### Generate CA and certs
```bash
# Create CA
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "/CN=Internal CA"

# Generate service cert
openssl genrsa -out service.key 2048
openssl req -new -key service.key -out service.csr -subj "/CN=myservice.internal"
openssl x509 -req -in service.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
        -out service.crt -days 365 -sha256
```

### Nginx mTLS config
```nginx
server {
    listen 443 ssl;
    
    ssl_certificate /etc/nginx/certs/service.crt;
    ssl_certificate_key /etc/nginx/certs/service.key;
    
    # Require client cert
    ssl_client_certificate /etc/nginx/certs/ca.crt;
    ssl_verify_client on;
    
    # Modern TLS only
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
}
```

## Encrypted Backups

### Backup with age encryption
```bash
#!/bin/bash
BACKUP_KEY="age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
DATE=$(date +%Y%m%d)

# Dump and encrypt
pg_dump mydb | age -r $BACKUP_KEY -o backup-$DATE.sql.age

# Verify decryption works (test with first 1KB)
age -d -i /path/to/key backup-$DATE.sql.age | head -c 1024 > /dev/null
if [ $? -ne 0 ]; then
    echo "ALERT: Backup decryption verification failed!"
    exit 1
fi

# Upload to cold storage
aws s3 cp backup-$DATE.sql.age s3://backups-encrypted/
```

### Verify backup is actually encrypted
```bash
# Should NOT show readable SQL
head -c 100 backup-$DATE.sql.age | file -
# Expected: "data" not "ASCII text"
```

## Secret Rotation Script

```bash
#!/bin/bash
# Rotate database password with zero downtime

NEW_PASS=$(openssl rand -base64 32)

# 1. Add new password to database (keeps old valid)
psql -c "ALTER USER appuser WITH PASSWORD '$NEW_PASS';"

# 2. Update in Vault
vault kv put secret/myapp/db password="$NEW_PASS"

# 3. Rolling restart of app pods (they'll pick up new secret)
kubectl rollout restart deployment/myapp

# 4. After grace period, invalidate old password
sleep 300
# (old sessions will have reconnected by now)
```

## TLS Hardening Check

```bash
#!/bin/bash
# Quick TLS audit
DOMAIN=$1

# Check protocols
echo "=== Protocols ==="
nmap --script ssl-enum-ciphers -p 443 $DOMAIN | grep -E "TLSv|SSLv"

# Check certificate
echo "=== Certificate ==="
echo | openssl s_client -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates -subject -issuer

# Check headers
echo "=== Security Headers ==="
curl -sI https://$DOMAIN | grep -iE "strict-transport|content-security|x-frame"
```

## Compliance Evidence Generation

```bash
#!/bin/bash
# Generate SOC2/PCI-DSS evidence report

echo "# Encryption Evidence Report - $(date)" > evidence.md
echo "" >> evidence.md

echo "## TLS Configuration" >> evidence.md
echo "\`\`\`" >> evidence.md
testssl.sh --quiet --severity HIGH example.com >> evidence.md
echo "\`\`\`" >> evidence.md

echo "## Encryption at Rest" >> evidence.md
echo "### Database" >> evidence.md
psql -c "SHOW ssl;" >> evidence.md
echo "### Disk" >> evidence.md
lsblk -o NAME,FSTYPE,MOUNTPOINT | grep crypt >> evidence.md

echo "## Key Rotation Log (last 90 days)" >> evidence.md
vault kv metadata get -format=json secret/myapp | jq '.data.versions' >> evidence.md
```
