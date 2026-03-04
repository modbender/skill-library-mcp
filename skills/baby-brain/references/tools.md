# BABY Brain - Tools Documentation

## Overview

This document describes the tools and utilities integrated into BABY Brain for various operations.

---

## Shell Utilities

### curl

**Purpose**: HTTP requests, API calls, fetching content

**Common Usage**:
```bash
# Basic GET
curl -sL "https://example.com"

# With headers
curl -sI -A "Mozilla/5.0" "https://example.com"

# POST request
curl -sL -X POST -d "key=value" "https://api.example.com"

# With authentication
curl -sL -H "Authorization: Bearer token" "https://api.example.com"

# Download file
curl -sL -o filename.zip "https://example.com/file.zip"

# With proxy
curl -sL --proxy "socks5://127.0.0.1:9050" "https://example.com"
```

**Options**:
| Option | Description |
|--------|-------------|
| `-s` | Silent mode |
| `-L` | Follow redirects |
| `-I` | Fetch headers only |
| `-o` | Output to file |
| `-d` | POST data |
| `-H` | Add header |
| `-A` | User-Agent |
| `--proxy` | Use proxy |
| `--connect-timeout` | Timeout |
| `-v` | Verbose |

---

### wget

**Purpose**: Download files

**Common Usage**:
```bash
# Download file
wget "https://example.com/file.zip"

# Download with custom name
wget -O custom_name.zip "https://example.com/file.zip"

# Download in background
wget -b "https://example.com/largefile.zip"

# Resume download
wget -c "https://example.com/file.zip"

# Mirror website
wget --mirror --convert-links --adjust-extension "https://example.com"
```

---

### jq

**Purpose**: JSON processing

**Common Usage**:
```bash
# Pretty print
cat data.json | jq .

# Extract field
cat data.json | jq '.key'

# Extract nested
cat data.json | jq '.parent.child'

# Array operations
cat data.json | jq '.items[]'

# Filter
cat data.json | jq '.users[] | select(.age > 18)'

# Transform
cat data.json | jq '{name: .user, id: .id}'

# Multiple fields
cat data.json | jq '. | {name, email, city}'

# Output as CSV
cat data.json | jq -r '.[] | [.name, .email] | @csv'
```

---

### yq

**Purpose**: YAML processing

**Common Usage**:
```bash
# Pretty print
cat config.yaml | yq .

# Extract field
cat config.yaml | yq '.server.port'

# Convert to JSON
cat config.yaml | yq -o json

# Convert from JSON
cat data.json | yq -o yaml

# Update value
cat config.yaml | yq '.server.port = 8080' > config_new.yaml
```

---

### grep

**Purpose**: Text pattern matching

**Common Usage**:
```bash
# Basic search
grep "pattern" file.txt

# Case insensitive
grep -i "pattern" file.txt

# Recursive
grep -r "pattern" directory/

# Show line numbers
grep -n "pattern" file.txt

# Count matches
grep -c "pattern" file.txt

# Only filenames
grep -l "pattern" *.txt

# Invert match
grep -v "pattern" file.txt

# Extended regex
grep -E "pattern1|pattern2" file.txt

# Context lines
grep -A 5 -B 2 "pattern" file.txt
```

---

### sed

**Purpose**: Stream editing

**Common Usage**:
```bash
# Replace text
sed 's/old/new/g' file.txt

# In-place edit
sed -i 's/old/new/g' file.txt

# Delete lines
sed '/pattern/d' file.txt

# Print specific lines
sed -n '10,20p' file.txt

# Insert line
sed '5i new line' file.txt

# Append line
sed '$a new line at end' file.txt
```

---

## Security Tools

### nmap

**Purpose**: Network scanning and enumeration

**Common Usage**:
```bash
# Quick scan
nmap -sS target.com

# Detailed scan
nmap -sS -sV -O target.com

# Full port scan
nmap -p- target.com

# Service detection
nmap -sV target.com

# OS detection
nmap -O target.com

# Script scan
nmap --script=vuln target.com

# Output to file
nmap -oN scan_results.txt target.com
```

