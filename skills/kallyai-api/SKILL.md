---
name: kallyai-api
description: "KallyAI Executive Assistant — AI that handles phone calls (outbound + inbound), email, bookings, research, errands, multi-channel messaging, and phone number management on your behalf. Use when users want to: make/receive calls, manage inbound rules, handle voicemails, provision phone numbers, send email, book restaurants/hotels, search for services, manage calendar, check inbox/messages, handle bills, order food/rides, run errands, check credits/budget, coordinate goals, manage channels (WhatsApp/Telegram/social), run outreach campaigns, referrals, or any delegation task. Triggers on: call, phone, reservation, appointment, email, search, book, find, schedule, cancel, inbox, messages, research, assistant, coordinate, goal, credits, budget, ride, food, errand, bill, dispute, calendar, KallyAI, inbound, receptionist, voicemail, phone number, forward, transfer, takeover, channels, WhatsApp, Telegram, outreach, referral, subscription."
---

# KallyAI Executive Assistant

KallyAI is an AI executive assistant that handles outbound + inbound calls, email, bookings, research, bills, rides, food orders, errands, multi-channel messaging, and phone number management — all from the terminal.

## Quick Start

```bash
# The 80% command — natural language, routes automatically
python kallyai.py ask "Book a table at Nobu for 4 tonight"
python kallyai.py ask "Email Dr. Smith to reschedule my Thursday appointment"
python kallyai.py ask "Find the best plumber near me and negotiate a quote"

# Check credits (NOT minutes — credits are the sole billing unit)
python kallyai.py credits balance

# Check your inbox
python kallyai.py messages inbox

# View incoming calls handled by your AI receptionist
python kallyai.py inbound calls
```

## Complete Workflow

### Step 1: Gather Intent

Determine what the user needs. KallyAI covers 14 domains:

| Domain | Examples |
|--------|----------|
| **Coordination** | "Book a table", "Handle this for me", any multi-step request |
| **Calls** | Call a business, check on a reservation, negotiate |
| **Inbound** | View incoming calls, manage routing rules, voicemails, contacts |
| **Phone** | Provision numbers, set up forwarding, manage caller ID |
| **Actions** | Calendar events, bookings, bill analysis, rides, food, errands |
| **Messages** | Check inbox, read messages, view threads |
| **Search** | Find businesses, research options, compare prices |
| **Email** | Send emails, manage accounts, train voice profile |
| **Channels** | Manage WhatsApp, Telegram, email contacts, channel status |
| **Outreach** | Multi-channel outreach tasks (call + email + messaging) |
| **Budget** | Estimate costs, approve budgets, view breakdowns |
| **Credits** | Check balance, view history, spending breakdown, plans |
| **Subscription** | Change plan, view status, cancel pending changes |
| **Referrals** | Get referral code, view stats, track referrals |

**For most requests, use `ask`** — it routes through the coordination AI automatically.

### Step 2: Authenticate

Authentication is automatic. First API call opens browser for Google/Apple sign-in.

```bash
python kallyai.py login         # Force re-auth
python kallyai.py logout        # Clear credentials
python kallyai.py auth-status   # Check login
```

### Step 3: Execute

**Natural language (preferred):**
```bash
python kallyai.py ask "Reserve a table for 4 at 8pm at Nobu"
```

**Direct commands (when you know the domain):**
```bash
python kallyai.py calls make -p "+15551234567" -t "Reserve table for 4 at 8pm"
python kallyai.py actions calendar create --title "Dinner" --start "2026-02-14T20:00"
python kallyai.py search run "best Italian restaurant downtown"
python kallyai.py inbound calls --status completed
python kallyai.py phone list
```

### Step 4: Monitor & Follow Up

```bash
# Check goal status
python kallyai.py coord goals --status active
python kallyai.py coord goal <GOAL_ID>

# Review outbound call results
python kallyai.py calls history
python kallyai.py calls info <CALL_ID>
python kallyai.py calls transcript <CALL_ID>

# Review inbound calls handled by AI receptionist
python kallyai.py inbound calls
python kallyai.py inbound call <CALL_ID>
python kallyai.py inbound transcript <CALL_ID>

# Check inbox for responses
python kallyai.py messages inbox --unread
```

---

## Domain Command Reference

### `ask` — Natural Language (80% of usage)

```bash
python kallyai.py ask "Your request in plain English"
```

Routes through coordination AI. Creates goals, makes calls, sends emails — whatever is needed.

### `coord` — Coordination & Goals

```bash
coord message "text"           # Chat with coordination AI
coord goals [--status X]       # List goals
coord goal <id>                # Goal details
coord goal-tree <id>           # Goal + sub-goals
coord cancel-goal <id>         # Cancel goal
coord cascade-cancel <id>      # Cancel goal + sub-goals
coord escalate <id>            # Escalate for attention
coord approve-step <id>        # Approve next step
coord accept <id>              # Accept outcome
coord continue <id>            # Continue negotiating
coord archive <id>             # Archive goal
coord batch-archive <id>...    # Archive multiple
coord budget <id>              # Goal budget details
coord history                  # Conversation history
coord conversations            # List conversations
coord new                      # New conversation
```

### `calls` — Outbound Phone Calls

```bash
calls make -p "+1..." -t "task"  # Make a call
calls history                     # List calls
calls info <id>                   # Call details
calls transcript <id>             # Transcript
calls recording <id>              # Recording URL
calls calendar <id>               # Calendar .ics
calls cancel <id>                 # Cancel call
calls reschedule <id>             # Reschedule
calls stop <id>                   # Stop active call
```

### `inbound` — AI Receptionist (Incoming Calls)

