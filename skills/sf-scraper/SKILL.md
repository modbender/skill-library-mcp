---
name: sf-scraper
description: >
  Scrape employee data from a logged-in SAP SuccessFactors browser session using browser automation.
  Use when: user provides an employee ID and wants employee details (name, email, department, manager, etc.)
  scraped directly from the SuccessFactors UI — NOT via OData/API. Requires the user to have
  SuccessFactors open and logged in via Chrome with the OpenClaw Browser Relay extension attached.
  Triggers on: "get employee name", "look up employee", "scrape SF", "find employee in SuccessFactors",
  or any request combining an employee ID with SuccessFactors data lookup.
---

# SF Scraper — SuccessFactors Browser Scraping Skill

Scrape employee data from a live, logged-in SAP SuccessFactors session via browser automation.
This skill uses ONLY browser snapshots and actions — zero API calls.

## Prerequisites

- User must have SAP SuccessFactors open and logged in on a Chrome tab.
- OpenClaw Browser Relay Chrome extension must be active (badge ON) on that tab.
- **Always** use `profile="chrome"` for all browser calls (we need the authenticated session).

## Step-by-Step Workflow

### Step 1: Verify Session & Get Base URL

```
browser(action="snapshot", profile="chrome", compact=true)
```

**Check for these states:**

- **Login page detected** (look for: "Log in", "Username", "Password", "Company ID" fields) → Tell user to log in first and re-attach the relay.
- **Session expired** ("Session Timeout", "session has expired") → Same, ask user to re-login.
- **SF Home/Dashboard** → Good. Extract the base URL from the page URL in the snapshot. It will be one of:
  - `https://<company>.successfactors.com`
  - `https://<company>.successfactors.eu`
  - `https://<company>.sapsf.com`
  - `https://pmsalesdemo<N>.successfactors.com` (demo instances)
  - `https://hcm<N>preview.sapsf.com` (preview instances)

Store the base URL — all subsequent navigation uses it.

### Step 2: Navigate to Employee Profile

Try these navigation strategies **in order**. Move to the next only if the current one fails.

#### Strategy A: People Profile Deep Link (preferred)

```
browser(action="navigate", profile="chrome", targetUrl="{base_url}/sf/liveprofile?selected_user={employee_id}")
```

Wait 2-3 seconds for load, then snapshot. This is the most reliable deep link in modern SF instances.

**Success indicators:**
- Page contains a heading with a person's name
- You see sections like "Personal Information", "Job Information", "About Me"
- URL contains `liveprofile` and the employee ID

**Failure indicators:**
- Blank page, spinner that never resolves
- "Page not found", "Error", or redirect to home
- Generic dashboard with no employee context

#### Strategy B: Alternative Deep Links

If Strategy A fails, try these one at a time:

```
{base_url}/xi/ui/peopleprofile/pages/index.xhtml?selected_user={employee_id}
{base_url}/sf/peopleprofile?selected_user={employee_id}
{base_url}/#/userprofile/{employee_id}
{base_url}/sf/admin/employeefiles?selected_user={employee_id}
```

Same validation — snapshot after each and check for profile content.

#### Strategy C: Global Search Bar

If all deep links fail, use the search:

1. **Snapshot** the current page.
2. **Find the search element.** Look for:
   - A `searchbox` role element (most common)
   - A `textbox` with placeholder containing "Search", "Search People", "Find Someone"
   - An element with aria-label containing "search"
   - The magnifying glass icon / search icon button (click it first to expand the search bar)
3. **Click** the search box to focus it.
4. **Type** the employee ID:
   ```
   browser(action="act", profile="chrome", request={kind: "type", ref: "<search_ref>", text: "{employee_id}"})
   ```
5. **Press Enter** or click the search button:
   ```
   browser(action="act", profile="chrome", request={kind: "press", ref: "<search_ref>", key: "Enter"})
   ```
6. **Wait 2-3 seconds**, then snapshot the results.
7. **Parse the results:**
   - If one result → click it to open the profile.
   - If multiple results → look for the one matching the employee ID. Results typically show as a list with name, ID, and photo. Click the correct one.
   - If no results → report to user that employee ID was not found.

