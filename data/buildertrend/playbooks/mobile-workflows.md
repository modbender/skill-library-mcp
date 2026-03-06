# Mobile Workflows
> Key mobile-specific workflows for daily logs, bills, POs, selections from phone

## Trigger
- the user is in the field and needs to create a daily log, bill, or PO from mobile
- Field crew needs to scan a receipt or capture site photos
- the user asks about mobile-specific BT operations

## Error Handling
| Issue | Resolution |
|---|---|
| App not syncing | Check internet connection, force-close and reopen app |
| Photos not uploading | Check storage permissions, try Wi-Fi instead of cellular |
| Daily log not saving | Save as draft, retry when connection is stable |
| Receipt scan unreadable | Retake photo with better lighting, ensure flat surface |
| BT session expired on mobile | Re-login in the app |

---

## Overview
Buildertrend's mobile app gives field teams the power to manage projects on-site. Key mobile capabilities:
- **Daily Logs** — Real-time job documentation
- **Bills & POs** — Create bills, scan receipts, manage purchase orders
- **Selections** — Review/approve selections, manage allowances
- **Quick Add** — Expedited creation of common items

---

## DAILY LOGS ON MOBILE

### Creating a Daily Log
1. Tap **Daily Logs** at bottom of screen
2. Tap **+ icon**
3. Select a **Job**
4. Fill out fields:
   - **Title** — Brief summary
   - **Date** — Cannot be future date
   - **Notes** — Detailed work/activity (use voice-to-text!)
   - **Attachments** — Camera photos, file uploads
   - **Share** — Toggle visibility:
     - Internal Users
     - Subs/Vendors
     - Clients
   - **Notify Users** — Send alerts on save
   - **Weather** — Auto-populates from job address
   - **Weather Notes** — Weather impact on work
   - **Tags** — For organization/search
5. Choose:
   - **Close Draft** — Save for later (only accessible on YOUR device)
   - **Save** — Submit the log

### Pro Tips for Field Use
- 📱 **Quick Add menu** — Fastest way to start a daily log
- 🎤 **Voice-to-text** — Dictate Notes instead of typing
- 📸 **Camera** — Before/after photos of work
- 🖼️ **Bulk photo select** — Multiple photos/videos from library
- 📝 **Draft system** — Update throughout the day, submit at end

### Related Items from Daily Logs
- Create **To-Do's** directly from a Daily Log
- Leave **Comments** for team coordination

---

## BILLS & PURCHASE ORDERS ON MOBILE

### Navigation
1. Select a **Job** from Jobs List
2. Tap **More** > **Bills / POs** (under Financial)

> Without selecting a job, shows Bills/POs from ALL active jobs.

### Creating a Purchase Order
1. Tap **+** from Purchase Orders tab
2. Fill out fields:
   - **PO #** — Auto-generated or custom
   - **Title** — Clear description
   - **Assignee** — Internal user or sub/vendor
   - **Materials Only** — Toggle for material-only POs
   - **Scope of Work** — Use voice-to-text!
   - **Link To** — Schedule item (for dynamic scheduling)
   - **Deadline & Time**
   - **Attachments** — Photos, scans, files
   - **Variance** — Toggle if this is a variance of a previous PO
   - **Line Items** — Itemized costs
3. Tap **Save**

### Releasing a PO from Mobile
1. Open saved PO
2. Tap **Save and Release**
3. Sub/vendor receives email to Approve or Decline
4. If sub has BT portal access, can approve from there

### Approving PO on Behalf of Sub (Mobile)
Ideal for in-person approvals or verbal confirmations:
1. Open released PO
2. Tap pencil icon next to Approval request
3. Click **Manually Approve**
4. Confirm you're approving on behalf of sub
5. **Sign with finger** — no tools needed on mobile!

