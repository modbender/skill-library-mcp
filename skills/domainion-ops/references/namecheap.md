# Namecheap API Reference

Base URL: `https://api.namecheap.com/xml.response` (XML, production)
Sandbox: `https://api.sandbox.namecheap.com/xml.response`

Auth: All requests are GET with query params. No JSON — Namecheap API returns XML.
Get API key: namecheap.com → Profile → Tools → API Access → Enable + whitelist your IP

Required params on every request:
```
ApiUser=$NAMECHEAP_USERNAME
ApiKey=$NAMECHEAP_API_KEY
UserName=$NAMECHEAP_USERNAME
ClientIp=$NAMECHEAP_CLIENT_IP
```

> **IP Whitelist:** Your client IP must be whitelisted in Namecheap API settings. Dynamic IPs require updating the whitelist before each session.

---

## Parsing XML responses

Namecheap returns XML. Use `xmllint` or `python3` to parse:

```bash
# Quick parse with python3
curl -s "https://api.namecheap.com/xml.response?..." | \
  python3 -c "import sys,xml.etree.ElementTree as ET; \
  root=ET.parse(sys.stdin).getroot(); \
  [print(ET.tostring(c, encoding='unicode')) for c in root.iter()]" | head -50

# Or use xmllint (brew install libxml2)
curl -s "https://api.namecheap.com/xml.response?..." | xmllint --format -
```

---

## Domain Operations

### Check domain availability
```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.check\
&DomainList=example.com,example.net"
```

### List domains in account
```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.getList\
&PageSize=100&Page=1"
```

### Get domain info
```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.getInfo\
&DomainName=example.com"
```

### Register a domain
```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.create\
&DomainName=example.com&Years=1\
&RegistrantFirstName=John&RegistrantLastName=Doe\
&RegistrantAddress1=123 Main St&RegistrantCity=Anytown\
&RegistrantStateProvince=CA&RegistrantPostalCode=90210\
&RegistrantCountry=US&RegistrantPhone=+1.5555555555\
&RegistrantEmailAddress=admin@example.com\
&TechFirstName=John&TechLastName=Doe\
&TechAddress1=123 Main St&TechCity=Anytown\
&TechStateProvince=CA&TechPostalCode=90210\
&TechCountry=US&TechPhone=+1.5555555555\
&TechEmailAddress=tech@example.com\
&AdminFirstName=John&AdminLastName=Doe\
&AdminAddress1=123 Main St&AdminCity=Anytown\
&AdminStateProvince=CA&AdminPostalCode=90210\
&AdminCountry=US&AdminPhone=+1.5555555555\
&AdminEmailAddress=admin@example.com\
&AuxBillingFirstName=John&AuxBillingLastName=Doe\
&AuxBillingAddress1=123 Main St&AuxBillingCity=Anytown\
&AuxBillingStateProvince=CA&AuxBillingPostalCode=90210\
&AuxBillingCountry=US&AuxBillingPhone=+1.5555555555\
&AuxBillingEmailAddress=billing@example.com"
```

### Renew domain
```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.renew\
&DomainName=example.com&Years=1"
```

### Get auth/EPP code (for transfer out)
```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.getRegistrarLock\
&DomainName=example.com"
# Then unlock, then request EPP via:
# Command=namecheap.domains.transfer.getStatus (after initiating transfer)
```

---

## Nameserver Operations

### Set custom nameservers
```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.dns.setCustom\
&SLD=example&TLD=com\
&Nameservers=ns1.cloudflare.com,ns2.cloudflare.com"
```
> Note: Split domain into SLD (`example`) and TLD (`com`) separately.

### Reset to Namecheap default nameservers
```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.dns.setDefault\
&SLD=example&TLD=com"
```

### Get current nameservers
```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.dns.getList\
&SLD=example&TLD=com"
```

---

## DNS Record Operations

> Only works when using Namecheap BasicDNS or PremiumDNS (their nameservers). Custom NS → manage DNS at that NS provider.

### Get all DNS records
```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.dns.getHosts\
&SLD=example&TLD=com"
```

### Set DNS records (replaces ALL existing records)

> ⚠️ Namecheap's `setHosts` REPLACES the entire zone. Always GET existing records first and include them in your PUT.

```bash
# Build full record set and submit:
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.dns.setHosts\
&SLD=example&TLD=com\
&HostName1=@&RecordType1=A&Address1=1.2.3.4&TTL1=300\
&HostName2=www&RecordType2=CNAME&Address2=example.com.&TTL2=300\
&HostName3=@&RecordType3=MX&Address3=mail.example.com.&TTL3=300&MXPref3=10"
```

**Namecheap record type names:**

| Type | RecordType value | Notes |
|---|---|---|
| A | `A` | |
| AAAA | `AAAA` | |
| CNAME | `CNAME` | |
| MX | `MX` | Add `MXPref{N}` param |
| TXT | `TXT` | URL-encode spaces |
| NS | `NS` | Subdomain delegation |
| SRV | `SRV` | |
| URL redirect | `URL` | 301 redirect |
| URL (frame) | `FRAME` | iframe masking |

### Adding a single record (safe workflow)

Since setHosts replaces all records, always:
1. GET current hosts
2. Parse all existing records
3. Append your new record
4. Submit the full set via setHosts

```bash
# Step 1: get current
CURRENT=$(curl -s "https://api.namecheap.com/xml.response?...\
&Command=namecheap.domains.dns.getHosts&SLD=example&TLD=com")

# Step 2: parse + rebuild (do this in python or manually)
# Step 3: setHosts with all records + new one
```

---

## URL Forwarding (Redirect)

Add via `setHosts` with `RecordType=URL`:

```bash
curl -s "https://api.namecheap.com/xml.response?\
ApiUser=$NAMECHEAP_USERNAME&ApiKey=$NAMECHEAP_API_KEY\
&UserName=$NAMECHEAP_USERNAME&ClientIp=$NAMECHEAP_CLIENT_IP\
&Command=namecheap.domains.dns.setHosts\
&SLD=example&TLD=com\
&HostName1=@&RecordType1=URL&Address1=https://target.com&TTL1=300"
```

---

## Useful Notes

- **SLD/TLD split:** Always split `example.com` → `SLD=example&TLD=com`. For `sub.example.co.uk` → `SLD=sub.example&TLD=co.uk`
- **setHosts = full replace:** Most dangerous call — always GET first
- **IP whitelist:** Must update before API use if on dynamic IP. Check: `curl ifconfig.me`
- **XML output:** No JSON option. Parse with `xmllint --format -` or python `xml.etree.ElementTree`
- **Sandbox:** `api.sandbox.namecheap.com` — requires separate sandbox account registration at namecheap.com/sandbox
- **Rate limit:** 20 requests/minute for most commands; domain registration is 3/minute
- **DNSSEC:** Available via API (`namecheap.domains.dns.setHosts` with DNSSEC params) — see Namecheap docs for DS record format
