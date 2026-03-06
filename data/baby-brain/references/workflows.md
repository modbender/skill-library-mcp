# BABY Brain - Workflow Guides

## Overview

This guide provides step-by-step workflows for common tasks using BABY Brain. Each workflow includes prerequisites, steps, and expected outcomes.

---

## 1. Security Assessment Workflow

### Objective
Perform a complete security assessment of a target domain.

### Prerequisites
- Authorized target
- Network connectivity
- Tools: nmap, nuclei, theHarvester (auto-installed)

### Steps

```bash
# Step 1: Reconnaissance
bash ~/baby-brain/scripts/research.sh osint target.com

# Step 2: Port scanning
bash ~/baby-brain/scripts/security.sh scan target.com

# Step 3: Subdomain enumeration
bash ~/baby-brain/scripts/research.sh osint target.com | grep -E "\."

# Step 4: Vulnerability scanning
bash ~/baby-brain/scripts/security.sh scan target.com --type full

# Step 5: Generate comprehensive report
bash ~/baby-brain/scripts/security.sh audit --output ./security_report
```

### Expected Outputs
- `osint/` directory with subdomains, ports, DNS, technologies
- `vulnscan/` directory with nikto, nuclei, nmap results
- `security_report/` with audit summary

### Duration
30-60 minutes (depending on target size)

---

## 2. Shopping Automation Workflow

### Objective
Automate purchasing a gift card or product.

### Prerequisites
- Boss profile configured (`~/.baby-brain/shopping/boss-profile.json`)
- Payment method set up
- Valid URLs

### Steps

```bash
# Step 1: Configure boss profile (if not done)
cat > ~/.baby-brain/shopping/boss-profile.json << 'EOF'
{
  "name": "Boss",
  "email": "boss@gmail.com",
  "phone": "+1234567890",
  "preferences": {
    "shopping": {
      "max_limit": 100,
      "preferred_platforms": ["amazon", "steam"]
    }
  }
}
EOF

# Step 2: Test gift card purchase (dry run)
bash ~/baby-brain/scripts/shopping.sh giftcard \
  --platform amazon --amount 10 --dry-run

# Step 3: Actual purchase (when ready)
bash ~/baby-brain/scripts/shopping.sh giftcard \
  --platform amazon --amount 10 \
  --recipient "email@example.com"

# Step 4: Verify purchase
bash ~/baby-brain/scripts/shopping.sh track --all
```

### Expected Outputs
- Gift card code delivered to email
- Order confirmation logged

### Duration
2-5 minutes

---

## 3. WhatsApp Broadcast Workflow

### Objective
Send the same message to multiple WhatsApp groups.

### Prerequisites
- WhatsApp gateway linked and working
- Groups approved in config

### Steps

```bash
# Step 1: List available groups
bash ~/baby-brain/scripts/whatsapp.sh groups --list

# Step 2: Draft message
MESSAGE="🎉 Important Announcement! 🎉

Hello everyone! This is a test broadcast message from BABY Brain.

- Feature 1: Complete automation
- Feature 2: Multi-group support
- Feature 3: 100% reliable

Best regards,
BABY Brain 🤖"

# Step 3: Send broadcast (test first)
echo "$MESSAGE" | bash ~/baby-brain/scripts/whatsapp.sh broadcast \
  --message "$(cat)" --groups=ALL --dry-run

# Step 4: Send for real
echo "$MESSAGE" | bash ~/baby-brain/scripts/whatsapp.sh broadcast \
  --message "$(cat)" --groups=ALL
```

### Expected Outputs
- Message delivered to all configured groups
- Delivery confirmation

### Duration
1-2 minutes

---

## 4. System Health Monitoring Workflow

### Objective
Monitor system resources and get alerts.

### Prerequisites
- OpenClaw installed
- Gateway running

### Steps

```bash
# Step 1: Quick health check
bash ~/baby-brain/scripts/system.sh health

# Step 2: Start monitoring in background
bash ~/baby-brain/scripts/system.sh monitor \
  --cpu 80 --memory 90 --disk 85 \
  --duration 3600 &

# Step 3: Check diagnostics if issues arise
bash ~/baby-brain/scripts/system.sh diag --verbose

# Step 4: Auto-fix issues
bash ~/baby-brain/scripts/system.sh fix
```

### Expected Outputs
- Health check shows CPU, memory, disk, services status
- Monitoring logs alerts when thresholds exceeded
- Fixes applied automatically

### Duration
Ongoing (monitoring can run indefinitely)

---

## 5. Web Scraping Workflow

### Objective
Extract structured data from a website.

