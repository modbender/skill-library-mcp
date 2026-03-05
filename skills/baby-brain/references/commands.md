# BABY Brain - Complete Command Reference

## Overview

BABY Brain is the ultimate AI assistant platform combining 34+ skills into one powerful package. This reference covers all available commands and their usage.

---

## Quick Command Map

| Category | Command | Description |
|----------|---------|-------------|
| **General** | `baby-brain` | Main command prefix |
| **Automation** | `automation.sh` | Batch processing, scheduling |
| **Security** | `security.sh` | Recon, scanning, exploits |
| **Shopping** | `shopping.sh` | Gift cards, purchases, tracking |
| **WhatsApp** | `whatsapp.sh` | Messaging, group management |
| **Research** | `research.sh` | OSINT, scraping, analysis |
| **System** | `system.sh` | Health checks, diagnostics |
| **Web** | `web.sh` | Fetching, scraping, APIs |

---

## automation.sh Commands

### Batch Processing
```bash
automation.sh batch --input ./files --operation compress
automation.sh batch --input ./data --operation list
automation.sh batch --input ./data --operation count
automation.sh batch --input ./data --operation delete --pattern "*.tmp"
```

### Scheduling
```bash
automation.sh schedule --task backup --cron "0 2 * * *"
automation.sh schedule --task health --cron "*/5 * * * *"
automation.sh schedule --list
automation.sh schedule --remove "task_name"
```

### Workflow Execution
```bash
automation.sh workflow --file workflow.yaml
```

### Backup
```bash
automation.sh backup --source ~/data --destination ~/backups
automation.sh backup --source ~/data --compress
```

### Sync
```bash
automation.sh sync --source ~/local --destination ~/remote --push
automation.sh sync --source ~/remote --destination ~/local --pull
```

### Clean
```bash
automation.sh clean --all
automation.sh clean --no-logs --no-cache
automation.sh clean --no-temp
```

### Monitor
```bash
automation.sh monitor --directory ~/project --interval 5
```

### Convert
```bash
automation.sh convert --input data.json --output data.csv --from json --to csv
automation.sh convert --input config.yaml --output config.json --from yaml --to json
```

### Validate
```bash
automation.sh validate --file config.json
automation.sh validate --url https://api.example.com
automation.sh validate --type email "user@example.com"
```

### Template
```bash
automation.sh template --type api --name my-api
automation.sh template --type script --name my-script
automation.sh template --type docker
automation.sh template --type README
```

---

## security.sh Commands

### Reconnaissance
```bash
security.sh recon target.com
security.sh recon target.com --output ./report
```

### Vulnerability Scanning
```bash
security.sh scan target.com
security.sh scan target.com --output ./scan_results
security.sh scan target.com --type full --threads 20
```

### SQL Injection Testing
```bash
security.sh sqli "https://target.com/login?id=1"
security.sh sqli "https://target.com/page?id=1" --tor
```

### XSS Testing
```bash
security.sh xss "https://target.com/search?q=test"
```

### WAF Bypass
```bash
security.sh waf target.com
security.sh waf target.com --tor
```

### Security Hardening
```bash
security.sh hardening
security.sh hardening --output ./hardening_report
```

### Security Audit
```bash
security.sh audit
security.sh audit --output ./audit_report
```

### Real-time Monitoring
```bash
security.sh monitor --duration 300
```

---

## shopping.sh Commands

### Gift Cards
```bash
shopping.sh giftcard --platform amazon --amount 10
shopping.sh giftcard --platform steam --amount 25
shopping.sh giftcard --platform apple --amount 50
shopping.sh giftcard --platform netflix --amount 25
```

### Product Purchase
```bash
shopping.sh buy --url "https://amazon.com/dp/B08XYZ..."
shopping.sh buy --url "https://..." --quantity 2
shopping.sh buy --url "https://..." --dry-run
```

### Subscription
```bash
shopping.sh subscribe --service netflix --plan standard
shopping.sh subscribe --service spotify --plan premium
shopping.sh subscribe --service disney-plus
```

### Order Tracking
```bash
shopping.sh track --order-id 123-456789
shopping.sh track --all
```

### Price Monitoring
```bash
shopping.sh monitor --url "https://..." --target-price 99.99
shopping.sh monitor --url "https://..." --interval 300 --duration 86400
```

