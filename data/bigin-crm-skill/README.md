# ClawBigin — Bigin CRM Skill for OpenClaw

A comprehensive Bigin CRM skill for OpenClaw that provides CLI and programmatic interfaces for managing pipelines, contacts, companies, tasks, events, and calls through the Bigin REST API v2.

## 🚀 Features

- **🔐 OAuth2 Authentication** — Secure token-based authentication with auto-refresh
- **📊 Pipeline Management** — Full CRUD operations for sales pipelines (core feature)
- **👥 Contact Management** — Create, update, search, and bulk import contacts
- **🏢 Company Management** — Manage companies/accounts with contact associations
- **✅ Task Management** — Create tasks, set reminders, track completion
- **📅 Event/Meeting Management** — Schedule and manage meetings
- **📞 Call Logging** — Log inbound and outbound calls
- **📈 Reporting & Analytics** — Pipeline reports, forecasts, and performance metrics
- **🤖 Pipeline Automation** — Auto-assign, follow-up reminders, stage advancement

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- `requests` library
- Bigin account (developer sandbox recommended)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd bigin-crm-skill
   ```

2. **Install dependencies:**
   ```bash
   pip install requests
   ```

3. **Configure OAuth credentials:**
   Edit `config/oauth-config.json` and add your Zoho OAuth credentials:
   ```json
   {
     "oauth": {
       "client_id": "YOUR_CLIENT_ID",
       "client_secret": "YOUR_CLIENT_SECRET"
     }
   }
   ```

4. **Authenticate:**
   ```bash
   python scripts/auth.py auth
   ```

## 🔧 Configuration

### Creating Zoho OAuth App

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Click "Add Client" → "Server-based Application"
3. Set redirect URI: `http://localhost:8888/callback`
4. Select scopes:
   - `ZohoBigin.modules.ALL`
   - `ZohoBigin.settings.ALL`
5. Note down Client ID and Client Secret

### Data Centers

The skill supports multiple Zoho data centers:
- `com` — United States (default)
- `eu` — Europe
- `in` — India
- `au` — Australia
- `jp` — Japan
- `uk` — United Kingdom
- `ca` — Canada

## 💻 Usage

### Authentication Commands

```bash
# Authenticate with Bigin
python scripts/auth.py auth

# Check current user
python scripts/auth.py whoami

# Revoke tokens
python scripts/auth.py revoke
```

### Pipeline Management

```bash
# Create a pipeline
python scripts/pipelines.py create \
  --contact-id 12345 \
  --company-id 67890 \
  --stage "Prospecting" \
  --amount 50000 \
  --closing-date "2026-03-15" \
  --owner "sales@company.com" \
  --name "Acme Deal"

# List all pipelines
python scripts/pipelines.py list --limit 50

# Update pipeline stage
python scripts/pipelines.py update \
  --id 12345678 \
  --stage "Negotiation" \
  --amount 75000 \
  --probability 70

# Advance to next stage
python scripts/pipelines.py advance --id 12345678

# Mark as won/lost
python scripts/pipelines.py win --id 12345678
python scripts/pipelines.py lose --id 12345678 --reason "Budget constraints"

# Search pipelines
python scripts/pipelines.py search --query "Acme"

# Bulk update
python scripts/pipelines.py bulk-update \
  --stage "Negotiation" \
  --new-stage "Closed Won" \
  --criteria "probability-gt-80"
```

### Contact Management

```bash
# Create a contact
python scripts/contacts.py create \
  --first-name "John" \
  --last-name "Doe" \
  --email "john@company.com" \
  --phone "+1-555-1234" \
  --company "Acme Inc" \
  --source "Website"

# Search contacts
python scripts/contacts.py search --query "Doe" --limit 100

# Update contact
python scripts/contacts.py update \
  --id 87654321 \
  --phone "+1-555-9999"

# Get contact with pipelines
python scripts/contacts.py get \
  --id 87654321 \
  --include-pipelines

# Import from CSV
python scripts/contacts.py import \
  --file examples/bulk-import-contacts.csv
```

### Company Management

```bash
# Create a company
python scripts/companies.py create \
  --name "Acme Inc" \
  --industry "Technology" \
  --website "https://acme.com" \
  --employees 50 \
  --address "123 Business Park"

# Search companies
python scripts/companies.py search --query "Acme"

# Get company with contacts and pipelines
python scripts/companies.py get \
  --id 67890 \
  --include-contacts \
  --include-pipelines

# Find or create company
python scripts/companies.py find-or-create --name "New Company LLC"
```

### Task Management

