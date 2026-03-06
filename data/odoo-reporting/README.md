# Odoo Financial Intelligence Skill for OpenClaw

Production-grade Odoo accounting intelligence for OpenClaw with **native RPC reporting**, **IFRS-compliant financial statements**, **modern visualizations**, and **evidence-backed outputs**.

> **⚠️ SECURITY NOTICE**: This skill requires Odoo credentials and implements strict read-only access. See [SECURITY.md](SECURITY.md) for full details.

## Features

### v2.0 - Modern Reports
- **5 Pre-built Reports:** Financial Health, Revenue Analytics, AR/AP Aging, Expense Breakdown, Executive Summary
- **Compliant Financial Statements:** P&L, Balance Sheet, Cash Flow
- **Automatic Standard Detection:** Detects company's accounting standard (IFRS, US GAAP, Ind-AS, UK GAAP, SOCPA, CAS, JGAAP, etc.) and formats accordingly
- **Ad-hoc Builder:** Custom comparisons (revenue vs expenses, direct vs indirect, etc.)
- **Dual Output:** WhatsApp cards (dark theme) + PDF reports (light theme)
- **Interactive:** Prompts for missing params — no assumptions

### Core Features
- Financial summary (sales, expenses, receivables/payables)
- VAT reporting (input/output/net)
- Cash-flow snapshots
- Trend analysis + chart generation
- Rules-based anomaly detection
- AI-assisted anomaly narration and NL Q&A (via OpenClaw agent runtime)
- Hard read-only enforcement at connector layer (no create/write/unlink)

## Installation

**Prerequisites:**
- Python 3.10+
- Odoo 16+ (tested on Odoo 19)
- Odoo API key or credentials

**Step 1: Clone and Install**
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/ashrf-in/odoo-openclaw-skill odoo
cd odoo/assets/autonomous-cfo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Or use the install script:**
```bash
cd odoo/assets/autonomous-cfo
./install.sh
```

## Configuration

**REQUIRED**: Create `assets/autonomous-cfo/.env` with your Odoo credentials:

```env
ODOO_URL=https://your-instance.odoo.com
ODOO_DB=your_database_name
ODOO_USER=your_email@example.com
ODOO_PASSWORD=your_odoo_api_key
```

**Get an Odoo API Key (Recommended for Production):**
1. Log into Odoo → Settings → Account Security → API Keys
2. Generate a new API key
3. Use this key as `ODOO_PASSWORD`

**Why API keys?**
- Scoped permissions (can be read-only)
- Can be revoked independently
- Better audit trail in Odoo

**Copy the template:**
```bash
cp assets/autonomous-cfo/.env.example assets/autonomous-cfo/.env
# Edit with your credentials
nano assets/autonomous-cfo/.env
```

> **Security**: Credentials are stored locally in `.env` (excluded from git). Never commit this file.
>
> ⚠️ **Important**: For production, create a dedicated **read-only Odoo user** with minimal permissions. Don't use an admin account.

## Usage

### Modern Reports (v2.0)

```bash
# Financial Health - cash flow, liquidity, burn rate
python3 src/tools/cfo_cli.py health --from 2025-01-01 --to 2025-02-10

# Revenue Analytics - MoM trends, top customers
python3 src/tools/cfo_cli.py revenue --from 2025-01-01 --to 2025-02-10

# AR/AP Aging - overdue buckets
python3 src/tools/cfo_cli.py aging --as-of 2025-02-10

# Expense Breakdown - by vendor/category
python3 src/tools/cfo_cli.py expenses --from 2025-01-01 --to 2025-02-10

# Executive Summary - one-page CFO snapshot
python3 src/tools/cfo_cli.py executive --from 2025-01-01 --to 2025-02-10

# Ad-hoc custom comparison
python3 src/tools/cfo_cli.py adhoc --metric-a "revenue" --metric-b "expenses"
```

### Output Formats

```bash
--output whatsapp   # Dark theme 1080x1080 PNG cards
--output pdf        # Light theme A4 PDF
--output both       # Generate both
```

### Classic Reports

```bash
python3 src/tools/cfo_cli.py summary --days 30
python3 src/tools/cfo_cli.py cash_flow
python3 src/tools/cfo_cli.py vat --date-from 2025-01-01 --date-to 2025-03-31
python3 src/tools/cfo_cli.py trends --months 12 --visualize
python3 src/tools/cfo_cli.py anomalies
python3 src/tools/cfo_cli.py ask "What was my highest expense month?"
```

### Health Check

```bash
python3 src/tools/cfo_cli.py doctor
```

## Report Themes

- **WhatsApp Cards:** "Midnight Ledger" — Navy-black (#0a0e1a), copper glow (#cd7f32)
- **PDF Reports:** Clean white, copper accents, professional layout

## Output Locations

```
output/
├── charts/           # Line/bar charts (PNG)
├── whatsapp_cards/   # Square cards (1080x1080 PNG)
└── pdf_reports/      # A4 PDF reports
```

## RPC Backend Support

- `--rpc-backend auto` (default) — detects Odoo 19+ and uses JSON-2
- `--rpc-backend json2` — Odoo 19+ External API
- `--rpc-backend xmlrpc` — Legacy XML-RPC

## Safety & Security

### Read-Only Enforcement
- **Strict read-only** at connector level
- Mutating methods (`create`, `write`, `unlink`, `action_post`) are blocked
- Only safe methods allowed: `search`, `search_read`, `read`, `fields_get`
- Attempting blocked methods raises `PermissionError`

### User Invocation Only
- **Model invocation DISABLED** - Cannot be invoked autonomously by AI
- User MUST explicitly request every operation
- Every invocation requires direct user intent

### Data Privacy
- All reports generated locally (no cloud upload)
- Credentials never logged or transmitted elsewhere
- Only connects to your specified Odoo URL
- No telemetry or analytics

### Output Locations
All outputs are local files only:
```
assets/autonomous-cfo/output/
├── charts/           # PNG chart images
├── whatsapp_cards/   # PNG social media cards
├── pdf_reports/      # PDF reports
└── excel/            # Excel spreadsheets
```

See [SECURITY.md](SECURITY.md) for comprehensive security documentation.

## Requirements

- Python 3.10+
- Odoo 16+ (tested on Odoo 19)
- OpenClaw (for AI features)

## Dependencies

```
requests>=2.31.0
matplotlib>=3.8.0
pillow>=10.0.0
fpdf2>=2.8.0
```

## Repository Structure

```
├── SKILL.md                    # Agent execution protocol
├── README.md                   # This file
├── assets/autonomous-cfo/
│   ├── .env                    # Credentials (not in git)
│   ├── requirements.txt        # Python dependencies
│   └── src/
│       ├── connectors/         # Odoo RPC client
│       ├── logic/              # Finance & intelligence engines
│       ├── reporters/          # Report generators (v2.0)
│       ├── visualizers/        # Charts, cards, PDFs
│       ├── validators/         # Param checking
│       └── tools/              # CLI entrypoint
```

## License

MIT — ashrf