### Cart Management
```bash
shopping.sh cart --list
shopping.sh cart --clear
shopping.sh cart --add "product_id"
shopping.sh cart --remove "product_id"
```

### Checkout
```bash
shopping.sh checkout --card "4111111111111114"
shopping.sh checkout --address "123 Main St"
shopping.sh checkout --dry-run
```

### Search
```bash
shopping.sh search --query "laptop"
shopping.sh search --query "headphones" --limit 20
```

### Price Comparison
```bash
shopping.sh compare --product "iPhone 15"
```

---

## whatsapp.sh Commands

### Send Message
```bash
whatsapp.sh send --to "+1234567890" --message "Hello!"
whatsapp.sh send --to "group@whatsapp.net" --message "Group message"
```

### Broadcast
```bash
whatsapp.sh broadcast --message "Hello all!"
whatsapp.sh broadcast --message "Announcement" --groups=ALL
whatsapp.sh broadcast --message "Update" --groups="group1,group2"
```

### List Groups
```bash
whatsapp.sh groups --list
whatsapp.sh groups --info "group_jid"
```

### Create Group
```bash
whatsapp.sh create --name "My New Group" --members="+1234567890,+0987654321"
```

### Add/Remove Members
```bash
whatsapp.sh add --group "group_jid" --members="+1111111111"
whatsapp.sh remove --group "group_jid" --members="+1111111111"
```

### Send Media
```bash
whatsapp.sh media --media "/path/to/image.jpg" --to "+1234567890"
whatsapp.sh media --media "/path/to/video.mp4" --to "group@whatsapp.net" --caption "Check this out!"
```

### Group Settings
```bash
whatsapp.sh settings --group "group_jid" --subject "New Name"
whatsapp.sh settings --group "group_jid" --description "Group description"
```

### Message Operations
```bash
whatsapp.sh delete --chat "chat_jid" --message "message_id"
whatsapp.sh pin --chat "chat_jid" --message "message_id"
whatsapp.sh react --chat "chat_jid" --message "message_id" --emoji "👍"
```

### Archive
```bash
whatsapp.sh archive --chat "chat_jid"
whatsapp.sh archive --chat "chat_jid" --unarchive
```

---

## research.sh Commands

### Web Search
```bash
research.sh search --query "latest AI developments"
research.sh search --query "Python tutorials" --limit 20
research.sh search --query "news" --engine google
```

### OSINT Gathering
```bash
research.sh osint target.com
research.sh osint target.com --output ./osint_report
```

### Web Scraping
```bash
research.sh scrape --url "https://example.com"
research.sh scrape --url "https://..." --selector ".product"
```

### Email Harvesting
```bash
research.sh emails --domain company.com
research.sh emails --domain company.com --output ./emails.txt
```

### Social Media OSINT
```bash
research.sh social --username johndoe
research.sh social --username johndoe --platform twitter
```

### News Monitoring
```bash
research.sh news --topic "technology"
research.sh news --topic "AI developments" --limit 15
```

### Report Generation
```bash
research.sh report --topic "Research Summary"
research.sh report --topic "Market Analysis" --format markdown
```

---

## system.sh Commands

### Health Check
```bash
system.sh health
system.sh check
```

### Full Diagnostic
```bash
system.sh diag
system.sh diag --verbose
system.sh diag --output ./diagnostic_report.txt
```

### Auto-Fix
```bash
system.sh fix
system.sh repair
```

### Monitoring
```bash
system.sh monitor --cpu 80 --memory 90 --disk 85 --duration 300
```

### Resource Monitoring
```bash
system.sh cpu --alert 85
system.sh memory --alert 90
system.sh disk --alert 80
```

### Network Diagnostics
```bash
system.sh network
system.sh network-check
```

### Cleanup
```bash
system.sh clean
system.sh clean --no-logs --no-cache
system.sh clean --no-temp
```

### Backup
```bash
system.sh backup
```

### Update
```bash
system.sh update
```

### System Info
```bash
system.sh info
system.sh information
```

### View Logs
```bash
system.sh logs
system.sh logs --lines 100
system.sh logs --file /path/to/logfile
```

---

## web.sh Commands

### Fetch URL
```bash
web.sh fetch --url "https://example.com"
web.sh fetch --url "https://..." --headers
web.sh fetch --url "https://..." --output ./page.html
```

