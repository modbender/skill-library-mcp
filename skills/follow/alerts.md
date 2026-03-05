# Alert Configuration

## Tiers

| Tier | Meaning | Delivery |
|------|---------|----------|
| **Immediate** | Drop everything | Push notification now |
| **Daily** | Important but not urgent | Morning digest |
| **Weekly** | Nice to know | Weekly summary |
| **Passive** | Logged only | Query when curious |

---

## Configuring Tiers

In `~/follow/alerts.md`:

```markdown
## Immediate Alerts
- @naval posts thread (not single tweets)
- Any source mentions "acquisition" + company in watchlist
- Security advisory for tech in my stack
- Insider selling >$1M

## Daily Digest
- New posts from high-priority sources
- Topics I track get >3 mentions
- Competitor launches campaign

## Weekly Summary
- Trends across all sources
- New sources discovered
- Content I might have missed

## Passive (log only)
- Routine updates from casual follows
- Retweets, likes, minor activity
```

---

## Trigger Examples

### Person-based
- `@person posts` — any content
- `@person posts about [topic]` — filtered
- `@person goes silent for 7 days` — unusual pattern
- `@person appears on podcast` — guest appearance

### Topic-based
- `[topic] mentioned by 3+ sources` — convergence
- `[topic] + [company]` — intersection
- `[topic] sentiment shift` — narrative changing

### Event-based
- `[company] files SEC form` — regulatory
- `[repo] releases new version` — technical
- `[person] changes job` — LinkedIn signal

---

## Digest Format

### Daily Digest
```
## Follow Digest — Feb 13

### 🔴 High Priority
- @naval: New thread on AI and leverage (12 tweets)
- Competitor X: Pricing page changed (diff attached)

### 📊 Updates
- 3 sources discussed "AI agents" yesterday
- New episode: @lexfridman with @sama

### 📁 Logged
- 14 items archived, nothing urgent
```

### Weekly Summary
- Trends: What topics dominated?
- Gaps: Sources that went quiet
- Recommendations: Suggested new follows
- Stats: X items captured, Y alerts sent
