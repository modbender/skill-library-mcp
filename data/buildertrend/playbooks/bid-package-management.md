# Bid Package Management (Agent-Assisted)

## Overview
The agent helps the user create bid packages in Buildertrend, invite subs to bid, track responses, compare bids side-by-side, award the winning bid, and auto-create a PO from the awarded bid. This workflow bridges estimating → procurement by formalizing sub pricing requests and keeping everything documented in BT.

## Trigger
- the user says "send bids for [project]" or "bid out [trade]"
- New project needs sub pricing for estimate
- procurement agent () requests formal bid process for a trade
- Estimate built → ready to solicit sub pricing
- the user asks "where are we on bids for [project]?"

---

## Step 1: Identify Project
**Action:** Confirm which project

**Message to the user:**
```
📨 Bid Package — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_bid_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_bid_project_1` |
| 🏗️ Project Beta | `primary` | `bt_bid_project_2` |
| 🏗️ Project Beta | `primary` | `bt_bid_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_bid_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_bid_project_4` |
| 🏗️ Project Eta | `primary` | `bt_bid_project_5` |
| ❌ Cancel | `danger` | `bt_bid_cancel` |

---

## Step 2: Choose Action
**Message to the user:**
```
📨 Bids for [project] — what do you need?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➕ Create Bid Package | `success` | `bt_bid_create` |
| 📋 View Active Bids | `primary` | `bt_bid_view_active` |
| 📊 Compare Responses | `primary` | `bt_bid_compare` |
| 🏆 Award Bid | `primary` | `bt_bid_award` |
| ❌ Cancel | `danger` | `bt_bid_cancel` |

---

## Step 3: Create Bid Package

### 3A: Trade / Scope Selection
**Message to the user:**
```
📨 New Bid Package — which trade or scope?
```

**Inline buttons (common trades):**
| Button | Style | callback_data |
|---|---|---|
| 🔨 Demolition | `primary` | `bt_bid_trade_demo` |
| 🧱 Framing / Carpentry | `primary` | `bt_bid_trade_framing` |
| ⚡ Electrical | `primary` | `bt_bid_trade_electrical` |
| 🔧 Plumbing | `primary` | `bt_bid_trade_plumbing` |
| ❄️ HVAC | `primary` | `bt_bid_trade_hvac` |
| 🧱 Drywall | `primary` | `bt_bid_trade_drywall` |
| 🎨 Painting | `primary` | `bt_bid_trade_painting` |
| 🪵 Flooring | `primary` | `bt_bid_trade_flooring` |
| 🪨 Masonry | `primary` | `bt_bid_trade_masonry` |
| 🔩 Steel / Metal | `primary` | `bt_bid_trade_steel` |
| 🪟 Windows & Glazing | `primary` | `bt_bid_trade_windows` |
| 🧯 Fire Protection | `primary` | `bt_bid_trade_fire` |
| ✏️ Custom Scope | `primary` | `bt_bid_trade_custom` |

### 3B: Bid Package Details
**Message to the user:**
```
📝 Bid Package Details:

