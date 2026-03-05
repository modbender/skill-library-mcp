# Pocket AI Usage Examples

## Quick Queries (Copy-Paste Ready)

### 1. What action items do I have?
```bash
API_KEY=$(cat ~/.config/pocket-ai/api_key)
curl -s -X POST -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d '{"query": "action items tasks todo follow up"}' \
  "https://public.heypocketai.com/api/v1/public/search" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'• {l.split(\"Action item:\")[1].strip()}') for m in d.get('data',{}).get('relevantMemories',[]) for l in m.get('content','').split('\n') if 'Action item:' in l]"
```

### 2. What did I discuss about your company?
```bash
curl -s -X POST -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d '{"query": "your company manufacturing team decisions"}' \
  "https://public.heypocketai.com/api/v1/public/search"
```

### 3. What's my current mental state / priorities?
```bash
curl -s -X POST -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d '{"query": "priorities focus frustrations challenges"}' \
  "https://public.heypocketai.com/api/v1/public/search" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'• {c[:150]}...') for c in d.get('data',{}).get('userProfile',{}).get('dynamicContext',[])[:5]]"
```

### 4. Find conversations with a specific person
```bash
curl -s -X POST -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d '{"query": "conversations with Dylan Acquisition.com"}' \
  "https://public.heypocketai.com/api/v1/public/search"
```

### 5. Get trading insights I've mentioned
```bash
curl -s -X POST -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d '{"query": "trading psychology patience discipline strategy"}' \
  "https://public.heypocketai.com/api/v1/public/search"
```

---

## Python Examples

### Get daily briefing data
```python
from pocket_api import PocketAI

pocket = PocketAI()
briefing = pocket.daily_briefing_data()

print("=== ACTION ITEMS ===")
for item in briefing["action_items"]:
    print(f"☐ {item}")

print("\n=== KEY DECISIONS ===")
for decision in briefing["key_decisions"]:
    print(f"📌 {decision['content'][:100]}...")

print("\n=== CURRENT FOCUS ===")
for insight in briefing["profile_insights"][:3]:
    print(f"• {insight}")
```

### Search for a topic
```python
from pocket_api import PocketAI

pocket = PocketAI()

# Find all discussions about team restructuring
results = pocket.search_topic("team restructuring firing hiring")

for memory in pocket.get_memories("team changes", limit=5):
    print(f"{memory['date']}: {memory['content'][:150]}...")
```

### Cross-reference with tasks
```python
from pocket_api import PocketAI

pocket = PocketAI()

# Get action items from recordings
recording_items = pocket.get_action_items()

# Compare with existing task list
existing_tasks = ["Print W-2 forms", "Review QuickBooks", "Schedule Charlene meeting"]

new_items = [item for item in recording_items if item not in existing_tasks]
print("NEW ACTION ITEMS FROM MEETINGS:")
for item in new_items:
    print(f"  ☐ {item}")
```

---

## Integration Patterns

### Heartbeat Check (every 4 hours)
```python
# During heartbeat, check for new action items
from pocket_api import PocketAI

pocket = PocketAI()
action_items = pocket.get_action_items()

urgent_keywords = ["urgent", "ASAP", "today", "immediately", "deadline"]
urgent_items = [
    item for item in action_items 
    if any(kw in item.lower() for kw in urgent_keywords)
]

if urgent_items:
    # Alert user about urgent items
    print("🚨 URGENT ACTION ITEMS:")
    for item in urgent_items:
        print(f"  • {item}")
```

### Athena Context Injection
```python
# Before Athena schedules, understand user bandwidth
from pocket_api import PocketAI

pocket = PocketAI()
profile = pocket.get_user_profile("busy schedule meetings workload")

# Check for administrative overload
overload_signals = [p for p in profile if "overload" in p.lower() or "swamped" in p.lower()]
if overload_signals:
    print("⚠️ User showing signs of overload - schedule carefully")
```

### Daily Briefing Generation
```python
from pocket_api import PocketAI
from datetime import datetime

pocket = PocketAI()

briefing = f"""
# Daily Briefing - {datetime.now().strftime('%Y-%m-%d')}

## Action Items from Recent Meetings
"""

for item in pocket.get_action_items()[:10]:
    briefing += f"- [ ] {item}\n"

briefing += "\n## Current Focus Areas\n"
for insight in pocket.get_user_profile()[:5]:
    briefing += f"- {insight}\n"

print(briefing)
```

---

## Common Queries by Category

### Business Operations
- `"your company entities streamlining strategy"`
- `"manufacturing team performance issues"`
- `"intercompany invoices setup"`
- `"QuickBooks accounting review"`

### Trading & Investing
- `"trading psychology rules discipline"`
- `"market timing patience strategy"`
- `"crypto positions decisions"`
- `"macro economic outlook"`

### Family & Personal
- `"family financial planning kids college"`
- `"529 Roth IRA investment"`
- `"hockey schedule games"`
- `"vehicle maintenance truck issues"`

### Team & People
- `"employee performance frustrations"`
- `"hiring firing team changes"`
- `"meetings scheduled with"`
- `"Charlene Adrienne Dylan conversations"`

### Administrative
- `"W-2 1099 tax documents"`
- `"license renewals deadlines"`
- `"administrative tasks overdue"`
- `"paperwork filing requirements"`
