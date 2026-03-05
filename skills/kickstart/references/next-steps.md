# Next Steps — Growing Beyond Kickstart

You've got the foundation. Here's how to scale your agent's capabilities progressively.

---

## Phase 1: Channel Skills (Week 1-2)

Create one skill per communication channel. Each channel gets its own permanent context — the skill tells your agent what that channel is for and how to behave in it.

### Why
Without channel skills, your agent treats every channel the same. With them, it knows #finances is for budget tracking and #work is for project management — different tools, different tone, different rules.

### How
```
skills/
├── finances/SKILL.md      → Budget tracking, debt, income analysis
├── work-project/SKILL.md  → Project-specific context, tasks, blockers
├── lifestyle/SKILL.md     → Health, fitness, routines, reading
└── creative/SKILL.md      → Design, branding, creative projects
```

Map channels to skills in your OpenClaw config:
```json
{
  "channels": {
    "discord": {
      "guilds": {
        "YOUR_GUILD_ID": {
          "channels": {
            "CHANNEL_ID": { "skill": "finances" }
          }
        }
      }
    }
  }
}
```

---

## Phase 2: Project Skills (Week 2-4)

For any project that lasts more than a few days, create a dedicated skill with references.

### Structure
```
skills/my-project/
├── SKILL.md              → What the project is, how to work on it
└── references/
    ├── architecture.md   → Technical decisions, stack, structure
    ├── todo.md           → Current tasks and priorities
    └── people.md         → Key contacts and their roles
```

### When to Create
- Starting a new side project
- Taking on a new client
- Beginning a multi-week initiative
- Any work that needs persistent context across sessions

---

## Phase 3: Automation Skills (Week 4+)

Build skills that run autonomously — scanners, digesters, monitors.

### Examples
- **Content scanner** — Monitors X/Reddit/news, generates daily digest
- **Project monitor** — Checks CI/CD, deployment status, error logs
- **Finance tracker** — Scans bank feeds, categorises expenses
- **Social scheduler** — Plans and queues content across platforms

### Pattern
1. Build the skill with manual triggers first
2. Test it works reliably
3. Add a cron job to run it automatically
4. Monitor for a week before trusting it fully

---

## Phase 4: Integration Skills (Ongoing)

Connect your agent to external services for deeper capabilities.

### High-Value Integrations
- **Email processing** — Summarise, draft replies, flag urgent
- **Calendar management** — Schedule, remind, prep for meetings
- **Code review** — Auto-review PRs, suggest improvements
- **Data pipelines** — ETL from APIs, generate reports
- **Content creation** — Draft posts, generate images, schedule

### Build vs Install
- Check ClawHub first: `npx clawhub search "what you need"`
- If a skill exists and is well-rated, install it
- If nothing fits, build your own using the skill-creator patterns

---

## Scaling Principles

1. **One thing at a time.** Don't build 10 skills simultaneously. Get one solid, then move on.
2. **Manual before automatic.** Test every workflow manually before adding cron automation.
3. **Monitor everything.** Check cron run history regularly. Failing silently is worse than failing loudly.
4. **Prune ruthlessly.** Disable skills and crons you're not using. They eat context and create noise.
5. **Document as you go.** Future-you (and future sessions of your agent) will thank you.

---

## Community Resources

- **ClawHub:** `npx clawhub explore` — Browse community skills
- **OpenClaw Docs:** docs.openclaw.ai — Official documentation
- **OpenClaw Discord:** discord.com/invite/clawd — Community support
- **OpenClaw GitHub:** github.com/openclaw/openclaw — Source and issues
