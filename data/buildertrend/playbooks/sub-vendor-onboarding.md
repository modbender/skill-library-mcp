# Sub/Vendor Onboarding (Agent-Assisted)

## Overview
the agent guides the user through onboarding a new sub or vendor into the company ecosystem — adding them to Buildertrend with contact info and trade, inviting them to the BT portal, requesting required documents (COI, W-9, license, sub agreement), tracking document submission, assigning to jobs, and coordinating with other agents (bookkeeper agent for QBO vendor setup, CRM agent for CRM, receipt agent for Drive filing).

## Trigger
- the user says "add new sub" or "onboard [vendor name]"
- New bid awarded → winning sub needs to be set up
- the user received a referral for a new trade partner
- Project needs a trade not yet in the system
- Sub sends initial documents → start onboarding

---

## Step 1: Collect Sub/Vendor Information
**Action:** Gather basic details

**Message to the user:**
```
👷 New Sub/Vendor Onboarding — tell me about them:

• Company name:
• Contact person (name):
• Email:
• Phone:
• Trade/specialty:
• Address (optional):
```

**Or shortcut: "Just tell me the name and trade — I'll ask for the rest as we go."**

### Trade Selection
**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔨 Demolition | `primary` | `bt_sub_trade_demo` |
| 🧱 Framing / Carpentry | `primary` | `bt_sub_trade_framing` |
| ⚡ Electrical | `primary` | `bt_sub_trade_electrical` |
| 🔧 Plumbing | `primary` | `bt_sub_trade_plumbing` |
| ❄️ HVAC | `primary` | `bt_sub_trade_hvac` |
| 🧱 Drywall / Insulation | `primary` | `bt_sub_trade_drywall` |
| 🎨 Painting | `primary` | `bt_sub_trade_painting` |
| 🪵 Flooring / Tile | `primary` | `bt_sub_trade_flooring` |
| 🪨 Masonry / Concrete | `primary` | `bt_sub_trade_masonry` |
| 🪟 Windows / Glazing | `primary` | `bt_sub_trade_windows` |
| 🔩 Steel / Iron | `primary` | `bt_sub_trade_steel` |
| 🧯 Fire Protection | `primary` | `bt_sub_trade_fire` |
| 🪵 Millwork / Cabinets | `primary` | `bt_sub_trade_millwork` |
| 🪨 Countertops | `primary` | `bt_sub_trade_countertops` |
| 🏗️ Scaffold / Sheds | `primary` | `bt_sub_trade_scaffold` |
| 🧹 Cleaning | `primary` | `bt_sub_trade_cleaning` |
| 📦 Material Supplier | `primary` | `bt_sub_trade_supplier` |
| 🚛 Equipment Rental | `primary` | `bt_sub_trade_rental` |
| ✏️ Other | `primary` | `bt_sub_trade_other` |

---

## Step 2: Add to Buildertrend
**Action:** Create the sub/vendor in BT

### Browser Relay Execution
1. Navigate to Users → Subs/Vendors (via top navigation)
2. Snapshot → verify Subs/Vendors page
3. Click **"New Sub/Vendor"**
4. In the form, fill:
   - **Company Name** (text input)
   - **First Name / Last Name** (contact person)
   - **Email** (required for portal invitation)
   - **Phone** (text input)
   - **Trade** (combobox — select or create)
   - **Address** fields (street, city, state, zip)
5. Click **Save**
6. Snapshot → confirm sub created, capture sub ID

**Report back:**
```
✅ Sub/Vendor added to Buildertrend!

👷 [Company Name]
👤 Contact: [Name]
📧 Email: [email]
📞 Phone: [phone]
🔧 Trade: [trade]
📊 Status: Added (not yet invited)
```

---

## Step 3: Assign to Job(s)
**Action:** Grant job access

**Message to the user:**
```
🏗️ Which job(s) should [Company Name] be assigned to?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_sub_job_1` |
| 🏗️ Project Alpha | `primary` | `bt_sub_job_1` |
| 🏗️ Project Beta | `primary` | `bt_sub_job_2` |
| 🏗️ Project Beta | `primary` | `bt_sub_job_2` |
| 🏗️ Project Epsilon | `primary` | `bt_sub_job_3` |
| 🏗️ Project Gamma | `primary` | `bt_sub_job_4` |
| 🏗️ Project Eta | `primary` | `bt_sub_job_5` |
| ⏭️ No Job Yet | `primary` | `bt_sub_job_skip` |
| ✅ Done Selecting | `success` | `bt_sub_job_done` |

