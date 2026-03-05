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

## Prerequisites

- User must have SAP SuccessFactors open and logged in on a Chrome tab.
- OpenClaw Browser Relay Chrome extension must be active (badge ON) on that tab.
- Use `profile="chrome"` for all browser calls.

## Workflow

### 1. Discover the SuccessFactors Base URL

Take a snapshot of the attached Chrome tab to identify the current SF domain:

```
browser(action="snapshot", profile="chrome", compact=true)
```

Extract the base URL (e.g., `https://<company>.successfactors.com` or `https://pmsalesdemo8.successfactors.com`).

### 2. Navigate to Employee Search / People Profile

SuccessFactors supports deep-link URLs. Use the following pattern to go directly to an employee's profile:

**Primary pattern (People Profile / Live Profile):**
```
{base_url}/sf/liveprofile?selected_user={employee_id}
```

**Fallback patterns if primary doesn't work:**
```
{base_url}/xi/ui/peopleprofile/pages/index.xhtml?selected_user={employee_id}
{base_url}/sf/home?selected_user={employee_id}
```

Navigate using:
```
browser(action="navigate", profile="chrome", targetUrl="{constructed_url}")
```

Wait briefly for the page to load, then snapshot.

### 3. If Deep Link Fails — Use Search

If the deep link lands on a generic page or errors, fall back to the global search:

1. Snapshot the page to find the search bar (usually top-right, role: `searchbox` or `textbox` with name containing "Search").
2. Click the search box, type the employee ID, press Enter.
3. Snapshot results, click the matching employee profile link.

### 4. Scrape Employee Data

Once on the profile page, take a snapshot:

```
browser(action="snapshot", profile="chrome", compact=true)
```

Extract the following fields from the rendered accessibility tree:

| Field | Where to Look |
|-------|---------------|
| **Name** | Page heading / `heading` role, or prominent text near avatar |
| **Employee ID** | Usually in a details section or the URL itself |
| **Email** | Look for `link` with mailto: or text containing @ |
| **Job Title** | Near name, often under heading |
| **Department** | In profile details / info card |
| **Manager** | In profile details, often a clickable link |
| **Location** | In profile details section |
| **Phone** | In contact info section |

Not all fields will always be visible — return what's available.

### 5. If Profile Page Uses Tabs/Sections

SuccessFactors profiles often have tabs (Personal Info, Employment Info, Job Info, etc.). If needed data isn't visible:

1. Snapshot to find tab elements.
2. Click the relevant tab (e.g., "Personal Information", "Job Information", "Employment Details").
3. Snapshot again and extract.

### 6. Return Results

Format results clearly:

```
Employee: John Doe
ID: 12345
Email: john.doe@company.com
Title: Senior Developer
Department: Engineering
Manager: Jane Smith
Location: Bangalore, India
```

Only include fields that were actually found on the page. Do not guess or fabricate data.

## Configuration

The user should create a config in `TOOLS.md` or the workspace with:

```markdown
### SuccessFactors
- Base URL: https://yourcompany.successfactors.com
```

If no base URL is configured, discover it from the currently open tab.

## Error Handling

- **Not logged in**: If snapshot shows a login page, tell the user to log in first.
- **Access denied / no profile found**: Report clearly — the user may lack permissions for that employee.
- **Page timeout**: Retry snapshot once after 3 seconds. If still loading, inform the user.
- **Search returns multiple results**: List them and ask the user to clarify.

## Batch Mode

If user provides multiple employee IDs, iterate through each one sequentially using the same workflow. Collect results and present as a table.

## Important Notes

- **Never use OData API, REST endpoints, or any programmatic API.** This skill is purely browser-based scraping.
- Always use `profile="chrome"` — never `profile="openclaw"` (we need the user's authenticated session).
- Be patient with page loads — SF can be slow. Use snapshots to verify page state before extracting.
- Respect the user's session — don't navigate away from SF without warning.