#### Strategy D: Admin Center / Employee Files

Last resort — navigate through menus:

1. Navigate to `{base_url}/sf/admin`
2. Snapshot, look for "Employee Files" or "Manage Employees" link
3. Click it, then use the search/filter within that view
4. Find and click the employee

### Step 3: Handle Page Loading & Iframes

SuccessFactors heavily uses iframes and lazy loading. Critical handling:

**Iframe detection:**
- After navigating, if the snapshot shows minimal content or an iframe structure, try:
  ```
  browser(action="snapshot", profile="chrome", compact=true, frame="main")
  ```
- Common iframe names/ids in SF: `"main"`, `"contentFrame"`, `"bizmuleApp"`, `"xCalApp"`
- If `frame` doesn't work, take a full (non-compact) snapshot to see the full DOM tree

**Lazy loading / SPA transitions:**
- SuccessFactors is a Single Page Application. After navigation, content may take 3-5 seconds to render.
- **Always snapshot twice** if the first snapshot shows loading indicators:
  - Loading spinners: look for "Loading", "Please wait", spinner icons, progress bars
  - Wait 3 seconds between snapshots
  - If still loading after 2 retries (total ~9 seconds), inform user of slow load

**Popup/Modal handling:**
- SF sometimes shows popups ("What's New", cookie consent, tour prompts)
- If a modal/dialog appears, look for "Close", "X", "Dismiss", "Got it", "Skip" buttons
- Click to dismiss, then re-snapshot

### Step 4: Scrape the Profile Page

Once on the employee profile, take a detailed snapshot:

```
browser(action="snapshot", profile="chrome")
```

**SuccessFactors People Profile has these typical sections/cards:**

