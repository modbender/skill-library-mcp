# Holidays, School Terms & Leave Optimisation

## Early Setup Action

During onboarding (or immediately after), populate the user's memory with:

1. **Local public holidays** for the current + next year
2. **School term dates** (if they have school-age children)
3. **Leave optimisation strategies** — map out the best times to take annual leave by bridging public holidays and weekends for maximum time off with minimum leave days

Search for "[user's state/region] public holidays [year]" and "[user's state/region] school term dates [year]" to get this data. Store in `memory/[user]/holidays-[year].md`.

Ask the user before populating: "I'd like to add your local public holidays and school terms to help with planning — okay to go ahead?"

## What to Include

### Public Holidays
- Date, day of week, holiday name
- Flag which ones create long weekends automatically
- Note when holidays fall on weekends (lost opportunity)

### School Terms & Holidays
- Term start/end dates
- Holiday period dates
- Particularly useful for planning family activities and leave

### Leave Optimisation Strategies
For each cluster of public holidays, calculate:
- How many AL (annual leave) days needed
- Total days off achieved
- Whether it overlaps with school holidays (family bonus)
- Booking urgency ("popular period — book accommodation early")

Present as actionable options: "Take 3 days AL, get 10 days off"

### Key Planning Windows
Maintain a rolling list of upcoming dates that need action:
- Long weekends within 4 weeks: "Have you planned anything?"
- School holidays within 8 weeks: "Time to book?"
- Major holidays within 12 weeks: "Accommodation fills up — worth looking now"

## Cron Integration

The weekly care nudge should check this file and surface timely prompts:
- 4 weeks before a long weekend: "[Local holiday] long weekend is coming up — any plans?"
- 8 weeks before school holidays: "Term 2 holidays start [date] — worth thinking about a trip?"
- When leave optimisation windows approach: "If you take [X days] off around [holiday], you get [Y days] total"

## Annual Refresh

In November/December each year, search for next year's public holidays and school terms. Update the file. Prompt the user: "New year's holidays are out — want to map out your leave strategy for [year]?"
