# Lien Waiver Tracking (Agent-Assisted)

## Overview
The agent helps the user track and manage lien waivers in Buildertrend — ensuring every sub/vendor provides the appropriate waiver (conditional or unconditional) before payments are released. This protects the company from mechanics liens and keeps payment documentation clean for lender/bank draws. The agent proactively alerts on missing waivers and generates status reports.

## Trigger
- the user says "check waivers for [project]" or "lien waiver status"
- Before making a payment — verify waivers are signed
- Monthly payment cycle — review all outstanding waivers
- the user asks "which subs are missing waivers?"
- Heartbeat check — flag paid bills without waivers
- Lender/bank requests waiver package for draw

---

## Step 1: Identify Project
**Action:** Confirm which project

**Message to the user:**
```
📜 Lien Waiver Tracking — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_lw_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_lw_project_1` |
| 🏗️ Project Beta | `primary` | `bt_lw_project_2` |
| 🏗️ Project Beta | `primary` | `bt_lw_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_lw_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_lw_project_4` |
| 🏗️ Project Eta | `primary` | `bt_lw_project_5` |
| 📊 All Projects | `primary` | `bt_lw_project_all` |
| ❌ Cancel | `danger` | `bt_lw_cancel` |

---

## Step 2: Choose Action
**Message to the user:**
```
📜 Lien Waivers — [project] — what do you need?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📊 Waiver Status Report | `success` | `bt_lw_report` |
| ⚠️ Missing Waivers | `danger` | `bt_lw_missing` |
| 📧 Request Waivers from Subs | `primary` | `bt_lw_request` |
| ✅ Verify Before Payment | `primary` | `bt_lw_verify_payment` |
| 📋 View by Sub | `primary` | `bt_lw_by_sub` |
| ❌ Cancel | `danger` | `bt_lw_cancel` |

---

## Step 3: Waiver Status Report
**Action:** Pull comprehensive waiver status from BT

### Browser Relay Execution
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/Bills`
3. Snapshot → parse bills table, focusing on:
   - **Lien Waivers** column
   - **Bill Status** column (Open, Paid)
   - **Pay To** column (sub/vendor name)
   - **Bill Amount** column
4. Cross-reference: each bill should have a corresponding waiver

**Present to the user:**
```
📜 Lien Waiver Report — [project]:

📊 Summary:
• Total bills: [N]
• Paid bills: [N]
• Waivers received: [N] ✅
• Waivers missing: [N] ⚠️
• Waivers pending: [N] ⏳

| # | Sub/Vendor | Bill # | Amount | Bill Status | Waiver Status |
|---|------------|--------|--------|-------------|---------------|
| 1 | [sub name] | [#] | $X,XXX | Paid | ✅ Unconditional signed |
| 2 | [sub name] | [#] | $X,XXX | Paid | ⚠️ MISSING |
| 3 | [sub name] | [#] | $X,XXX | Open | ⏳ Conditional pending |
| 4 | [sub name] | [#] | $X,XXX | Open | ✅ Conditional signed |

💰 Total paid without waivers: $[amount] ⚠️
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Request Missing Waivers | `danger` | `bt_lw_request_missing` |
| 🔒 Hold Payments Until Waived | `primary` | `bt_lw_hold` |
| 📄 Export Report | `primary` | `bt_lw_export` |
| 🔄 Refresh | `primary` | `bt_lw_refresh` |

---

## Step 4: Missing Waivers Alert
**Action:** Identify bills with missing waivers — especially paid bills

### Logic:
1. Filter bills where: status = Paid AND lien waiver = None/Missing
2. Sort by amount (largest risk first)

**Message to the user:**
```
⚠️ Missing Waivers — [project]:

🔴 PAID bills without waivers (HIGH RISK):

1. [Sub name] — Bill #[num] — $[amount] — Paid [date]
   ⚠️ No waiver on file — lien risk!

2. [Sub name] — Bill #[num] — $[amount] — Paid [date]
   ⚠️ No waiver on file — lien risk!

🟡 OPEN bills without waivers (pending):

3. [Sub name] — Bill #[num] — $[amount] — Open
   ⏳ Get waiver before payment

💰 Total at risk (paid, no waiver): $[total]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Request All Missing Waivers | `danger` | `bt_lw_request_all_missing` |
| 📧 Request from Specific Sub | `primary` | `bt_lw_request_specific` |
| ⏭️ Acknowledge Risk | `primary` | `bt_lw_acknowledge` |

---

## Step 5: Request Waivers from Subs
**Action:** Send waiver requests to subs via BT

### Browser Relay Execution (per bill)
1. Navigate to `/app/Bills`
2. Open the specific bill → **Lien Waiver tab**
3. Check if a waiver form is attached
4. If not: Apply the lien waiver form to the bill
5. Active subs can sign electronically via Sub Portal
6. For inactive subs: send via email

