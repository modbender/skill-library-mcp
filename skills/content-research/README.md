# Content Research Skill

An [OpenClaw](https://openclaw.ai) skill for researching trending topics and generating platform-specific content.

## What It Does

**Phase 1: Research**
- Searches for recent news on any topic (DuckDuckGo or Brave API)
- Fetches and extracts article content
- Filters to last 7 days, removes fluff
- Presents top findings with summaries

**Phase 2: Content Creation**
- Generate 5 different angles for any platform
- Supports Reddit, X/Twitter, Discord, LinkedIn
- Optional brand voice configuration
- Ready-to-post output

## Installation

### Via ClawHub (Recommended)
```bash
clawhub install content-research
```

### Manual
Copy the `SKILL.md` file to your OpenClaw skills directory:
```bash
cp SKILL.md ~/.openclaw/skills/content-research/SKILL.md
```

## Usage

```
research [topic]           # Find recent news
what's new in [topic]      # Same thing
#3 for reddit              # Generate Reddit content for finding #3
create content for twitter # Generate Twitter content
```

### Example Session

```
You: research AI agents

Agent: ## AI Agents Research — Feb 16, 2026

1. **Anthropic launches Claude 4** - TechCrunch - 2 days ago
   Major upgrade with improved reasoning...

2. **OpenAI GPT-5 rumors** - The Verge - 4 days ago
   Sources suggest...

You: 1 for reddit

Agent: [5 Reddit post angles]

You: angle 2

Agent: [Ready-to-copy Reddit post]
```

## Brand Configuration

For branded content, create `brand-config.md` in your workspace:

```markdown
# Brand: Acme Corp

## Voice
- Professional but approachable
- Data-driven claims only
- Never overpromise

## Avoid
- "Revolutionary" or "game-changing"
- Competitor comparisons
- Unverified claims

## Include
- Links to documentation
- Acknowledge limitations
```

See `examples/brand-config.md` for a full template.

## Platform Support

| Platform | Formats | Angles |
|----------|---------|--------|
| Reddit | Post, Comment | News, Discussion, Analysis, ELI5, Contrarian |
| X/Twitter | Tweet, Thread | Breaking, Hot take, Thread, Quote, Meme |
| Discord | Message, Thread | Alert, Summary, Discussion, Thread, Meme |
| LinkedIn | Post | Insight, Lessons, Prediction, Career, Case study |

## Requirements

- [OpenClaw](https://openclaw.ai) v2024.2.0+
- Browser automation OR Brave Search API key (optional)

## License

MIT
