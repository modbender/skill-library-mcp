---
name: community-intel
description: Automated community intelligence gathering for any open-source project or product. Searches Reddit, Hacker News, Twitter/X, GitHub, and YouTube for mentions, use cases, tips, complaints, and trends. Compiles findings into structured reports. Use when you want to monitor community sentiment, track adoption, discover use cases, or stay on top of ecosystem developments around a project.
---

# Community Intel

Automated community intelligence gathering and trend monitoring for open-source projects and products.

## Requirements

- Web search and fetch capabilities (`web_search`, `web_fetch` tools)
- Optional: Discord channel for posting reports (`message` tool)
- Optional: Email integration for delivering reports (AgentMail, Resend, or any email skill)

## How It Works

Run as a nightly or weekly cron job. The agent searches multiple platforms for mentions of a target project/product, reads full threads, and compiles a structured intelligence report. Over time, it learns which sources are productive and adjusts accordingly.

## Configuration

Set these in your cron message or workspace config:

```yaml
PROJECT_NAME: "YourProject"
SEARCH_TERMS: ["yourproject", "your-project", "YourProject"]
SUBREDDITS: ["r/yourproject", "r/selfhosted", "r/programming"]
INTEL_FILE: "memory/project-intel.md"       # cumulative findings log
DISCORD_CHANNEL: ""                          # optional: channel ID for posting
EMAIL_TO: ""                                 # optional: email for delivery
```

## Research Sources

### Primary (search every run)
| Source | What to search | Best for |
|--------|---------------|----------|
| **Reddit** | Project subreddit + related subs | Use cases, complaints, tips |
| **Hacker News** | `site:news.ycombinator.com` + project name | Technical discussion, launches |
| **GitHub** | Issues, discussions, new repos | Bug reports, feature requests, forks |
| **Twitter/X** | Project name + hashtags | Viral moments, announcements |

### Secondary (rotate or check weekly)
| Source | What to search | Best for |
|--------|---------------|----------|
| **YouTube** | Project name + "tutorial" / "review" | Adoption trends, developer content |
| **Blog posts** | Medium, Substack, dev.to | Deep dives, experience reports |
| **Product Hunt** | Launches building on the project | Ecosystem growth |
| **Academic papers** | ArXiv, Google Scholar | Research using/studying the project |

## OpenClaw Cron Setup

Add via CLI:

```bash
openclaw cron add \
  --name "Community Intel" \
  --schedule "45 22 * * *" \
  --tz "America/Chicago" \
  --session-target isolated \
  --timeout 600 \
  --message "$(cat <<'EOF'
You are doing community research for [PROJECT_NAME].

Search for mentions across Reddit, Twitter/X, Hacker News, GitHub, and YouTube.
Look for: interesting use cases, creative integrations, tips and tricks,
new tools, complaints, security issues, and feature requests.

Steps:
1. Read [INTEL_FILE] for context on past findings and best sources
2. Search each platform for [SEARCH_TERMS]
3. Go deep -- read full threads, follow links, check comments
4. Compile findings into a structured summary
5. Append findings to [INTEL_FILE] with today's date and run number
6. Post summary to Discord channel [DISCORD_CHANNEL] (if configured)
7. Rate each source 1-3 stars based on today's yield

Be thorough. Quality over speed. If a source has nothing new, note that
so we can deprioritize it over time.
EOF
)"
```

Or add via `config.patch`:

```json
{
  "cron": [{
    "name": "Community Intel",
    "schedule": "45 22 * * *",
    "tz": "America/Chicago",
    "sessionTarget": "isolated",
    "timeout": 600,
    "message": "You are doing community research for [PROJECT_NAME]..."
  }]
}
```

## Report Format

Each run produces a report in this structure:

```markdown
### YYYY-MM-DD (run N) -- Research Run

**Headline:** [one-line summary of biggest findings]

**🔥 Cool Use Cases**
- [Description with source link]

**💡 Tips & Tricks**
- [Practical discovery with details]

**🛠️ New Tools / Integrations**
- [New project, tool, or integration discovered]

**📢 Community Buzz**
- [Sentiment, complaints, praise, trends]

**🔒 Security / Risks**
- [Any security findings, vulnerabilities, concerns]

**📊 Source Quality**
- Reddit: ⭐⭐⭐ (active discussions)
- HN: ⭐⭐ (one thread)
- Twitter: ⭐ (quiet day)
- YouTube: ⭐⭐⭐ (new tutorials)
```

## Intel File Structure

Maintain a cumulative intel file (`INTEL_FILE`) with three sections:

```markdown
# [PROJECT_NAME] Intel

## Best Sources (updated YYYY-MM-DD, run N)
- **Reddit** ⭐⭐⭐ -- Active community, good use cases
- **Hacker News** ⭐⭐ -- Occasional deep technical threads
- **GitHub** ⭐⭐ -- Steady issue flow
- **Twitter/X** ⭐ -- Mostly retweets, low signal
- **YouTube** ⭐⭐⭐ -- Tutorial explosion lately

## Community Resources Discovered
- [tool-name](url) -- Description
- [directory-site](url) -- Curated list of projects

## Findings Log
### YYYY-MM-DD (run N)
... (newest first, oldest at bottom)
```

The agent reads this file at the start of each run to:
- Know which sources to prioritize
- Avoid reporting duplicate findings
- Track trends over time ("X was a complaint in run 5, fixed by run 12")

## Research Techniques

**Search query patterns that work well:**
- `"project-name" site:reddit.com` -- Reddit mentions
- `"project-name" site:news.ycombinator.com` -- HN threads
- `"project-name" tutorial OR guide OR setup` -- How-to content
- `"project-name" vs OR alternative OR competitor` -- Competitive landscape
- `"project-name" security OR vulnerability OR CVE` -- Security issues
- `"project-name" after:YYYY-MM-DD` -- Only recent results

**Reading threads effectively:**
- Don't stop at the title. The real insights are in comment replies.
- Look for upvote counts -- high-upvote comments often contain the most useful info.
- Check who's commenting. Maintainers, power users, and industry people carry more signal.
- Note when the same complaint appears across multiple platforms -- that's a real issue.

## Tips

- **Quality over speed.** Read full threads, don't just skim titles.
- **Track source quality.** Rate each source 1-3 stars per run. Deprioritize sources that consistently yield nothing.
- **Note sentiment shifts.** "People used to complain about X, now they praise it" is valuable signal.
- **Flag security issues immediately.** Don't wait for the next scheduled run.
- **Keep the findings log trimmed.** Archive entries older than 30 days to a separate file to keep the intel file under 100KB.
- **Search variations.** Try the project name with and without hyphens, abbreviations, and common misspellings.
- **Track run numbers.** Increment each run so you can reference "this was first spotted in run 14" for trend tracking.
