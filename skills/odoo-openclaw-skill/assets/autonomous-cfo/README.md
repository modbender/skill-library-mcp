# Autonomous CFO Engine (Odoo)

## Purpose

Reliable, evidence-backed financial intelligence on top of Odoo for OpenClaw skills.

## Reports (v2.0)

| Command | Description |
|---------|-------------|
| `health` | Financial health (cash, burn rate, runway) |
| `revenue` | Revenue analytics (trends, top customers) |
| `aging` | AR/AP aging report with overdue buckets |
| `expenses` | Expense breakdown by vendor/category |
| `executive` | One-page CFO snapshot (default) |
| `adhoc` | Custom metric comparisons |

## Output Formats

- `--output whatsapp` - Dark theme 1080x1080 PNG cards
- `--output pdf` - Light theme A4 PDF reports
- `--output both` - Generate both (default for executive)

## API Backends

- `json2` (preferred on Odoo 19+)
- `xmlrpc` (fallback for older Odoo)
- `auto` routing in `cfo_cli.py` chooses backend by server version

## Dependencies

```bash
# Install in venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

requirements.txt (pinned versions for reproducibility):
- `requests==2.32.3`
- `matplotlib==3.10.0`
- `pillow==11.1.0`
- `fpdf2==2.8.2`

## AI Runtime

AI analysis is routed through **OpenClaw native local agent runtime** (`openclaw agent --local`), not standalone Gemini API flows.

## Key Files

- `src/connectors/odoo_client.py` — JSON-2 + XML-RPC connector
- `src/tools/cfo_cli.py` — command interface
- `src/logic/finance_engine.py` — deterministic accounting logic
- `src/logic/intelligence_engine.py` — VAT/trend/anomaly orchestration
- `src/visualizers/` — PDF, charts, WhatsApp cards
- `src/reporters/` — Report generators
- `src/reporters/ifrs.py` — **IFRS-compliant financial statements** (IAS 1, IAS 7)

## IFRS Reports

The `FinancialStatementReporter` class generates compliant financial statements for any jurisdiction:

- **Statement of Financial Position** (Balance Sheet)
- **Statement of Profit or Loss** (P&L)
- **Statement of Cash Flows**

**Automatic Standard Detection:**
```python
# Auto-detect from company country
reporter.generate(company_id=1, ...)

# Force a specific standard
reporter.generate(company_id=1, standard="US_GAAP", ...)
```

**Supported Standards:**
- IFRS (International)
- US GAAP (United States)
- Ind-AS (India)
- UK GAAP (United Kingdom)
- SOCPA (Saudi Arabia)
- EU IFRS (European Union)
- CAS (China)
- JGAAP (Japan)
- ASPE (Canada)
- AASB (Australia)

## Environment Variables

Required in `.env`:
- `ODOO_URL` - Odoo instance URL
- `ODOO_DB` - Database name
- `ODOO_USER` - Username
- `ODOO_PASSWORD` - Password or API key

## Notes

- Read-only by default (create/write/unlink blocked)
- Use `rpc-call` for advanced read-only queries only
- See `AUDIT.md` for known issues and recommendations
