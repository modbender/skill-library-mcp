# Documents Deep Dive

## Structure with Styles

**Why use Styles:**
- Automatic Table of Contents
- Consistent formatting throughout
- Easy global changes (change Heading 1 once, all update)

**Hierarchy:**
- Title → document name
- Heading 1 → major sections
- Heading 2 → subsections
- Heading 3 → sub-subsections
- Normal → body text

**Modify Style:** Right-click style → Modify → Change font, spacing, color

---

## Page Layout

### Section Breaks
- Use for different headers/footers in parts of document
- Insert → Break → Section Break (Next Page)
- Unlink sections to have different content

### Page Numbers
**Start on page 3:**
1. Insert Section Break before page 3
2. Double-click footer on page 3
3. Uncheck "Link to Previous"
4. Insert Page Number → Format → Start at 1

### Different First Page
- Design → Different First Page (checkbox)
- First page can have no header, rest have header

---

## Mail Merge

**Use cases:** Personalized letters, labels, envelopes, emails

**Process:**
1. **Data source:** Excel file with columns (Name, Address, etc.)
2. **Main document:** Template with placeholders
3. **Merge:** Combine to produce individual documents

**Steps (Word):**
1. Mailings → Start Mail Merge → Letters
2. Select Recipients → Use Existing List → select Excel file
3. Insert Merge Fields where personalization needed
4. Preview Results to check
5. Finish & Merge → Edit Individual Documents (or Print)

**Conditional content:**
```
{IF {MERGEFIELD Gender} = "M" "Mr." "Ms."}
```

---

## Formatting Fixes

| Problem | Solution |
|---------|----------|
| Paragraph spacing inconsistent | Select all → set Before/After spacing explicitly |
| Tab stops not aligning | View ruler → clear tabs → set new tab stops |
| Images jumping around | Right-click image → Wrap Text → choose wrap style |
| Page breaks in wrong places | Insert manual Page Break where needed |
| Table breaking across pages | Table Properties → Row → uncheck "Allow row to break" |

---

## Tables

**Convert text to table:** Select text → Insert → Table → Convert Text to Table
**Repeat header row:** Table Properties → Row → Repeat as header row
**Resize columns:** Double-click column border to auto-fit

---

## Track Changes

**Enable:** Review → Track Changes
**Accept/Reject:** Review → Accept/Reject buttons
**Compare documents:** Review → Compare → select original and revised

---

## Keyboard Shortcuts (Word)

| Action | Windows | Mac |
|--------|---------|-----|
| Heading 1 | Ctrl+Alt+1 | Cmd+Option+1 |
| Heading 2 | Ctrl+Alt+2 | Cmd+Option+2 |
| Page break | Ctrl+Enter | Cmd+Enter |
| Find & Replace | Ctrl+H | Cmd+H |
| Select all | Ctrl+A | Cmd+A |
