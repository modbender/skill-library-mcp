# Financial Settings & Configuration Deep Dive

## Overview
Configure Buildertrend's financial module settings — taxes, invoice formatting, bill approval workflows, PO numbering, change order markup defaults, cost code structure, QBO sync rules, online payments, and retainage defaults. All settings are under Company Settings → Financials section at `/app/Settings`.

## Trigger
- "Change tax rate", "update invoice settings"
- "Set up bill approval workflow", "PO numbering"
- "Change order markup default", "financial settings"
- "QBO sync settings", "online payments setup"
- "Configure retainage defaults", "cost code settings"
- New project setup requiring financial configuration review

---

## Step 1: Navigate to Financial Settings
**Action:** Open the financial settings hub

### Browser Relay Steps
1. Navigate to `/app/Settings`
2. Scroll to Section 7: Financials
3. Snapshot → view all financial setting categories

### Financial Settings Map
| Setting | URL | What It Controls |
|---|---|---|
| Cost Codes | `/app/Settings/CostCodes` | Cost code categories and codes |
| Catalog | `/app/Settings/CostCatalogSettings?viewType=1` | Pre-built cost items for bills/POs |
| Bids | `/app/Settings/BidSettings` | Bid package defaults |
| Estimates | `/app/Settings/EstimateSettings` | Estimate formatting, markup, templates |
| Bills / POs / Budget | `/app/Settings/BudgetSettings` | Bill workflows, PO settings, budget tracking |
| Invoices | `/app/Settings/OwnerInvoiceSettings` | Invoice format, numbering, terms |
| Online Payments | `/app/PaymentsOverview` | Payment processing setup |
| Taxes | `/app/Settings/TaxesSettings` | Tax rates by jurisdiction |
| Change Orders | `/app/Settings/ChangeOrderSettings` | CO markup, numbering, approval |
| Accounting (QBO) | `/app/Settings/Settings/Accounting` | QuickBooks sync configuration |

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💰 Tax Settings | `primary` | `bt_finsettings_tax` |
| 🧾 Invoice Settings | `primary` | `bt_finsettings_invoice` |
| 📋 Bill/PO Settings | `primary` | `bt_finsettings_billpo` |
| 📝 Change Order Settings | `primary` | `bt_finsettings_co` |
| 🔗 QBO Sync Settings | `primary` | `bt_finsettings_qbo` |
| 💳 Online Payments | `primary` | `bt_finsettings_payments` |
| 📊 Cost Code Settings | `primary` | `bt_finsettings_costcodes` |
| 📐 Estimate Settings | `primary` | `bt_finsettings_estimate` |

---

## Step 2: Tax Settings
**URL:** `/app/Settings/TaxesSettings`

### Current Company Configuration
| Setting | Value |
|---|---|
| Tax Rate | {{tax_jurisdiction}} {{tax_rate}}% |
| Breakdown | {{state_tax}}% + {{city_tax}}% |
| Auto-apply | On invoices and estimates |
| QBO Sync | Mapped to QBO tax rate |

### Browser Relay Steps
1. Navigate to `/app/Settings/TaxesSettings`
2. View existing tax rates
3. To add a new rate:
   - Click "Add tax rate"
   - Enter name (e.g., "NJ Sales Tax")
   - Enter rate (e.g., 6.625%)
   - Set jurisdiction
   - Save
4. To edit existing rate:
   - Click on tax rate row
   - Modify rate or name
   - Save

### Jurisdiction-Specific Tax Notes
| Jurisdiction | Rate | When to Use |
|---|---|---|
| {{jurisdiction}} (default) | {{tax_rate}}% | Most company projects — commercial |
| State (outside city) | 4% + local | suburban/regional projects |
| NJ | 6.625% | Project Beta and other NJ projects |
| CT | 6.35% | Connecticut projects |

### Auto Sales Tax
- When job address is set, BT can auto-calculate sales tax
- Requires: Job address with zip code
- Auto-applies to invoices and estimates

### Receipt Tax Lines
- Toggle: "Automatically include tax line items on receipts"
- When checked: receipts in Cost Inbox will include tax lines
- Useful for accurate cost tracking

---

## Step 3: Invoice Settings
**URL:** `/app/Settings/OwnerInvoiceSettings`

### Key Invoice Settings
| Setting | Description | {{company_name}} Recommended |
|---|---|---|
| Invoice Prefix | Custom prefix before invoice # | "{{company_prefix}}-" |
| Numbering | Auto or manual | Auto-assign |
| Payment Terms | Default terms on new invoices | Net 30 |
| Logo | Company logo on invoices | {{company_name}} logo uploaded |
| Footer | Custom footer text | {{company_name}} address + license info |
| Format | Line items vs flat fee default | Line items |
| Tax default | Default tax rate | {{tax_jurisdiction}} {{tax_rate}}% |