### Creating a Bill from Scratch
1. Tap **+** from Bills tab > **Add Bill**
2. Fill out fields:
   - **Bill #** — Vendor's bill number
   - **Title** — Clear description
   - **Ready for Payment** — Check when finalized
   - **Pay To** — Sub/vendor or Misc (manual name)
   - **Description** — Purpose details
   - **Date Billed** / **Date Paid**
   - **Link To** — Schedule item
   - **Deadline & Time**
   - **Variance** — Toggle + Variance Code + Related PO
   - **Line Items** — Itemized costs
   - **Docs / Receipts** — Photos, scans, files
3. Tap **Save**

### Creating a Bill from a PO
1. Open the Purchase Order
2. Tap **Related Bills** tab
3. Tap **+ icon**
4. Select **Adjust Total Percentage** — enter % of PO to bill
5. Review/enter bill details
6. Tap **Save**

### ⭐ Scanning Receipts to Bills (Field Workflow)
1. Tap **+** from Bills tab
2. Select **Scan to New Bill**
3. Use phone camera to scan receipt
4. Receipt auto-attached to new bill

> **Better option:** Use the **Cost Inbox** feature for OCR auto-read of line items!

---

## SELECTIONS ON MOBILE

### Navigation
1. Select **Job** from Jobs List
2. Tap **More** > **Selections** (under Project Management)

### Creating a Selection
1. Tap **+** icon
2. Fill out fields:
   - **Title**, **Category**, **Location**
   - **Link To** — Schedule item deadline
   - **Deadline & Time**
   - **Single vs Shared** allowance
   - **Allowance** amount
   - **Required** — Toggle if client must choose
   - **Allow Multiple** — Toggle for multi-select
   - **Instructions** (visible to client)
   - **Internal Notes** (internal only)
   - **Attachments**
   - **Participation** settings:
     - Client: Allow to Add/Edit Choices
     - Vendors: Involved subs
     - Installers: Assigned for installation
3. Tap **Save**

### Adding Choices
1. Open the selection > tap **Edit**
2. Scroll to **Choices** section
3. Tap **Add Choice**
4. Fill out:
   - **Title**, **Attachments**
   - **Cost Format:** Flat Fee | Line Items | Request From Vendor
   - **Show Line Items to Client**
   - **Include in Budget**
   - **Builder Cost & Client Price**
   - **Client Price TBD?**
   - **Product Link**, **Description**, **Vendor**
5. Tap **Save** — repeat for all choices

### Releasing a Selection
Tap **paper airplane icon** or **Save & Release** to send to client.

### Approving on Behalf of Client
If client is inactive or doesn't have portal access:
1. Open selection > tap the choice
2. Select **Approve**
3. Confirm approving on behalf of client
4. Add comments if needed
5. Notification sent to team + listed subs/vendors/installers

### Managing Allowances
1. Navigate to **Allowances** tab in Selections
2. Tap **+** icon
3. Fields: Title, linked Selections, Notes, Line Items toggle, Builder Cost & Allowance Totals
4. Tap **Save**

---

## MOBILE BEST PRACTICES

### Daily Routine (Field Team)
1. ☀️ **Morning:** Clock in, check Today's Schedule
2. 📸 **Throughout day:** Take photos of work progress
3. 📝 **End of day:** Create/finalize Daily Log with notes + photos
4. 🧾 **As receipts come in:** Scan to Bill or Cost Inbox

### Receipt Capture Workflow
1. **Immediate:** Open BT app > Bills > + > Scan to New Bill
2. **Better:** Use Cost Inbox for OCR auto-read of line items
3. **Tag with:** Job, cost code, vendor name
4. **Attach receipt photo** to the bill

### Field Communication
- **Comments** on Daily Logs for status updates
- **To-Do's** from Daily Logs for follow-up items
- **PO approvals** in-person with finger signature

### Offline Considerations
- Draft Daily Logs save locally on YOUR device only
- Ensure connectivity before submitting financial items
- Photos attach from phone library even if taken offline