```bash
inbound calls [--status X]          # List incoming calls
inbound call <id>                    # Call details
inbound transcript <id>              # Call transcript
inbound recording <id>               # Call recording
inbound summary                      # Incoming call summary/stats
inbound analytics [--from X --to X]  # Call analytics
inbound transfer <id> --to "+1..."   # Transfer call
inbound takeover <id>                # Take over live call
inbound reject <id> [--reason X]     # Reject call
inbound rules                        # List routing rules
inbound add-rule --name "..." --action "..." # Create rule
inbound update-rule <id> ...         # Update rule
inbound delete-rule <id>             # Delete rule
inbound voicemails                   # List voicemails
inbound voicemail <id>               # Voicemail details
inbound voicemail-playback <id>      # Voicemail audio
inbound contacts                     # List contacts
inbound add-contact --name "..." --phone "+1..." # Add contact
inbound update-contact <id> ...      # Update contact
inbound delete-contact <id>          # Delete contact
inbound import-contacts <file>       # Import contacts
inbound events [--from X --to X]     # Event log
```

### `phone` — Phone Number Management

```bash
phone list                           # List your numbers
phone info <id>                      # Number details
phone countries                      # Supported countries
phone available --country US         # Search available numbers
phone provision --country US         # Provision new number
phone forwarding <id> --target "+1..." # Set call forwarding
phone remove-forwarding <id>         # Remove forwarding
phone verify-start <number>          # Start verification
phone verify-check <number> --code X # Check verification code
phone caller-id <id> --name "..."    # Set caller ID
phone release <id>                   # Release number
```

### `actions` — Autonomous Actions

```bash
actions calendar create --title "..." --start "..."
actions calendar slots [--date X]
actions calendar sync
actions calendar delete <id>
actions restaurant search "query" [--location X]
actions booking create --type restaurant [--date X]
actions booking cancel <id>
actions bill analyze "description" [--amount X]
actions bill dispute "description" [--reason X]
actions ride --pickup "..." --destination "..."
actions food "order description" [--address X]
actions errand "errand description"
actions email send --to "..." --subject "..." "body"
actions email approve <id>
actions email cancel <id>
actions email outbox
actions email replies <id>
actions log [--type X]
actions undo <id>
```

### `messages` — Unified Inbox

```bash
messages inbox [--channel email|sms|call|chat] [--unread]
messages read <id>
messages thread <conversation_id>
messages mark-read <id> [<id>...]
```

### `search` — Research

```bash
search run "query" [--location X]
search quick "query"
search history
search sources
```

### `email` — Email Account Management

```bash
email accounts                          # List connected
email connect gmail|outlook             # Connect provider
email disconnect <id>                   # Disconnect
email list [--classification important] # List messages
email read <id>                         # Read email
email respond <id> [instructions]       # Respond
email voice-profile                     # Get voice profile
email train-voice                       # Train from samples
```

### `channels` — Multi-Channel Management

```bash
channels status                  # All channel statuses
channels email-add <address>     # Add email contact
channels email-list              # List email contacts
channels email-update <id> ...   # Update email contact
channels email-delete <id>       # Delete email contact
channels email-verify <token>    # Verify email
channels mailbox                 # Get KallyAI mailbox address
channels connect <channel>       # Connect WhatsApp/Telegram
channels test <channel>          # Test channel connection
channels disconnect <channel>    # Disconnect channel
```

### `outreach` — Multi-Channel Outreach

```bash
outreach tasks [--status X]      # List outreach tasks
outreach task <id>               # Task details
outreach create --channel call --target "+1..." "description"
outreach retry <id>              # Retry failed task
outreach cancel <id>             # Cancel task
```

### `budget` — Cost Management

```bash
budget estimate --type call "description"
budget approve <goal_id>
budget breakdown <goal_id>
budget ack-cap <goal_id>
```

### `credits` — Balance & Usage

```bash
credits balance     # Current balance (credits, NOT minutes)
credits history     # Usage history
credits breakdown   # Spending breakdown by action type
credits costs       # Credit cost reference
credits plans       # Available credit plans
```

### `subscription` — Plan Management

```bash
subscription status               # Current plan status
subscription change-plan <plan>   # Change to new plan
subscription cancel-change        # Cancel pending plan change
```

### `referrals` — Referral Program

```bash
referrals code        # Get your referral code
referrals stats       # Referral statistics
referrals history     # Referral history
```

### `notifications` — Notifications

```bash
notifications pending   # Check pending notification counts
```

---

## Output Format

Default output is **JSON** (machine-readable for Claude Code). Add `--human` for formatted tables.

```bash
python kallyai.py credits balance              # JSON
python kallyai.py credits balance --human      # Pretty table
```

## Backward Compatibility

Old flags still work — they map to new subcommands:

```bash
python kallyai.py --phone "+1..." --task "..."   → calls make
python kallyai.py --usage                         → credits balance
python kallyai.py --history                       → calls history
python kallyai.py --call-info ID                  → calls info ID
python kallyai.py --transcript ID                 → calls transcript ID
```

---

## Security

- Tokens stored in `~/.kallyai_token.json` with 0600 permissions
- Only localhost redirect URIs accepted for CLI auth
- CSRF protection via `state` parameter
- Tokens expire after 1 hour, auto-refresh supported

## Common Errors

| Code | HTTP | Action |
|------|------|--------|
| `quota_exceeded` | 402 | User needs more credits — kallyai.com/pricing |
| `missing_phone_number` | 422 | Ask user for phone number |
| `emergency_number` | 422 | Cannot call emergency services |
| `country_restriction` | 403 | Country not supported |
| `budget_exceeded` | 402 | Goal over budget — approve or cancel |
| `email_not_connected` | 400 | Need to connect email account first |
| `phone_not_provisioned` | 400 | Need to provision a phone number first |

## Full API Reference

See [references/api-reference.md](references/api-reference.md) for complete endpoint documentation.
