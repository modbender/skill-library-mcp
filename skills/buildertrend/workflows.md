# Buildertrend Workflows
> Step-by-step procedures extracted from official Buildertrend Help Center articles
> Created: February 19, 2026

---

## Table of Contents
1. [How to Create a Job](#1-how-to-create-a-job)
2. [How to Create/Manage Schedule Items](#2-how-to-createmanage-schedule-items)
3. [How to Create Daily Logs](#3-how-to-create-daily-logs)
4. [How to Create/Manage Change Orders](#4-how-to-createmanage-change-orders)
5. [How to Create/Manage POs and Bills](#5-how-to-createmanage-pos-and-bills)
6. [How to Create Invoices](#6-how-to-create-invoices)
7. [How to Manage Selections](#7-how-to-manage-selections)
8. [How to Use Job Costing](#8-how-to-use-job-costing)
9. [How to Sync with QuickBooks Online](#9-how-to-sync-with-quickbooks-online)
10. [How to Create Estimates/Proposals](#10-how-to-create-estimatesproposals)
11. [How to Manage Bids](#11-how-to-manage-bids)
12. [How to Use the Cost Inbox](#12-how-to-use-the-cost-inbox)
13. [How to Set Up and Manage To-Dos](#13-how-to-set-up-and-manage-to-dos)
14. [How to Manage RFIs](#14-how-to-manage-rfis)
15. [How to Track Time](#15-how-to-track-time)
16. [How to Manage Documents/Photos/Videos](#16-how-to-manage-documentsphotosvideos)
17. [How to Add/Invite Clients](#17-how-to-addinvite-clients)
18. [How to Add/Manage Subcontractors](#18-how-to-addmanage-subcontractors)

---

## 1. How to Create a Job

### From Scratch
1. Go to **Jobs Menu** → click **New Job**
2. Select **From Scratch**
3. Fill in required fields:
   - **Title** (required) — use consistent naming (address or address + client name)
   - **Type** (required) — select project type (new construction, remodel, etc.)
   - **Contract Type** (required) — Fixed Price or Open Book
   - **Work Days** (required) — set default work week
   - **Zip Code** (required) — in address section
4. Fill optional fields:
   - Prefix, Job Group, Status, Contract Price
   - Project Managers, Square feet, Permit number, Lot info
   - Projected/Actual start and completion dates
   - Schedule color, Notes (internal / sub-vendor), Custom fields
5. Click **Save**

### From a Template
1. Go to **Jobs Menu** → click **New Job**
2. Select **Your Templates**
3. Fill in required job information under **New Job Information**
4. Select template from **Source Template** dropdown
5. Use **checkboxes** to select templated items to import (Estimate, Schedule, Selections, To-Dos, etc.)
6. Review/modify **Project Managers, Subs/Vendors, and Workdays**
7. Click **Save**

### After Creating a Job
- Add clients (see Workflow #17)
- Set up cost codes and estimate
- Build schedule
- Invite subs/vendors

---

## 2. How to Create/Manage Schedule Items

### Setting Up Workdays (Do This First)
1. Select job → **Job Info**
2. Adjust **Work Days** dropdown
3. For exceptions: use **Workday Exceptions** (temporary additions/removals)
4. ⚠️ Changing workdays on active jobs may shift existing items

### Creating Schedule Items
1. Job → **Project Management** → **Schedule**
2. Create via:
   - Click **New Schedule Item**, OR
   - Click on a specific calendar day, OR
   - Highlight multiple days
3. Fill in: Title, Display Color, Assignees, Start/End Dates, Work Days
4. Click **Save**

### Importing Schedule from Template
1. Schedule → **More Actions** → **Import from Templates**
2. Select **Source Template**
3. Check **Schedule** under Items to Copy
4. Set **New Start Date**
5. Click **Import**

### Adding Details to Schedule Items
- **Notes tab:** All Notes (everyone), Internal Notes (team), Sub Notes (team + subs), Client Notes (team + clients)
- **Files tab:** Create Word/Excel doc or upload files; set visibility per user type

### Setting Up Predecessors (Dependencies)
1. Switch to **Gantt view**
2. **Finish-To-Start:** Drag circle from END of Task A to START of Task B
3. **Start-To-Start:** Drag circle from START of Task A to START of Task B
4. **Lag time:** Add positive number (delay between tasks)
5. **Lead time:** Add negative number (overlap between tasks)
6. To remove: click the connecting line → confirm

### Setting the Baseline
1. **Baseline tab** → click **Set Baseline** (once initial schedule is complete)
2. View expected vs actual dates, durations, and slips

### Publishing Your Schedule
- **Offline mode:** Private building, no notifications to trades/clients
- **Online mode:** Live, notifications active, schedule conflicts shown
- Toggle via the Schedule on/off switch

### Mobile Schedule Management
- Covered in "Schedule on Mobile" article
- Create/edit tasks, adjust dates, assign users from phone

---

## 3. How to Create Daily Logs

### Desktop
1. Job → **Project Management** → **Daily Logs**
2. Click **+ Daily Log**
3. Add: Notes, Attachments
4. Optional: Title, Tags
5. Date defaults to today (adjustable); Weather auto-updates by zip code
6. Click **Save**
7. After saving: add To-Dos, Comments, or RFIs

### Mobile
1. Select Job → **Daily Logs** (menu bar)
2. Tap **(+)** button
3. Add Notes, Attachments (camera roll or real-time photo/video)
4. Set Weather Conditions visibility
5. To annotate photos: select paintbrush icon → highlight, circle, etc. → Attach
6. Click **Save**
7. To edit: tap the Log → Edit → add attachments/update notes → Save
8. Use Comments or To-Do at bottom of log
9. Filters: Keywords, Dates, etc.

### Best Practices
- Include photos of job progress daily
- Tag logs for easy categorization (e.g., Rainout, Inspection, Delivery)
- Document safety incidents, client conversations, meeting minutes
- File attachments carry over as permanent documentation

---

## 4. How to Create/Manage Change Orders

### Creating a Change Order
1. Job → **Project Management** → **Change Orders**
2. Click **+Change Order**
3. **Details Tab:**
   - Title, ID # (auto or custom), Approval Deadline
   - Payment: "Invoice upon client approval" (auto-creates invoice)
   - Introduction Text, Closing Text
   - Attachments, Subs/Vendors (auto-notified on approval)
   - Notes: Internal, Sub/vendor, Client
4. **Estimate Tab:**
   - Choose **Flat Fee** or **Line Items** (Line Items recommended for proper cost coding)
   - Add items manually, from Cost Catalog, or Cost Codes
   - Include Profit & Tax
5. **Client Preview Tab:**
   - Review client view
   - Control visible information
6. Click **Send** to share with client

### Internal Approval (on behalf of client)
1. Select Change Order from dashboard
2. Details tab → scroll to **Approval Status** → **Approve**
3. Apply e-signature → **Approve**

### Client Approval
- Via email: click approve link
- Via Client Portal: navigate to Change Orders → approve
- Digital signature collected

### Allowing Client CO Requests
1. Job Details → Clients tab → check **Change Order Requests** permission
2. Client: CO dashboard → **+Change Order Request** → submit

### Mobile Change Orders
- More → Project Management → Change Orders
- View details, add attachments, comments
- Full creation and management available

### Key Tips
- Use Line Items (not Flat Fee) for accurate job costing
- Set Approval Deadlines to keep project on schedule
- Auto-invoice option streamlines billing
- CO costs flow to Revised Budget and Job Running Total

---

## 5. How to Create/Manage POs and Bills

### Creating a Purchase Order
1. Job → **Financials** → **Purchase Orders**
2. Click **+Purchase Order** → **Purchase Order**
3. Fill fields: Title, Assignee, Scope of Work, Deadline, Line Items
4. Click **Send** (to sub/vendor) or **Save** (without releasing)

### Creating PO from Other Features
- From Change Orders, Bids, Selections, or Estimate
- Check items → **Create PO** or **Add to Existing PO**

### Releasing & Approving POs
1. Click **Send** to release to sub/vendor
2. Sub receives email → Review → **Approve** (sign) or **Decline**
3. Or approve internally: **Approve** or **Approve With Signature**

### Amending Approved POs
1. Click **Amend** on approved PO
2. Edit/add line items
3. View changes breakdown
4. Resend for sub reapproval
5. ⚠️ Cannot reduce below already-billed amounts

### Creating a Bill from Scratch
1. Job → **Financials** → **Bills** → **+Bill**
2. Fill: Title, Pay To, Date Billed, Description, Line Items
3. Add Approvers if needed
4. Click **Save**

### Creating a Bill from a Purchase Order
1. Open PO → **Bills/Lien Waivers** → **New Bill**
2. Set % or amount per line item → **Create Bill**
3. Auto-fills: Title, Pay To, Linked PO, Costs

### Auto-Fill Bill from Receipt (OCR)
1. Click **Star Icon** → upload file
2. OCR auto-fills: Title, Vendor, Dates, Cost Items
3. Use **Bulk Actions** for Merge, Edit Cost Codes, Edit Cost Types
4. Side-by-side view available → **Save**

### Creating a Bill from Cost Inbox
- See Workflow #12

### Paying Bills
Three options:
1. **Pay Online** (Buildertrend Payments)
2. **Record Offline Payment** (external payment like QuickBooks)
3. **Mark Ready for Payment** (sends notification)

### Mass Actions (Checked Boxes)
- **Bill Remaining Amount:** Immediately create bill from PO
- **Mark Work Complete:** Show item ready for billing
- Mass pay available (full amounts only, 1 email per PO)

### Mobile POs and Bills
1. Job → More → Bills/POs
2. **PO:** + → fill fields → Save → Save and Release
3. **Bill:** + → Add Bill or Scan to New Bill → fill → Save
4. **Bill from PO:** Select PO → Related Bills → + → adjust % → Save

---

## 6. How to Create Invoices

### Creating an Invoice
1. Job → **Financials** → **Invoices** → **+ Invoice**
2. Fill: Title, ID #, Due Date (date, payment terms, or linked schedule item)
3. Set Tax rate (if applicable)
4. Choose **Flat Fee** or **Line Items**
5. Add costs:
   - Manually (+ Item)
   - From Estimate, Change Orders, Selections, Bills, Time Clock, QB Costs
6. Click **Save**

### Adding Costs from Existing Features
- **Fixed Price:** Add from Estimate + Selections (track within contract), Change Orders (deviations)
- **Open Book:** Add from Costs (uninvoiced Bills, Time Clock, QB Costs); filter by date

### Progress Invoicing (Bank/Commercial Projects)
1. Arrow next to Invoice → **Progress Invoice**
2. Auto-pulls Schedule of Values from Estimate
3. Enter **% complete** per line
4. Export for lender adjustments
5. Send to client; push to QB

### Draw Schedule (Fixed Price Only)
1. Job Details → Advanced Settings OR Invoice dashboard → **+Create Draw**
2. Set number of draws, percentages, titles
3. Optional: link each draw to schedule item
4. After estimate sent to budget: draft invoices auto-created
5. Share Draw Schedule with client

### Formatting
1. Save invoice → **…** → **Format & Preview**
2. Options: Hide Line Items, Show Edit Options, Combine by cost code
3. Click **Save**

### Sending to Client
1. Click **Send**
2. Select clients to receive email notification
3. Click **Send**
4. Non-active clients: email only; Active: BT + email

### Recording Payment
1. **Buildertrend Payments:** Client pays through portal
2. **QuickBooks/Xero:** Marked as paid when synced
3. **Record Offline:** Record payment → Date, Amount, Method, Receiver → **Record Payment** → Notify client

---

## 7. How to Manage Selections

### Creating a Selection
1. Job → **Project Management** → **Selections** → **New Selection**
2. Fill: Title, Category, Location, Deadline
3. Options: Require client selection, Single vs Shared allowance, Allowance amount
4. Add Public Instructions (client-facing) and Internal Notes
5. Add Attachments → **Save**

### Adding Choices
1. Open Selection → **Create New Choice** or **Add Choices**
2. Fill: Choice Title, Product Link, Include in Budget
3. Add Attachments (💡 include photos!)
4. Price Details: **Flat Fee**, **Line Items**, or **Request From Sub/Vendor**
5. Add Product Description → **Save**
6. Repeat for multiple choices
7. Click **Send** when ready for client review

### Client Approval
- Active clients approve via Client Portal
- Builder can approve on behalf: click **Approve** next to choice
- Client provides signature and optional comments
- Notification sent to team and listed subs/vendors

### Sub/Vendor Price Requests
- Outstanding Pricing Requests show in Sub Portal
- Sub clicks **Submit Price(s)** → select Choice → enter Price Details → **Save**
- Sub can also **Add Choices** if permitted

### Templating Selections
- Create templates for reuse across projects
- Build from scratch or copy from existing job
- Break into tier groups or all-inclusive catalogs

---

## 8. How to Use Job Costing

### Initial Setup
1. **Confirm accounting method:** Company Settings → Bills/POs/Budget → Cash or Accrual
2. **If using QBO:** Enable "Sync from QuickBooks" for alignment
3. **Establish Cost Codes** (CRITICAL: do this before any financial features)

### Populating the Budget
1. Build your **Estimate** (see Workflow #10)
2. From Estimate → click **Send to Budget**
3. Review Total Price, Builder Cost, Profit, Margin → **Send to Budget**
4. Budget is now active with Original Budget Costs

### Monitoring the Budget
- **Profitability Summary** (top of budget): Shows Projected Total Costs, Client Price, Invoiced amounts
- **Cost Code drill-down:** Click any item for detailed info without leaving budget
- **Related Items:** View specific bills, POs, time entries linked to each cost code

### Customizing Your View
- Use pre-saved views: Job Costing, Client Pricing, Profit View, Standard View
- Create custom views: bottom-right dropdown → ellipsis → create
- Filter by Related Items or Cost Types

### Making Cost Adjustments
When you anticipate changes but lack documentation:
1. Click **Projected Costs** total for a cost code
2. Click **+Adjustment**
3. Enter amount and note → **Save**
4. ⚠️ **Delete adjustment** when proper documentation (bill/PO) arrives to avoid duplicates

### Sharing with Clients
1. Job Settings → **Client tab**
2. Select columns to share with Customer Portal
3. Default: NOT shared

### Key Budget Concepts
- **Original Budget = Signed Proposal**
- **Revised Budget = Original + Selections + Change Orders**
- **Committed = Approved POs + Variance POs + Unapproved Time**
- **Actual = Bills + Variance Bills + Approved Time + QB Costs**
- **Projected = Greatest of Revised, Committed, or Actual**
- **Complete flag = Projected resets to equal Actual**

---

## 9. How to Sync with QuickBooks Online

### Initial Connection
1. Company Settings → **Accounting** → **Get started with QuickBooks**
2. Follow prompts to connect your QBO account
3. Configure default accounting options

### Linking Entities

**Cost Codes → QBO Products & Services:**
1. Company Settings → Cost Codes → Import → QuickBooks
2. Map each QB item to a BT Cost Code (create new or select existing)

**Jobs → QBO Customers/Projects:**
1. Job Details → Accounting tab → **Link job**
2. Select corresponding QBO Customer/Job
3. Or auto-link during job creation (if enabled in settings)

**Subs/Vendors → QBO Vendors:**
1. Sub/Vendor contact card → Accounting tab → **Link sub**
2. Select corresponding QBO Vendor

### Pushing Bills to QBO
1. Create Bill in BT
2. Check **Send to QuickBooks** → **Save** (pushes immediately)
3. Or save without checking → push later from Bills dashboard → **Send to QuickBooks**
4. 💡 Set default in Accounting settings to auto-check

### Pushing Invoices to QBO
1. Create Invoice in BT
2. Check **Invoice to QuickBooks on Send**
3. Send to client → auto-pushes to QBO
4. Or push later: open sent invoice → **Create Invoice** from QB Status section

### Pushing Time Clock to QBO
- Enable auto-push in Accounting settings
- Or manually: approve shift → **Send to QuickBooks**
- Mass actions: multi-select → approve → send to QB in bulk

### Pushing Deposit Payments
1. Create deposit → collect payment (BT Payments or offline)
2. Open paid deposit → **Send to QuickBooks**
3. Creates payment in Undeposited Funds
4. In QBO: Create Bank Deposit → match to bank transaction
5. ⚠️ Turn off auto-apply credits in QBO

### Pushing Credit Memos
- With active client: "Send to QuickBooks on Release" checkbox
- Without active client: Save → ellipsis → **Save to Accounting**

### Receiving Data from QBO

**Import Estimate:** Estimate → External Import → QuickBooks → Map fields/codes

**Invoice Payments:** Paid in QBO → auto-marked Paid in BT

**Bill Payments:** Paid in QBO → auto-marked Paid in BT

**QB Expenses → Budget:**
1. Enable: Company Settings → "Include costs entered in QuickBooks in budget by default when linking jobs"
2. Or per job: Job Details → Advanced Settings → "Include costs entered in QuickBooks in the budget"
3. Expense types pulled: Bill, Expense, Check, Vendor Credit, Credit Card Credit

### Bank Feed Matching (Important)
1. Create Bill in BT → Push to QBO
2. QBO → Bank transactions → Find matching transaction
3. Click **Match** to create Bill payment
4. Both BT and QBO bills marked as paid
5. If no auto-match: manually search in "Find other matches"

---

## 10. How to Create Estimates/Proposals

### Prerequisites
- ⚠️ **Establish Cost Codes FIRST**

### Creating an Estimate

**Method 1: Add Items Line by Line**
1. Job → Financials → Estimate → **Add Item**
2. Fill: Title, Cost Code, Cost Type, Group, Description, Internal Notes
3. Set: Unit Cost, Quantity, Unit label, Markup/Margin
4. Option: Include Item in Catalog → **Save**

**Method 2: Import from Excel**
1. **External Import → Excel**
2. Download template → fill in data → save
3. Browse Computer → select file → Map columns → Map cost codes → Import

**Method 3: Import from Template**
1. **Template Import → Import Job Template**
2. Select template → Check Estimates → **Import**

**Method 4: Add from Cost Catalog**
1. Click **Add from Cost Catalog** → select items → **Add To Estimate**

**Method 5: Add from Cost Codes**
1. Click **Add from Cost Codes** → select codes → **Add** (creates blank lines)

### Making Items Taxable
1. Set job tax rate: Job Details → Advanced Settings
2. Check **Taxable** on individual items or use bulk actions
3. Tax totals shown in Tax column

### Organizing the Estimate
- **Custom Grouping:** Room-by-room, lists, assemblies; Add Group → create title/description
- **Cost Code Grouping:** Auto-format by cost categories/phases
- Move items between groups: checkboxes → Move Items → select destination
- Reorder: drag six-dot handle

### Locking the Estimate
1. Click **Lock Estimate** (prevents edits except approved Bids/Selections)
2. Unlock anytime if changes needed

### Creating a Proposal
1. Click **+Proposal**
2. **Details tab:** Set signatures, signees, title, deadline, intro/closing text, attachments
3. **Client Preview tab:** Choose Standard or Custom Layout
   - Custom: adjust Layout Options, Company/Contact Info display
   - Select fields to show: Item Title, Cost Code, Description, Quantity, Unit Price, Total Price, etc.
4. Click **Send** to release to client

### Client Approval
- Active clients: approve in Client Portal
- Non-active: approve via email link
- Internal approval: ellipsis → Approve for "signee" → signature → Approve

### After Proposal Approval: Send to Budget
1. From Estimate → **Send to Budget**
2. Review Total Price, Builder Cost, Profit, Margin
3. Click **Send to Budget** → Job Costing Budget activated

### Multiple Proposals
- Update estimate → create new proposal for each iteration
- All versions shown on **Proposal Dashboard**
- Can pull cost lines from previous proposals: View Worksheet → checkbox → Copy to estimate

---

## 11. How to Manage Bids

### Overview
- Bids are requests for pricing sent to subs/vendors
- Grouped into Bid Packages with plans and documents

### Key Actions:
- Add subs to released Bids: open Bid → Edit Bid Package → Requests tab → select sub
- Add documents to multiple Bids: check boxes → Add Documents → upload
- Create Schedule Item from approved Bid: Bids grid → "Add Schedule Item"
- Approved Bids update Estimate (even when locked)

### Sub/Vendor Bid Response:
- Active subs: respond through Sub Portal
- Inactive subs: respond via email
- Both can receive and respond to Bid Requests

---

## 12. How to Use the Cost Inbox

### Overview
Central hub for incoming financial data (receipts and expenses).

### Key Features:
- Upload receipts directly into Cost Inbox
- OCR technology reads receipt and inputs line items
- Create Bills from scanned receipts
- Auto-include tax line items option (Company Settings)

### Permissions Required:
- View, Add, Edit minimum
- "Global – Can see all Receipts" for all receipts (not just your uploads)

### Mobile Workflow:
1. Bills/POs → + → **Scan to New Bill**
2. Use camera to scan receipt
3. OCR processes → review/edit → Save

---

## 13. How to Set Up and Manage To-Dos

### Desktop
1. Job → **Project Management** → **To-Do's**
2. Click **New To-Do**
3. Fill: Title, Notes, Priority, Due Date, Attachments
4. Add **Checklist Items** for sub-tasks
5. Assign to self or other users
6. **Save**

### Completing To-Dos
1. Mark Checklist Items complete (check circle)
2. When all items done: **To-Do is Complete** → **Save**
3. Builder receives notification

### From Subs/Clients
- Builders assign To-Dos to subs
- Subs can create To-Dos for themselves (auto-assigned, visibility options)
- Clients can create To-Dos for themselves in Client Portal

### Mobile
1. Job → To-Do's (menu bar) → (+)
2. Add Title, Notes, Deadline, Reminders, Checklist Items, Priority
3. Use Filters for Keywords, Dates, etc.

### Best Practice Tags:
Client ToDo, Client Meeting, Inspection, Punchlist, PM Tasks, Material Orders, Pre-Con Checklist, Clean Up, Safety Meeting

---

## 14. How to Manage RFIs

### Overview
RFIs (Requests for Information) are formal messaging with deadlines for project questions. Responses documented and stored.

### Creating RFIs
- From Schedule Items, Daily Logs, Change Orders, POs, Files, Comments
- Select **Create RFI** within the feature
- Set title, question, deadline, assignee

### RFI Capabilities:
- Internal users, subs, and clients can create/respond
- Responses documented and logged
- Available on Desktop and Mobile
- Accessible from multiple features

---

## 15. How to Track Time

### Overview
Time Clock tracks labor for job costing and payroll with GPS verification.

### Key Concepts:
- Time Clock Labor Codes: Cost Codes marked available for Time Clock
- Default Labor Code per user (streamlines clock-in)
- Breaks: Designated pauses during shifts
- GPS tracking for location verification

### Time Clock + Budget:
- Company Settings: "Include Time Clock Labor in Job Costing Budget on new jobs"
- Unapproved shifts → Committed Costs
- Approved shifts → Actual Costs

### Time Clock + QuickBooks:
- Auto-push on approval (if enabled)
- Manual: approve → Send to QuickBooks
- Mass actions for bulk processing
- ⚠️ Overtime hours NOT auto-sent to QBD; manual entry needed

### Tags for Time Clock:
Left Early, Overtime, PTO, Approved, Amended Time, Extra Work Day, Forgot to Clock In, Mileage, Shift Edit, Pickup/Delivery, Errand, Change Order Labor

---

## 16. How to Manage Documents/Photos/Videos

### File Types:
- **Documents:** Supports annotations and sharing
- **Photos:** Upload via Files tab or attach to features
- **Videos:** Upload via Files tab or attach to features

### File Locations:
- **Job Files:** Stored in folders within each job
- **Global Documents:** Company-wide files not tied to specific job
- **Feature Attachments:** Attached to Daily Logs, To-Dos, etc.

### Sub/Vendor Files:
- View permitted folder files
- Personal "Subcontractor Uploaded Files" folder (visible to builder + sub only)
- Can share documents with customers (if permitted)

### Client Files:
- Upload to "Client Uploaded Files" folder
- Within Photos, Documents, or Video sections

### Mobile:
- Upload from camera roll or capture in real-time
- Annotate photos (highlight, circle, draw)
- Attach to Daily Logs, To-Dos, etc.

---

## 17. How to Add/Invite Clients

### Adding a Client
1. Job Details → **Clients tab**
2. **+ New Contact:** Fill out contact info → Save
3. **+ Existing Contact:** Search and select from Contact List
4. Click **Save**
5. If email provided: prompted to invite immediately (or later)

### Inviting a Client
1. Review **permissions** (what they can access)
   - 💡 Use "Edit from Client Portal" to preview their view
2. Review **notification settings** (email, text, push)
3. Save any permission/notification changes
4. Click **Send Invite** from client card
5. Client receives email invitation
6. Status: **Pending** → **Active** (when credentials created)
7. Can cancel/resend from contact info
8. Default invitation text editable in Company Settings → Jobs tab

### Client Permissions Include:
- Schedule access, Daily Log visibility
- Change Order Requests, Selection choices
- Invoice viewing and payment
- File access, Warranty claims
- Job Costing Budget visibility (if shared)

---

## 18. How to Add/Manage Subcontractors

### Adding Subs/Vendors
1. **Users** → **Subs/Vendors**
2. **Import** (from Excel) or **New Sub/Vendor** (individual)
3. Add Contact Information
4. Grant **Job Access** (required for task assignment)
   - ⚠️ Does NOT send invitation; separate step

### Inviting Subs/Vendors
1. Subs/Vendors list → check boxes → **Invite** (bulk)
2. Or open profile → **Invite Sub/Vendor** (individual, email required)
3. Preview invitation text → **Send on Save**
4. They create account or use existing BT credentials
5. Free for subs/vendors

### Setting Permissions
1. After adding to job → **Permission Wizard**
2. Select features to grant access
3. **Update Permissions** or **Do Not Update**

### Reassigning (Placeholders → Actual)
1. Job Details → **Subs/Vendors tab**
2. Find placeholder → **Reassign Items**
3. Select replacement → **Continue** → review affected items → **Reassign**

### Advanced Settings:
- View Owner Information, Share comments with owner
- Certifications with expiration/reminders
- Notification preferences
- Accounting integration linking
- Trade Agreement (upload, send, electronic approval)

---

*End of Workflows*
