---
name: ds160-autofill
description: Automate filling of US nonimmigrant visa DS-160 forms using CDP for element location, CSV data source for user information, LLM assistance for complex cases (captcha, missing elements), and session persistence for resume capability. Use when user needs to: (1) Fill DS-160 visa application forms automatically, (2) Resume filling an interrupted DS-160 application, (3) Handle captcha and complex form elements with LLM assistance. Supports Chinese input with automatic translation to English.
---

# DS-160 Auto-fill Skill

This skill automates the filling of US nonimmigrant visa DS-160 forms by combining:
- CDP (Chrome DevTools Protocol) for fast element location
- CSV data source for user information
- LLM assistance for complex cases (captcha, missing elements)
- Session persistence for resume capability
- Chinese to English translation for user input

## Quick Start

### Starting a New Application

1. **Provide CSV data**: User must provide a CSV file with their personal information (use `ds160-user-info.csv` as template)

2. **Open DS-160 website**: Use `browser` tool to open `https://ceac.state.gov/genniv/` with profile `openclaw`

3. **Initialize session**: Load and execute `scripts/ds160-filler.js` to parse mappings and CSV

4. **Start filling**: Begin with the home page, handle captcha with LLM, then proceed page by page

### Resuming an Application

1. **Load existing session**: Check `ds160/ds160-session.json` for saved Application ID

2. **Open application**: Use the saved Application ID to resume on DS-160 website

3. **Continue filling**: Load CSV from saved location and continue from last page

## Core Workflow

### Step 1: Prepare Data

**Always check if session exists first:**
```javascript
// Read ds160/ds160-session.json
// If exists → Resume mode
// If not → New application mode
```

**New application mode:**
- Ask user for CSV file path or content
- Save CSV to `ds160/ds160-user-info.csv` using `write` tool
- Initialize session data in `ds160/ds160-session.json`:
  ```json
  {
    "applicationId": null,
    "securityQuestion": null,
    "securityAnswer": null,
    "currentPageIndex": 0,
    "completedPages": [],
    "startDate": "2026-02-06T21:00:00Z"
  }
  ```

**Resume mode:**
- Load CSV from `ds160/ds160-user-info.csv`
- Load session from `ds160/ds160-session.json`
- Report current progress to user

### Step 2: Initialize Browser

```javascript
// Open browser with openclaw profile
browser_start: { profile: "openclaw", targetUrl: "https://ceac.state.gov/genniv/" }

// For resume mode, add Application ID to URL
// Example: https://ceac.state.gov/GenNIV/Common/ConfirmApplicationID.aspx
```

### Step 3: Fill Current Page

**For each page in sequence:**

1. **Snapshot page** to understand current state:
   ```javascript
   browser_snapshot: { refs: "role", profile: "openclaw" }
   ```

2. **Load mappings** from `references/ds160-elements.yaml`

3. **Execute fill logic** using `browser act` with evaluate:
   ```javascript
   // Load ds160-filler.js
   // Call fillPage(page, currentUrl, userData, yamlData)
   ```

4. **Handle results**:
   - **Success**: Continue to next page
   - **Needs LLM assistance**: Call LLM and retry
   - **Needs user input**: Save progress and pause

### Step 4: Handle Special Cases

**Captcha:**
- Take screenshot of captcha area
- Use `image` tool to analyze captcha
- Fill captcha code via browser evaluate

**Missing element:**
- Call LLM with page snapshot
- Ask LLM to locate element and provide alternative selector
- Retry fill operation

**Translation needed:**
- Call LLM with field context and Chinese value
- Ask LLM to translate to appropriate English value
- Update CSV and retry fill operation

**Missing user data:**
- Identify which field is missing
- Report to user with field name and description
- **Important**: Save current page using browser evaluate before pausing
- Wait for user to provide data

### Step 5: Save Progress & Continue

**After completing a page:**

1. **Update session data**:
   ```json
   {
     "applicationId": "AA00FBLCQP",
     "securityQuestion": "What is the given name of your mother's mother?",
     "securityAnswer": "LiMei",
     "currentPageIndex": 5,
     "completedPages": ["home", "security_question", "personal_1", "personal_2"],
     "startDate": "2026-02-06T21:00:00Z"
   }
   ```

2. **Save to file**: `write(ds160/ds160-session.json, JSON.stringify(sessionData))`

3. **Report progress to user**:
   - Current page completed
   - Next page name
   - Application ID
   - Security question/answer (first time only)
   - Overall progress (X/Y pages)

4. **Click "Continue" button** to proceed to next page