```bash
# Create a task
python scripts/tasks.py create \
  --subject "Send proposal" \
  --related-to pipeline:12345678 \
  --due "2026-02-25" \
  --priority "High"

# List upcoming tasks
python scripts/tasks.py upcoming --days 7

# List overdue tasks
python scripts/tasks.py overdue

# Complete a task
python scripts/tasks.py complete --id 54321

# Create follow-up task
python scripts/tasks.py follow-up \
  --related-to contact:87654321 \
  --subject "Check in" \
  --days 3
```

### Event Management

```bash
# Create an event
python scripts/events.py create \
  --title "Product Demo" \
  --start "2026-02-24 14:00" \
  --duration 30 \
  --related-to contact:87654321 \
  --location "Zoom"

# List upcoming events
python scripts/events.py upcoming --days 7
```

### Call Logging

```bash
# Log an outbound call
python scripts/calls.py outbound \
  --contact-id 87654321 \
  --subject "Discovery call" \
  --duration 15 \
  --outcome "Interested, follow-up scheduled"

# Log an inbound call
python scripts/calls.py inbound \
  --contact-id 87654321 \
  --subject "Support inquiry" \
  --duration 10

# List all calls
python scripts/calls.py list --type Outbound
```

### Reporting

```bash
# Pipeline report
python scripts/reports.py pipeline \
  --by-stage \
  --by-owner \
  --output pipeline-report.csv

# Sales forecast
python scripts/reports.py forecast --month "2026-03"

# Performance report
python scripts/reports.py performance \
  --owner "sales@company.com" \
  --month "2026-02"

# Activity report
python scripts/reports.py activity \
  --user "me" \
  --week "2026-08" \
  --include-calls \
  --include-tasks \
  --include-events
```

### Automation

```bash
# Auto-assign unassigned pipelines
python scripts/automation.py assign \
  --unassigned \
  --round-robin \
  --owners sales1@company.com sales2@company.com

# Create follow-up tasks for stale pipelines
python scripts/automation.py follow-up \
  --stale-days 7 \
  --create-tasks

# Auto-advance pipelines
python scripts/automation.py advance \
  --criteria "proposal-sent-and-7-days"

# Identify stuck pipelines
python scripts/automation.py stuck --days 14
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_pipelines
python -m unittest tests.test_contacts
python -m unittest tests.test_automation
```

## 📁 Project Structure

```
bigin-crm-skill/
├── SKILL.md                          # Skill documentation
├── README.md                         # This file
├── config/
│   ├── bigin-config.json             # API endpoints config
│   └── oauth-config.json             # OAuth template
├── scripts/
│   ├── bigin_crm.py                  # Main CRM client
│   ├── auth.py                       # OAuth2 authentication
│   ├── pipelines.py                  # Pipeline operations
│   ├── contacts.py                   # Contact management
│   ├── companies.py                  # Company management
│   ├── tasks.py                      # Task management
│   ├── events.py                     # Event management
│   ├── calls.py                      # Call logging
│   ├── reports.py                    # Reporting
│   └── automation.py                 # Automation workflows
├── examples/
│   ├── bulk-import-contacts.csv      # Sample import file
│   ├── pipeline-mapping.json         # Stage mapping
│   └── automation-workflows/         # Pre-built workflows
│       ├── auto-assign.yaml
│       ├── follow-up-reminders.yaml
│       └── stage-advancement.yaml
└── tests/
    ├── test_pipelines.py             # Pipeline tests
    ├── test_contacts.py              # Contact tests
    └── test_automation.py            # Automation tests
```

## 🔗 API Reference

### Bigin vs Zoho CRM

| Product | Base URL |
|---------|----------|
| Zoho CRM | `https://www.zohoapis.com/crm/v2/` |
| Bigin | `https://www.zohoapis.com/bigin/v2/` |

### Module Mapping

| Bigin Module | API Name | Notes |
|--------------|----------|-------|
| Pipelines | `Pipelines` | Core sales module |
| Contacts | `Contacts` | Same as CRM |
| Companies | `Accounts` | Called "Accounts" in API |
| Tasks | `Tasks` | Same as CRM |
| Events | `Events` | Same as CRM |
| Calls | `Calls` | Same as CRM |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📚 Resources

- [Bigin API Documentation](https://www.bigin.com/developer/docs/apis/v2/)
- [Zoho OAuth Guide](https://www.bigin.com/developer/docs/apis/v2/oauth-overview.html)
- [Zoho API Console](https://api-console.zoho.com/)

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check the Bigin API documentation
- Review the SKILL.md for detailed specifications

---

**Built with ❤️ for the OpenClaw ecosystem**