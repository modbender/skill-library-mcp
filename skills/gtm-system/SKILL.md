# GTM Tracking System Skill

A Go-To-Market tracking system for Expanso/Prometheus.

## Location
`/home/daaronch/.openclaw/workspace/gtm-system/`

## CLI Tool
`python3 /home/daaronch/.openclaw/workspace/gtm-system/scripts/gtm.py [command]`

## Quick Commands

### Daily Operations
```bash
# Get today's actions and priorities
python3 scripts/gtm.py actions

# Generate digest for Telegram
python3 scripts/gtm.py digest

# View pipeline
python3 scripts/gtm.py pipeline

# List unprocessed signals
python3 scripts/gtm.py signals
```

### Contact Management
```bash
# Add a contact
python3 scripts/gtm.py add-contact "Name" "email@co.com" --company "Company" --role "CTO"

# List contacts
python3 scripts/gtm.py contacts
```

### Opportunity Management
```bash
# Create opportunity
python3 scripts/gtm.py add-opp "Company Name" --contact 1 --description "Interested in Bacalhau" --priority 3

# Move stage (awareness → interest → evaluation → negotiation → closed_won/closed_lost)
python3 scripts/gtm.py move-stage 1 evaluation

# Log an interaction
python3 scripts/gtm.py log "Had demo call, very interested" --opp 1
```

### Reminders
```bash
# Set a reminder
python3 scripts/gtm.py remind "Send pricing proposal" --opp 1 --date 2024-02-15

# Complete a reminder
python3 scripts/gtm.py complete 1
```

### Crawling
```bash
# Run all crawlers (HN, Reddit, GitHub)
python3 scripts/gtm.py crawl

# Run specific crawlers
python3 scripts/gtm.py crawl --sources hn,github

# Mark signal as processed
python3 scripts/gtm.py process-signal 1
```

### Keywords
```bash
# Add a tracking keyword
python3 scripts/gtm.py add-keyword "new-keyword" --category domain --weight 1.5
```

## Pipeline Stages
1. `awareness` - They know we exist
2. `interest` - Showed interest, had initial contact
3. `evaluation` - Actively evaluating, demos, trials
4. `negotiation` - Discussing terms/pricing
5. `closed_won` - Deal closed successfully
6. `closed_lost` - Deal lost

## Database Location
`/home/daaronch/.openclaw/workspace/gtm-system/data/gtm.db` (SQLite)

## Natural Language Queries
When user asks about GTM/pipeline/opportunities, use the CLI to fetch data and summarize:
- "What's in my pipeline?" → Run `pipeline` command
- "Any follow-ups today?" → Run `actions` command
- "Add a contact..." → Use `add-contact` command
- "Check for new opportunities" → Run `crawl` then `signals`