## Data Structures

### CSV Format

The CSV must have these columns:
1. `页面` - Page name
2. `字段名称` - Field identifier (matches YAML `name` field)
3. `英文说明` - English description
4. `中文说明` - Chinese description
5. `必填` - Required? (是/否)
6. `示例值` - Example value
7. `用户填写` - **User-provided value** (this is what gets filled)

**Important**: Users can provide values in Chinese. The script includes a built-in translation dictionary for common fields (gender, marital status, countries, etc.). For fields not in the dictionary, LLM will be called for translation automatically.

### YAML Structure

Each page in `ds160-elements.yaml` contains:
- `page_id`: Unique page identifier
- `page_name`: Human-readable page name
- `url`: Page URL pattern
- `elements`: Array of form elements with:
  - `id`: Element ID
  - `name`: Field identifier (matches CSV)
  - `type`: Element type (text, select, radio, checkbox, button)
  - `label`: English label
  - `label_cn`: Chinese label
  - `required`: Is required?
  - `options`: Available options (for select)
  - `group`: Radio group name

## Error Handling

### Element Not Found

**Symptoms**: `fillPage` returns `needsLLM: true`

**Action**:
1. Take page snapshot
2. Call LLM with:
   - Current URL
   - Element information (id, name, type)
   - Page HTML snippet
   - Ask LLM to analyze and provide alternative selector
3. Retry with LLM-suggested selector

### Translation Needed

**Symptoms**: `fillPage` returns `needsTranslation: true`

**Action**:
1. Call LLM with translation context:
   - Field name and description (EN/CN)
   - Field type and available options
   - Original Chinese value
   - Ask LLM to translate to appropriate English value for the field
2. Update CSV with translated value
3. Retry fill operation with translated value

**Example LLM prompt for translation**:
```
I need to translate this Chinese value for a DS-160 form field:

Field: ${elementName}
Type: ${elementType}
English label: ${label}
Chinese label: ${label_cn}
Chinese value: "${originalValue}"

Available options (if select): ${options}

Please provide the correct English value for this field. Consider:
- The field type and context
- Available options (if applicable)
- Standard DS-160 terminology

Return only the English value, no explanation.
```

### Data Missing

**Symptoms**: `fillPage` returns `needsUserInput: true`

**Action**:
1. **CRITICAL**: Save current page before pausing:
   ```javascript
   // Find and click "Save" button
   browser_act: {
     request: { kind: "click", ref: "save_button" }
   }
   ```
2. Report missing field to user:
   - Field name (English and Chinese)
   - Description
   - Whether it's required
3. Update CSV with new data using `write` tool
4. Resume filling

### Captcha

**Symptoms**: Captcha image detected on page

**Action**:
1. Take screenshot of captcha area
2. Use `image` tool:
   ```javascript
   image: {
     image: "/path/to/captcha.png",
     prompt: "What is the code shown in this captcha? Return only the code characters."
   }
   ```
3. Fill captcha field via browser evaluate
4. Submit form

## Page Sequence

The pages are filled in this order:

1. **home** - Start application, select location, handle captcha
2. **security_question** - Confirm Application ID, set security question
3. **personal_1** - Personal information (name, gender, DOB)
4. **personal_2** - Nationality, other nationalities, IDs
5. **travel** - Travel purpose, dates, who is paying
6. **travel_companions** - People traveling with you
7. **previous_us_travel** - Previous US visits
8. **address_phone** - Current address and phone
9. **passport** - Passport information
10. **us_contact** - US point of contact
11. **family_relatives** - Family information
12. **work_education** - Work and education history
13. **security_background** - Security questions

## Progress Reporting

**Report to user after each page:**

```
✓ Completed: Personal Information 1
📄 Next: Personal Information 2
🆔 Application ID: AA00FBLCQP
🔐 Security Question: What is the given name of your mother's mother?
🔑 Answer: LiMei
📊 Progress: 3/13 pages completed
```

**Include in every report:**
- Application ID (once obtained)
- Security question and answer (once generated)
- Current progress (X/Y pages)
- Next page name

## LLM Integration

### When to Call LLM

1. **Captcha detection**: Always use LLM to read captcha
2. **Element not found**: When multiple locator strategies fail
3. **Translation needed**: When user provides Chinese value not in built-in dictionary
4. **Complex elements**: For elements that require understanding context
5. **Validation errors**: When form submission fails with unclear reason

### LLM Prompts

