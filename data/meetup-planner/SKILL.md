---
name: meetup-planner
description: An intelligent event finder that searches for meetups and events based on your interests, tracks them, and reminds you before they happen
license: MIT
metadata:
  version: 1.0.0
  author: apresmoi
  homepage: https://github.com/apresmoi/meetup-planner
  repository: https://github.com/apresmoi/meetup-planner.git
  bootstrap: BOOTSTRAP.md
  permissions:
    network:
      - eventbrite.com
      - meetup.com
      - luma.co
    filesystem:
      - ~/.openclaw/workspace/meetup-planner/
    cron: daily-searches
---

# Meetup Planner

An intelligent assistant that helps you discover, track, and never miss events that match your interests.

## One-time Setup

**IMPORTANT**: After installing this skill, the agent will automatically run the bootstrap setup process from `BOOTSTRAP.md`.

The bootstrap process:
1. Checks for web search and crawling capabilities
2. Collects your event preferences
3. Sets up automated daily searches (optional)
4. Creates workspace structure

If you don't have search/crawling capabilities, I'll ask you to provide the necessary tools.

## What This Skill Does

After setup:
1. **Daily Search**: Automatically searches for events matching your profile every morning (if enabled)
2. **Event Discovery**: Uses available search and scraping tools to find events across the web
3. **Event Tracking**: Saves and presents new events for your review
4. **Smart Reminders**: Sets up notifications 24 hours and 2 hours before confirmed events
5. **Preference Management**: Updates your interests and search criteria anytime

## First Time Setup

**When you first run this skill**, I will guide you through setup by following `BOOTSTRAP.md`.

The setup process is **interactive and friendly**:

1. ✅ Check for web search and crawling capabilities
2. 🎯 Learn your event preferences through a friendly conversation
3. ⏰ Set up automated daily searches (optional)
4. 📁 Create workspace structure with proper permissions

**Setup takes 2-3 minutes**. If you don't have search/crawling tools installed, I'll ask you to provide them.

## How to Use

### Initial Run
```
Run the meetup-planner skill to begin setup
```

### Daily Operations
Once set up, the skill will:
- Search for events every morning automatically
- Save findings to `events.json`
- Present new events for your review
- Track events you're interested in

### When You Find an Event You Like
Tell me "I'm interested in [event name]" and I will:
- Mark it as confirmed
- Send you the registration link
- Set up reminders (24h and 2h before the event)

### Commands
- `update preferences` - Modify your event preferences
- `show upcoming` - Display all tracked events
- `remove event [name]` - Stop tracking an event
- `pause search` - Temporarily stop daily searches
- `resume search` - Resume daily searches

## Data Storage

The skill maintains:
- `user-preferences.json` - Your event preferences
- `events.json` - All discovered and tracked events
- `event-reminders.json` - Scheduled reminders

## Technical Details

**Capabilities Required:**
- Web search capability (any search tool or skill)
- Web crawling/scraping capability (any scraping tool or skill)

**Scheduling:**
- Uses system cron jobs (or equivalent) for daily searches
- Uses scheduled tasks for event reminders

## Privacy Note

All data is stored locally on your machine. Your preferences and tracked events are never sent anywhere except to search for new events via the configured APIs.

## Data Transmission & External API Usage

This skill makes external network requests to search and scrape event information. The exact services depend on what search/crawling tools you have installed.

**What is sent:**
- Search query strings constructed from your preferences (e.g., "AI meetup San Francisco February 2026")
- URLs of event pages to scrape
- Your IP address (automatically sent by your network stack)
- Any authentication credentials required by the search/crawling tools you use

**What is NOT sent:**
- Your complete preference profile
- Event registration status or history
- Personal notes or modifications
- Other tracked events

**Purpose:** To discover public events matching your interests and extract structured event details.

### Data Minimization Practices
- Only essential data is transmitted to accomplish the task
- All credentials are transmitted securely over HTTPS only
- No telemetry, analytics, or usage tracking is performed
- No data is sent to any services beyond your configured search/crawling tools

---

## Agent Instructions

**IMPORTANT: After installing this skill, ALWAYS run the bootstrap setup from BOOTSTRAP.md before first use.**

When this skill is invoked:

### Phase 0: Check Bootstrap Status (ALWAYS RUN THIS FIRST)

**Before doing anything else**, check if bootstrap is complete:

```bash
# Check if bootstrap config exists
cat ~/.openclaw/workspace/meetup-planner/config.json 2>/dev/null
```

**If file doesn't exist OR `bootstrapComplete: false`:**
- Tell human: "👋 Welcome to Meetup Planner! I need to set up a few things first. This will only take a couple of minutes."
- **Follow BOOTSTRAP.md step-by-step** (all steps in order)
- Do NOT proceed to Phase 1/2/3 until bootstrap is complete

