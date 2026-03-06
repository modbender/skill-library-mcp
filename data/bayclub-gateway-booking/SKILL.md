---
name: bayclub_manager
description: "Book and manage tennis/pickleball courts at Bay Club."
user-invocable: true
metadata: { 
  "openclaw": { 
    "emoji": "🎾",
    "requires": { "bins": ["node"] },
    "category": "Utilities"
  } 
}
---

# Bay Club Manager
This skill uses Stagehand and TypeScript to automate browser bookings.

## Instructions
When the user asks to book or check courts:
1. Use the `shell` tool to run the implementation script.
2. The command to run is: `NODE_ENV=development STAGEHAND_ENV=LOCAL HEADLESS=true npx ts-node --transpile-only {baseDir}/bayclub_skills.ts`
3. Pass user arguments (date, time, club) as strings to the script.

## Files
- Logic: `{baseDir}/bayclub_skills.ts`
- Browser Engine: `{baseDir}/BayClubBot.ts`