**For element location:**
```
I need to find this form element on a DS-160 page:
- Element ID: {elementId}
- Field name: {fieldName}
- Element type: {elementType}
- Current URL: {url}

Please analyze the page and provide:
1. The correct way to locate this element (CSS selector or JavaScript)
2. Any visible labels or text associated with it
```

**For captcha:**
```
Please read the captcha code from this image. Return only the code characters, no explanation.
```

## Translation Dictionary

The script includes a built-in translation dictionary for common Chinese values. This covers:

**Gender**:
- 男/男性 → MALE
- 女/女性 → FEMALE

**Marital Status**:
- 已婚 → MARRIED
- 未婚 → SINGLE
- 离异 → DIVORCED
- 丧偶 → WIDOWED
- 合法分居 → LEGALLY SEPARATED
- 事实婚姻 → COMMON LAW MARRIAGE
- 民事结合 → CIVIL UNION/DOMESTIC PARTNERSHIP

**Yes/No**:
- 是/有/是，有 → Yes
- 否/没有/否，没有 → No

**Countries**:
- 中国 → CHINA
- 美国 → USA
- 英国 → UNITED KINGDOM
- 日本 → JAPAN
- 韩国 → KOREA, SOUTH

**Visa Types**:
- 旅游/商务/商务/旅游 → B1/B2
- 学生 → F1
- 访问学者 → J1
- 工作 → H1B

**Payment**:
- 自己/自费 → SELF
- 公司 → OTHER COMPANY
- 其他人 → OTHER PERSON

**Relationship (US Point of Contact)**:
- 朋友 → Friend
- 亲戚 → Relative
- 同事 → Colleague
- 配偶 → Spouse
- 同学 → Classmate
- 其他 → Other

**Other Values**:
- 不适用/不，不适用 → Does Not Apply

**For values not in this dictionary**, LLM will be automatically called for translation.

## Session Persistence

**Session file location**: `ds160/ds160-session.json`

**Session data structure**:
```json
{
  "applicationId": "AA00FBLCQP",
  "securityQuestion": "What is the given name of your mother's mother?",
  "securityAnswer": "LiMei",
  "currentPageIndex": 5,
  "completedPages": ["home", "security_question", "personal_1", "personal_2", "travel", "travel_companions"],
  "startDate": "2026-02-06T21:00:00Z",
  "lastUpdated": "2026-02-06T21:30:00Z"
}
```

**When to save session:**
- After completing each page
- Before pausing for user input
- After receiving Application ID
- After setting security question/answer

## Browser Automation Notes

**Always use `openclaw` profile** to maintain session across pages.

**Use `browser act` with `evaluate` for form filling**:
- More reliable than individual click/type actions
- Can execute complex JavaScript
- Better error handling

**Use `browser snapshot` before each page**:
- Check page state
- Identify dynamic elements
- Verify page loaded correctly

## Testing Checklist

Before using this skill with real data:

- [ ] Test element location on each page type
- [ ] Verify CSV parsing with sample data
- [ ] Test captcha handling with LLM
- [ ] Verify session save/load functionality
- [ ] Test resume from middle of application
- [ ] Verify "Save" button clicking works before pauses
- [ ] Test with various element types (text, select, radio, checkbox)
- [ ] Verify progress reporting format
- [ ] Test Chinese to English translation

## Example Usage

**User says**: "Help me fill DS-160 form with my data in this.csv"

**Agent workflow**:
1. Load SKILL.md (this file)
2. Check for existing session
3. Save CSV to ds160/ds160-user-info.csv
4. Initialize session
5. Open browser to DS-160
6. Fill page by page
7. Report progress after each page
8. Handle errors with LLM or user input
9. Save progress and continue

**User says**: "Continue filling my DS-160 form"

**Agent workflow**:
1. Load SKILL.md
2. Load existing session
3. Open browser to DS-160 with Application ID
4. Load CSV from saved location
5. Continue from last page
6. Report progress
7. Complete remaining pages

## Files Reference

- **scripts/ds160-filler.js** - Core automation logic (run via browser evaluate)
- **references/ds160-elements.yaml** - Element mappings (read-only)
- **references/ds160-user-info.csv** - User data template (copy to workspace)
- **ds160/ds160-session.json** - Session persistence (auto-created)
- **ds160/ds160-user-info.csv** - Active user data (auto-created)

## Important Notes

- **NEVER submit the final form** - this is for automation/testing only
- **Always save before pausing** - prevents data loss
- **Report progress frequently** - at least every page
- **Keep Application ID secure** - it's sensitive information
- **Use fake data for testing** - don't use real personal info
- **Chinese input is supported** - use built-in dictionary or LLM for translation