### Prerequisites
- Target URL
- Understanding of page structure

### Steps

```bash
# Step 1: Fetch page
bash ~/baby-brain/scripts/web.sh fetch \
  --url "https://example.com/products" \
  --output ./raw_page.html

# Step 2: Inspect structure (view first 50 lines)
head -50 ./raw_page.html

# Step 3: Extract data using selectors
# Example: Extract all product names
grep -o 'class="product-name"[^>]*>[^<]*' ./raw_page.html > products.txt

# Step 4: Use web.sh for cleaner extraction
bash ~/baby-brain/scripts/web.sh scrape \
  --url "https://example.com/products" \
  --selector ".product-card"

# Step 5: Save structured data
bash ~/baby-brain/scripts/web.sh api \
  --url "https://api.example.com/data" \
  --output data.json
```

### Expected Outputs
- Raw HTML saved
- Extracted data in text/JSON format

### Duration
5-15 minutes

---

## 6. Research & OSINT Workflow

### Objective
Gather intelligence on a target (person, company, domain).

### Prerequisites
- Target name/domain
- Legal authorization (for security research)

### Steps

```bash
# Step 1: Domain OSINT
bash ~/baby-brain/scripts/research.sh osint target.com

# Step 2: Email harvesting
bash ~/baby-brain/scripts/research.sh emails \
  --domain targetcompany.com

# Step 3: Social media search
bash ~/baby-brain/scripts/research.sh social \
  --username "targetusername"

# Step 4: Web search
bash ~/baby-brain/scripts/research.sh search \
  --query "target company news" --limit 20

# Step 5: Generate report
bash ~/baby-brain/scripts/research.sh report \
  --topic "Target Intelligence Report"

# Step 6: Compile all findings
mkdir -p osint_complete
cp -r osint_* osint_complete/
cp emails_* osint_complete/
cp search_* osint_complete/
cat osint_complete/*/README.md > osint_complete/summary.md
```

### Expected Outputs
- Complete OSINT dossier
- Email list
- Social profiles
- News mentions
- Comprehensive report

### Duration
30-60 minutes

---

## 7. API Testing Workflow

### Objective
Test API endpoints for functionality and security.

### Prerequisites
- API documentation
- Test endpoints (staging/dev)

### Steps

```bash
# Step 1: Test basic connectivity
bash ~/baby-brain/scripts/web.sh test \
  --url "https://api.example.com/health"

# Step 2: GET request
bash ~/baby-brain/scripts/web.sh api \
  --url "https://api.example.com/users"

# Step 3: POST with data
bash ~/baby-brain/scripts/web.sh api \
  --url "https://api.example.com/users" \
  --method POST \
  --data '{"name": "Test", "email": "test@example.com"}' \
  --output create_user.json

# Step 4: Check response format
cat create_user.json | python3 -m json.tool

# Step 5: Test authentication
bash ~/baby-brain/scripts/web.sh api \
  --url "https://api.example.com/protected" \
  --headers "Authorization: Bearer YOUR_TOKEN"

# Step 6: Document findings
cat > api_test_results.md << 'EOF'
# API Test Results

## Health Check
- Endpoint: /health
- Status: 200 OK
- Response: {"status": "healthy"}

## Create User
- Endpoint: /users (POST)
- Status: 201 Created
- Response: {"id": 123, "name": "Test"}
EOF
```

### Expected Outputs
- API response codes and times
- JSON data extracts
- Authentication test results
- Documentation

### Duration
15-30 minutes

---

## 8. Complete Purchase Workflow

### Objective
Buy a product from start to finish.

### Prerequisites
- Product URL
- Payment configured
- Shipping address configured

### Steps

```bash
# Step 1: Check cart
bash ~/baby-brain/scripts/shopping.sh cart --list

# Step 2: Add product to cart
bash ~/baby-brain/scripts/shopping.sh cart --add "PRODUCT_ID"

# Step 3: Verify cart
bash ~/baby-brain/scripts/shopping.sh cart --list

# Step 4: Checkout (dry run first)
bash ~/baby-brain/scripts/shopping.sh checkout --dry-run

# Step 5: Complete purchase
bash ~/baby-brain/scripts/shopping.sh checkout

# Step 6: Track order
bash ~/baby-brain/scripts/shopping.sh track --all
```

### Expected Outputs
- Order confirmation
- Order ID for tracking

### Duration
5-10 minutes

---

## 9. Security Hardening Workflow

### Objective
Assess and improve system security posture.

### Prerequisites
- Root/sudo access
- Configuration backup

### Steps

