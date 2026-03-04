# Infrastructure Security Audits

## Cloud Configuration Checklist

### AWS/GCP/Azure
- [ ] No public S3 buckets/GCS buckets with sensitive data
- [ ] IAM roles follow least-privilege principle
- [ ] MFA enabled for all console access
- [ ] Root/owner account locked down, not used for daily operations
- [ ] CloudTrail/Audit logs enabled
- [ ] VPC flow logs enabled for forensics
- [ ] Security groups don't allow 0.0.0.0/0 on sensitive ports
- [ ] KMS keys rotate automatically
- [ ] No access keys older than 90 days

### Hetzner/VPS/Bare Metal
- [ ] SSH key-only auth (password disabled)
- [ ] SSH on non-standard port
- [ ] fail2ban or equivalent active
- [ ] Firewall rules explicit (deny by default)
- [ ] Automatic security updates enabled
- [ ] Root login disabled
- [ ] Regular user with sudo for admin tasks

## Container Security

### Docker
- [ ] Not running as root inside container
- [ ] Using official/verified base images
- [ ] Minimal base images (alpine, distroless)
- [ ] No secrets in Dockerfile or image layers
- [ ] Resource limits set (memory, CPU)
- [ ] Read-only filesystem where possible
- [ ] Health checks defined

### Kubernetes
- [ ] Pod security policies/standards enforced
- [ ] Network policies segment workloads
- [ ] Secrets stored in external vault (not K8s secrets)
- [ ] RBAC configured properly
- [ ] Admission controllers enabled
- [ ] Container images from trusted registry only

## Network Security

- [ ] TLS 1.2+ everywhere (no SSL, no TLS 1.0/1.1)
- [ ] Strong cipher suites only
- [ ] HSTS enabled with preload
- [ ] Certificate expiry monitoring
- [ ] Internal services not exposed to internet
- [ ] Database ports not publicly accessible
- [ ] API rate limiting on auth endpoints

## Code Security

### Pre-Commit Checks
- [ ] Secrets scanning (no API keys, passwords in code)
- [ ] Dependency vulnerability check
- [ ] SAST for obvious vulnerabilities

### CI/CD Pipeline
- [ ] Dependency scanning on every build
- [ ] Container image scanning
- [ ] No secrets in CI/CD logs
- [ ] Signed commits required (optional but recommended)
- [ ] Branch protection on main/production

## Access Control

- [ ] MFA mandatory for all users
- [ ] Password policy enforced (length, complexity)
- [ ] Session timeout configured
- [ ] Privileged access logged
- [ ] Service accounts have minimal permissions
- [ ] Offboarding revokes access within 24h
- [ ] Regular access reviews (quarterly minimum)

## Logging & Monitoring

### Minimum Viable Logging
- [ ] Authentication events (login success/failure)
- [ ] Authorization events (access denied)
- [ ] Admin actions (user create/delete, permission changes)
- [ ] Data access to sensitive tables
- [ ] API calls with request/response metadata
- [ ] Error/exception logs (without sensitive data)

### Alert Triggers
- [ ] Failed login spikes
- [ ] New admin user created
- [ ] Firewall rule changes
- [ ] Unusual outbound traffic
- [ ] Database queries to sensitive tables from unexpected sources
