# Buildertrend Skill for OpenClaw

Complete Buildertrend automation via Browser Relay — no API required.

**43 playbooks** covering the full BT platform: sales pipeline, project management, financials, scheduling, change orders, daily logs, RFIs, punch lists, invoicing, procurement, and more.

---

## How It Works

Buildertrend has no public API. This skill automates the actual BT interface through OpenClaw's Chrome Extension Browser Relay:

1. User logs into Buildertrend in Chrome
2. User clicks the Browser Relay toolbar icon (badge goes ON)
3. The agent controls the tab: **snapshot → read → act → verify**

Every action is visible, auditable, and requires user approval for financial operations.

---

## What's Included

| Category | Playbooks | Examples |
|---|---|---|
| **Sales & Pre-Construction** | 6 | Lead pipeline, proposals, estimates, bid packages |
| **Project Management** | 9 | Schedule, daily logs, RFIs, to-dos, punch lists, photos |
| **Financial** | 12 | POs, invoices, change orders, job costing, lien waivers |
| **Client Management** | 4 | Client portal, contacts, sub onboarding, surveys |
| **Setup & Admin** | 7 | Cost codes, users, templates, settings, HD integration |
| **Integrations** | 1 | Marketplace + QBO sync |
| **Closeout** | 2 | Project closeout, warranty management |
| **Labor** | 1 | Time clock management |
| **Mobile** | 1 | Mobile-specific workflows |

Plus:
- **bt-ui-patterns.md** — 16-section reference for interacting with BT's custom UI components (combobox dropdowns, modals, grids, navigation)
- **knowledge-base.md** — 2,300+ line BT module reference
- **qbo-sync-guide.md** — QuickBooks Online integration guide
- **workflows.md** — Official BT workflow procedures

---

## Quick Start

### Prerequisites
- [OpenClaw](https://github.com/openclaw/openclaw) v2026.2.20+
- OpenClaw Browser Relay Chrome extension
- Buildertrend account
- Chrome browser

### Install
```bash
# Copy to your OpenClaw workspace
cp -R buildertrend/ ~/.openclaw/workspace/SKILLS/buildertrend/
```

### Configure
Find and replace `{{placeholders}}` with your company values. See **Setup & Configuration** in [SKILL.md](SKILL.md) for the full placeholder table and step-by-step guide.

### Test
1. Create a test job in Buildertrend
2. Log in and attach the tab with Browser Relay
3. Run a simple playbook (e.g., create a daily log)
4. Verify the agent can snapshot, navigate, and interact

---

## File Structure

```
buildertrend/
├── SKILL.md              # Main skill file — rules, setup guide, playbook index
├── STRATEGY.md           # Automation strategy and phase tracking
├── bt-ui-patterns.md     # UI interaction patterns (16 sections, 432 lines)
├── knowledge-base.md     # BT module reference (2,349 lines)
├── workflows.md          # Official BT workflow procedures
├── qbo-sync-guide.md     # QuickBooks Online integration reference
├── skill.json            # Skill manifest
├── LICENSE               # MIT License
├── playbooks/
│   ├── README.md         # Full playbook index with cross-references
│   └── *.md              # 43 automation playbooks
```

---

## Security

- **The agent never handles credentials** — all login/authentication is done by the user
- **Financial actions require user approval** — inline buttons for confirm/cancel on every PO, invoice, and change order
- **Session timeout protection** — agent stops and notifies user if BT session expires
- **No external data transmission** — all automation stays within BT/QBO/Google Drive
- **No system commands** — skill operates entirely through browser automation
- **JavaScript evaluation** is limited to DOM click/query patterns for BT's custom UI components (no data extraction)

---

## Multi-Agent Support (Optional)

This skill includes references to specialized agents (bookkeeper, receipt, procurement, CRM). These are **optional** — the skill works fully with a single agent. If you run a multi-agent setup, configure the workspace paths in the setup guide.

---

## Requirements

- **OpenClaw** v2026.2.20 or later
- **Browser Relay** Chrome extension
- **Buildertrend** account (any plan — skip playbooks for modules not on your plan)

---

## License

MIT — see [LICENSE](LICENSE)