• Title: [suggested: "[Trade] — [Project]"]
• Description/scope of work: (what's included?)
• Cost codes: [auto-suggested based on trade]
• Deadline: (when do you need bids back?)
```

**Smart defaults by trade:**
| Trade | Suggested Title | Suggested Cost Codes | Typical Deadline |
|---|---|---|---|
| Demolition | "Demolition — [Project]" | 20.10 Demolition | 1 week |
| Electrical | "Electrical — [Project]" | 08.00 Electrical | 2 weeks |
| Plumbing | "Plumbing — [Project]" | 07.00 Plumbing | 2 weeks |
| HVAC | "HVAC — [Project]" | 09.00 HVAC | 2 weeks |
| Framing | "Framing — [Project]" | 05.00 Carpentry/Framing | 1 week |
| Drywall | "Drywall — [Project]" | 10.00 Insulation & Drywall | 2 weeks |
| Painting | "Painting — [Project]" | 14.00 Painting and Coating | 1 week |
| Flooring | "Flooring — [Project]" | 15.00 Flooring & Tile | 2 weeks |

### 3C: Attach Plans & Documents
**Message to the user:**
```
📎 Attach plans and documents to the bid package?

Subs need drawings, specs, and scope details to price accurately.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📎 Upload Files | `primary` | `bt_bid_attach_upload` |
| 📁 Select from BT Files | `primary` | `bt_bid_attach_bt` |
| ⏭️ No Attachments | `primary` | `bt_bid_no_attach` |

---

## Step 4: Select Subs to Invite

**Message to the user:**
```
👷 Which subs should receive this bid request?
```

### Browser Relay: Pull Subs List
1. Navigate to BT's sub/vendor list for this job (or global)
2. Filter by trade matching the bid package
3. Present as buttons

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ☑️ [Sub 1 — Trade] | `primary` | `bt_bid_sub_[id]` |
| ☑️ [Sub 2 — Trade] | `primary` | `bt_bid_sub_[id]` |
| ☑️ [Sub 3 — Trade] | `primary` | `bt_bid_sub_[id]` |
| ✅ All [Trade] Subs | `success` | `bt_bid_sub_all` |
| ➕ Add New Sub | `primary` | `bt_bid_sub_new` |
| ✅ Done Selecting | `success` | `bt_bid_sub_done` |

**Note:** Subs don't need to be active BT users to receive bid requests — inactive subs receive via email.

---

## Step 5: Final Review & Send

**Message to the user:**
```
📨 Bid Package Ready:

📋 Title: [title]
🏗️ Project: [project]
📝 Scope: [description summary]
💰 Cost Codes: [XX.XX — Name]
📅 Deadline: [date]
📎 Attachments: [N] files
👷 Invited Subs: [N] subs
  • [Sub 1]
  • [Sub 2]
  • [Sub 3]

Send bid requests?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Send Bid Requests | `success` | `bt_bid_send` |
| ✏️ Edit Package | `primary` | `bt_bid_edit` |
| 💾 Save as Draft | `primary` | `bt_bid_save_draft` |
| ❌ Cancel | `danger` | `bt_bid_cancel` |

---

## Step 6: Create Bid Package via Browser Relay
**Action:** Execute in Buildertrend

### Browser Relay Execution
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/BidPackages`
3. Snapshot → verify Bids page loaded
4. Click **"Create new Bid Package"** button
5. In the bid package form:
   - Set **Title** (text input)
   - Set **Description / Scope of Work** (rich text — CKEditor)
   - Set **Cost Codes** (combobox — select matching codes)
   - Set **Deadline** (date picker)
   - **Requests tab:** Select subs to invite
     - Click sub names to add them to the bid request
   - **Attachments:** Upload plans/docs or link from BT files
6. Click **Send** (releases bid requests to subs) or **Save** (draft)
7. Snapshot → confirm bid package created

**Report back:**
```
✅ Bid Package sent!

📨 [title]
🏗️ Project: [project]
👷 Sent to [N] subs
📅 Deadline: [date]
📊 Status: Released — awaiting responses
```

---

## Step 7: Track Responses
**Action:** Monitor bid responses

### Browser Relay Execution
1. Navigate to `/app/BidPackages`
2. Snapshot → parse bid package table
3. Check response status per sub

**Present to the user:**
```
📊 Bid Responses — [trade] — [project]:

📅 Deadline: [date] ([N] days remaining / PASSED)

| # | Sub | Amount | Status | Submitted |
|---|-----|--------|--------|-----------|
| 1 | [Sub name] | $XX,XXX | ✅ Received | [date] |
| 2 | [Sub name] | $XX,XXX | ✅ Received | [date] |
| 3 | [Sub name] | — | ⏳ Pending | — |
| 4 | [Sub name] | — | ❌ Declined | [date] |

📊 [N] received / [N] total invited
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Remind Pending Subs | `primary` | `bt_bid_remind` |
| 📊 Compare Bids | `primary` | `bt_bid_compare` |
| 🏆 Award Bid | `success` | `bt_bid_award` |
| ➕ Invite More Subs | `primary` | `bt_bid_invite_more` |
| 🔄 Refresh | `primary` | `bt_bid_refresh` |

---

## Step 8: Compare Bids Side-by-Side
**Action:** Present bid comparison

**Message to the user:**
```
📊 Bid Comparison — [trade] — [project]:

| | [Sub 1] | [Sub 2] | [Sub 3] |
|---|---------|---------|---------|
| **Total** | $XX,XXX | $XX,XXX | $XX,XXX |
| **vs Budget** | ✅ -$X,XXX | ⚠️ +$X,XXX | ✅ -$XXX |
| **Scope Notes** | [notes] | [notes] | [notes] |
| **Exclusions** | [any] | [any] | [any] |
| **Timeline** | [if stated] | [if stated] | [if stated] |

💰 Budget estimate: $[budgeted amount from estimate]
💡 Lowest: [Sub name] — $XX,XXX
💡 Highest: [Sub name] — $XX,XXX
📊 Spread: $[difference]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏆 Award to [Lowest] | `success` | `bt_bid_award_[id]` |
| 🏆 Award to [Other] | `primary` | `bt_bid_award_[id]` |
| 📧 Request Revised Bid | `primary` | `bt_bid_revise` |
| ⏭️ Defer Decision | `primary` | `bt_bid_defer` |

---

## Step 9: Award Bid
**Action:** Award the winning bid and optionally auto-create PO

**Message to the user:**
```
🏆 Award [trade] bid to [Sub name] — $[amount]?

This will:
• Mark bid as Approved in BT
• Update Estimate with awarded pricing (even if locked)
• Notify [Sub name] they won
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏆 Award & Create PO | `success` | `bt_bid_award_po` |
| 🏆 Award Only (No PO Yet) | `primary` | `bt_bid_award_only` |
| 📧 Notify Losing Subs | `primary` | `bt_bid_notify_losers` |
| ❌ Cancel | `danger` | `bt_bid_cancel` |

### Auto-Create PO from Awarded Bid
1. Navigate to the awarded bid in BT
2. Click **"Add Schedule Item"** or **"Create PO"** action (from Bids grid)
3. BT pre-fills PO from bid: cost codes, amounts, vendor
4. Review → fill any missing fields (deadline, scope notes)
5. Save or Release PO

Follow `create-po.md` playbook for PO details.

### Notify Losing Subs
**Template message (comment on their bid):**
```
Thank you for your bid on [trade] for [project]. After careful review, we've decided to go with another contractor for this scope. We appreciate your time and look forward to working together on future projects.
```

---

## Step 10: Post-Action
After bid is awarded:

1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Update Apple Reminders** — track PO creation and sub mobilization
3. **Notify procurement agent** — bid awarded, PO created/pending
4. **Notify bookkeeper agent** — new committed cost, PO amount
5. **Update Estimate** — awarded bid auto-updates estimate (even when locked)
6. **Add Schedule Item** — from bid (if construction timeline is set)

---

## Batch Mode: Multiple Bid Packages
When bidding out multiple trades for a new project:

1. Ask: "Which trades need bids?"
2. Present trade checklist with inline buttons
3. Create bid packages for each selected trade
4. Use same plans/docs across packages where applicable
5. Set consistent deadlines
6. Summary: "Created [N] bid packages — invited [N] subs total"

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Sub not in BT system | Ask to add sub first (Users → Subs/Vendors) |
| Sub has no email | Cannot send bid request — ask to add email |
| No cost codes on job | Create from estimate or add manually |
| Bid deadline passed | Warn, offer to extend deadline |
| Attachment too large | Compress or split file, or link from external source |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |

---

## Bid Status Lifecycle

| Status | Meaning | Next Action |
|---|---|---|
| Draft | Package created, not sent | Edit & send |
| Released | Sent to subs | Awaiting responses |
| Received | Sub submitted pricing | Review & compare |
| Pending | Sub hasn't responded yet | Follow up / remind |
| Declined | Sub declined to bid | Note, invite others |
| Approved | Bid awarded | Create PO, notify subs |

---

## URL Patterns
| Page | URL |
|---|---|
| Bid Packages | `/app/BidPackages` |
| Bid Settings | `/app/Settings/BidSettings` |