---

### sqlmap

**Purpose**: SQL injection detection and exploitation

**Common Usage**:
```bash
# Basic test
sqlmap -u "https://example.com/page?id=1"

# POST data
sqlmap -u "https://example.com/login" --data="user=admin&pass=123"

# Enumerate databases
sqlmap -u "url" --dbs

# Enumerate tables
sqlmap -u "url" -D database_name --tables

# Dump data
sqlmap -u "url" -D database_name -T users --dump

# With Tor
sqlmap -u "url" --tor --tor-type=SOCKS5
```

---

### nikto

**Purpose**: Web server vulnerability scanning

**Common Usage**:
```bash
# Basic scan
nikto -h target.com

# SSL scan
nikto -h https://target.com

# Output
nikto -h target.com -o nikto_results.html

# With authentication
nikto -h target.com -id "user:pass"
```

---

### nuclei

**Purpose**: Template-based vulnerability scanning

**Common Usage**:
```bash
# Scan target
nuclei -u target.com

# Scan list
nuclei -list targets.txt

# Specific severity
nuclei -u target.com -severity critical,high

# Output
nuclei -u target.com -o results.txt

# With custom templates
nuclei -u target.com -t ~/templates/
```

---

## Browser Automation

### Chrome/Chromium (Headless)

**Purpose**: Screenshot capture, page rendering

**Common Usage**:
```bash
# Screenshot
chromium --headless --disable-gpu --screenshot=output.png "https://example.com"

# Full page screenshot
chromium --headless --disable-gpu --screenshot=page.png \
  --full-page-screenshot "https://example.com"

# PDF output
chromium --headless --disable-gpu --print-to-pdf=output.pdf "https://example.com"
```

---

### curl_cffi (Python)

**Purpose**: Browser impersonation for WAF bypass

**Python Usage**:
```python
from curl_cffi import requests as curl_requests

# Chrome 120 impersonation
response = curl_requests.get(
    "https://target.com",
    impersonate="chrome120",
    timeout=30
)

# POST request
response = curl_requests.post(
    "https://api.example.com",
    json={"key": "value"},
    impersonate="chrome120"
)

print(response.status_code)
print(response.text)
```

---

## Data Processing

### Python

**Purpose**: General scripting, data processing

**Common Usage**:
```python
# HTTP requests
import requests
response = requests.get("https://api.com")
data = response.json()

# Web scraping
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
links = soup.find_all('a')

# JSON processing
import json
data = json.load(open('file.json'))
json.dump(data, open('output.json', 'w'))

# Data manipulation
import pandas as pd
df = pd.read_csv('data.csv')
df_filtered = df[df['column'] > value]
```

---

### BeautifulSoup

**Purpose**: HTML/XML parsing

**Common Usage**:
```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')

# Find elements
soup.find('div', class_='content')
soup.find_all('a', href=True)

# Extract text
soup.get_text()

# Extract attributes
link = soup.find('a')['href']

# CSS selectors
soup.select('.classname')
soup.select('#idname')
soup.select('div > a')
```

---

## Communication

### openclaw message

**Purpose**: Send messages via configured channels

**Common Usage**:
```bash
# Send WhatsApp message
openclaw message send --channel whatsapp --to "+1234567890" "Hello!"

# Send to group
openclaw message send --channel whatsapp --to "group@whatsapp.net" "Group message"

# With media
openclaw message send --channel whatsapp --to "+123" --media "/path/file.jpg"
```

---

## System Tools

### systemctl

**Purpose**: Service management

**Common Usage**:
```bash
# Check status
systemctl --user status openclaw-gateway

# Start service
systemctl --user start openclaw-gateway

# Stop service
systemctl --user stop openclaw-gateway

# Restart service
systemctl --user restart openclaw-gateway

# Enable on boot
systemctl --user enable openclaw-gateway
```

---

### crontab

**Purpose**: Scheduled task management

