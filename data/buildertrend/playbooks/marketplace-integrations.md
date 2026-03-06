# Buildertrend Marketplace & Integrations

## Overview
Manage Buildertrend's ecosystem of third-party integrations — accounting (QBO, Xero), payroll (Gusto), CRM (HubSpot, Salesforce, Pipedrive), purchasing (Home Depot, Lowe's), estimating (BT Takeoff), automation (Zapier), and financing (Nelnet). Monitor sync health, troubleshoot errors, and connect new services.

## Trigger
- "Connect [integration]", "set up Gusto", "check marketplace"
- "Is QuickBooks syncing?", "sync error", "integration status"
- "What integrations do we have?", "marketplace"
- "Set up Zapier automation", "automate [workflow]"
- "Data entry services", "BT services"

---

## Step 1: Review Current Integration Status
**Action:** Check what's connected and what's available

### {{company_name}}'s Current Integration Status
| Integration | Status | Settings URL |
|---|---|---|
| QuickBooks Online | ✅ Connected | `/app/Settings/Settings/Accounting` |
| The Home Depot | ⚠️ Available | `/app/Settings/TheHomeDepotSettings` |
| Lowe's PRO | ⚠️ Available | `/app/Settings/LowesSettings` |
| Gusto | ⚠️ Available | `/app/Settings/PayrollSettings` |
| HubSpot | ⚠️ Available | `/app/Settings/IntegrationsSettings/1` |
| Salesforce | ⚠️ Available | `/app/Settings/IntegrationsSettings/2` |
| Pipedrive | ⚠️ Available | `/app/Settings/IntegrationsSettings/3` |
| BT Takeoff | ⚠️ Available | `/app/Settings/TakeoffSettings` |
| Zapier | ⚠️ Available | Marketplace external link |
| Xero | ⚠️ Available | Company Settings → Accounting |
| Nelnet | ⚠️ Available | Marketplace external link |

