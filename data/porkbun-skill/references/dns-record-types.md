# DNS Record Types Reference

Quick reference for common DNS record types and field requirements.

## Record Types

### A (Address)
Maps a hostname to an IPv4 address.
- **name**: Hostname (e.g., "www", "@" for root, "*" for wildcard)
- **content**: IPv4 address (e.g., "1.1.1.1")
- **ttl**: Time to live in seconds (min 600, default 600)

### AAAA (IPv6 Address)
Maps a hostname to an IPv6 address.
- **name**: Hostname
- **content**: IPv6 address (e.g., "2001:0db8:85a3:0000:0000:8a2e:0370:7334")
- **ttl**: Time to live

### CNAME (Canonical Name)
Creates an alias for another domain name.
- **name**: Alias hostname (e.g., "www")
- **content**: Target domain (e.g., "example.com")
- **ttl**: Time to live

### MX (Mail Exchange)
Specifies mail servers for the domain.
- **name**: Usually "@" (root domain)
- **content**: Mail server hostname (e.g., "mail.example.com")
- **prio**: Priority (lower = higher preference, e.g., 10, 20)
- **ttl**: Time to live

### TXT (Text)
Stores text data, commonly used for SPF, DKIM, verification.
- **name**: Hostname
- **content**: Text string (quotes for spaces, e.g., "v=spf1 include:_spf.google.com ~all")
- **ttl**: Time to live

### NS (Name Server)
Specifies authoritative name servers for the domain.
- **name**: Usually "@" (at delegation points) or subdomain name
- **content**: Nameserver hostname (e.g., "ns1.example.com")
- **ttl**: Time to live

### ALIAS
Similar to CNAME but works at the root domain level.
- **name**: Usually "@"
- **content**: Target domain or hostname
- **ttl**: Time to live

### SRV (Service)
Specifies location of services (e.g., LDAP, VoIP).
- **name**: Service name format: `_service._protocol` (e.g., "_sip._tcp")
- **content**: Priority, weight, port, target (e.g., "10 60 5060 sipserver.example.com")
- **prio**: Not used for SRV
- **ttl**: Time to live

### CAA (Certification Authority Authorization)
Restricts which CAs can issue certificates for your domain.
- **name**: Usually "@"
- **content**: Flags tag value (e.g., "0 issueletsencrypt.org")
- **ttl**: Time to live

### TLSA (TLS Authentication)
Specifies TLS certificate information for DANE.
- **name**: Port format: `_port._protocol` (e.g., "_443._tcp")
- **content**: Certificate usage, selector, matching type, certificate association data
- **ttl**: Time to live

### HTTPS / SVCB (Service Binding)
Modern DNS record types for HTTPS and service binding.
- **name**: Hostname
- **content**: Priority, target, service params
- **ttl**: Time to live

### SSHFP (SSH Fingerprint)
Stores SSH public key fingerprints.
- **name**: Hostname
- **content**: Algorithm, type, fingerprint (hex)
- **ttl**: Time to live

## Common TTL Values

- **300** (5 minutes) - Fast-changing records (dynamic DNS)
- **600** (10 minutes) - Default minimum, common for dynamic records
- **3600** (1 hour) - Standard for most records
- **86400** (24 hours) - Stable records with infrequent changes

## MX Priority Pattern

Typical MX configuration:
- Priority 10: Primary mail server
- Priority 20: Secondary/failover mail server
- Priority 30: Tertiary backup mail server

Email delivery tries lowest priority first.

## Example TXT Records

### SPF (Sender Policy Framework)
```
v=spf1 include:_spf.google.com ~all
v=spf1 ip4:192.0.2.0/24 -all
v=spf1 a mx include:sendgrid.net ~all
```

### Domain Verification
```
google-site-verification=your-verification-token
```

### DKIM
```
k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...
```