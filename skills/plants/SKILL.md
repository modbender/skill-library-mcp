---
name: Plants
description: Build a personal plant care system with watering schedules, care logs, and seasonal reminders.
metadata: {"clawdbot":{"emoji":"🌱","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User mentions a plant → create entry with care requirements
- Track watering and care → remind when due
- Seasonal prompts → fertilizing, repotting, pruning timing
- Create `~/plants/` as workspace

## When User Adds a Plant
- Name (common and scientific if known)
- Location: room, windowsill, outdoor
- Light conditions: direct sun, bright indirect, low light
- Acquired date: helps track age and growth
- Photo: visual reference for health comparison

## Plant File Structure
One file per plant: `pothos-living-room.md`
- Basic info: name, species, location
- Care requirements: water, light, humidity, temperature
- Care log: dated entries of watering, fertilizing, issues
- Notes: quirks, observations, what works

## Watering Tracking
- Log date when watered
- Note method: thorough soak, light water, bottom watering
- Track frequency that works — adjust by season
- "Last watered 5 days ago" surfacing when asked

## Watering Reminders
- Calculate based on plant type and last watering
- Succulents: 10-14 days
- Tropicals: 5-7 days
- Adjust by season — less in winter, more in summer
- Group plants by watering day to simplify routine

## Seasonal Care Calendar
- Spring: repotting season, increase watering, start fertilizing
- Summer: peak growth, watch for pests, more frequent water
- Fall: reduce fertilizing, prepare for dormancy
- Winter: reduce watering, no fertilizing, watch for dry air

## Problem Tracking
- Yellow leaves, brown tips, pests → log with photo
- What was tried, what worked
- Build knowledge base per plant species
- "Last time pothos had yellow leaves, I reduced watering"

## Fertilizing Schedule
- Track last fertilizing date
- Most houseplants: monthly during growing season
- Remind when due based on plant type
- Note which fertilizer used

## Repotting Log
- When repotted: date, pot size, soil mix used
- Next repotting estimate: usually 1-2 years
- Signs to watch: roots circling, water runs straight through

## Progressive Enhancement
- Week 1: add plants as they come up
- Week 2: start logging watering
- Month 2: add care requirements, set reminders
- Month 3: seasonal calendar integration
- Ongoing: photo log for growth tracking

## Folder Structure
```
~/plants/
├── indoor/
│   ├── pothos-living-room.md
│   └── monstera-bedroom.md
├── outdoor/
├── wishlist.md
└── care-calendar.md
```

## Photo Tracking
- Periodic photos show growth over time
- Before/after for problem resolution
- Reference for "is this normal for this plant?"
- Store in plant folder or link from file

## Propagation Tracking
- Parent plant reference
- Date started
- Method: cutting, division, seeds
- Progress log until established

## Plant Death / Removal
- Don't delete — move to archive
- Note cause if known: overwatering, pests, neglect
- Lessons learned for future
- "RIP monstera, root rot from overwatering winter 2024"

## What NOT To Suggest
- Complex apps before files work
- Automated watering systems — manual observation is valuable
- Over-precise schedules — plants aren't machines
- Guilt about plant deaths — it happens, learn and move on

## Common Questions to Handle
- "When did I last water the fiddle leaf?" → check log
- "Why is my pothos drooping?" → suggest common causes
- "What plants are good for low light?" → recommendations from knowledge
- "Time to repot anything?" → check repotting dates

## Integration Points
- Habits: "water plants" as recurring habit
- Calendar: seasonal care reminders
- Shopping: fertilizer, pots, soil when needed