**Present to the user:**
```
🔌 Integration Status:

✅ Connected:
• QuickBooks Online Plus — {{company_name}}

⚠️ Available (not connected):
• Gusto (payroll)
• Home Depot / Lowe's PRO (purchasing)
• HubSpot / Salesforce / Pipedrive (CRM)
• BT Takeoff (estimating)
• Zapier (automation)
• Nelnet (client financing)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔍 Check QBO sync health | `primary` | `bt_int_qbo_health` |
| 💰 Set up Gusto (payroll) | `primary` | `bt_int_gusto` |
| 🏠 Connect Home Depot | `primary` | `bt_int_homedepot` |
| 🔧 Connect Lowe's PRO | `primary` | `bt_int_lowes` |
| ⚡ Set up Zapier | `primary` | `bt_int_zapier` |
| 📊 Connect CRM | `primary` | `bt_int_crm` |
| ℹ️ View all options | `primary` | `bt_int_all` |

---

## Step 2: Integration Setup Workflows

### QuickBooks Online (Already Connected)
**Settings URL:** `/app/Settings/Settings/Accounting`
**Status:** Connected to QBO Plus — {{company_name}}

**Health Check Steps:**
1. Navigate to `/app/Settings/Settings/Accounting`
2. Snapshot → verify "Connected to QuickBooks" status
3. Check for sync errors or warnings
4. Review sync settings:
   - Bill edits sync to QBO (toggle)
   - Include QBO costs in budget (toggle)
   - Auto-push vs manual push
5. Report status to the user

**⚠️ Note:** Administrative Assistant role does NOT have access to update Accounting Settings. the user (Admin) must make changes.

### Gusto (Payroll)
**Settings URL:** `/app/Settings/PayrollSettings`

**Setup Steps:**
1. Navigate to `/app/Settings/PayrollSettings`
2. Select "Create a Gusto Account" or "Connect to Gusto"
3. Authorize BT to access Gusto data
4. Map BT time clock entries → Gusto payroll
5. Verify payroll period filter appears in Time Clock

**What Syncs:**
- BT time clock hours → Gusto for payroll processing
- Follows Gusto's payroll period (BT doesn't change it)
- New filter ensures correct payroll period
- Accurate tracking of every hour for pay calculation

### Home Depot
**Settings URL:** `/app/Settings/TheHomeDepotSettings`
**Detailed playbook:** See `home-depot-integration.md`

### Lowe's PRO
**Settings URL:** `/app/Settings/LowesSettings`

**Setup Steps:**
1. Navigate to Lowe's settings page
2. ⚠️ HAND OFF TO USER — the user enters Lowe's PRO account credentials directly (agent does not handle credentials)
3. Authorize data sharing
4. Map purchases to BT jobs and cost codes

### CRM Integrations (HubSpot / Salesforce / Pipedrive)
| CRM | Settings URL |
|---|---|
| HubSpot | `/app/Settings/IntegrationsSettings/1` |
| Salesforce | `/app/Settings/IntegrationsSettings/2` |
| Pipedrive | `/app/Settings/IntegrationsSettings/3` |

**Setup Steps (same pattern):**
1. Navigate to integration settings URL
2. Click "Connect" or "Authorize"
3. Log into CRM account
4. Map fields (BT leads ↔ CRM contacts/deals)
5. Set sync direction (one-way or two-way)
6. Test sync with existing lead

### BT Takeoff
**Settings URL:** `/app/Settings/TakeoffSettings`
**Detailed playbook:** See `takeoff-estimating.md`

### Zapier
**Access:** Marketplace external link → zapier.com/apps/buildertrend

**Available BT Triggers:**
- New lead created
- New job created
- New bill created
- New invoice created
- Invoice status changed
- Schedule item updated

**Available BT Actions:**
- Create lead
- Create task/to-do
- Update job status
- Send notification

**Company-Relevant Automations:**
| Trigger | Action | Use Case |
|---|---|---|
| New lead in BT | Create card in Trello/Notion | Pipeline tracking |
| Invoice sent | Slack/email notification | AR awareness |
| New bill created | Google Sheets row | Financial log |
| Schedule item overdue | Email/SMS alert | Deadline management |

### Nelnet (Client Financing)
- Offer financing options to clients through BT portal
- Client applies for financing within their portal view
- Payment plans for larger projects

### Data Entry Services
**Access:** Setup → Additional Services
- BT offers outsourced data entry for receipts, bills, financial data
- BT team inputs your documents into the system
- Useful for bulk backlog entry

---

## Step 3: Monitor Integration Health
**Action:** Check sync status and troubleshoot errors

### QBO Sync Health Check
**Browser Relay Steps:**
1. Navigate to `/app/Bills` → check "QuickBooks Status" column
2. Look for: ✅ Synced, ⚠️ Error, ⬜ Not Pushed
3. Navigate to `/app/OwnerInvoices` → check "QuickBooks invoice" column
4. Report sync failures

**Present to the user:**
```
🔍 QBO Integration Health:
• Connection: ✅ Active
• Bills synced: [X] of [Y]
• Bills with errors: [count]
• Invoices synced: [X] of [Y]
• Last sync: [timestamp]
```

### Troubleshooting Sync Errors
| Error | Fix |
|---|---|
| Bill won't push to QBO | Check: vendor exists in QBO, cost code mapped, amount > $0 |
| Invoice sync failed | Check: customer exists in QBO, tax rate configured |
| Duplicate entries | Don't create in both systems — let BT push to QBO |
| Amount mismatch | Tax rounding difference — typically < $0.01, expected |
| Connection lost | Re-authorize: Settings → Accounting → Reconnect |

---

## Step 4: Access Marketplace
**Action:** Browse available integrations

### Browser Relay Steps
1. Click Setup menu (top-right, user initials)
2. Click "Integrations" → opens `https://buildertrend.com/marketplace/`
3. Browse available apps by category
4. Click integration → view details and setup instructions

**OR navigate directly:**
- Company Settings: `/app/Settings` → Section 9: Integrations

---

## Smart Suggestions

| Context | Suggestion |
|---|---|
| the user mentions payroll | "Want to connect Gusto to sync time clock → payroll?" |
| QBO sync error detected | "QBO sync issue found — want me to investigate?" |
| New integration question | Show current status + recommend based on {{company_name}} needs |
| Bulk data entry needed | "BT offers data entry services — want to explore?" |
| Lead management discussion | "Consider connecting HubSpot for better lead tracking" |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Integration page access denied | May need Admin role — notify the user |
| External marketplace page won't load | Try direct URL in new tab |
| Integration authorization fails | Check credentials, try incognito, clear cookies |
| Sync errors accumulating | Screenshot error list, compile for the user review |
| Browser relay disconnected | Stop, ask the user to re-enable extension |

---

## URL Patterns
| Page | URL |
|---|---|
| Company Settings | `/app/Settings` |
| Accounting (QBO) | `/app/Settings/Settings/Accounting` |
| Gusto | `/app/Settings/PayrollSettings` |
| Home Depot | `/app/Settings/TheHomeDepotSettings` |
| Lowe's PRO | `/app/Settings/LowesSettings` |
| HubSpot | `/app/Settings/IntegrationsSettings/1` |
| Salesforce | `/app/Settings/IntegrationsSettings/2` |
| Pipedrive | `/app/Settings/IntegrationsSettings/3` |
| BT Takeoff | `/app/Settings/TakeoffSettings` |
| Marketplace | `https://buildertrend.com/marketplace/` |
| Additional Services | `https://buildertrend.com/additional-customer-services/` |
| Online Payments | `/app/PaymentsOverview` |