### Browser Relay Steps
1. Navigate to `/app/Settings/OwnerInvoiceSettings`
2. Snapshot → review current settings
3. Update desired fields:
   - Set invoice prefix
   - Set default payment terms
   - Upload company logo
   - Set footer text
   - Configure line item defaults
4. Save changes

---

## Step 4: Bill / PO / Budget Settings
**URL:** `/app/Settings/BudgetSettings`

### Key Bill Settings
| Setting | Description | {{company_name}} Recommended |
|---|---|---|
| Bill approval workflow | Require approver(s) before payment | Enable for bills > $1,000 |
| Bill numbering | Auto or manual | Auto-assign |
| Payment terms | Default terms | Net 30 |
| Lien waiver forms | Custom lien waiver templates | Create conditional + unconditional |
| Auto-include tax on receipts | Tax lines on Cost Inbox items | Enabled |

### Key PO Settings
| Setting | Description | {{company_name}} Recommended |
|---|---|---|
| PO numbering | Auto or manual prefix/sequence | Auto with "PO-" prefix |
| PO approval chain | Who must approve POs | the user for > $5,000 |
| Variance POs | Allow creating variance POs from COs | Enabled |
| PO types | Standard vs Variance toggle | Both enabled |

### Lien Waiver Forms
1. Navigate to Bills/POs settings
2. Create custom lien waiver forms:
   - **Conditional Waiver** — upon progress payment
   - **Unconditional Waiver** — upon final payment
   - **Partial Waiver** — for partial releases
3. Forms auto-attach to bills for sub signature

### Browser Relay Steps
1. Navigate to `/app/Settings/BudgetSettings`
2. Review each section:
   - Bill settings tab
   - PO settings tab
   - Budget settings tab
   - Lien waiver forms
3. Update as needed
4. Save changes

---

## Step 5: Change Order Settings
**URL:** `/app/Settings/ChangeOrderSettings`

### Key CO Settings
| Setting | Description | {{company_name}} Recommended |
|---|---|---|
| CO numbering | Prefix + auto-increment | Auto with job prefix |
| Default markup | Markup % applied to CO builder cost | 15-20% |
| Approval workflow | Who approves COs | Client approval required |
| Auto-create invoice | Create invoice when CO approved | Optional — review first |
| Variance PO auto-create | Create variance PO from CO | Enabled |

### Browser Relay Steps
1. Navigate to `/app/Settings/ChangeOrderSettings`
2. Set default markup percentage
3. Configure approval workflow
4. Set numbering convention
5. Save

---

## Step 6: QBO Sync Settings
**URL:** `/app/Settings/Settings/Accounting`

### Current Configuration
- **Status:** ✅ Connected to QuickBooks Online Plus
- **Company:** {{company_name}}
- **⚠️ Admin access required** — AA role cannot modify

### Key Sync Settings
| Setting | Description | {{company_name}} Status |
|---|---|---|
| Allow bill edits to sync | Changes in BT push to QBO | Recommended: ON |
| Include QBO costs in budget | QBO-entered costs show in BT | Recommended: ON |
| Auto-push bills | Bills auto-send to QBO on status change | Review with the user |
| Auto-push invoices | Invoices auto-send to QBO | Review with the user |
| Job mapping | BT jobs → QBO classes/customers | Must be configured per job |
| Vendor mapping | BT subs → QBO vendors | Auto-matched by name |
| Cost code → Account mapping | BT codes → QBO expense accounts | Must be configured |

### What Pushes vs Pulls
| Direction | Items |
|---|---|
| BT → QBO (Push) | Bills, Invoices, Payments, POs |
| QBO → BT (Pull) | Costs entered in QBO (when enabled), Payment status |
| Two-Way | Bill edits (when enabled), Payment reconciliation |

### Sync Monitoring
1. Bills page → "QuickBooks Status" column shows sync state
2. Invoices page → "QuickBooks invoice" column shows sync state
3. Bills filter → "Sent To Accounting" filter for pushed status
4. Common statuses: Synced ✅, Error ⚠️, Not Pushed ⬜

---

## Step 7: Online Payments Settings
**URL:** `/app/PaymentsOverview`

### Current Status: NOT Active

### Available Options
| Feature | Rate | Limit |
|---|---|---|
| Client — Credit/Debit | 2.99% | $120K per transaction |
| Client — ACH | $15 flat | $120K per transaction |
| Client — Digital Wallets | 2.99% | $120K per transaction |
| Bill Pay — ACH | $1 flat | $200K per transaction |
| Bill Pay — Printed Check | $2 flat | $200K per transaction |
| Processing time | 3-5 business days | — |