### API Request
```bash
web.sh api --url "https://api.example.com"
web.sh api --url "https://api..." --method POST --data '{"key":"value"}'
web.sh api --url "https://api..." --headers "Authorization: Bearer token"
```

### Web Scraping
```bash
web.sh scrape --url "https://example.com"
web.sh scrape --url "https://..." --selector ".product"
web.sh scrape --url "https://..." --selector ".price" --output prices.txt
```

### Browser Automation
```bash
web.sh browse --url "https://example.com"
web.sh browse --url "https://..." --action screenshot --output screenshot.png
```

### Data Extraction
```bash
web.sh extract --file data.html --pattern "class=\"product\""
```

### Download
```bash
web.sh download --url "https://example.com/file.zip"
web.sh download --url "https://..." --output custom_name.zip --retries 3
```

### Screenshot
```bash
web.sh screenshot --url "https://example.com"
web.sh screenshot --url "https://..." --output screenshot.png --full-page
```

### Extract Images
```bash
web.sh images --url "https://example.com"
web.sh images --url "https://..." --limit 50 --output ./images
```

### HTTP Headers
```bash
web.sh headers --url "https://example.com"
```

### Test Endpoint
```bash
web.sh test --url "https://api.example.com/health"
web.sh test --url "https://..." --method POST --timeout 30
```

### Monitor URL
```bash
web.sh monitor --url "https://example.com"
web.sh monitor --url "https://..." --interval 60 --changes
```

### JSON Processing
```bash
web.sh json --file data.json
web.sh json --file config.json --query "data.settings"
```

---

## Global Options

### Common Options (All Scripts)
| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message |
| `-v, --version` | Show version |
| `--output, -o` | Output file/directory |
| `--format` | Output format (json, csv, markdown, text) |
| `--dry-run` | Simulate without making changes |
| `--verbose` | Verbose output |
| `--quiet` | Minimal output |
| `--timeout` | Timeout in seconds |

### Proxy Options
| Option | Description |
|--------|-------------|
| `--tor` | Route through Tor network |
| `--proxy` | Use specific proxy |
| `--proxychains` | Use proxychains |

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Permission denied |
| 5 | Command/operation failed |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BABY_BRAIN_CONFIG` | Config directory (default: ~/.baby-brain) |
| `BABY_BRAIN_LOG` | Log file path |
| `BABY_BRAIN_DEBUG` | Enable debug mode (1 = true) |

---

## Configuration Files

### Boss Profile (`~/.baby-brain/shopping/boss-profile.json`)
```json
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
```

---

## Tips & Tricks

### 1. Dry Run First
Always use `--dry-run` for destructive operations:
```bash
shopping.sh buy --url "..." --dry-run
automation.sh clean --dry-run
```

### 2. Output to File
Capture results for later analysis:
```bash
security.sh scan target.com --output ./scan_results.md
research.sh osint target.com --output ./intelligence/
```

### 3. Use Aliases
Add to your `.bashrc`:
```bash
alias bb-health='bash ~/baby-brain/scripts/system.sh health'
alias bb-scan='bash ~/baby-brain/scripts/security.sh scan'
alias bb-shop='bash ~/baby-brain/scripts/shopping.sh'
```

### 4. Chain Commands
Use with other tools:
```bash
# Search and then scrape
research.sh search --query "products" && web.sh scrape --url "top_result.com"

# Monitor and alert
system.sh monitor --cpu 90 &
```

### 5. Scheduling with Cron
Add to crontab:
```bash
# Daily health check
0 9 * * * ~/baby-brain/scripts/system.sh health >> ~/baby-brain/logs/health.log

# Weekly backup
0 2 * * 0 ~/baby-brain/scripts/automation.sh backup --source ~/data
```

---

## Troubleshooting

### Command Not Found
Ensure scripts are executable:
```bash
chmod +x ~/baby-brain/scripts/*.sh
```

### Permission Denied
Run with appropriate permissions or use sudo where needed.

### Slow Performance
- Reduce `--threads` for scanning
- Use `--timeout` to limit wait times
- Enable caching where available

### Network Issues
- Use `--tor` for anonymity
- Try `--retries 3` for downloads
- Check firewall settings

---

## See Also

- **SKILL.md**: Main documentation
- **references/tools.md**: Detailed tool documentation
- **references/workflows.md**: Complete workflow guides
- **assets/templates/**: Reusable templates

---

*Last Updated: February 2026*
*Version: 1.0.0*