**Waiver Types:**
| Type | When to Use |
|---|---|
| **Conditional** | Before payment is made — "I'll waive lien rights once I receive $X" |
| **Unconditional** | After payment is received — "I have received $X and waive lien rights" |

### Request Flow:
1. **Before payment:** Request conditional waiver → sub signs → release payment
2. **After payment:** Request unconditional waiver → sub signs → file complete

**Message to the user after request:**
```
📧 Waiver request sent:

👷 [Sub name]
💰 Bill #[num] — $[amount]
📜 Type: [Conditional / Unconditional]
📊 Status: Pending sub signature
```

---

## Step 6: Verify Before Payment
**Action:** Pre-payment checklist — ensure all waivers are in order

**Message to the user:**
```
🔒 Payment Verification — [project]:

Bills ready for payment:

| # | Sub | Bill # | Amount | Waiver? |
|---|-----|--------|--------|---------|
| 1 | [sub] | [#] | $X,XXX | ✅ Conditional signed |
| 2 | [sub] | [#] | $X,XXX | ⚠️ MISSING — hold payment |
| 3 | [sub] | [#] | $X,XXX | ✅ Conditional signed |

✅ Clear to pay: [N] bills — $[total]
⚠️ Hold — missing waiver: [N] bills — $[total]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💳 Pay Cleared Bills | `success` | `bt_lw_pay_cleared` |
| 📧 Request Missing & Hold | `danger` | `bt_lw_hold_and_request` |
| 💳 Pay All (Override) | `danger` | `bt_lw_pay_override` |
| ❌ Cancel | `danger` | `bt_lw_cancel` |

---

## Step 7: View by Sub
**Action:** Show all waivers for a specific sub across all their bills

**Message to the user:**
```
Which sub/vendor?
```

**Show subs with bills on the project as inline buttons.**

**After selection:**
```
📜 Waiver History — [Sub name] — [project]:

| # | Bill # | Amount | Date Paid | Waiver Type | Status |
|---|--------|--------|-----------|-------------|--------|
| 1 | [#] | $X,XXX | [date] | Unconditional | ✅ Signed |
| 2 | [#] | $X,XXX | [date] | Conditional | ✅ Signed |
| 3 | [#] | $X,XXX | — | — | ⚠️ Missing |

💰 Total billed: $[total]
💰 Total with waivers: $[amount]
💰 Total without waivers: $[amount] ⚠️
```

---

## Lender/Bank Draw Package
When preparing a draw package that requires waivers:

**Message to the user:**
```
📦 Draw Package — waiver status for Draw #[N]:

| # | Sub | Amount This Draw | Waiver Type | Status |
|---|-----|-----------------|-------------|--------|
| 1 | [sub] | $X,XXX | Conditional | ✅ |
| 2 | [sub] | $X,XXX | Conditional | ⚠️ Missing |

✅ Ready: [N]/[total] waivers collected
⚠️ Missing: [N] — must collect before submitting draw
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Request All Missing | `danger` | `bt_lw_draw_request` |
| 📄 Export Waiver Package | `primary` | `bt_lw_draw_export` |
| ✅ Submit Draw (All Clear) | `success` | `bt_lw_draw_submit` |

---

## Post-Action
After waiver actions:

1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Update Apple Reminders** — track outstanding waiver requests
3. **Notify bookkeeper agent** — payment clearance status
4. **Flag for follow-up** — set reminder to check waiver status in 3 days

---

## Proactive Monitoring (Heartbeat)
On heartbeat checks, the agent can:

1. Navigate to `/app/Bills` → filter by Paid + No Waiver
2. If any found → alert the user:
```
⚠️ Found [N] paid bills without lien waivers on [project(s)].
Total at risk: $[amount]. Want me to pull the details?
```

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Waiver form not configured | Direct to Settings → Bills/POs/Budget → Lien Waivers |
| Sub not active (can't sign electronically) | Request waiver via email or paper |
| Waiver hidden on job | Check if "Hide on all jobs" is enabled in Settings |
| Sub can't access portal | Re-invite sub or send waiver via email |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |

---

## Waiver Type Decision Tree

```
Payment NOT yet made?
  └→ Request CONDITIONAL waiver
     └→ Sub signs: "I'll release lien upon receipt of $X"
     └→ Once signed → safe to release payment

Payment ALREADY made?
  └→ Request UNCONDITIONAL waiver
     └→ Sub signs: "I received $X and release all lien rights"
     └→ File for records
```

---

## Lien Waiver Settings
**URL:** Company Settings → Bills/POs/Budget → Lien Waivers section
**Options:**
- Hide on all jobs (disable lien waivers)
- Default additional signature line (e.g., notary)
- Custom lien waiver forms
- Online payments: require sub signature before receiving payment

---

## URL Patterns
| Page | URL |
|---|---|
| Bills (with waiver column) | `/app/Bills` |
| Bill Detail (Lien Waiver tab) | `/app/Bills/Bill/{billId}/{jobId}` |
| Lien Waiver Settings | `/app/Settings/BudgetSettings` |