### Enrollment Requirements
1. Legal company name
2. Company address
3. EIN (Employer Identification Number)
4. 6+ months in business
5. Beneficial owner information
6. Bank account for deposits

### Account Executive
- Dylan Chamberlain
- Email: CSAE@buildertrend.com

---

## Step 8: Cost Code Settings
**URL:** `/app/Settings/CostCodes`
**Full playbook:** See `cost-code-setup.md`

### Quick Reference
- {{company_name}} has 200+ cost codes across 43 categories
- Organized: BILLABLE (41 categories), NON-BILLABLE (9 codes), TIME TRACKING (2 codes)
- Variances tab for variance code management
- Import from CSV supported
- Cost codes map to QBO expense accounts

---

## Step 9: Estimate Settings
**URL:** `/app/Settings/EstimateSettings`

### Key Settings
| Setting | Description | {{company_name}} Recommended |
|---|---|---|
| Default markup | Standard markup % | 15% (adjust per project) |
| Proposal format | How proposals display to clients | Custom grouping |
| Template management | Save/load estimate templates | Use company templates |
| Lock/unlock control | Who can lock/unlock estimates | Admin + PM |
| Cost type defaults | Labor, material, subcontractor, etc. | Match QBO categories |

---

## Company-Specific Recommended Settings

### For Commercial Contractor
| Category | Setting | Recommended Value | Why |
|---|---|---|---|
| Tax | Default rate | {{tax_jurisdiction}} {{tax_rate}}% | Most projects in jurisdiction |
| Invoice | Prefix | "{{company_prefix}}-" | Professional, trackable |
| Invoice | Terms | Net 30 | Industry standard |
| Bills | Approval | Required > $1,000 | Prevent unauthorized spending |
| POs | Approval | the user approval > $5,000 | Control commitments |
| COs | Default markup | 15-20% | Cover overhead + profit |
| COs | Client approval | Required | Legal protection |
| Retainage | Default % | 10% | standard commercial practice |
| QBO | Bill edit sync | ON | Keep books in sync |
| QBO | Include QBO costs | ON | Complete budget picture |
| Lien Waivers | Auto-attach to bills | ON | lien law compliance |

### Financial Settings Audit Checklist
Run this quarterly:
- [ ] Tax rates current for all jurisdictions
- [ ] Invoice numbering sequential with no gaps
- [ ] Bill approval workflow active
- [ ] PO approval chain correct
- [ ] CO markup defaults match current pricing strategy
- [ ] QBO sync healthy (no errors)
- [ ] Lien waiver forms up to date
- [ ] Cost codes match QBO accounts
- [ ] Online payment rates competitive (if active)

---

## Smart Suggestions

| Context | Suggestion |
|---|---|
| New project in NJ | "Need to set tax rate to NJ 6.625% for this job" |
| Invoice created without prefix | "Invoice settings don't have prefix — want to set '{{company_prefix}}-'?" |
| Bill over $5K without approval | "This bill needs the user's approval per your workflow" |
| QBO sync error detected | "QBO sync issue — check accounting settings?" |
| New jurisdiction project | "Need to add a new tax rate for [location]?" |
| First invoice for new job | "Verify: job mapped to QBO customer, tax rate correct" |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Settings page access denied | Need Admin role — notify the user to make changes |
| QBO settings locked (AA role) | Only Admin/Owner can modify accounting settings |
| Tax rate change won't save | Check for QBO-synced rates that need updating in QBO first |
| Invoice prefix conflicts | Ensure unique prefix not used by another system |
| Browser relay disconnected | Stop, ask the user to re-enable extension |

---

## URL Patterns
| Page | URL |
|---|---|
| Company Settings Hub | `/app/Settings` |
| Cost Codes | `/app/Settings/CostCodes` |
| Catalog | `/app/Settings/CostCatalogSettings?viewType=1` |
| Bids | `/app/Settings/BidSettings` |
| Estimates | `/app/Settings/EstimateSettings` |
| Bills / POs / Budget | `/app/Settings/BudgetSettings` |
| Invoices | `/app/Settings/OwnerInvoiceSettings` |
| Online Payments | `/app/PaymentsOverview` |
| Taxes | `/app/Settings/TaxesSettings` |
| Change Orders | `/app/Settings/ChangeOrderSettings` |
| Accounting (QBO) | `/app/Settings/Settings/Accounting` |
| Company Information | `/app/Settings/CompanySettings` |
| Branding/Logo | `/app/Settings/BrandingSettings` |
| Job Settings | `/app/Settings/JobSettings` |
