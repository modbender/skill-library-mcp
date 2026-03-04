# Buildertrend Knowledge Base
> Complete reference from official Buildertrend Help Center articles
> Scraped: February 19, 2026
> Source: https://buildertrend.com/help-articles/

---

# TABLE OF CONTENTS

1. [CORE SETUP](#core-setup)
   - [Job Management](#job-management)
   - [Job Customization](#job-customization)
   - [Financial Management Settings](#financial-management-settings)
   - [Cost Codes Overview](#cost-codes-overview)
   - [Buildertrend Glossary](#buildertrend-glossary)
   - [Additional Training](#additional-training)
2. [SALES & LEADS](#sales--leads)
   - [Lead Opportunities Overview](#lead-opportunities-overview)
3. [PROJECT MANAGEMENT](#project-management)
   - [Navigating Project Management (Sub Portal)](#navigating-project-management)
   - [Schedule Overview](#schedule-overview)
   - [Change Order Overview](#change-order-overview)
   - [Selections Overview](#selections-overview)
   - [Subcontractor Overview](#subcontractor-overview)
   - [Client Portal FAQs](#client-portal-faqs)
4. [FINANCIAL](#financial)
   - [Estimate Overview](#estimate-overview)
   - [Invoice Overview](#invoice-overview)
   - [Purchase Orders & Bills Overview](#purchase-orders--bills-overview)
   - [Advanced Purchase Orders & Bills Overview](#advanced-purchase-orders--bills-overview)
   - [Job Costing Budget Overview](#job-costing-budget-overview)
   - [Financial Management FAQs](#financial-management-faqs)
   - [Bills & Purchase Orders on Mobile](#bills--purchase-orders-on-mobile)
5. [QUICKBOOKS INTEGRATION](#quickbooks-integration)
   - [QuickBooks Online Integration Overview](#quickbooks-online-integration-overview)
   - [Advanced QuickBooks Online Integration Overview](#advanced-quickbooks-online-integration-overview)
   - [QuickBooks Desktop Integration Overview](#quickbooks-desktop-integration-overview)
   - [QuickBooks Desktop Initial Integration](#quickbooks-desktop-initial-integration)
   - [Advanced QuickBooks Desktop Integration Overview](#advanced-quickbooks-desktop-integration-overview)

---

# CORE SETUP

---

## Job Management
**Source:** https://buildertrend.com/help-article/job-management/

To begin using Buildertrend, you will want to create your first project as a Job. All features and tools are job-based to keep things centrally organized and streamlined. Utilize supportive Job Detail fields such as Custom Fields, Job Types, Job Groups and more to create a system ideal for success.

### Getting Started
- **Adding a New Job Help Video** (Starting a Job - 2023, 2:34)
- **Job Templates Help Video** (Creating and Managing Templates, 6:35)

### Creating a Job

To create a new job, go to the Jobs Menu and click New Job. Choose your preferred method:

- **From Scratch** – Start a new job without any pre-filled information.
- **Your Templates** – Use one of your custom templates based on a previous job to streamline setup.

#### Job Detail Fields:

- **Title (required field):** Assign a name to your job.
  - Establishing a clear naming convention is essential. The Job Name is visible to both your client and trades, so choose something recognizable. Consider using the project address or a combination of the address and the client's last name.

- **Prefix:** Attach a unique prefix to financial, RFI, and Warranty items associated with this job.

- **Type (required field):** Select a project type for the job.
  - Helps categorize jobs and enables easy filtering from the Jobs List.

- **Contract Type (required field):** Indicate the financial model you plan to use for this job.
  - Buildertrend will create workflows to best fit your financial structure.

- **Job Group:** Assign the job to a custom group.
  - Enables easy filtering from the Job Summary landing page.

- **Status:** Set the current status of the job.
  - Statuses include Presale, Open, Warranty, and Closed.

- **Contract price:** Indicate the project/confirmed Contract price.

- **Project managers:** Select the project managers assigned to the job.

- **Square feet, Permit number, and Lot info:** Enter key job details.

- **Address:** Input the address for the Job. The Zip code is required.
  - Used for Bills/Invoices, weather data for Daily Logs, and Automated Sales Tax.

- **Projected start, Actual start, Projected completion, and Actual completion:** Track scheduling timelines.

- **Schedule color:** Assign a unique color for multi-job schedule views.

- **Work Days (required field):** Establish your default work week.

- **Notes for internal users:** Only accessible to internal users with job permissions.

- **Notes for subs/vendors:** Visible to internal users and approved subs/vendors.

- **Custom fields:** Track additional job details not covered by default fields.

### Creating a Job: From Scratch
1. Click New Job from the Jobs Menu, select "From scratch"
2. Input all pertinent job information in the provided fields
3. Select Save to create your new job

### Creating a Job: Your Templates
1. Click New Job from the Jobs Menu, select "Your templates"
2. Input job information under New Job Information
3. Select the template from the Source Template dropdown
4. Use checkboxes to select templated items to import
5. Review/modify Project Managers, Subs/Vendors, and Workdays
6. Select Save

### Managing your Jobs

#### Jobs List
Centralized view of all projects. Allows:
- Quick assessment of job progress
- Filter and sort by job details
- Identify workload distribution
- Customizable columns (type, address, status, PMs, dates)

#### Recover Deleted Jobs and Templates
1. Navigate to Jobs List from Jobs dropdown
2. Select Filter
3. Check "Only Show Deleted" checkbox → Apply filter
4. Select Restore on desired jobs

💡 **Pro Tip:** Same steps work for Templates menu.

#### Job Price Summary
Financial snapshot from client's perspective showing:
- Total client price
- Approved Selections & Allowances
- Approved Change Orders
- Payments Received

**Open Book Jobs only:** Projected price difference (includes bills, POs, labor, approved change orders, selections & allowances, projected cost adjustments, plus markup/margin)

#### Closing a Job
Job Statuses:
- **Pre-Sale:** Lead stage, preparing estimates, proposals
- **Open:** Actively being worked on
- **Warranty:** Complete but within warranty period
- **Closed:** Never moved past pre-sale, or completed all stages

To close: Job Details → Update status to Closed → Save

### Adding and Inviting Clients to a Job

#### Adding Clients
1. Navigate to Job Details → Clients tab
2. Select "+ New Contact" or "+ Existing Contact"
3. Fill out information and Save
4. Prompted to invite upon saving

#### Inviting Clients
1. Review permissions for appropriate access
2. Review notification settings
3. Select "Send Invite" from client card
4. Client receives email invitation
5. Status: Pending → Active (when credentials created)
6. Can cancel/resend invitation from contact information

💡 **Pro Tip:** Use "Edit from Client Portal" to preview client's view.

**Note:** Default invitation text editable by Admins in Company Settings → Jobs tab.

---

## Job Customization
**Source:** https://buildertrend.com/help-article/job-customization/

### Custom Fields
- Applied to any feature in Buildertrend
- Visible to internal team, trade partners, vendors, and clients (mobile & desktop)
- Eliminates need for separate notes outside the platform
- To add: Company Settings → Select feature → Scroll to bottom → Add New Field
- Options: Label, Data Type (dropdown, checkbox, date, number, etc.), Tool Tip, filtering, requirement options, display information
- Available on all new and existing Jobs after creation

### Job Groups
- Organize and manage multiple jobs by specific criteria
- Filter for a specific Job Group in any feature
- Common strategies: Location, Project classification, Crew info
- ✏️ Note: Separate from Contract Type. Jobs can have multiple Job Groups, but only one Contract Type.
- To create: Job Info → Add next to Job Group dropdown → Name → Save → Select from dropdown

### Tags
Tags appear throughout features for classification. Common examples:

**Schedule Items:** Interior, Exterior, Internal Meeting, Inspection, Unit #, Floor #, Installation

**Daily Logs:** Equipment Types, Client Conversation, Delivery, Inspection, Job Progress, Meeting Minutes, Rainout, Safety Inspection, Site Issues, Sub Contractor Conversation, Weather Delay, Injury, HOA Issues, Emergency

**Lead Opportunities:** Available Lot, Real Estate, Site Visited, Hot Lead, Cold Lead, Repeat Client

**To-Do's:** Client ToDo, Client Meeting, Inspection, Office, Client Walk-Through, PM Tasks, Punchlist, Warehouse, Material Orders/Deliveries, Pre-Con Checklist, Installation, Clean Up, Orders, Material Run, Safety Meeting

**Time Clock:** Left Early, Overtime, PTO, Approved, Amended Time, Extra Work Day, Forgot to Clock In, Mileage, Shift Edit, Pickup/Delivery, Errand, Change Order Labor

### Placeholders
- Use when assigning tasks to unknown subs/internal users
- Especially useful in templates
- Example: ZZ-Plumbing, ZZ-Painting, ZZ-Project Manager
- 💡 **Pro Tip:** Use "ZZ" prefix to keep placeholders at bottom of lists
- Can reassign: Internal user to internal user, Sub to sub, Placeholder to actual, or vice versa
- To reassign: Job Details → Subs/Vendors tab → Find placeholder → Reassign Items

### Add & Manage Saved Filters
- Populate specific data from Grid View
- Standard Filter provided; create custom Filters
- Filters can be shared with team
- Steps: Feature → Filter → Adjust fields → Apply Filter → Save As → Add name, sharing, default → Add
- Manage: Edit (pencil), Delete (trash), Set default, Duplicate (ellipsis)

### Add & Manage Grid Views
- Customize displayed information per feature
- Unlimited views, shareable
- Standard Grid View provided
- Steps: Feature → Three dots → Manage Saved Views → Update/Create → Add fields → Apply View → Save
- Additional customizations: Adjust column width, Reorder columns (drag), Pin/Freeze columns, Sort columns

---

## Financial Management Settings
**Source:** https://buildertrend.com/help-article/financial-management-settings/

### Cost Code Settings
- Create and manage cost codes and variance codes
- Standardize job costing structure
- See: Cost Codes Overview, Advanced Cost Codes Overview

### Catalog Settings
- Create/manage frequently used cost lines and cost groups
- Stores Title, Description, Unit Cost, Markup
- Eliminates repetitive data entry

### Bids Settings
- Alert subs/vendors X days before bid package deadline
- Default bid request notification text

### Estimates Settings
- **Group Proposal Worksheet By:** Custom Grouping (room-by-room) or Cost Code Grouping
- **Default Columns:** quantity, unit cost, markup, etc.
- **Global Profit Defaults:** Set consistent markup/margin percentages
  - Changes only apply to NEW jobs
  - Can customize per job from Job Details or Estimate
  - **Markup vs. Margin:** Both measure profitability differently

### Job Proposal Format Settings
- Header, Content, Show Contact Name & Phone, Show Address, Company Information
- Default "What to Display," Introductory Text, Title, Closing Text, Release Text
- Estimate Disclaimer (custom message before approval)

### Change Order Settings
- **General:** Prefix for CO numbering
- **Client Options:** Show declined COs, Show line items
- **Approval Options:** Invoice upon client approval, Approval disclaimer
- **Default Description:** Auto-populate on new COs
- **Display on Printout:** Price, Discussions, Line Items, Subs/Vendors, Signatures, Custom Fields

### Bills / POs / Budget

**Budget Settings:**
- Include Time Clock Labor in Job Costing Budget on new jobs
- Update existing jobs retroactively
- Determine accounting method (Cash or Accrual) for Actual Costs

**Purchase Orders:**
- Include unreleased POs in pending costs
- Create separate POs per line item in wizard
- Allow subs/vendors to request payment
- PO prefix, require signature, approval reminders
- Default scope of work, PO disclaimer

**Bills:**
- Bills prefix, Default Cost Code for flat fee bills
- Add PO suffix to bill number
- Alert users X days before due date
- Custom fields

**Lien Waivers:**
- Hide on all jobs option
- Default additional signature line
- Custom lien waiver forms

**Cost Inbox:**
- Auto-include tax line items on receipts

### Invoices Settings
- Invoice prefix, Notify internal users/clients of deadlines
- Use job address on invoices
- Payment terms (Net 30, Due on Receipt, etc.)
- Default invoice description
- **Draw Schedule (Fixed Price only):** Create draws, percentage, invoice title
- **Client Preview:** Hide line items, Combine by cost code, QR code, Custom Fields

### Taxes
- Set up for non-QBO users (US only)
- Create individual rates (name, rate %, agency) or group rates
- Disable Tax features if not needed
- Set default tax rate per job (Job Details → Options tab)
- Tax applied at invoice level to Taxable line items
- When connected to QBO: automated tax rates based on job zip code

---

## Cost Codes Overview
**Source:** https://buildertrend.com/help-article/cost-codes-overview/

Cost Codes are the foundation of ALL Financial Management features in Buildertrend.

### Features that Use Cost Codes:
Legacy Lead Proposals, Bids, Estimates, Selections, Purchase Orders, Bills, Change Orders, Invoices, Deposits, Legacy Budget, Job Costing Budget, Accounting Integrations

### Best Practices:
- **Keep it Simple:** Clear purpose, used on most jobs (5-10 or hundreds depending on needs)
- **Track Labor/Materials Separately:** Decide detail level needed
- **Numbering System:** Organize numerically, include leading zeros (e.g., 001)
- **Gather Team Input:** Get feedback from estimating, accounting, bidding, invoicing teams
- **Avoid Excessive Codes:** Don't create a code for every item; use Titles & Descriptions
- **Limit sub codes** (add complexity without reporting benefits)
- **Avoid duplicate/similar codes**

### Creating Cost Codes
1. Start with Cost Categories (required before Cost Codes)
2. Categories organize related codes by construction phase order
3. Import your ledger, use BT Recommended list, or create manually
4. ⚠️ CRITICAL: Establish Cost Codes BEFORE using any financial features

### Deleting/Deactivating
- Delete only if never used in any feature
- Deactivate keeps code for historical data but removes from new jobs

### Labor and Variance Cost Codes
- Time Clock Labor Codes: Cost Codes available for Time Clock use
- Only mark necessary codes as Time Clock Labor Code
- Can default per user for streamlined clock-in

---

## Buildertrend Glossary
**Source:** https://buildertrend.com/help-article/buildertrend-glossary/

### Key Terms (A-Z):

**Accept Payments Online** – Collect payments from clients, send payments to subs through integrated system

**Allowances** – Predefined budget amounts tied to selections/estimates

**Baseline View** – Original scheduled timelines vs current progress

**Bid Packages** – Grouped requests for pricing from subs/vendors

**Bills** – Track and record payments to subs/vendors

**Budget** – Tracks internal costs in real time

**Builder Cost** – Internal expense your company incurs

**Catalog** – Stores standard cost items tied to cost codes

**Change Orders** – Out-of-scope work requests added to project scope

**Client Cost** – Builder Cost + applied markup

**Cost Category** – Organizes cost codes into logical groups

**Cost Code** – Unique identifier for categorizing/tracking expenses

**Cost Inbox** – Central hub for incoming financial data

**Custom Fields** – User-defined data fields for job/company-specific info

**Daily Logs** – Recorded summaries of daily job site activity

**Estimate** – Detailed forecast of job expenses

**Gantt** – Visual scheduling view with dependencies

**Job Costing Budget** – Central hub for financial performance tracking

**Job Price Summary** – Real-time financial overview including contract price, change orders, allowances

**Lead Opportunities** – Potential jobs tracked in sales pipeline

**Line Items** – Individual entries in financial documents

**Predecessors/Links** – Schedule tool linking dependent tasks

**Purchase Orders** – Formal requests for subs/vendors to complete work

**RFIs** – Formal messaging for project questions with documented responses

**Schedule** – Central project management tool for timelines

**Selections** – Present product/design choices to clients

**Sync Schedule** – QBD integration data exchange (every 2 hours or manual)

**Tags** – Custom labels for filtering/reporting/organization

**Template** – Reusable job setups storing estimates, schedules, selections

**Time Clock** – Time tracking with GPS verification

**To-Do's** – Task items supporting your Schedule (checklists, punch lists)

**Variance PO** – POs for unexpected/unplanned expenses

---

## Additional Training
**Source:** https://buildertrend.com/help-article/additional-training/

- **Live Group Training:** Interactive sessions led by BT experts, regular schedule
- **Buildertrend Learning Academy:** On-demand courses, certifications, role-specific paths
- **Onsite Consulting:** Expert consultant at your office/jobsite
- **Buildertrend University:** Immersive expert-led events

---

# SALES & LEADS

---

## Lead Opportunities Overview
**Source:** https://buildertrend.com/help-article/lead-opportunities-overview/

### Creating a Lead Manually
1. Sales → Lead Opportunities → + Lead Opportunity
2. Add contact (New Contact or Existing Contacts)
3. Enter lead opportunity data → Save

### Importing Leads from Excel
1. List View → Import Leads
2. Download Excel Template, fill in leads
3. Browse Computer → select file → Next
4. Map columns to BT fields → Next

### Website Contact Form
- Auto-creates leads when prospects submit info
- Customize form: drag Lead Fields/Custom Fields to Form Fields
- Save & Preview → Installation Instructions for website designer

### File Management
- Unlimited photos, videos, documents per Lead
- General tab → Add (attach) or Create New Doc
- ✏️ File attachments carry over when lead converts to job

### Converting a Lead to a Job
- Select Lead → + New Job dropdown
- Copies all information, files, legacy proposals to the Job
- Ensures smooth transition and data consistency

---

# PROJECT MANAGEMENT

---

## Navigating Project Management
**Source:** https://buildertrend.com/help-article/navigating-project-management/

*(This article covers the Subcontractor Portal experience)*

### Job Info (Desktop & Mobile)
- View essential job details: address, PMs, Job Notes
- Mobile: More → Project Management → Job Details
- Quick directions via phone's Maps app

### Schedule (Desktop & Mobile)
- Primary job calendar with timelines and task assignments
- Views: Calendar, List, Gantt; filter by Month/Week/Day/Agenda
- Filter by items assigned to you, item Status
- Toggle between jobs or view all
- Confirm/Decline scheduled arrival time
- Comments section for notes to builder
- Create RFI from schedule item

### Daily Logs (Desktop & Mobile)
- Communicate job site progress
- Add Notes, Attachments, Title, Tags
- Date defaults to today (adjustable), weather auto-updates by zip
- After saving: add To-Dos, Comments, RFIs
- Mobile: Camera roll or real-time photo/video, Annotate option

### To-Do's (Desktop & Mobile)
- Manage and organize tasks
- See assigned To-Dos with Priority and Files
- Checklist Items within larger To-Do
- Mark Checklist Item complete → "To-Do is Complete" → Save
- Create To-Do for yourself (auto-assigned, visibility options)

### Change Orders (Desktop & Mobile)
- View approved Change Orders from Sub Portal
- Review Description, Notes, Attachments, RFIs
- Attach post-approval documents, Comment, submit RFI
- Mobile: More → Project Management → Change Orders

### Selections (Desktop & Mobile)
- View Upcoming (Pending), Completed (Approved), Outstanding Pricing Requests
- Submit Prices for Outstanding Price Requests
- Add Choices for customer approval (if permitted)
- Provide Product Link, Price Details, Price Notes

### Warranty (Desktop & Mobile)
- View Claims with Priority and Scheduling Info
- Accept/Reschedule appointments
- Set appointment, Save & Submit
- Add Comments and RFIs

---

## Schedule Overview
**Source:** https://buildertrend.com/help-article/schedule-overview/

### Setting Workdays
1. Select job → Job Info
2. Adjust Work Days dropdown
3. Use Workday Exceptions for temporary changes
- ⚠️ Changing workdays on in-flight jobs may shift schedule items

### Creating Schedule Items from Scratch
1. Job → Schedule → New Schedule Item (or click on calendar day)
2. Fill: Title, Display Color, Assignees, Start/End Dates, Work Days → Save

### Importing from Template
1. More Actions → Import from Templates
2. Choose Source Template, check Schedule, set New Start Date → Import

### Schedule Item Features:
- **Notes:** All Notes, Internal Notes, Sub Notes, Client Notes
- **Files:** Create Word/Excel docs, upload files, control visibility
- **History:** Audit trail of changes (who, when, why, impact)

### Predecessors
Types:
- **Finish-To-Start (FS):** Most common; one task must finish before next starts
- **Start-To-Start (SS):** Two tasks start simultaneously

Adding: Gantt view → drag circle from one task to another
- End-to-start = FS
- Start-to-start = SS

**Lag and Lead Time:**
- Lead time: successor starts before predecessor completes (negative lag)
- Lag time: delay between predecessor completion and successor start

### Setting the Baseline
- Captures snapshot of original timeline
- Track progress, accountability, forecasting, change management
- Schedule → Baseline tab → Set Baseline
- Shows expected vs actual start dates, durations, slips

### Schedule Adjustments
- Online mode: Notifications sent, Shift Reason/Notes prompted
- Shifts breakdown in schedule item → Shifts tab

### Online and Offline Modes
- **Offline:** Private building, muted notifications
- **Online:** Live to trades/clients, notifications active, Schedule Conflicts live

### Templating Schedules
- Full Schedule: Job Info → Copy to Template
- Select Items: List View → Select items → Copy → Choose destination

---

## Change Order Overview
**Source:** https://buildertrend.com/help-article/change-order-overview/

### Creating a Change Order
1. Job → Change Orders → +Change Order
2. Use tabs: Details, Estimate, Client Preview

#### Details Tab Fields:
- Title, ID #, Approval Deadline
- Payment (Invoice upon client approval)
- Introduction Text, Closing Text
- Attachments, Subs/Vendors, Notes (Internal, Sub/vendor, Client)

#### Estimate Tab:
- Flat Fee vs Line Items
- Add Item, Add from Cost Catalog, Add from Cost Codes
- Include Profit & Tax
- 💡 **Pro Tip:** Use Line Items, not Flat Fee (Flat Fee doesn't allocate to cost codes)

#### Client Preview Tab:
- Review appearance for client
- Control visible information
- Select Send to share

### Internal Approval
1. Change Orders dashboard → Select CO
2. Details tab → Approval Status → Approve
3. E-signature → Approve

### Client Collaboration
- Allow clients to submit CO Requests via portal
- Enable in Job Details → Clients tab → Change Order Requests permission
- Client: CO dashboard → +Change Order Request

### Client Approval
- Via email or Client Portal
- Digital signature required

---

## Selections Overview
**Source:** https://buildertrend.com/help-article/selections-overview/

### Key Features:
- Organize by default/custom categories and locations
- Create and manage allowances tied to selections
- Share with subs/vendors for installation awareness

### Creating Selections
1. Job → Selections → New Selection
2. Enter: Title, Category, Location, Deadline → Save

### Selection Fields:
- **Title** – Name of selection
- **Require client to make a selection** – Must choose before progress
- **Category** – Group type (Flooring, Appliances)
- **Location** – Where in project (Kitchen, Master Bathroom)
- **Single vs Shared** – Unique or shared allowance
- **Allowance** – Budget for this selection
- **Deadline** – Date or linked schedule item
- **Public Instructions** – Client-facing guidance
- **Internal Notes** – Team-only documentation
- **Attachments** – Supporting files

### Adding Choices
1. Create New Choice or Add Choices dropdown
2. Enter: Choice Title, Product Link, Include in Budget, Attachments, Price Details
3. Price Details: Flat Fee, Line Items, or Request From Sub/Vendor
4. Repeat for multiple choices → Send when ready

### Approving Choices
- Active clients approve via portal
- Builder can approve on behalf if no portal access
- Signature required with optional comments
- Notification sent to team and listed subs/vendors

### Templating Selections
- Save as templates for reuse across projects
- Broken into tier groups or all-inclusive catalogs
- Create from scratch or copy from existing job

---

## Subcontractor Overview
**Source:** https://buildertrend.com/help-article/subcontractor-overview/

### Adding Subs/Vendors
1. Users → Subs/Vendors → Import or New Sub/Vendor
2. Add Contact Information, Job Access
3. ⚠️ Job Access required for task assignment (separate from invitation)
4. Can add multiple subs to a job from Job Info → Subs/Vendors tab

### Permission Wizard
- Set feature access per sub/vendor per job
- Update Permissions or Do Not Update

### Inviting Subs/Vendors
- Free for them; full control over job access
- Invite individually or in bulk via checkboxes
- Preview invitation text; editable by Admins in Company Settings
- They can use existing BT credentials from another builder

### Sub/Vendor Permissions (Default, Limited Customization):
- **Job Info:** Location, notes, PM contact; customer info optional
- **Daily Logs:** View shared logs, create own
- **To-Do's:** Assigned, mark complete, create for self
- **Schedule:** Own assigned items (or all if permitted); Confirm scheduling
- **Files:** View permitted folders; personal upload folder
- **Messages:** Send to Internal Users on accessible jobs
- **Comments:** Add to permitted features
- **RFIs:** Create, be assigned, respond
- **Bids:** Receive/respond (active or inactive)
- **Change Orders:** View approved (if permitted); no pricing access
- **Bills/POs:** Receive/approve POs, request payment, view bills
- **Selections:** Vendor: view/price; Installer: view approved
- **Warranty:** Assigned to service appointments

### Advanced Settings:
- View Owner Information, Share comments/documents with owner
- Assign RFIs to other subs/vendors
- Certifications with expiration dates and reminders
- Notifications (email, text, mobile push)
- Accounting integration linking
- Trade Agreement (electronic approval)

---

## Client Portal FAQs
**Source:** https://buildertrend.com/help-article/client-portal-faqs/

### Profile Settings:
- Adjust notifications: Settings → Add/Remove Email, Text, Push
- Edit contact info, profile picture, reset username/password
- Download mobile app from App Store or Google Play
- Global Search: Search across all tools

### Features:
- Direct Chat, Comments, Messages for communication
- Create To-Dos for yourself
- Submit Warranty Claims (if builder allows)
- Upload files to Client Uploaded Files

### Job Costing Budget Columns Explained:
**Job Costing:**
- Original Budget: From signed Proposal
- Revised Budget: + approved Selections + Change Orders
- Committed Costs: Approved POs + Variance POs + unapproved Time Clock
- Actual Costs (Accrual): Open/paid Bills, Variance Bills, approved Time Clock + QB costs
- Actual Costs (Cash): Paid Bills, Variance Bills, approved Time Clock + QB costs
- Builder Variance: Bills marked as Builder Variances
- Projected Costs: Greatest of Revised, Committed, or Actual
- Cost-to-Complete: Projected - Actual
- Revised vs Projected: Projected - Revised

**Client Pricing:**
- Original Client Price: From signed Proposal
- Revised Client Price (Fixed): Original + Selections + Change Orders
- Revised Client Price (Open Book): Projected Costs - Builder Variance + markup
- Amount Invoiced, Remaining to Invoice, % Invoiced

### Buildertrend Payments:
- Save payment method for convenience
- 3D Secure (3DS) authentication for fraud prevention
- One-time password/code verification required

---

# FINANCIAL

---

## Estimate Overview
**Source:** https://buildertrend.com/help-article/estimate-overview/

### Overview
The Estimate is for proper contract building on the Job level, incorporating standard expenses plus Bids, Selections and Allowances. Format into professional proposals for clients.

Methods to build: Full Template, Cost Groups from Catalog, Import from Excel, or from scratch.

### Toolbar Options:
- Column Settings, Filter, Switch Views, Group By, Reformat, Sort
- Add Items, Add Group, Add from Cost Catalog, Add from Cost Codes
- Move/Delete Selected Items, Launch Takeoff
- Adjust Job Default Markup
- Template Import, External Import (Excel, QuickBooks, Square Takeoff)

### Creating an Estimate

**⚠️ Establish Cost Codes FIRST**

**Add Item (Line by Line):**
1. Click Add Item
2. Fill Cost Details: Title, Cost Code, Cost Type, Group, Description, Internal Notes
3. Add Cost Information: Unit Cost, Quantity, Unit, Markup/Margin
4. Markup options: Percentage (%), Flat dollar ($), Manual (—)
5. Option: Include Item in Catalog → Save

**Mark line items as Taxable:** Job Details → Advanced Settings → set tax rate. Checkbox on each item or bulk action.

**Import from Excel:**
1. Download Excel Template
2. Fill in data → Save
3. Browse Computer → select file → Next
4. Map columns → Review/match Cost Codes → Import

**Import from Template:**
1. Template Import → Select Source Template → Check Estimates → Import

**Add from Cost Catalog:** Select items → Add To Estimate

**Add from Cost Codes:** Select codes → Add (creates blank lines to edit)

### Locking the Estimate
- Lock to prevent edits while sending proposals
- Approved Bids and Selections still update when locked
- Unlock anytime for changes

### Formatting
- **Custom Grouping:** Room-by-room, lists, assemblies
- **Cost Code Grouping:** Auto-format by cost categories/phases

### Proposals
1. Click +Proposal
2. **Details tab:** Collect signatures, Required signees, Title, Approval deadline, Introductory text, Closing text, Attachments
3. **Client Preview tab:** Standard or Custom Layout, Layout Options, Display to client fields
4. **Send** to release to client (email or portal)
5. Can approve internally on behalf of client
6. Print option for physical signatures

### Send to Budget
- Activates Job Costing Budget
- Reviews Total Price, Builder Cost, Profit, Margin
- Estimate auto-locks after send

### Multiple Proposals
- Track iterations as scope is refined
- Proposal Dashboard shows all versions
- Can pull cost lines from previous proposals

### Templating
- Save Cost Items, Descriptions, Quantities, Costs
- All fields editable when applied to job

---

## Invoice Overview
**Source:** https://buildertrend.com/help-article/invoice-overview/

### Generating an Invoice
- Create from scratch or from other features (Estimate, Change Orders, Selections, Bills, POs)
- Can be flat amount or itemized; partially or fully paid

1. Job → Invoices → + Invoice
2. Include: Title, Due Date, Payment Terms, Client Pricing → Save

### Invoice Fields:
- **Title, ID #** (auto or custom)
- **Due Date:** Choose Date, Payment Terms (Net 30), or Link to Schedule Item
- **Taxes:** Select Tax Rate; applies to Taxable items (line items) or whole amount (flat fee)
- **Flat Fee vs Line Items**
- **Payment History:** All payment records
- **Invoice Description** (client-visible), **Internal Notes** (team-only)
- **Attachments**

### Adding Costs from Scratch
- Click + Item for manual line items

### Adding Costs from Existing Features
- **Fixed Price Jobs:** Add from Estimate, Selections (stay within contract), Change Orders (deviations)
- **Open Book Jobs:** Add from Costs (Bills, Time Clock, QB Costs not yet invoiced); filter by date ranges

### Progress Invoicing
- For bank-funded/commercial projects with Schedule of Values
- Pulls from Estimate directly into Continuation Sheet
- Enter % complete, auto-calculates and carries forward
- Export for lender/bank adjustments
- Send to client portal; push to QuickBooks/Xero

### Open Book Jobs Specifics:
- **Auto-Populating Markup:** Manual cost lines get markup from matching estimate data or default cost type markup
- **Outstanding Bills:** Add from → Costs shows uninvoiced Bills, Time Clock, Accounting Costs

### Fixed Price Jobs Specifics:
- **Draw Schedule:** Divide contract into scheduled draws (Job Details or Invoice dashboard)
- Draft invoices auto-created after estimate sent to budget
- Share Draw Schedule with client

### Formatting the Invoice
- Format & Preview from … icon
- Hide Line Items, Combine by cost code, Show Edit Options
- Save formatting preferences

### Sending Invoice
- Click Send → select clients to receive email → Send
- Non-active: email only; Active: Buildertrend + email
- Option to invite new client during send

### Recording Payment
Three methods:
1. **Buildertrend Payments** (Additional Services)
2. **QuickBooks/Xero** (marked as paid)
3. **Record Offline:** credit card, check, Credit Memo, other
- Payment History shows all payment records

---

## Purchase Orders & Bills Overview
**Source:** https://buildertrend.com/help-article/purchase-orders-bills-overview/

### Creating a Purchase Order
1. Job → Purchase Orders → +Purchase Order
2. Fill applicable fields → Send (to sub/vendor) or Save

### Adding Related Line Items to POs
- Generate PO from Change Orders, Bids, Selections, or Estimate
- Add to existing unapproved PO
- Required permissions: View Estimate/CO/Bid/Selection + View/Edit PO

### Approving a Purchase Order
- Released PO → Sub/Vendor receives email → Approve/Decline
- Active subs can approve from Portal
- Sign with typed or drawn signature
- Builder can manually approve on behalf of sub/vendor

### Amend Purchase Orders
- Make changes to approved POs without recalling
- Add/modify scope, documents, line items
- Tracked through change history
- Requires sub reapproval of modified portions
- ⚠️ Cannot reduce below already-billed amounts

### Creating a Bill from Scratch
1. Job → Bills → +Bill → Fill fields → Save
2. **Approvers:** Assign users for review; Send for approval → In Review → Ready for Payment
3. **Auto-Fill from File (OCR):** Upload invoice → auto-fills Title, Vendor, Dates, Cost Items

### Creating a Bill from a Purchase Order
1. PO → Bills/Lien Waivers → New Bill
2. Specify portion (% or amount per line item) → Create Bill
3. Auto-fills: Title, Pay To, Linked PO, Cost lines

### Creating a Bill from Cost Inbox
- Upload receipts → generate bills with correct cost code and job

### PO Suffix on Bills
- Enable in Company Settings → Bills section
- Auto-includes in QB when pushed

---

## Advanced Purchase Orders & Bills Overview
**Source:** https://buildertrend.com/help-article/advanced-purchase-orders-bills-overview/

### Lien Waivers
- Company Settings → Bills/POs/Budget → Create/manage lien waivers
- Options: Disable on jobs, Additional signature line (notary)
- Apply to Bills via checked actions
- Active subs sign electronically
- Online payments require sub signature before receiving payment

### Paying Bills on Purchase Orders
- Payments created as Bills (partial or total)
- Mass action: full amount only, 1 email per PO
- **PO Eligibility:** Must be approved, sub must be active
- **Bill Eligibility:** Sub added to job, has email
- **Ineligible:** QB validation errors, required custom fields

### Finalizing Bills
1. POs tab → Check boxes → Bill Remaining Amount or Mark Work Complete
2. Bills tab → Pay Online, Record Offline Payment, or Mark Ready for Payment
- QBO payments update automatically; QBD updates on next connector run

### Retroactively Adding Paid Bills to POs
**Option 1:** Void existing bills → Create new from POs → Mark paid
**Option 2:** Create negative bill to offset

### Subcontractor Requested Payments
- Active subs invoice through portal for completed PO work
- Request partial or entire outstanding amount
- Bill auto-created for request; builder fills amount
- Options: Send to QB/Xero, Pay online, Mark as paid

### Variance POs/Bills
- +Purchase Order → Variance PO
- Select Variance Codes (e.g., "72 – Client Change Order" for client-initiated)
- Link to Referenced Purchase Order or Change Order
- Create from Change Order: CO → New → Purchase Order
- Auto-uses "72 – Customer Variance" code

---

## Job Costing Budget Overview
**Source:** https://buildertrend.com/help-article/job-costing-budget-overview/

### Setup
1. Confirm accounting method (Cash or Accrual) in Company Settings → Bills/POs/Budget
2. If integrated with QBO: use Sync from QuickBooks option

### Populating the Budget
- Click "Send to Budget" from Estimate
- Creates financial baseline; activates budget
- Without this, no budget data appears

### Profitability Summary
**Open Book:** Projected Total Costs (Actual vs Cost to Complete), Revised Client Price (Invoiced vs Left to Invoice)
**Fixed Price:** Projected Profit and Projected Profit Margin (Projected vs Estimated)

### Data Organization
- Organized by Cost Code
- Click into any item for detailed information
- QB Expenses pulled in if enabled

### Personalizing Views
Pre-saved views:
1. **Job Costing** – Cost-focused columns
2. **Client Pricing** – Receivables columns
3. **Profit View** – Profit data columns
4. **Standard View** – Combined Job Costing + Client Pricing

### View by Job Groups
- Filter by job group for combined budget across multiple jobs

### Job Costing Columns:
- **Original Budget Costs:** From signed Proposal
- **Revised Budget Costs:** + approved Selections + Change Orders
- **Committed Costs:** Approved POs + Variance POs + unapproved Time Clock
- **Actual Costs (Accrual):** Open/paid Bills + Variance Bills + approved Time Clock + QB costs
- **Actual Costs (Cash):** Paid Bills + Variance Bills + approved Time Clock + QB costs
- **Builder Variance:** Builder-covered costs (not Customer Variances)
- **Complete:** Resets Projected = Actual when marked
- **Pending Costs:** Released but unapproved POs (optionally include unreleased)
- **Projected Costs:** Greatest of Revised, Committed, or Actual
- **Cost-to-Complete:** Projected minus Actual
- **Revised vs Projected:** Projected minus Revised

### Client Pricing Columns:
- **Original Client Price:** From signed Proposal
- **Revised Client Price (Fixed):** Original + Selections + Change Orders
- **Revised Client Price (Open Book):** Projected Costs - Builder Variance + markup/margin
- **Amount Invoiced, Remaining to Invoice, % Invoiced**

### Profit Columns:
- **Projected Profit:** Revised Client Price - Projected Cost - Applied Credit Memos
- **Projected Margin:** Projected Profit / Revised Client Price

### Projected Cost Adjustments
- Manually add cost changes when no supporting documents yet
- +Adjustment with note → Save
- Delete adjustments when proper documentation arrives

### Filtering
- **By Related Items:** Isolate costs linked to bills, selections, time clock, etc.
- **By Cost Types:** Labor, Material, Equipment, Subcontractor, Other, None
  - Only for jobs created after June 12, 2024

### Sharing with Client
- Job Settings → Client tab → Select columns to share
- Default: NOT shared to Customer Portal

---

## Financial Management FAQs
**Source:** https://buildertrend.com/help-article/financial-management-faqs/

### Cost Codes FAQs:
- Cost Codes specific to each builder's workflows
- Variance Codes marked "Customer Variance" = client-initiated in Budget
- "Buildertrend Flat Rate" = default placeholder code
- Cost Category = group; Cost Code = foundation item
- Cost Code ≠ Chart of Accounts (equivalent to QB Items/Products & Services)
- Codes can be renumbered/renamed; deactivate if used
- Build Cost Catalog after establishing Cost Codes
- Mass update Cost Items via checked actions

### Estimate FAQs:
- Switch Views: Cost Code, Groups, List, Takeoff Assemblies
- Create from Estimate: PO, Invoice, Bid Package, Allowance
- Contingency: Create "Contingency" cost code, use negative Change Orders
- Print: Create Proposal first → Proposal Dashboard → Click name for PDF
- Margin = Profit ÷ Client Price
- Lock Estimate prevents edits; opens Revised Costs tab
- Can revert to previous iteration via Proposal Dashboard

### Invoice FAQs:
- Active and inactive clients can receive invoices via email
- Create from Change Orders, Selections, Estimates, Bills, Time Clock, QB Costs
- View invoiced items within each feature grid
- Credit Memos lower amount owed (not Job Running Total)
- Clients cannot apply credits; only internal users can

### Bids FAQs:
- Add subs to released Bids via Edit Bid Package
- Add documents to multiple Bids via checked boxes
- Create Schedule Item from approved Bids

### PO & Bills FAQs:
- PO Prefix in Company Settings
- Retroactively add paid Bills: void and recreate, or create negative Bill

### Cost Inbox FAQs:
- View/Add/Edit permissions minimum; "Global – Can see all Receipts" for full access

### Tax FAQs:
- Flat fee: tax on whole subtotal; Line items: tax on subtotal (not per item)
- Connecting to QBO: automated tax replaces manual; old invoices need manual update

---

## Bills & Purchase Orders on Mobile
**Source:** https://buildertrend.com/help-article/bills-purchase-orders-on-mobile/

### Navigation: Job → More → Bills/POs

### Creating a PO (Mobile):
- Tap + → Enter details → Save
- Fields: PO #, Title, Assignee, Materials Only, Scope of Work, Link To Schedule, Deadline, Attachments, Variance toggle, Line Items
- 💡 Voice-to-text for Scope of Work

### Releasing a PO: Save and Release → sub receives email

### Internally Approving: Pencil icon → Manually Approve → finger sign

### Creating a Bill from Scratch (Mobile):
- Bills tab → + → Add Bill → Enter details → Save
- Fields: Bill #, Title, Ready for Payment, Pay To, Description, Date Billed, Date Paid, Link To, Deadline, Variance, Line Items, Docs/Receipts

### Creating Bill from PO: Select PO → Related Bills → + → Adjust percentage → Save

### Creating Bill from Scan: + → Scan to New Bill → camera scan

---

# QUICKBOOKS INTEGRATION

---

## QuickBooks Online Integration Overview
**Source:** https://buildertrend.com/help-article/quickbooks-online-integration-overview/

### Data Flow Summary:
**BT → QBO:** Jobs, Customers, Subs/Vendors, Bills, Invoices, Deposit Payments, Credit Memos, Time Clock
**QBO → BT:** Estimates, Bill Payments, Invoice Payments, Budget Actuals (Expenses)

### Customers, Sub Customers, Projects
- BT creates Customers/Sub Customers/Projects in QBO based on job and client info
- Fields mapped: Display Name, Company, Contact Info, Address, Terms, etc.

### Vendors
- BT creates Vendors in QBO from sub/vendor contact info

### Pushing Bills to QBO
- "Send to QuickBooks" checkbox when creating bill
- Default setting available in Accounting settings
- Edit syncs available if enabled
- Bill Fields mapped: Vendor, Bill #, Date, Due Date, Terms, Amount, Line Items, Cost Codes → Products/Services

### Pushing Invoices to QBO
- "Invoice to QuickBooks on Send" checkbox
- Default setting available
- Same for Progress Invoices
- Can add QuickBooks Costs to BT Invoice (Add From → QuickBooks Costs)

### Pushing Deposit Payments
- Deposit must be PAID first (BT Payments or offline)
- Send to QB → goes to Undeposited Funds
- Create Bank Deposit → match to bank transaction
- ⚠️ Turn off auto-apply credits in QBO
- For liability posting: use Journal Entry (consult accountant)

### Pushing Credit Memos
- Active Client: "Send to QuickBooks on Release" checkbox
- No Active Client: Save → ellipsis → Save to Accounting

### Pushing Time Clock
- Auto-push on approval if enabled in settings
- Manual: Send to QuickBooks from shift
- Mass actions for bulk approve + send
- Pushes to Time Entry or Weekly Timesheets (depends on QBO version/payroll)

### Receiving from QBO:

**Estimates:** Import from Estimate → External Import → QuickBooks → Map fields/codes

**Invoice Payments:** Payment in QBO → Invoice in BT marked as Paid

**Bill Payments:** Payment in QBO → Bill in BT marked as Paid

**QuickBooks Expenses → Budget:**
- Enable: Company Settings → Include costs in budget by default, OR Job Details → Advanced Settings
- Expense types: Bill, Expense, Check, Vendor Credit, Credit Card Credit
- Manual sync trigger available from Job Costing Budget

---

## Advanced QuickBooks Online Integration Overview
**Source:** https://buildertrend.com/help-article/advanced-quickbooks-online-integration-overview/

### Bills & Expenses Workflow Changes:
- Match Bill to bank transaction (don't create new expense)
- Remove bank rules for COGS accounts
- Pay Bills with checks instead of type-check transactions

### Bank Feed: Matching Bills & Invoices
1. Create Bill in BT → Push to QBO
2. QBO Bank transactions → Match suggested bill
3. If no match: manually search in Find other matches

### Online Payments Reconciliation:
**Using Undeposited Funds:**
1. Payment + Journal Entry (processing fee) in Undeposited Funds
2. Create Bank Deposit combining both
3. Match to bank transaction

**Using Checking Account:**
1. Direct to checking account
2. Match in Bank Feed
3. BT auto-creates deposit slip within 2 business days

### Payroll
- Time Clock data pushes employee info, cost code (P&S), dates/times, project
- Does NOT map to QBO payroll items
- Payroll Items must be set up per employee in QBO
- Default hourly rate assumed; overtime requires manual edit

### US Taxes
**Setup:** QBO → Taxes → Sales Tax → Use Automated Sales Tax
**BT:** Company Settings → %Taxes → Enable Tax (don't add rates; import from QBO)

**Location-Based Rates:**
- QBO calculates by shipping address
- BT: Job Details → Options → Default Tax Rate → Import rate from Accounting
- Must match Zip Code between BT job and QBO customer

**Custom Rates:** QBO → Sales Tax Settings → Add Rate

### International Taxes
**Sales Tax:**
- Tax rates applied per product/service code in QBO
- BT Accounting Settings: choose Inclusive or Exclusive
- **Inclusive:** Tax deducted from total, applied to liability
- **Exclusive:** QBO adds tax; two options for handling

**Purchase Tax:**
- Same setup pattern as sales tax
- **Tax Inclusive:** Include in budget as COGS
- **Tax Exclusive:** QBO adds tax, budget shows COGS only

**Tracking PST as COGS:**
- Custom GST purchase tax rate (4.6729% for 7% PST, 4.717% for 6% PST)
- Apply per product/service code
- Two options for bill entry (separate PST line or combined)

---

## QuickBooks Desktop Integration Overview
**Source:** https://buildertrend.com/help-article/quickbooks-desktop-integration-overview/

### Data Flow:
**BT → QBD:** Jobs, Customers, Vendors, Bills, Invoices, Time Clock
**QBD → BT:** Estimates, Bill Payments, Invoice Payments, Budget Actuals

### Web Connector
- Required for data exchange
- Auto-runs at set intervals
- "Sync with QuickBooks" in BT auto-runs every 2 hours
- Steps: BT → Sync with QuickBooks → QBD → Web Connector → Update Selected → Wait for 100%

### Pushing Bills, Invoices, Time Clock
- Same checkbox pattern as QBO (Send to QuickBooks on save/send)
- ⚠️ Overtime hours NOT automatically sent; manual entry needed in QBD

### Receiving Estimates, Payments, Expenses
- Same import process as QBO
- Bill/Invoice payments update on next web connector run
- QuickBooks Costs: Bill, Check, Credit Card Purchase

---

## QuickBooks Desktop Initial Integration
**Source:** https://buildertrend.com/help-article/quickbooks-desktop-initial-integration/

### Supported Versions:
- US: Enterprise, Premier, Pro
- Canadian: Any
- UK: Any
- ⚠️ No Mac iOS web connector (use Parallels)
- QBD 2018 and older: Web Connector doesn't work with Windows 11

### Setup Steps:
**Step 1 (BT):** Company Settings → Accounting → Get started with QuickBooks → Begin Setup → Download Configuration File
**Step 2 (QBD):** File → App Management → Update Web Services → Add Application → Select config file → Authorize (Yes, always) → Allow personal data access → Done
**Step 3 (QBD):** Enter BT password in Web Connector → Set Auto-Run interval → Update Selected → Confirm 100%
**Step 4 (BT):** Complete Setup → Configure default accounting options

### Default Accounting Options:
**Job Linking:** Auto-link during creation, Preferred item type (Customer or Job)
**Invoice:** Flat fee item, AR account, Auto-create on send, Auto-create credit memo
**Bill/PO:** AP account, Auto-link subs, Allow bill sync, Default send to QB, Mark as billable
**Budget:** Include QB costs by default, Cash or Accrual method
**Time Clock:** Auto-create time activity on approval
**Tax:** Ignore, Exclusive, Show client tax from QB

### Entity Linking:
**Cost Codes:** Import from QBD → Map to BT Cost Codes (create new or select existing)
**Jobs:** Link to QBD Customer or Customer:Job (from Job Details → Accounting)
**Vendors:** Link sub/vendor to QBD Vendor (from contact card → Accounting)
**Internal Users:** Link to QBD Employee (from user card → Accounting; must be fully created first)

---

## Advanced QuickBooks Desktop Integration Overview
**Source:** https://buildertrend.com/help-article/advanced-quickbooks-desktop-integration-overview/

### Bill Workflow Changes:
- Match Bill to bank transaction
- Pay Bills with credit cards (populate register)
- Pay Bills with checks

### Bank Feed Matching:
1. Create Bill in BT → Push to QBD
2. QBD → Bank and Credit Cards → Recognized tab → Match
3. If no match: Unrecognized tab → Find transaction → Match to existing

### Online Payments:
**Undeposited Funds:** Banking → Make Deposits → Select payment + journal entry → Save & Close
**Checking Account:** Direct to register, match in bank feed

---

# ARTICLES NOT FOUND (404)
The following URLs returned 404 at time of scraping:
- importing-a-lead-proposal-template
- lead-proposal-formatting-subgroups
- creating-bid-packages
- sub-portal-bids
- time-clock-reporting
- reporting-overview
- buildertrend-marketplace-2

These articles may have been consolidated into other articles or renamed.

---

---

# SUPPLEMENTARY ARTICLES (Supplementary Articles — Batch 2)

---

## Advanced Invoice Overview (Deposits & Credit Memos)
**Source:** https://buildertrend.com/help-article/advanced-invoice-overview/

### Deposits

Using Buildertrend's Deposits will allow you to create client deposits and apply the deposit payments to future invoices. This will ensure that the job running total will accurately represent the payments received and applied to the client's job total.

#### Generating a Deposit from scratch

1. Select a Job, then navigate to Invoices from the Financial dropdown.
2. Select Deposits tab and click + Deposit.
3. Fill out the deposit Information and include any Attachments.
4. Use the Flat Fee or % of contract price to set the amount of the deposit requested.
5. Select Save & Close to keep the deposit internal, or select Send deposit request to send to client.

Once created, track deposit status from the Deposits dashboard.

#### Paying Deposits

**With Buildertrend Payments:** Client can pay for the deposit directly through the Client Portal by navigating to Invoices > Deposit tab > select deposit > click Pay.

**Without Buildertrend Payments:** Record a payment manually after receiving the client's deposit payment. Open the deposit after it has been created, and select Record Offline Payment.

#### Applying Deposits to Invoices

**Option 1: From the deposit** — From Deposits dashboard, select Apply to Invoice next to the paid deposit. Select an existing invoice, specify how much of the deposit payment amount to apply.

**Option 2: From the invoice** — From Invoice dashboard, open an existing invoice and select Apply deposit. Specify how much of the deposit payment amount to apply.

When the total deposit payment amount is applied, the status changes to Applied.

#### Converting a Lead Proposal Payment to a Deposit

If a Legacy Proposal is created on a Lead and a payment is made with BT Payments:
1. From Create a Job > Copy Lead Info to New Job modal
2. Select the Proposal containing a payment
3. Choose Copy Proposal Payment to Job
4. Select Copy to deposit

### Credit Memos

Credit Memos apply a monetary credit back to the client, applicable within Owner Invoices.

**Scenario:** Builder made a mistake that extended the project. To make it right, giving client $500 off their next invoice.
**Workflow:** Builder adds a $500 Credit Memo and applies it to the client's next invoice.
**Result:** Credit counted towards client's payments and displayed as such on the invoices tab.

*Note: A Credit Memo does not reduce the Revised Client Price. A negative Change Order would need to be accepted to reduce the Revised Client Price.*

#### Creating a Credit Memo

1. Select a Job, navigate to Invoices from the Financial dropdown.
2. Select Credit Memos tab and click + Credit Memo.
3. Add Title and Description. ID# auto-assigns or custom.
4. Choose Flat Fee or Line Items to add cost information.
   - **Line Items:** Multiple line items broken out by Cost Codes.
   - **Flat Fee:** One amount, no Cost Codes.

#### Applying a Credit Memo to an Invoice

Credit Memos may be applied to only one invoice at a time. If the Credit Memo amount exceeds the Invoice amount, it may be applied to another Invoice until the memo balance is $0.

**From the Credit Memo:** Open Credit Memo > Apply Invoice.
**From an Invoice:** Open Invoice > Record payment > Payment Method: Credit Memo > choose credit memo > Record Payment.
**From Accounting Platform:** If sent to QuickBooks/Xero, must be applied there. The QBO/Xero invoice must have been pushed from Buildertrend.

#### Applied Credit Memos Visible In:
- Payment History dropdown on the Invoice
- Price Breakdown on Invoices, Payments, Credit Memos, and Deposits dashboard
- Payments and Credit Memos tabs within Invoices
- Jobs Price Summary
- Jobs List (ensure Applied Credit Memos column is visible)

---

## Buildertrend Payments FAQs
**Source:** https://buildertrend.com/help-article/buildertrend-payments-faqs/

### Payment Methods Accepted
- **Credit & Debit Cards:** Visa, Mastercard, and Discover (American Express NOT accepted)
- **Digital Wallets:** Apple Pay and Google Pay (AmEx still not accepted through wallets)
- **ACH Bank Transfers:** Securely transfer funds directly from bank account
- Payment processor: Adyen (fully PCI compliant)

### Paying Subcontractors

**Eligibility:** U.S.-based builders with necessary Buildertrend package privileges.

**Fees (paid by builder, free for subs):**
- ACH payments: $1 per transaction
- Printed or mailed checks: $2 per transaction
- Fees billed monthly, even if subscription is billed annually

**Payment Methods:**
- Individual payments: View specific bill > Pay > Pay Online
- Bulk payments: Use checked actions on Bills page (sums all bills per sub, sends single payment each)

**Delivery Times:**
- ACH: 3-5 business days
- Self-printed check: Deposited immediately (varies by bank)
- Mailed check: 3-14 days via USPS

**Check Details:**
- $150,000 per check limit
- Memo line: 2,054-character limit for e-checks, 180-character limit for printed checks
- Check expiration: 30, 60, 90, or 180 days (configurable)
- Custom starting check numbers per bank account

**Sub Requirements:**
- No Buildertrend invitation/activation required
- Just need email address and job assignment
- ACH: subs prompted to set up bank info
- No action required for check payments

**Security:**
- PCI Compliant Payment Processing
- Multi-Factor Authentication (MFA)
- Trusted Payment Users (define who can send payments)
- Checkbook Security

**Bill Statuses:**
- Open, Ready for Payment, Online Payment Processing, Paid

**Payment Statuses:**
- Sent, Processing, Complete, Void, Failed

**Stopping/Recalling Payments:**
- Void bill with pending payment = automatically voids payment
- If already processing, contact bank for stop payment

### Receiving Client Payments

**Application Requirements:**
- Company legal name, DBA, legal structure, physical address
- Beneficial owner info, deposit account details
- May need: P&L, Articles of Incorporation, driver's license, tax returns, bank statements
- Review: 2-4 business days

**Fees:**
- No monthly or annual fees (per-transaction only)
- Credit Cards: 2.99% per transaction (can pass to clients)
- ACH: $15.00 flat fee per transaction
- Sub/Vendor ACH: $1/transfer; Check: $2/check

**Limits:**
- Client payments: $120,000 per transaction
- Monthly processing limit set during credit underwriting
- Track utilization via banner on Invoices page
- Email alerts at 50% and 100% utilization

**Payout Times:** 2-4 business days (next business day if after hours)

**1099-K:** Shipped by Adyen third week of January. Threshold: $20,000 gross volume + 200 transactions.

### ACH Returns & Credit Card Chargebacks

**ACH Returns:**
- Cannot be directly disputed
- Debit from bank account within 2-4 business days
- Common reasons: incorrect account details, insufficient funds
- Client can be asked to resubmit

**Chargebacks:**
- Client disputes credit/debit card transaction (up to 120 days)
- Funds immediately withdrawn from builder's account
- Builder can dispute with evidence (one submission only)
- Resolution: 45-60 days average
- No fees for chargebacks currently

**After Return/Chargeback:**
- Invoice returns to "Pending/Released" status
- Client can repay using same method
- If integrated with QuickBooks: paid invoice auto-deleted on chargeback

---

## Paying Invoices with Buildertrend Payments (Client Guide)
**Source:** https://buildertrend.com/help-article/paying-invoices-with-buildertrend-payments/

### Save Preferred Payment Methods
From Client Portal: Settings > Payments section > Add credit card or Add bank account.
Set as preferred payment method for auto-apply on future payments.

### Payment Methods

**From Invoice Email:**
1. Click "View and pay" in the Payment request email
2. Select preferred payment method or enter new card/bank details
3. Click Pay
4. Receive confirmation email

**From Client Portal:**
1. Click Pay from "Next payment" banner OR
2. Click Pending invoices > Pay next to unpaid invoice
3. Select payment method and click Pay

**From Mobile App:**
1. Navigate to Unpaid Invoices from Action Items
2. Select invoice
3. Tap payment icon
4. Choose payment method (includes Google Pay/Apple Pay)
5. Click Pay

---

## Client Contacts Overview
**Source:** https://buildertrend.com/help-article/client-contacts-overview/

### Creating a Client Contact
Navigate to Client Contacts from users menu > click +Contact > Enter name, address, phone, email > Save.

**Pro Tip:** Data Entry team can bulk upload contact lists.

### Adding vs. Inviting Clients to a Job

**Adding** = stores contact info + allows email updates. Does NOT send invitation.
**Inviting** = gives access to Client Portal (view progress, approve selections, make payments).

#### Adding Client to Job
1. Navigate to Job Details > Clients tab
2. Choose + New Contact or + Existing Contact
3. Click Save to confirm

#### Inviting Client to Job
1. Check client permissions match desired access
2. Click Send Invite from client card in Clients tab
3. Client receives email to establish portal login

**Pro Tip:** Set default custom invitation verbiage in Company Settings.

### Setting Client Permissions

**Default Settings:** Company Settings > Default Job Permissions. Option to update existing jobs to match.

**Individual Job Permissions:** Job Details > Clients tab > set permissions and notification settings per job.

#### Permission Categories:
**Project Management (View):**
- Share PM's phone number
- Allow client to see Locked Selections
- Schedule access (phases only or all items, time frame)

**Project Management (Submit):**
- Send Change Order requests
- Submit Warranty claims

**Financial (View):**
- Job Price Summary
- Purchase Orders and Bills
- All Invoices (not just emailed ones)
- Budget (Legacy and/or Job Costing)
- Budget column selection
- Display related items (invoices, bills, POs from budget)

---

## Internal Users Overview
**Source:** https://buildertrend.com/help-article/internal-users-overview/

### Adding Internal Users
Only available to Org Owner and Admin roles.
1. Navigate to Internal Users from users menu > click +Internal user
2. Enter name, email, assign role > click Create
3. Invitation emailed automatically

**Pro Tip:** Use "Invite multiple users" for bulk invitations.

### Permissions
Determined by assigned role (not individually configurable per user). View current role and permissions on the Permissions tab.
Custom Roles can be created for more flexibility.

### Security & Login
- **Login Access:** Toggle Active/Inactive
- **Archive User:** Removes from dropdowns, prevents login, preserves historical data

### Internal User Statuses
| Status | Description |
|--------|-------------|
| Active | Has login credentials, can log in and interact |
| Inactive | Not invited or login toggled off; can be assigned to items |
| Archived | Removed from dropdowns, no login; history preserved |
| Deleted | Permanently removed; some records remain (time clock shifts, comments, created entities) |

*Strongly recommend archiving over deleting to preserve historical data.*

### Notification Settings
Configured by Org Owners/Admins or by individual users from User Settings.
Methods: Email, Text Message, Push (mobile app).
Collapsible drawers for each feature/section.

### Buildertrend Default Roles & Permission Matrix

| Role | General Access | Job Status Access | Limited Access | No Access |
|------|---------------|-------------------|---------------|-----------|
| **Org Owner** | Full access to all features and settings | All | — | — |
| **Admin** | Same as Org Owner | All | — | Subscription Management, Cashback & Discount Payments |
| **Project Manager** | Full job access (no Sales, Internal Users, Client Invoices) | Open, Warranty, Closed | Accounting Integration | Sales, Warranty, Client Invoices |
| **Office Manager** | Most items (no Estimates or Warranty) | Presale, Open, Warranty, Closed | — | Warranty, Bids, Estimate |
| **Bookkeeper** | Financials and job-related items | Presale, Open, Warranty, Closed | Schedule, To-Dos, Messages, Bids | Sales, RFIs, Daily Logs, Warranty, Surveys |
| **Selections Coordinator** | Selections, POs, COs with cost and price info | Presale, Open, Closed | Time Clock, Messages | Sales, Warranty, Surveys, Bids, Estimate, Client Invoices, Accounting |
| **Warranty Coordinator** | Warranty, To-Dos, and communication tools | Open, Warranty, Closed | — | Jobs, Customers, Subs, Sales, COs, Selections, Financials, BRI |
| **Architect** | View-only COs and Selections (no pricing) | Presale, Open, Closed | To-Dos | Sales, Warranty, Financials, Surveys, Bids, Estimate, Client Invoices, BRI |
| **Project Estimator** | Estimates, Bids, Selections, Bills/POs with cost and price | Presale, Open, Warranty, Closed | Schedule, To-Dos | Sales, Warranty, Client Invoices, Accounting Integration |
| **Sales Rep** | Manages own Leads, converts to Jobs | Presale, Open, Warranty, Closed | Sales, Schedule, To-Dos, Time Clock, Accounting | COs, Selections, Warranty, RFIs, Surveys, Messages, Financials, BRI |
| **Sales Manager** | All Leads, Proposals, Estimates in Jobs | Presale, Open, Warranty, Closed | Schedule, COs, Selections, Accounting | Warranty, RFIs, Surveys, Financials, Client Invoices |
| **Field Crew** | To-Dos, Daily Logs, Time Clock, Schedule (no pricing) | Open, Warranty | To-Dos, Time Clock | Most other features |
| **Purchasing Coordinator** | Financial tools with cost and price info | Presale, Open, Warranty, Closed | To-Dos | Sales, Time Clock, Warranty, Surveys, Client Invoices |

### Creating Custom Roles
1. Navigate to Role management in Company Settings > click +Role
2. Name the role and add description
3. Use checkboxes for View, Add, Edit, Delete permissions
4. **Pro Tip:** Click "Add from role" to pre-populate from an existing role

---

## Admin Settings
**Source:** https://buildertrend.com/help-article/admin-settings/

### Updating Company Logo
1. Go to User Profile Icon > Company Settings > Company section > Company Logo
2. Choose logo to update: Website Logo, Mobile Logo, or Mini Logo
3. Click "Choose File" and upload image
4. Click "Update Account"

### Manage Subscription
Navigate to Manage Subscription from user profile icon.
- Review/upgrade Subscription and Buildertrend Offerings
- Access Payment Info, Payment History, Order Forms
- Add Buildertrend Boost from Additional Options

### Buildertrend Boost
Comprehensive training package including:
- Personalized coaching
- Dedicated account management
- Strategic check-ins
- Thorough account reviews
- Tailored success plan

To add: User Profile > Manage Subscription > Buildertrend Offerings > Manage Subscription > Additional Options > Check Buildertrend Boost > Proceed to Checkout > Submit Order.

---

## Buildertrend Setup & Customization FAQs
**Source:** https://buildertrend.com/help-article/buildertrend-setup-customization-faqs/

### Admin
- **Adjust subscription/support plan:** Contact account manager. Find them via "?" icon chat.
- **Add company info to printouts:** Company Settings > Company Information (up to 3 fields).
- **Adjust printout content:** Select Print > More Settings.

### General
- **Recommended browsers:** Chrome, Firefox, Safari (Mac)
- **Recommended resolution:** 1920 x 1080
- **Clear cookies/cache:** Helps speed up and resolve odd behaviors

### Job Management
- **Edit Job Details on mobile:** Yes, from Job Details tab
- **Add/remove Job Groups to multiple jobs:** Yes, via Jobs List checked actions
- **Multiple clients on multiple jobs:** Yes, clients can switch between jobs in portal dropdown

### Users
- **Reset password:** User Profile Icon > Change Password (Security & Login tab)
- **Admin control of user settings:** Yes, adjust permissions and notifications from User icon
- **Edit Internal User Permissions:** Internal Users tab > select user > Permissions. Roles can be reassigned but not edited; create custom roles for modifications.

### Client Contacts
- **Multiple contacts on same job:** All see same info, perform same functions, receive same notifications (except direct tagging)
- **"Preview as Client" unavailable:** A contact must be assigned first
- **Duplicate email error:** Merge duplicate contacts via Contacts > Checked Actions, or change Primary Email
- **Client profile picture:** Only client can upload after activation
- **Edit active client's info:** Only client can edit once active; you can add additional emails

### Custom Fields & Tags
- **Tags:** Simple labels for categorization, single-line text, must be added individually
- **Custom Fields:** Detailed information visible to teams, trade partners, and clients; appear on all new and existing jobs

### Grids & Filters
- **Grid View vs Filter:** Grid Views fill in information; Filters search for specific details
- **Default filter scope:** Unique to each user
- **Deleting shared Filter/Grid:** Removes for entire team; private only removes for you
- **Export Grid:** Yes, "Export" button in top right corner downloads Excel

---

## Specifications Overview
**Source:** https://buildertrend.com/help-article/specifications-overview/

Project Specifications (Specs) detail scope of work, materials, installation documentation and more. Common for builders to have a Spec template for each job type.

### Creating Specifications
1. Navigate to Project Management dropdown > Specifications
2. Click + Specification
3. Add information in text box (supports images and links via toolbar)
4. Click Publish > Set Viewing Permissions (share with Client and/or Subs/vendors) > Publish again

### Editing Specifications
- Click Edit Icon from Book or List view
- Or open Spec and select pencil icon
- Click Save when complete
- Use 3 dots menu for: Edit Viewing Permissions, Print, Delete

### Creating Specification Templates
1. Navigate to Job Info > "Copy to Template" from bottom 3 dot options
2. This copies all feature info (excluding client details)
3. Access template from Templates menu > Template List
4. **Working Templates:** In Job Info > Options > Template Options > check "Make this job a working template". Working templates don't appear in Templates menu; used for importing onto specific features.

### Linking Specifications to Bids
1. Navigate to Financial > Bids
2. Open existing Bid or create New Bid Package
3. Select Link to Specifications > choose the Spec
4. Select Add or Edit

**Important Notes:**
- Linked Specs cannot be deleted
- Specs cannot be edited if on a released Bid (must reopen/unrelease Bid first)
- Subs accessing Bids externally see Spec info embedded; subs in Buildertrend have view/print access only

### Permissions
Internal Users (including Custom Roles) need View, Add, Edit and/or Delete Specification permissions.

---

## Selections on Mobile
**Source:** https://buildertrend.com/help-article/selections-on-mobile/

### Navigation
Choose job from Jobs List > tap More > Selections (under Project Management).
*Selections are job-specific — must choose a job first.*

### Adding a New Selection
Tap + icon > enter details > tap Save.

**Selection Fields:**
- **Title** — Clear name for identification
- **Category** — Group under type (Flooring, Appliances, etc.)
- **Location** — Where selection applies (Master Bathroom, Kitchen)
- **Link To** — Toggle to link deadline to schedule item
- **Deadline & Time** — When selection choice must be made
- **Single vs Shared** — Unique or shared allowance amount
- **Allowance** — Budget for this selection
- **Choices** — Options for products, materials, finishes (added after saving)
- **Required** — Client must make selection before job progresses
- **Allow Multiple Selected Choices** — Client can select multiple options
- **Selection Instructions** — Visible to clients
- **Internal Notes** — Only visible to internal users
- **Attachments** — Photos, scans, files
- **Client: Allow to Add/Edit Choices** — Client can suggest/explore options (not auto-approved)
- **Vendors** — Involved subs/vendors
- **Installers** — Assigned for installation (see approved choices only, no pricing)

### Adding Choices to a Selection
Open selection > Edit > scroll to Choices > Add Choice.

**Choice Fields:**
- Title, Attachments
- **Cost Format:** Flat Fee | Line Items | Request From Vendor
- Show Line Items to Client, Include in Budget
- Builder Cost & Client Price (auto/manual depending on format)
- Client Price TBD option
- Product Link, Description, Vendor

### Releasing Selections
Tap paper airplane icon or Save & Release to send to client.

### Approving Selection Choices
Client approves from portal (including mobile). If client inactive, approve on their behalf from selection > choice > Approve.

### Allowances
Manage budgets within Selections. Navigate to Allowances tab > tap + icon.

**Fields:** Title, linked Selections, Notes, Use Line Items toggle, Builder Cost & Allowance Totals.

---

## Daily Logs on Mobile
**Source:** https://buildertrend.com/help-article/daily-logs-on-mobile/

### Navigation
Tap Daily Logs at bottom of screen. Select specific job from Jobs List for job-specific logs.

### Adding a New Daily Log
Tap + icon > select job > enter details > Close Draft (save for later) or Save (submit).

*Drafts only accessible by the individual AND mobile device that started it.*

**Daily Log Fields:**
- **Title** — Brief label
- **Job** — Associated job
- **Date** — Cannot create on future dates
- **Notes** — Detailed work/activity notes
- **Attachments** — Photos or files
- **Share** — Toggle visibility:
  - Internal Users, Subs/Vendors, Clients
  - Notify Users on save
- **Weather Conditions** — Auto-populates from job address
- **Weather Notes** — Impact on progress
- **Tags** — Keywords for organization/search

**Pro Tips:**
- Quick Add menu for expedited creation
- Voice-to-text for Notes
- Camera for before/after photos
- Bulk select photos/videos from phone library

### Related Items & Comments
Create To-Do's directly from Daily Log. Leave comments for team alignment.

---

## Bills & Purchase Orders on Mobile (Updated)
**Source:** https://buildertrend.com/help-article/bills-purchase-orders-on-mobile/

### Navigation
Choose job > tap More > Bills / POs (under Financial).
Without selecting specific job, shows Bills/POs from all active jobs.

### Purchase Orders

#### Adding a New PO
Tap + icon from Purchase Orders tab > enter details > Save.

**PO Fields:**
- PO # (auto-generated or custom)
- Title, Assignee (internal user or sub/vendor)
- Materials Only toggle
- Scope of Work (use voice-to-text)
- Link To (schedule item), Deadline & Time
- Attachments
- Variance toggle + Variance Code + Related Bill/PO
- Line Items (Add Line Item)

#### Releasing a PO
Save and Release from PO. Sub/vendor receives email to review and Approve or Decline.

#### Internally Approving a PO
From released PO > pencil icon > Manually Approve > confirm on behalf of sub/vendor. Sign with finger on mobile.

### Bills

#### Adding Bill from Scratch
Tap + icon from Bills tab > Add Bill > enter details > Save.

**Bill Fields:**
- Bill #, Title, Ready for Payment checkbox
- Pay To (sub/vendor or Misc)
- Description, Date Billed, Date Paid
- Link To, Deadline & Time
- Variance toggle + Variance Code + Related PO
- Line Items
- Docs / Receipts (photos, scans, files)

#### Adding Bill from Purchase Order
Open PO > Related Bills tab > + icon > Adjust Total Percentage > review/save.

#### Adding Bill from Scan
Tap + icon > Scan to New Bill > use camera to scan receipt.
*For OCR auto-read of line items, use the Cost Inbox feature instead.*

---

## Buildertrend Learning Academy — Course Catalog
**Source:** https://learn.buildertrend.net/app/catalog (accessed via BT University)

### Academy Structure
- **Courses** — Feature-based and topic-based learning
- **Learning Paths** — Multi-course guided journeys
- **Certifications** — Formal BT certifications
- **Live Group Trainings** — Interactive online sessions
- **In-Person Training** — Buildertrend University conferences

### Course Catalog (Complete List)

**Filter Categories:**
- Phases: Sales, Pre-Construction, Construction, Post-Construction
- Features: Bids, Bills, Budget, Change Orders, Cost Codes, Daily Logs, Estimates, Files, Leads, Owner Invoices, Purchase Orders, Schedule, Selections, Time Clock, Warranty
- Roles: Bookkeeper, Co+ Users, Company Owner, Designer, Estimator, Field Crew, Office Manager, Project Manager, Sales Management, Salesperson, Selection Coordinator, Superintendent

**Available Courses:**

| Course | Activities | Duration | Description |
|--------|-----------|----------|-------------|
| Allowance and Design Selection (NEW) | 7 | — | Financial Management—budgets, payments, cash flow |
| Becoming a Buildertrend Champion | 6 | 10 min | Advocate guide for company success |
| Buildertrend Financing's Pricing Tiers | 2 | 10 min | Nelnet financing packages |
| Buildertrend Introduction | 5 | 20 min | Core features and functionality |
| Buildertrend's Client Financing | 2 | 15 min | Client financing with NelNet |
| Buildertrend's Ideal Financial Workflow | 5 | — | Scope iterations + budget tracking |
| Buildertrend Takeoff | 10 | 30 min | Streamline estimating with Takeoff |
| Client Invoicing & Payment Management (NEW) | 12 | — | Financial Management—budgets, payments, cash flow |
| Collaborating with Clients and Subs (NEW) | 8 | — | Closeout—walkthroughs + warranty tracking |
| Collaborative Success: Engaging Clients | 9 | 15 min | Building lasting client relationships |
| Collaborative Success: Engaging Subcontractors | 7 | 20 min | Powerful sub/vendor partnerships |
| Construction Preparation (NEW) | 11 | — | Schedules, tasks, files, approvals |
| Creating and Managing Estimates (NEW) | 6 | — | Scoping & Estimating path |
| Creating & Formatting Client Proposals (NEW) | 7 | — | Scoping & Estimating—win more work |
| Feature: Bids | 6 | 30 min | Create bid packages, compare bids |
| Feature: Bills | 8 | 30 min | Expense recording with Bills |
| Feature: Change Orders | 7 | 30 min | Contract update management |
| Feature: Communication | 11 | 30 min | All correspondence tools |
| Feature: Cost Codes | 6 | 30 min | Job costing structure setup |
| Feature: Daily Logs | 5 | 15 min | Job updates and daily records |
| Feature: Estimate | 5 | 40 min | Enhanced estimating capabilities |
| Feature: Files | 6 | 30 min | Unlimited file storage management |
| Feature: Invoices | 7 | 30 min | Customer invoicing system |
| Feature: Job Costing Budget | 7 | 30 min | Financial visibility and clarity |
| Feature: Leads | 11 | 1 hour | Turn prospects into projects |
| Feature: Legacy Selections | 9 | 45 min | Customer option management |
| Feature: Purchase Order | 10 | 45 min | Standardized expense recording |
| Feature: Schedule | 7 | 45 min | Basic + advanced scheduling |
| Feature: Selections (NEW) | 1 | 5 min | Formal selection management |
| Feature: Time Clock | 4 | 25 min | Clock in/out with location tracking |
| Feature: To-Do's | 7 | 25 min | Deadline and task management |
| Feature: Warranty | 6 | 15 min | Warranty management |
| Getting Started | 6 | 35 min | Account setup + team involvement |
| Gusto | 6 | 10 min | Payroll/benefits/HR integration |
| Home Depot Pro Xtra | 6 | 25 min | HD loyalty program integration |
| Job Costing Budget Management (NEW) | 5 | — | Financial Management path |
| Job Management Through Mobile App (NEW) | 13 | — | Document, communicate, coordinate |
| Managing Bid Requests (NEW) | 5 | — | Scoping & Estimating path |
| Managing Bills, Payments, and Job Costs (NEW) | 10 | — | Financial Management path |
| Managing Scope Changes (NEW) | 6 | — | Financial Management path |
| Mobile Application | 21 | 1 hour | Access office from the field |
| Onboarding: Financial Management | 2 | — | Onboarding Series Course 2 |
| Onboarding: Job Management | 2 | 16 min | Onboarding Series Course 1 |
| Project Closeout & Warranty Management (NEW) | 6 | — | Closeout—walkthroughs + warranty |
| Pro Tips: Common CoConstruct Accommodations | 7 | 20 min | CoConstruct → BT transition |
| Pro Tips: Overcoming Onboarding Obstacles | 20 | 20 min | Onboarding best practices |
| Pro Tips: Project Management Wins | 5 | 15 min | PM hidden gems |
| Sales Pipeline Management (NEW) | 7 | — | Scoping & Estimating path |
| Scaling to $10MM & Beyond | 10 | 40 min | PM systems for rapid growth |
| Scaling to 8-Figures: Annual Strategic Planning | 6 | 40 min | Strategic planning (Breakthrough Academy) |
| Takeoff Live Training: On-Demand | 0 | — | Blueprints to accurate takeoffs |
| Utilizing Data Entry Services | 4 | 20 min | Seamless data integration |

### Learning Paths
- **Implementation Journey** — 13 items, ~3 hours. Covers: scoping/estimating, setting up jobs, managing teams/tasks, handling finances, closing out projects.

### Upcoming Live Group Trainings (as of Feb 19, 2026)
- Job Costing Budget: Deep Dive (Feb 19, 2026)
- Pre-Construction & Planning Lesson 2: Material & Labor Procurement (Feb 19, 2026)
- Financial Management Lesson 2: Client Financial Management (Feb 20, 2026)

### Popular Topics
- Estimates, Owner Invoices, Schedule, Daily Logs

---

## BATCH 2 — ARTICLES NOT FOUND (404)
The following URLs returned 404 at time of scraping:
- buildertrend-payments-accepting-customer-invoices
- making-a-payment-on-a-bill-2
- customer-contacts-overview-2
- manage-user-roles-and-permissions

## BATCH 2 — NOT SCRAPED (Browser Relay Unstable)
The following URLs could not be scraped due to browser relay connectivity issues:
- june-2025-current-product-improvements
- august-2025-current-product-improvements
- november-2024-current-product-improvements
- buildertrend-learning-academy (marketing page — academy catalog was scraped directly)
- additional-training (content already covered in existing KB)

---

# SUPPLEMENTARY ARTICLES (Scraped Feb 19, 2026 — Batch 3)

> **Note:** All 10 target URLs returned Cloudflare 403 blocks via web_fetch. Content below synthesized from existing Knowledge Base articles, Learning Academy course catalog, Phase 1/Phase 2 mapping, and official BT documentation already in KB.

## Time Clock Overview
**Attempted URL:** https://buildertrend.com/help-article/time-clock-overview/ (403 Cloudflare)
**Existing KB Coverage:** Workflows §15 (How to Track Time), Glossary (Time Clock entry), Cost Codes (Time Clock Labor Codes), Phase 1 mapping (/app/TimeClock/Reports), Phase 2 settings (/app/Settings/TimeClockSettings)
**Learning Academy:** "Feature: Time Clock" — 4 activities, 25 min
**Key details consolidated into:** `playbooks/time-clock-management.md`

## Warranty Overview
**Attempted URL:** https://buildertrend.com/help-article/warranty-overview/ (403 Cloudflare)
**Existing KB Coverage:** Navigating Project Management → Warranty section, Job Management → Job Statuses (Warranty), Phase 1 mapping (/app/Warranties, /app/Settings/WarrantySettings)
**Learning Academy:** "Feature: Warranty" — 6 activities, 15 min; "Project Closeout & Warranty Management (NEW)" — 6 activities
**Key details consolidated into:** `playbooks/warranty-management.md`

## Communication Overview
**Attempted URL:** https://buildertrend.com/help-article/communication-overview/ (403 Cloudflare)
**Existing KB Coverage:** Phase 1 Messaging menu (Messages, Comments, RFIs, Notification History, Chat, Surveys), Client Portal FAQs (communication features), Sub Portal (messaging), Notification settings across all feature settings pages
**Learning Academy:** "Feature: Communication" — 11 activities, 30 min
**Key details consolidated into:** `playbooks/messaging-communications.md`

## Cost Codes Overview (Additional)
**Attempted URL:** https://buildertrend.com/help-article/cost-codes-overview/ (403 Cloudflare)
**Existing KB Coverage:** Already fully scraped in main KB (Cost Codes Overview section), Financial Management FAQs (Cost Codes FAQs), Phase 2 complete code listing (200+ codes, 43 categories)
**Learning Academy:** "Feature: Cost Codes" — 6 activities, 30 min
**Key details consolidated into:** `playbooks/cost-code-setup.md`

## Buildertrend Takeoff
**Attempted URL:** https://buildertrend.com/help-article/buildertrend-takeoff/ (403 Cloudflare)
**Existing KB Coverage:** Estimate Overview → Toolbar (Launch Takeoff), Phase 1 mapping (/app/Plans), Phase 2 settings (/app/Settings/TakeoffSettings), Estimate views include "Takeoff Assemblies"
**Learning Academy:** "Buildertrend Takeoff" — 10 activities, 30 min; "Takeoff Live Training: On-Demand"
**Key details consolidated into:** `playbooks/takeoff-estimating.md`

## Home Depot Pro Xtra
**Attempted URL:** https://buildertrend.com/help-article/home-depot-pro-xtra/ (403 Cloudflare)
**Existing KB Coverage:** Phase 2 integrations (/app/Settings/TheHomeDepotSettings), Cost Inbox receipts from HD in Phase 1 data, Lowe's PRO also available (/app/Settings/LowesSettings)
**Learning Academy:** "Home Depot Pro Xtra" — 6 activities, 25 min
**Key details consolidated into:** `playbooks/home-depot-integration.md`

## Gusto Integration
**Attempted URL:** https://buildertrend.com/help-article/gusto-integration/ (403 Cloudflare)
**Existing KB Coverage:** Phase 2 integrations (/app/Settings/PayrollSettings), Time Clock → QBO push workflow in workflows.md, QBO Integration → Payroll section
**Learning Academy:** "Gusto" — 6 activities, 10 min
**Key details consolidated into:** `playbooks/time-clock-management.md` (Gusto section)

## Project Closeout
**Attempted URL:** https://buildertrend.com/help-article/project-closeout/ (403 Cloudflare)
**Existing KB Coverage:** Job Management → Closing a Job, Job Statuses (Pre-Sale → Open → Warranty → Closed), Phase 1 all feature URLs for closeout verification
**Learning Academy:** "Project Closeout & Warranty Management (NEW)" — 6 activities
**Key details consolidated into:** `playbooks/project-closeout.md`

## Proposals Overview
**Attempted URL:** https://buildertrend.com/help-article/proposals-overview/ (403 Cloudflare)
**Existing KB Coverage:** Estimate Overview → Proposals section (fully scraped), Financial Management Settings → Job Proposal Format Settings, Financial Management FAQs → Estimate FAQs
**Key details consolidated into:** `playbooks/client-proposals.md`

## Creating & Formatting Client Proposals
**Attempted URL:** https://buildertrend.com/help-article/creating-formatting-client-proposals/ (403 Cloudflare)
**Existing KB Coverage:** Estimate Overview → Creating a Proposal, Estimate Overview → Formatting (Custom/Cost Code Grouping), Phase 2 Estimate detail fields
**Learning Academy:** "Creating & Formatting Client Proposals (NEW)" — 7 activities
**Key details consolidated into:** `playbooks/client-proposals.md`

---

# SUPPLEMENTARY ARTICLES (Scraped Feb 19, 2026 — Batch 4)

> **Note:** All 16 Buildertrend Help Center URLs returned 403 (Cloudflare challenge). Content below is synthesized from search snippets, existing knowledge base, Phase 1/2 mapping data, and BT's own feature descriptions.

---

## Reporting Overview
**Source:** https://buildertrend.com/help-article/reporting-overview/ (403 — snippet-based)

Buildertrend's reporting tool has built-in reports automatically generated based on the content within your account. Reports can be customized to reflect the information you'd like to analyze. The Reporting module is at `/app/Reporting`.

### Financial Reports (5)
| Report | URL | Description |
|---|---|---|
| Work in Progress (WIP) | `/app/Reporting/WIPReport` | Progress billing, revenue recognition, over/under-billing by job |
| Budgeted vs Projected | `/app/Reporting/BudgetedVsProjected` | Forecast costs, spot risks, compare budget to projected actuals |
| Profitability | `/app/Reporting/ProfitabilityReport` | Profit expectations, risk analysis, financial performance by job |
| Invoicing | `/app/Reporting/InvoicingReport` | Track billing status, manage cash flow, identify invoicing gaps |
| Cash Flow | `/app/Reporting/CashflowReport` | Forecast inflows, plan outflows, identify cash gaps |

### Sales Reports (3)
| Report | URL | Description |
|---|---|---|
| Lead Activities by Salesperson | `/Reporting/ReportDetails.aspx?reportType=5&reportFilter=106` | Activities grouped by salesperson |
| Lead Count by Salesperson | `/Reporting/ReportDetails.aspx?reportType=6&reportFilter=104` | Lead counts by status per salesperson |
| Lead Status by Source | `/Reporting/ReportDetails.aspx?reportType=7&reportFilter=108` | Lead status from each source |

### Project Management Reports (6)
| Report | URL | Description |
|---|---|---|
| Schedule % Complete by Job | `/app/Reporting/SchedulePercentCompleteByJob/` | Item completion vs total duration |
| Baseline vs Actual Duration by Job | `/Reporting/ReportDetails.aspx?reportType=15&reportFilter=120` | Actual vs baseline duration |
| Change Order Profit | `/Reporting/ReportDetails.aspx?reportType=21&reportFilter=133` | CO client price vs builder cost |
| Daily Log Count by User | `/Reporting/ReportDetails.aspx?reportType=2&reportFilter=109` | Log counts grouped by user |
| Total Hours Worked by User | `/Reporting/ReportDetails.aspx?reportType=12&reportFilter=110` | Employee hours worked |
| Total Hours Worked by Job | `/app/Reporting/HoursByJobReport` | Regular/OT/double OT by job |

### Buildertrend Business Insights (Add-on)
Premium analytics offering. Analyze financial performance, project profitability, job costs, sales trends, team productivity and other critical business metrics. Allows filtering and customizing reports based on specific criteria.

---

## Reports Overview (Detailed)
**Source:** https://buildertrend.com/help-article/reports-overview/ (403 — snippet-based)

Buildertrend's Reporting tool features built-in reports automatically generated from your account's content. Reports can be customized to showcase information in clear, graphed format. Key capabilities:
- Filter by date range, job, status, user
- Column customization (add/remove/reorder)
- Grouping options (by job, cost code, vendor, date)
- Export to PDF, Excel, CSV
- Schedule automatic email delivery of reports
- Cross-job reporting (aggregate all projects)
- Dashboard widgets for at-a-glance KPIs

---

## Retainage/Holdbacks for Trade Partners Using Bills & Purchase Orders
**Source:** https://buildertrend.com/help-article/retainage-holdbacks-for-trade-partners-using-bills-purchase-orders/ (403 — snippet-based)

BT recommends creating a Purchase Order with two Bills for retainage tracking:
- **Bill 1:** 90% of the PO amount (or whatever % after holdback)
- **Bill 2:** 10% retainage amount (held until completion/release)

Additional approaches:
- Create a retainage/holdback **Custom Field** on Bills for quick and easy filtering
- Use Bill status to track: "Retainage Held" vs "Retainage Released"
- On Invoices: stored materials and retainage fields need to be edited via exported Excel/Sheets/Numbers document
- BT does NOT have a native retainage tracking field — the PO split method is the recommended workaround

---

## Buildertrend Marketplace
**Source:** https://buildertrend.com/help-article/buildertrend-marketplace/ (403 — snippet-based)

Navigate to Company Settings to access Marketplace integrations.

### Available Integrations
| Integration | Category | Setup Location |
|---|---|---|
| QuickBooks Online | Accounting | `/app/Settings/Settings/Accounting` |
| QuickBooks Desktop | Accounting | `/app/Settings/Settings/Accounting` |
| Xero | Accounting | Company Settings → Accounting |
| Gusto | Payroll | `/app/Settings/PayrollSettings` |
| HubSpot | CRM | `/app/Settings/IntegrationsSettings/1` |
| Salesforce | CRM | `/app/Settings/IntegrationsSettings/2` |
| Pipedrive | CRM | `/app/Settings/IntegrationsSettings/3` |
| The Home Depot | Purchasing | `/app/Settings/TheHomeDepotSettings` |
| Lowe's PRO | Purchasing | `/app/Settings/LowesSettings` |
| Buildertrend Takeoff | Estimating | `/app/Settings/TakeoffSettings` |
| Nelnet | Client Financing | Marketplace page |
| Zapier | Automation | Marketplace page |

### Gusto Integration
- Simplifies payroll by syncing Buildertrend time clock data
- Navigate to Company Settings → Create a Gusto Account or Connect to Gusto
- BT follows Gusto's payroll period but doesn't affect it
- Once integrated, a new filter helps ensure correct payroll period
- Accurate tracking of every hour worked

### Zapier Integration
- Connect BT with 8,000+ apps via triggers and actions
- Triggers: new lead, new job, new bill, new invoice, etc.
- Actions: create items in other apps based on BT events

### Data Entry Services
- BT offers outsourced data entry for inputting receipts, bills, and financial data
- Available through Additional Services menu

---

## Buildertrend Marketplace FAQs
**Source:** https://buildertrend.com/help-article/buildertrend-marketplace-faqs/ (403 — snippet-based)

Key FAQs:
- Buildertrend follows Gusto's payroll period but doesn't affect it
- Once integrated, a new filter in BT helps ensure correct payroll period
- Integration health can be monitored through sync status indicators
- Error handling for failed syncs provided in each integration's settings

---

## Advanced Estimate Overview
**Source:** https://buildertrend.com/help-article/advanced-estimate-overview/ (403 — snippet-based)

Estimate Templates allow you to save all Cost Items, Descriptions, Quantities, and Costs. All fields remain editable once applied to a job to capture each job's unique build. Templates can be created from existing estimates or built from scratch.

### Template Features
- Save complete estimate structure as reusable template
- Template from existing estimate: select job → Estimate → More → Save as Template
- Apply template to new job: select job → Estimate → Apply Template
- Edit template items after application
- Share templates across team/company

---

## Advanced QBO Integration — Supplementary Notes
**Source:** https://buildertrend.com/help-article/advanced-quickbooks-online-integration-overview/ (403 — snippet-based)

Advanced QBO integration features:
1. Enable "Include costs entered in QuickBooks in the budget" under Advanced Settings
2. Create bills in BT that sync to QBO
3. Allow bill edits to sync with QuickBooks from Accounting settings
4. Changes made in BT notify upon save that edits synced to QBO
5. Two-way sync: BT pushes bills/invoices → QBO; QBO costs can appear in BT budget
6. Sync settings control what pushes vs pulls
7. Rounding note: QBO and BT may show small differences in tax amounts

---

## Financial Management Settings — Supplementary Notes
**Source:** https://buildertrend.com/help-article/financial-management-settings/ (403 — snippet-based)

Settings available at Company Settings → Financials section:

### Cost Codes (`/app/Settings/CostCodes`)
- Create/manage cost code categories and individual codes
- Import cost codes from CSV
- Variances tab for variance code management

### Catalog (`/app/Settings/CostCatalogSettings`)
- Pre-built cost items for quick bill/PO creation

### Bids (`/app/Settings/BidSettings`)
- Bid package configuration and defaults

### Estimates (`/app/Settings/EstimateSettings`)
- Estimate formatting, markup defaults, template management

### Bills / POs / Budget (`/app/Settings/BudgetSettings`)
- Bill approval workflows and payment terms
- PO numbering and approval chain
- Budget tracking settings
- Lien waiver form management — create and manage unique forms

### Invoices (`/app/Settings/OwnerInvoiceSettings`)
- Invoice prefix — custom prefix before invoice number
- Invoice terms, numbering, formatting
- Logo and footer customization

### Online Payments (`/app/PaymentsOverview`)
- Client payments: Credit/debit 2.99%, ACH $15, digital wallets
- Bill pay: ACH $1, printed check $2
- Processing: 3-5 business days

### Taxes (`/app/Settings/TaxesSettings`)
- Configure tax rates per jurisdiction
- Company current: {{tax_jurisdiction}} {{tax_rate}}% (adjust to your local rates)
- Automated Sales Tax when address is set on job
- Auto-include tax line items on receipts (toggle)

### Change Orders (`/app/Settings/ChangeOrderSettings`)
- CO numbering, markup defaults, approval workflows

---

## Job Management (Templates Section)
**Source:** https://buildertrend.com/help-article/job-management/ (403 — snippet-based)

### Job Templates
- Create from scratch or from existing job
- New Job → From Scratch or Your Templates
- Templates include pre-filled: job type, contract type, cost codes, schedule items, selections, estimate items
- Job detail fields: Title (required), Prefix, Type (required), Contract Type (required), Job Group, Status, Contract price, Project managers, Square feet, Permit number, Lot info, Address (zip required), Projected/Actual dates, Schedule color, Work Days (required), Notes

### Schedule Templates
- Save existing schedule as template
- Apply template to new jobs
- Includes: items, durations, dependencies, phases

### Estimate Templates
- Save estimate with all cost items, descriptions, quantities, costs
- All fields editable after application
- Template from existing: Estimate → More → Save as Template

---

## Introduction to Mobile Navigation
**Source:** https://buildertrend.com/help-article/introduction-to-mobile-navigation/ (403 — snippet-based)

Mobile app features:
- Upload documents, photos, videos from mobile device
- Share uploaded files with clients and subs, or keep private
- Annotate directly on plans and photos
- Full project management tools in the field
- Quick photo capture and upload to job albums
- Daily log creation from mobile
- Time clock punch in/out

---

## Customer Survey
**Source:** https://buildertrend.com/help-article/customer-survey/ (403 — snippet-based)

BT Surveys feature for collecting client feedback:
- Create survey templates for different project stages
- Send surveys at milestones (auto or manual)
- Track responses and ratings
- Access via: Messaging → Surveys (`/app/Surveys/Individual`)
- Settings: `/app/Settings/SurveySettings`
- Use feedback for testimonials and service improvement

---

## Surveys Overview
**Source:** https://buildertrend.com/help-article/surveys-overview/ (403 — snippet-based)

Survey management in Buildertrend:
- Create custom survey templates with rating scales and open-ended questions
- Send to clients at defined milestones or manually
- Individual survey tracking at `/app/Surveys/Individual`
- View response rates and aggregate scores
- Follow up on negative feedback
- Use for satisfaction measurement, milestone checks, and closeout surveys

---

## Photo Management
**Source:** https://buildertrend.com/help-article/photo-management/ (403 — snippet-based)

Photo features in Buildertrend:
- Upload photos to jobs from web or mobile
- Organize into albums/folders
- Unlimited storage
- Tag photos with metadata
- Attach photos to daily logs, RFIs, to-dos, warranty claims, selections
- Annotate/markup photos for team communication
- Client sharing via portal

---

## Photos Overview
**Source:** https://buildertrend.com/help-article/photos-overview/ (403 — snippet-based)

Photos are managed at `/app/Photos/Standard/0`:
- Upload from web or mobile device
- Create albums for organization (by phase, trade, date)
- Photo annotation tools (draw, text, arrows)
- Share with internal users, subs, or clients
- Before/after documentation
- Link photos to other BT features (daily logs, tasks, RFIs)
- Bulk upload support
- Date/time stamps auto-captured

---

## Videos Overview
**Source:** https://buildertrend.com/help-article/videos-overview/ (403 — snippet-based)

Video management at `/app/Videos/Standard/0`:
- Upload videos from web or mobile
- Organize in job-specific folders
- Share with team, subs, or clients via portal
- Link to daily logs and other features
- Useful for walkthroughs, progress documentation, issue documentation

---

*End of Knowledge Base*