```bash
# Step 1: Full diagnostic
bash ~/baby-brain/scripts/system.sh diag --verbose

# Step 2: Run security audit
bash ~/baby-brain/scripts/security.sh hardening --output ./hardening_report

# Step 3: Apply fixes
bash ~/baby-brain/scripts/system.sh fix

# Step 4: Create backup
bash ~/baby-brain/scripts/system.sh backup

# Step 5: Schedule regular checks
# Add to crontab:
# 0 9 * * * ~/baby-brain/scripts/system.sh health >> ~/logs/health.log
# 0 2 * * 0 ~/baby-brain/scripts/system.sh clean --no-logs
```

### Expected Outputs
- Diagnostic report
- Hardening recommendations
- Backup archive
- Scheduled monitoring

### Duration
30-60 minutes + ongoing monitoring

---

## 10. Data Pipeline Workflow

### Objective
Extract, transform, and load (ETL) data.

### Prerequisites
- Source data
- Transformation rules
- Destination ready

### Steps

```bash
# Step 1: Extract data
bash ~/baby-brain/scripts/web.sh api \
  --url "https://api.example.com/data" \
  --output raw_data.json

# Step 2: Transform (using Python)
python3 << 'PYEOF'
import json

# Load data
with open('raw_data.json') as f:
    data = json.load(f)

# Transform
transformed = []
for item in data:
    transformed.append({
        'id': item['user_id'],
        'name': item['full_name'].title(),
        'email': item['email'].lower(),
        'active': item['is_verified'],
        'created': item['created_at'][:10]  # YYYY-MM-DD
    })

# Save
with open('transformed_data.json', 'w') as f:
    json.dump(transformed, f, indent=2)
PYEOF

# Step 3: Convert format
bash ~/baby-brain/scripts/web.sh json \
  --file transformed_data.json \
  --output transformed_data.csv

# Step 4: Validate
automation.sh validate --file transformed_data.csv
```

### Expected Outputs
- Raw JSON
- Transformed JSON
- CSV export
- Validation report

### Duration
15-30 minutes

---

## Workflow Best Practices

### 1. Always Dry Run First
```bash
# For dangerous operations
command --dry-run

# Verify output
cat dry_run_output

# Only then run for real
command
```

### 2. Save Outputs
```bash
# Always capture logs
command > output.log 2>&1

# Use timestamps
command > "output_$(date +%Y%m%d_%H%M%S).txt"
```

### 3. Document Everything
```bash
# Create workflow log
cat > workflow_log.md << 'EOF'
# Workflow: [Name]
# Date: YYYY-MM-DD
# Target: [What was processed]

## Steps Executed
1. Step 1
2. Step 2

## Results
- Success: [What worked]
- Issues: [What failed]

## Next Actions
1. Todo
EOF
```

### 4. Error Handling
```bash
# Check for failures
command || echo "Command failed, but continuing..."

# Exit on critical errors
command || exit 1
```

---

## Custom Workflows

### Creating Custom Workflows

Save this as `workflows/custom.yaml`:

```yaml
version: '1.0'
name: my-custom-workflow

steps:
  - name: Step 1
    command: bash ~/baby-brain/scripts/web.sh fetch --url "{{.input_url}}"
    output: step1.html

  - name: Step 2
    command: grep -o 'pattern' step1.html > step2.txt
    depends: step1

  - name: Step 3
    command: python3 process.py step2.txt
    depends: step2
    output: results.json
```

Run with:
```bash
automation.sh workflow --file workflows/custom.yaml
```

---

## Troubleshooting Workflows

| Issue | Solution |
|-------|----------|
| Command hangs | Add `--timeout 30` |
| Permission denied | Check file permissions |
| No output | Check verbose mode |
| Wrong format | Use `--format json` |
| Slow execution | Reduce `--threads` |

---

## Workflow Templates

### Template 1: Research Pipeline
```bash
# 1. OSINT gathering
research.sh osint TARGET

# 2. Data extraction
web.sh api URL --output data.json

# 3. Processing
python3 process.py data.json

# 4. Report generation
research.sh report --topic "Analysis"
```

### Template 2: Security Audit
```bash
# 1. Recon
security.sh recon TARGET

# 2. Scan
security.sh scan TARGET

# 3. Test
security.sh sqli URL

# 4. Report
security.sh audit --output REPORT
```

### Template 3: Shopping Automation
```bash
# 1. Search
shopping.sh search QUERY

# 2. Monitor price
shopping.sh monitor URL --target-price LIMIT

# 3. Buy when ready
shopping.sh buy URL

# 4. Track
shopping.sh track ORDER_ID
```

---

*Last Updated: February 2026*