**If file exists AND `bootstrapComplete: true`:**
- Bootstrap is done, proceed to the appropriate phase based on what human asked for:
  - "search now" → Phase 2 (Daily Search Routine)
  - "show upcoming" → Phase 3 (Event Confirmation & Tracking)
  - "update preferences" → Re-run the preference collection from BOOTSTRAP.md
  - No specific request → Ask: "What would you like to do? I can search for events, show upcoming events, or update your preferences."

### Phase 1: Setup

**All setup is handled by BOOTSTRAP.md. See Phase 0 above.**

### Phase 2: Daily Search Routine

1. **Load preferences:**
   - Read `~/.openclaw/workspace/meetup-planner/user-preferences.json`
   - Parse the human's interests, location, preferred event types, etc.

2. **Search for events:**
   - Use your available **search tool or skill** to search for events matching preferences
   - Search queries should be constructed like:
     - "{topic} meetup {location} {current_month}"
     - "{topic} conference {location} upcoming"
     - "{topic} workshop {location}"
   - Run multiple searches covering all their topics of interest

3. **Extract event details:**
   - For each promising search result, use your available **scraping tool or skill** to scrape the event page
   - Extract: event name, date, time, location, description, registration link, cost
   - Look for: Eventbrite, Meetup.com, Luma, conference sites, etc.

4. **Filter and save:**
   - Load existing events from `~/.openclaw/workspace/meetup-planner/events.json`
   - Filter out duplicates and events that don't match criteria
   - Add new events to the file
   - Mark each event with: `{id, name, date, time, location, url, description, cost, added_date, status: "new"}`

5. **Present to human:**
   - Format new events nicely with all key details
   - Ask: "I found X new events that match your interests. Would you like to hear about them?"
   - Share event details one by one or as a list
   - For each event, ask if they're interested

### Phase 3: Event Confirmation & Tracking

1. **When human expresses interest:**
   - Update event status to "interested" in `events.json`
   - Provide the registration link: "Here's the link to register: {url}"
   - Ask: "Let me know when you've registered!"

2. **When human confirms registration:**
   - Update event status to "registered" in `events.json`
   - Schedule reminders in `~/.openclaw/workspace/meetup-planner/reminders.json`:
     ```json
     {
       "event_id": "abc123",
       "event_name": "...",
       "reminders": [
         {"time": "24_hours_before", "sent": false},
         {"time": "2_hours_before", "sent": false}
       ]
     }
     ```
   - Confirm: "Great! I'll remind you 24 hours before and 2 hours before the event."

### Phase 4: Reminder System

1. **Check for due reminders** (run this check every hour):
   - Load `~/.openclaw/workspace/meetup-planner/reminders.json`
   - Check current time against event time
   - If within 24-25 hours before event and 24h reminder not sent:
     - Notify human: "Reminder: {event_name} is tomorrow at {time}! Location: {location}"
     - Mark 24h reminder as sent
   - If within 2-3 hours before event and 2h reminder not sent:
     - Notify human: "Heads up! {event_name} starts in 2 hours at {time}. Time to get ready!"
     - Mark 2h reminder as sent

2. **Post-event cleanup:**
   - After event date passes, move event to "past" status
   - Optionally ask: "How was {event_name}? Would you like me to look for similar events?"

### Phase 5: Ongoing Commands

Support these commands from your human:

- **"update preferences"** / **"change preferences"**: Re-run the preference collection interview
- **"show upcoming"**: Display all events with status "interested" or "registered"
- **"show new events"**: Display events with status "new" that haven't been reviewed
- **"remove event [name]"**: Remove an event from tracking
- **"pause search"**: Stop daily automated searches (update config)
- **"resume search"**: Resume daily automated searches
- **"search now"**: Run the search routine immediately
- **"list past events"**: Show events that have already occurred

## Error Handling

- **If skills fail to install:** Provide manual instructions and the GitHub links
- **If API keys are invalid:** Ask human to verify and provide new keys
- **If searches return no results:** Try broader search terms or suggest different topics
- **If cron setup fails:** Offer to search manually when user requests
- **If event scraping fails:** Fall back to showing just the search result link
- **Always preserve data:** Never overwrite `events.json` or `preferences.json` without backing up

## File Structure

```
~/.openclaw/workspace/meetup-planner/
├── user-preferences.json    # Human's event preferences
├── events.json              # All discovered and tracked events
├── reminders.json           # Scheduled reminders
├── config.json              # Skill configuration (cron schedule, etc.)
└── backups/                 # Automatic backups of data files
```