#### Header / Banner Area
Contains the most important info, always visible at top:
- **Full Name** — Large heading text, usually `heading` level 1 or 2
- **Job Title** — Text directly below the name
- **Photo** — Avatar image (not scrapable as data, but confirms you're on the right profile)
- **Employee ID** — Sometimes shown near name, sometimes in a subtitle like "ID: 12345"
- **Quick action buttons** — Email, phone icons (these contain contact data)

#### Info Cards / Sections (varies by company config)
Each card has a header and key-value pairs. Common patterns:

**"Personal Information" / "About" card:**
- First Name, Last Name, Middle Name
- Preferred Name / Display Name
- Date of Birth (may be restricted)
- Gender
- Nationality
- Marital Status

**"Job Information" card:**
- Job Title / Position Title
- Job Code
- Department / Division / Business Unit
- Cost Center
- Employment Type (Full-time, Part-time, etc.)
- Employee Class / Employee Type
- Regular/Temporary
- Standard Hours
- FTE (Full-Time Equivalent)
- Pay Grade
- Worker's Compensation Code

**"Employment Details" / "Employment Information" card:**
- Hire Date / Original Start Date
- Seniority Date
- Service Date
- Last Date Worked
- Termination Date (if applicable)
- Employment Status (Active, Terminated, Leave, etc.)

**"Compensation Information" card (may be restricted):**
- Annual Salary / Base Pay
- Pay Component
- Currency
- Compa-Ratio
- Range Penetration

**"Contact Information" card:**
- Business Email
- Personal Email
- Business Phone
- Mobile Phone
- Home Phone
- Business Address (Street, City, State, Zip, Country)
- Home Address

**"Organizational" / "Position" card:**
- Manager Name (usually a clickable link)
- Manager ID
- Position
- Direct Reports count
- Legal Entity
- Company Code

**"Spot Profile" / "About Me" card:**
- Bio / About Me text
- Skills
- Interests
- Social accounts

#### How to Extract Key-Value Pairs

In the accessibility tree snapshot, profile data appears as:
- **Labels** — `text` or `label` nodes with the field name (e.g., "Department")
- **Values** — Adjacent `text`, `link`, or `statictext` nodes with the value (e.g., "Engineering")
- Pattern: label followed by its value, often in a grid/table or definition list structure

Example snapshot patterns:
```
text "Department"
text "Engineering"
text "Manager"
link "Jane Smith"
text "Location"
text "Bangalore, India"
text "Email"
link "john.doe@company.com"
```

Scan sequentially and pair each label with its following value.

### Step 5: Navigate Tabs for More Data

SuccessFactors profiles often organize data into tabs or collapsible sections.

**Common tab names:**
- "Personal Information" / "Personal Info"
- "Job Information" / "Job Info"  
- "Employment Information" / "Employment Details"
- "Compensation Information" / "Compensation"
- "Pay Components" / "Pay Details"
- "Organizational Information" / "Organization"
- "Contact Information"
- "Documents"
- "Performance History"
- "Goal Plan"
- "Time Off" / "Leave"

**To navigate tabs:**
1. Snapshot and identify tab elements (role: `tab`, `tablist`, or clickable links with these names)
2. Click the tab you need:
   ```
   browser(action="act", profile="chrome", request={kind: "click", ref: "<tab_ref>"})
   ```
3. Wait 1-2 seconds for content to load
4. Snapshot again and extract the new section's data

**Collapsible sections:**
- Some profiles use expandable/collapsible sections instead of tabs
- Look for `button` elements with section names and expand/collapse indicators
- Click to expand if collapsed, then snapshot

### Step 6: Handle "Show More" / Pagination

- Some sections show limited data with a "Show More", "View All", or "See More" link
- Click it if present to reveal full data, then re-snapshot
- Employment history or compensation history may have multiple records — scrape all visible

### Step 7: Return Results

Format results clearly, grouped by section:

```
═══ Employee Profile ═══

👤 Basic Info
   Name: John Doe
   Employee ID: 12345
   Job Title: Senior Developer
   Department: Engineering
   
📧 Contact
   Email: john.doe@company.com
   Phone: +91-9876543210
   Location: Bangalore, India
   
🏢 Organization
   Manager: Jane Smith
   Division: Technology
   Business Unit: Product Development
   Legal Entity: Company India Pvt Ltd
   
📋 Employment
   Hire Date: 2020-03-15
   Status: Active
   Type: Full-Time Regular
```

**Rules:**
- Only include fields actually found on the page — NEVER fabricate data
- If a field's value is empty or hidden ("*****", "Restricted"), report it as restricted
- If the user only asked for a name, don't scrape every tab — just return what's visible in the header

## Batch Mode

For multiple employee IDs:
1. Process one at a time sequentially
2. After each profile, navigate to the next using Strategy A
3. Collect all results
4. Present as a formatted table at the end
5. Note any IDs that failed

## Configuration (Optional)

User can add to `TOOLS.md`:
```markdown
### SuccessFactors
- Base URL: https://yourcompany.successfactors.com
- Default fields: name, email, department, manager
```

If configured, use the base URL directly (skip discovery). If default fields are specified, only scrape those.

## Error Handling

| Scenario | Detection | Action |
|----------|-----------|--------|
| Not logged in | Login form visible | Tell user to log in and re-attach relay |
| Session expired | "Session Timeout" text | Same as above |
| Employee not found | Search returns 0 results | Report clearly, suggest checking ID |
| Access denied | "Unauthorized", "No access", "Insufficient privileges" | Report — user may lack permissions |
| Profile restricted | Fields show "*****" or "Restricted" | Report which fields are restricted |
| Page won't load | Loading spinner after 3 retries | Report timeout, suggest refreshing SF |
| Multiple matches | Search returns >1 result | List matches with names/IDs, ask user to pick |
| Wrong instance | URL doesn't match expected SF domain | Warn user, ask to confirm |

## Important Notes

- **NEVER use OData, REST API, or any programmatic endpoint.** Pure browser scraping only.
- **Always use `profile="chrome"`** — never `profile="openclaw"` (need the user's auth session).
- **Be patient** — SF can be slow. Always verify page state with snapshots before extracting.
- **Don't navigate away** from SF without warning the user.
- **Respect permissions** — if data is restricted/hidden in the UI, it's restricted for a reason. Don't try to circumvent.
- **Screenshot fallback** — if snapshot (accessibility tree) doesn't capture visible text, use `browser(action="screenshot", profile="chrome")` to see the rendered page visually and extract from the image.
