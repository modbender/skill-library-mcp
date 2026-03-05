# PMS Sheet Schemas

## PMS Task Tracker Sheet
**ID:** `1O07SzGzQa2FwpkBE7h2SUDWZlxsUpz8DxCpyxKjRi8U`
**Tab:** `Production`

| Column | Name | Format/Options |
|--------|------|----------------|
| A | Task ID | `PMS-TSKXXX` (auto-increment) |
| B | Description | Issue title |
| C | Reporter | `Tara Singh Kharwad` (always) |
| D | Date Submitted | `DD/MM/YYYY` |
| E | Status | New / In Progress / Completed / Under Review / Blocked / Testing |
| F | Task type | Issue / Feature / Testing |
| G | Priority | Critical / High / Medium / Low |
| H | Assigned To | `tarasinghrajput7261@gmail.com` (always) |
| I | Resolution Notes | GitHub issue URL |
| J | Resolution Date | DD/MM/YYYY (when closed) |
| K | Took Help from Roshan | Yes / No / Only Suggestion / Done by Roshan (manual) |

### Label Mappings

| GitHub Label | Sheet Value |
|--------------|-------------|
| bug | Issue |
| enhancement | Feature |
| P0 | Critical |
| P1 | High |
| P2 | Medium |
| P3 | Low |

---

## Team Daily Update Sheet
**ID:** `1GgRgfVBrF-ReGPRmntT6Cm2BjiLzJ3JiBaC4lMfrMQs`

### Format
- Column A: Date (DD/MM/YYYY)
- Column B: All tasks for that day in single cell

### Task Entry Format
```
- <Heading> - <Task description> - <Optional link>
- <Heading> - <Task description>
```

### Example Entry
```
- Website - Monitored and guided interns and solved related doubts
- Software - Updated and tested 7 new issues in the Github and PMS Task Tracker sheet
- PMS - Fixed login button issue - https://github.com/roshanasingh4/apni-pathshala-pms/issues/123
- Worked on the Live camera integration on the website
- Connect With: - Pranav bhai for the role and priorities of Tara
Working Hours : 8 Hrs
- Freelance Wala - Monitored Aman and his tasks
- Unwanted/Additional Tasks - Updated the Eklavya questionaire
```

### Appending PMS Tasks
Add under appropriate heading:
```
- PMS - <issue title> - <github_url>
```

---

## GitHub Repository
**Repo:** `roshanasingh4/apni-pathshala-pms`
**Default Assignee:** `roshanasingh4`

## Labels
- `bug` - For issues (maps to Task type: Issue)
- `enhancement` - For features (maps to Task type: Feature)
- `P0` - Critical priority
- `P1` - High priority
- `P2` - Medium priority
- `P3` - Low priority