**Common Usage**:
```bash
# List cron jobs
crontab -l

# Edit crontab
crontab -e

# Add job
echo "0 2 * * * /path/to/command" | crontab -

# Remove all
crontab -r
```

**Format**: `minute hour day month weekday command`

---

## File Management

### tar

**Purpose**: Archive and compression

**Common Usage**:
```bash
# Create archive
tar -czf archive.tar.gz directory/

# Extract archive
tar -xzf archive.tar.gz

# List contents
tar -tzf archive.tar.gz

# Extract to directory
tar -xzf archive.tar.gz -C /path/to/dir
```

---

### rsync

**Purpose**: File synchronization

**Common Usage**:
```bash
# Sync directories
rsync -avz source/ destination/

# With deletion
rsync -avz --delete source/ destination/

# Over SSH
rsync -avz -e ssh source/ user@host:/path/

# Dry run
rsync -avz --dry-run source/ destination/
```

---

## Network Tools

### ss

**Purpose**: Socket statistics

**Common Usage**:
```bash
# List listening ports
ss -tlnp

# Show all connections
ss -antp

# Show TCP/UDP
ss -t -u

# Summary
ss -s
```

---

### ping

**Purpose**: Network connectivity testing

**Common Usage**:
```bash
# Single ping
ping -c 4 target.com

# Continuous ping
ping target.com

# With timeout
ping -W 5 target.com
```

---

## Text Processing

### awk

**Purpose**: Column-based text processing

**Common Usage**:
```bash
# Print specific column
ls -l | awk '{print $5}'

# Sum column
ls -l | awk '{sum += $5} END {print sum}'

# Filter and print
df | awk '{if ($5 > 80) print $0}'

# Format output
echo "data" | awk '{printf "%-10s %d\n", $1, $2}'
```

---

### sort

**Purpose**: Sort lines

**Common Usage**:
```bash
# Sort alphabetically
sort file.txt

# Numeric sort
sort -n numbers.txt

# Reverse sort
sort -r file.txt

# Remove duplicates
sort -u file.txt

# By column
sort -k2 file.txt
```

---

### uniq

**Purpose**: Remove duplicate lines

**Common Usage**:
```bash
# Remove duplicates
uniq file.txt

# Count occurrences
uniq -c file.txt

# Only duplicates
uniq -d file.txt

# Unique only
uniq -u file.txt
```

---

## Conversion Tools

### pandoc

**Purpose**: Document conversion

**Common Usage**:
```bash
# Markdown to HTML
pandoc input.md -o output.html

# Markdown to PDF
pandoc input.md -o output.pdf

# HTML to Markdown
pandoc input.html -o output.md

# With options
pandoc input.md --standalone -o output.html
```

---

## Encryption

### openssl

**Purpose**: Encryption and certificates

**Common Usage**:
```bash
# Hash file
openssl sha256 file.txt

# Generate key
openssl rand -base64 32

# Encrypt file
openssl enc -aes-256-cbc -salt -in file.txt -out file.enc

# Decrypt file
openssl enc -aes-256-cbc -d -in file.enc -out file.txt

# Check certificate
openssl x509 -in cert.pem -text -noout
```

---

## Tool Installation

### Install Common Tools
```bash
# Ubuntu/Debian
apt update && apt install -y \
    curl wget jq yq \
    nmap nikto \
    chromium chromium-driver \
    python3 python3-pip \
    git rsync tar \
    openssl

# Python packages
pip3 install requests beautifulsoup4 pandas
pip3 install curl_cffi
```

---

## Tool Comparison

| Task | Recommended Tool |
|------|-----------------|
| HTTP requests | curl / requests (Python) |
| JSON processing | jq / Python json |
| YAML processing | yq |
| HTML parsing | BeautifulSoup |
| Network scanning | nmap |
| SQL injection | sqlmap |
| Web vulns | nikto / nuclei |
| Screenshots | chromium headless |
| WAF bypass | curl_cffi |

---

*Last Updated: February 2026*
