# GEO Audit Integrations

## CI/CD Integration

### GitHub Actions

```yaml
name: GEO Audit

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run GEO Audit
        run: |
          python scripts/geo_audit.py ${{ vars.SITE_URL }} --output json > audit.json
      
      - name: Check Score Threshold
        run: |
          SCORE=$(jq '.score' audit.json)
          if [ "$SCORE" -lt 20 ]; then
            echo "GEO score $SCORE below threshold (20)"
            exit 1
          fi
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: geo-audit-report
          path: audit.json
```

### GitLab CI

```yaml
geo_audit:
  script:
    - python scripts/geo_audit.py $CI_ENVIRONMENT_URL --output json > audit.json
    - python scripts/check_threshold.py audit.json --min-score 20
  artifacts:
    reports:
      junit: audit-junit.xml
```

## API Integration

### Webhook Notifications

```python
# config/webhooks.json
{
  "slack": {
    "url": "https://hooks.slack.com/services/...",
    "threshold": 20
  },
  "teams": {
    "url": "https://outlook.office.com/webhook/...",
    "threshold": 20
  }
}
```

### Programmatic Usage

```python
from geo_audit import run_audit

result = run_audit("example.com")
print(f"Score: {result['score']}/{result['total']}")

for dim in result['dimensions']:
    print(f"{dim['name']}: {dim['score']}/{dim['total']}")
```

## Dashboard Integration

### JSON Output Format

```json
{
  "site": "example.com",
  "timestamp": "2024-01-15T10:30:00Z",
  "score": 24,
  "total": 29,
  "grade": "A",
  "dimensions": [
    {
      "name": "AI Accessibility",
      "score": 8,
      "total": 10,
      "percentage": 80,
      "checks": [...]
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "dimension": "Structured Data",
      "issue": "Missing Organization schema",
      "how_to_fix": "Add JSON-LD Organization markup to homepage"
    }
  ]
}
```

### Grafana

Import the dashboard from `assets/grafana-dashboard.json` to visualize:
- Score trends over time
- Dimension breakdowns
- Pass/fail rates by check

## Scheduled Audits

### Cron Setup

```bash
# Daily audit at 6 AM
0 6 * * * cd /path/to/geo-audit && python scripts/geo_audit.py example.com --output json > reports/$(date +\%Y\%m\%d).json
```

### Using Systemd Timer

```ini
# /etc/systemd/system/geo-audit.service
[Unit]
Description=GEO Audit

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /opt/geo-audit/scripts/geo_audit.py example.com
```

```ini
# /etc/systemd/system/geo-audit.timer
[Unit]
Description=Run GEO Audit daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

## Bulk Audits

### From CSV

```csv
site_url,notes
example.com,Main site
blog.example.com,Blog subdomain
shop.example.com,E-commerce
```

```bash
python scripts/batch_audit.py sites.csv --output-dir ./reports/
```

### Competitive Analysis

```bash
# Audit competitors
python scripts/geo_audit.py competitor1.com --output json > reports/competitor1.json
python scripts/geo_audit.py competitor2.com --output json > reports/competitor2.json
python scripts/compare_audits.py reports/*.json --output comparison.html
```

## Export Formats

### PDF Report

```bash
python scripts/geo_audit.py example.com --output html > report.html
wkhtmltopdf report.html report.pdf
```

### CSV for Spreadsheets

```bash
python scripts/geo_audit.py example.com --output json | \
  jq -r '.dimensions[].checks[] | [.dimension, .check, .status, .notes] | @csv' > report.csv
```

## Notifications

### Email Report

```python
# config/email.json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "username": "audits@example.com",
  "to": ["team@example.com"],
  "threshold": 20
}
```

```bash
python scripts/geo_audit.py example.com --notify email
```

### Slack Alert on Score Drop

```bash
python scripts/geo_audit.py example.com --notify slack --compare-with previous.json
```