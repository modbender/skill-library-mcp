---
name: clawhub-skill-stats
description: "Query any ClawHub skill's statistics (stars, downloads, current installs, all-time installs) via curl and the public ClawHub API. Use when: user asks about a skill's popularity, stats, or metrics on ClawHub, wants to compare skill statistics, or needs to check how many stars/downloads/installs a ClawHub skill has — without opening the slow ClawHub web UI."
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["curl", "python3"] },
      },
  }
---

# ClawHub Skill Stats

Query skill statistics from the ClawHub public API using curl.

## Single Skill Query

Run this command, replacing `SKILL_SLUG` with the skill's slug:

```bash
curl -s "https://clawhub.ai/api/skill?slug=SKILL_SLUG" | python3 -c "
import sys, json
data = json.load(sys.stdin)
skill = data.get('skill', {})
stats = skill.get('stats', {})
owner = data.get('owner', {})
print('=== ClawHub Skill Stats ===')
print(f'Skill:  {skill.get(\"displayName\", skill.get(\"slug\", \"Unknown\"))}')
print(f'Author: {owner.get(\"handle\", owner.get(\"displayName\", \"Unknown\"))}')
print(f'Desc:   {skill.get(\"summary\", \"No description\")}')
print('---')
print(f'Stars:             {stats.get(\"stars\", \"N/A\")}')
print(f'Downloads:         {stats.get(\"downloads\", \"N/A\")}')
print(f'Current Installs:  {stats.get(\"installsCurrent\", \"N/A\")}')
print(f'All-time Installs: {stats.get(\"installsAllTime\", \"N/A\")}')
print(f'Comments:          {stats.get(\"comments\", \"N/A\")}')
print(f'Versions:          {stats.get(\"versions\", \"N/A\")}')
"
```

The slug is the last segment of a ClawHub URL: `https://clawhub.ai/{owner}/{slug}` → use `{slug}`.

## Batch Compare

```bash
for slug in "SLUG_1" "SLUG_2" "SLUG_3"; do
  curl -s "https://clawhub.ai/api/skill?slug=$slug" | python3 -c "
import sys, json
data = json.load(sys.stdin)
skill = data.get('skill', {})
stats = skill.get('stats', {})
owner = data.get('owner', {})
name = skill.get('displayName', skill.get('slug', 'Unknown'))
author = owner.get('handle', 'Unknown')
print(f'{name} (@{author}): Stars {stats.get(\"stars\",0)} | Downloads {stats.get(\"downloads\",0)} | Current {stats.get(\"installsCurrent\",0)} | All-time {stats.get(\"installsAllTime\",0)}')
"
done
```

## Search by Keyword

If the slug is unknown, search first:

```bash
curl -s "https://clawhub.ai/api/search?q=SEARCH_TERM" | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', [])
if not results:
    print('No results found.')
else:
    for r in results[:10]:
        sk = r if 'stats' in r else r.get('skill', r)
        s = sk.get('stats', {})
        print(f'{sk.get(\"slug\",\"?\")} — Stars {s.get(\"stars\",0)} | Downloads {s.get(\"downloads\",0)} | Current {s.get(\"installsCurrent\",0)}')
"
```

## Notes

- API is public, no auth needed.
- Endpoint: `GET https://clawhub.ai/api/skill?slug={slug}`
- Response: `{ "skill": { "stats": { "stars", "downloads", "installsCurrent", "installsAllTime", "comments", "versions" } }, "owner": { "handle" } }`