### Browser Relay Execution
1. Navigate to Job Details → Subs/Vendors tab (for each selected job)
2. Click **"+ Existing Contact"** or add from sub list
3. Select the new sub
4. **Permission Wizard** → set feature access:
   - Schedule (their items)
   - Daily Logs (view shared, create own)
   - To-Dos (assigned items)
   - POs (receive, approve)
   - Files (permitted folders)
   - RFIs (create, respond)
5. Click **Update Permissions**
6. Snapshot → confirm sub added to job

---

## Step 4: Invite to BT Portal
**Action:** Send portal invitation

**Message to the user:**
```
📧 Invite [Company Name] to the Buildertrend portal?

They'll be able to:
• View assigned schedule items
• Receive and approve POs
• Submit bills for payment
• Respond to RFIs
• View shared daily logs

(Free for subs — they just need to create an account)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Send Invite Now | `success` | `bt_sub_invite` |
| ⏭️ Invite Later | `primary` | `bt_sub_invite_later` |

### Browser Relay Execution
1. Navigate to Subs/Vendors list
2. Check the sub's row
3. Click **"Invite"** button
4. Preview invitation text → **Send on Save**
5. Snapshot → confirm invitation sent

**Report back:**
```
📧 Portal invitation sent to [Company Name]!

📧 Sent to: [email]
📊 Status: Pending (awaiting account creation)
💡 They can use existing BT credentials if they have them from another builder.
```

---

## Step 5: Request Required Documents
**Action:** Track document requests

**Message to the user:**
```
📋 Required documents for [Company Name]:

Which documents do you need from them?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🛡️ Certificate of Insurance (COI) | `primary` | `bt_sub_doc_coi` |
| 📄 W-9 | `primary` | `bt_sub_doc_w9` |
| 📋 License / Certification | `primary` | `bt_sub_doc_license` |
| 📝 Sub Agreement / Contract | `primary` | `bt_sub_doc_agreement` |
| 📄 Trade Agreement (via BT) | `primary` | `bt_sub_doc_trade_agreement` |
| ✅ All Standard (COI + W-9 + Agreement) | `success` | `bt_sub_doc_all_standard` |
| ⏭️ Skip — No Documents Needed | `primary` | `bt_sub_doc_skip` |

### Track Document Status
Create a tracking entry:

**Message to the user:**
```
📋 Document tracking — [Company Name]:

| Document | Status | Due |
|----------|--------|-----|
| COI | ⏳ Requested | [date +14 days] |
| W-9 | ⏳ Requested | [date +14 days] |
| Sub Agreement | ⏳ Requested | [date +14 days] |
| License | ⏳ Requested | [date +14 days] |
```

### Trade Agreement via BT
BT has a built-in Trade Agreement feature:
1. Navigate to sub's profile → Advanced Settings
2. Upload trade agreement document
3. Send for electronic approval
4. Sub signs digitally in the portal

### Document Request Email
If sending directly (not via BT portal):
```
Subject: {{company_name}} — Required Documents for [Company Name]

Hi [Contact Name],

Welcome to {{company_name}}! Before we get started, we'll need the following documents on file:

1. Certificate of Insurance (COI) — naming {{company_name}} as additional insured
2. W-9 form
3. Copy of your trade license
4. Signed subcontractor agreement (attached)

Please send these to {{admin_email}} at your earliest convenience.

Thank you,
{{company_name}}
```

---

## Step 6: Cross-System Setup
**Action:** Set up the sub/vendor across all company systems

### Parallel Tasks

**6A: QBO Vendor Setup (via bookkeeper agent)**
**Message to the user:**
```
💰 Set up [Company Name] as a vendor in QuickBooks?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Yes — Notify bookkeeper agent | `success` | `bt_sub_qbo_yes` |
| ⏭️ Skip QBO | `primary` | `bt_sub_qbo_skip` |

If yes: Notify bookkeeper agent to create QBO vendor with matching company name, contact, address, trade.

**6B: CRM Contact (via CRM agent)**
**Message to the user:**
```
📇 Add [Company Name] to CRM agent's CRM contacts?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Yes — Notify CRM agent | `success` | `bt_sub_crm_yes` |
| ⏭️ Skip CRM | `primary` | `bt_sub_crm_skip` |

