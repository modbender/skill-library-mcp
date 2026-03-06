# CPA Progress Tracking System

## File Structure in ~/cpa/

### profile.md
```markdown
# CPA Candidate Profile

## Basic Info
- State: [applying state]
- Education: [credits completed, accounting hours]
- Work Status: [full-time/part-time/student]
- Review Course: [Becker/Roger/Surgent/Wiley/etc.]

## Timeline
- Target completion: [date for all 4 sections]
- Hours available per week: [X hours]

## Current Status
- Sections passed: [list with dates]
- Currently studying: [section]
- Next exam date: [scheduled or target]

## NTS Status
- Applied: [date]
- Expires: [date]
- Sections covered: [list]
```

### sections/{section}.md
```markdown
# FAR Progress

## Current Status
- Target exam date: [date]
- Study start: [date]
- Weeks remaining: [X]

## Module Progress
| Module | MCQs Done | Accuracy | Status |
|--------|-----------|----------|--------|
| Conceptual Framework | 200/200 | 78% | ✓ |
| Revenue Recognition | 150/200 | 65% | In progress |
| Leases | 0/200 | -- | Not started |
| Government | 0/150 | -- | Not started |

## Weak Areas (from practice exams)
| Topic | Score | Priority |
|-------|-------|----------|
| Gov't Fund Accounting | 45% | ★★★★★ |
| Lease Modifications | 52% | ★★★★ |
| NFP Revenue | 58% | ★★★ |

## Practice Exam History
| Date | Score | vs. Passing |
|------|-------|-------------|
| 02-01 | 62 | -13 |
| 02-15 | 68 | -7 |
| 03-01 | 72 | -3 |

## Error Log (last 10 missed)
| Date | Topic | Error Type | Reviewed? |
|------|-------|------------|-----------|
| 03-05 | Consolidations | Concept | ✓ |
| 03-05 | Bonds | Calculation | ✓ |
```

### passed/{section}.md
```markdown
# FAR - PASSED

## Result
- Exam date: January 15, 2025
- Score: 81
- Credit expires: July 15, 2026

## Days until expiration: 487

## Score Report Breakdown
| Area | Performance |
|------|-------------|
| Conceptual Framework | Comparable |
| Financial Statements | Stronger |
| Transactions | Comparable |
| Government/NFP | Weaker |
```

### nts/current.md
```markdown
# Active NTS

- Applied: December 1, 2024
- Expires: June 1, 2025
- Days remaining: 89

## Sections Covered
- [ ] FAR - Scheduled: Jan 15
- [ ] AUD - Not scheduled
- [x] BEC - Passed Dec 20
- [ ] REG - Not scheduled

## Fees Paid
- Application: $85
- Exam fees: $850 (4 sections)
```

## Tracking Metrics

### Daily
- Hours studied
- MCQs completed
- Simulations practiced

### Weekly
- Total hours vs. target
- Accuracy trend by topic
- Weak areas addressed
- Practice exam scores

### Section Completion
- Final score
- Pass/fail
- Credit expiration date added to calendar
- 18-month clock updated

## Alerts System

| Condition | Alert Level | Action |
|-----------|-------------|--------|
| Credit expires <3 months | 🔴 Critical | Prioritize remaining sections |
| Credit expires <6 months | 🟡 Warning | Review timeline |
| NTS expires <1 month | 🔴 Critical | Schedule or lose fee |
| NTS expires <2 months | 🟡 Warning | Plan exam date |
| 3 days no study | 🟡 Warning | Check-in message |
| Practice score <70 | 🟡 Warning | Review weak areas |