**6C: Google Drive Filing**
1. Create folder in Shared Drive → Vendors & Subs → [Company Name]
2. Store master docs: COI, W-9, license, agreements
3. Follow Company Filing Policy from TOOLS.md

---

## Step 7: Document Submission Tracking
**Action:** Monitor document status and follow up

### On Document Received
When the user forwards a document (COI, W-9, etc.):

```
✅ Document received — [Company Name]:

📄 [Document type] received
📅 Date: [today]
📊 Status: On file

📋 Remaining documents:
| Document | Status |
|----------|--------|
| COI | ✅ Received |
| W-9 | ⏳ Pending |
| License | ⏳ Pending |
| Agreement | ⏳ Pending |
```

**Actions on receipt:**
1. Upload to BT (sub profile → Certifications/Files)
2. File to Google Drive (Vendors & Subs/[Company Name])
3. Update tracking status
4. Send to receipt agent for filing if needed

### Follow-Up on Missing Documents
**Heartbeat/scheduled check:**
```
⚠️ Outstanding documents — [Company Name]:

📄 W-9 — requested [N] days ago, still pending
📋 License — requested [N] days ago, still pending

Send a follow-up?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Send Follow-Up | `success` | `bt_sub_doc_followup` |
| ⏭️ Wait Another Week | `primary` | `bt_sub_doc_wait` |

### Certification Expiration Tracking
BT supports certification expiration dates with reminders:
1. Navigate to sub profile → Advanced Settings → Certifications
2. Set expiration date for COI (typically annual)
3. BT will auto-remind before expiration

---

## Step 8: Final Summary
**Message to the user:**
```
✅ Sub/Vendor Onboarding Complete — [Company Name]:

👷 Buildertrend:
  ✅ Profile created
  ✅ Assigned to: [job list]
  ✅ Portal invitation: [sent/pending]
  ✅ Permissions: [set/default]

📋 Documents:
  [✅/⏳] COI
  [✅/⏳] W-9
  [✅/⏳] License
  [✅/⏳] Sub Agreement

🔗 Cross-System:
  [✅/⏭️] QBO vendor ( bookkeeper agent)
  [✅/⏭️] CRM contact (CRM agent)
  [✅/⏭️] Drive folder (Vendors & Subs)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📨 Send Bids to This Sub | `primary` | `bt_sub_send_bids` |
| 📦 Create PO for This Sub | `primary` | `bt_sub_create_po` |
| 👷 Onboard Another Sub | `primary` | `bt_sub_new` |
| ✅ Done | `success` | `bt_sub_done` |

---

## Step 9: Post-Action
After onboarding:

1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Update Apple Reminders** — track document submission deadlines
   - Title: "[Company Name] — documents due [date]"
   - List: Company - [relevant project list] or Company - Admin
3. **Update sub/vendor registry** if maintained separately

---

## Batch Mode: Onboard Multiple Subs
When setting up a new project and need to add multiple subs:

1. Ask: "How many subs are we adding?"
2. Collect basic info for each (name + trade minimum)
3. Create all in BT sequentially
4. Assign all to the same job
5. Bulk invite to portal
6. Track all document requests together

**Summary:**
```
✅ Batch onboarding complete — [N] subs added:

| # | Company | Trade | Portal | Docs |
|---|---------|-------|--------|------|
| 1 | [name] | Electrical | ✅ Invited | ⏳ Pending |
| 2 | [name] | Plumbing | ✅ Invited | ⏳ Pending |
| 3 | [name] | HVAC | ✅ Invited | ⏳ Pending |
```

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Duplicate sub detected | Warn: "[Company Name] already exists in BT" → link to existing |
| Email missing | Cannot invite to portal — ask for email |
| Permission wizard fails | Set permissions manually from Job Details |
| QBO vendor creation fails | Note for bookkeeper agent, retry later |
| Drive folder creation fails | Retry or create manually |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |

---

## URL Patterns
| Page | URL |
|---|---|
| Subs/Vendors List | Users → Subs/Vendors (top nav) |
| Sub Settings | `/app/Settings/SubSettings` |
| Sub Contacts | `/app/Settings/SubSettings` |
| Internal Users | `/app/Settings/InternalUserSettings` |
| Client Contacts | `/app/Settings/CustomerContactSettings` |
