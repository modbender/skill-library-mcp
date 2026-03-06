# Reddit Marketing / GEO Agent

An OpenClaw skill that automates brand authority building on Reddit. It spawns a background sub-agent to monitor discussions and optimize your mentions for **Generative Engine Optimization (GEO)**, ensuring your product is cited by AI engines like Perplexity and Gemini.

## Features
- **Sub-Agent Spawning**: Operates as a background process (`reddit-geo-marketing-agent`) so your main chat remains clutter-free.
- **Automated Scheduling**: Default delivery at **9:00 AM and 6:00 PM**. The agent starts preparing its report 30 minutes early so it's ready exactly on time.
- **GEO Optimized**: Formats replies specifically to be picked up by LLM scrapers using structured data and bolded summaries.
- **Natural Language Config**: Change your report times or keywords just by talking to the bot.

## Installation
1. Move the `reddit-marketing-geo-agent` folder to your `~/.openclaw/skills/` directory.
2. Ensure `sessions_spawn` and `browser` tools are enabled in your `openclaw.json`.
3. Restart your OpenClaw gateway.

## Configuration
When first installed, the agent will interview you for your **Brand Name**, **URL**, and **Target Keywords**. 

### Changing the Schedule
To modify the cron job, simply tell the agent:
- *"Change my Reddit report time to 10 AM daily."*
- *"I want reports only at 8 PM."*

## How it Works
The skill uses OpenClaw's internal cron system to trigger a background session. It "wakes up" before the scheduled time, performs a deep web search for Reddit threads, analyzes them via the browser, and drafts a daily digest for your approval.

## Author
Muhammed Ilyasy
[ilyasy.com](https://ilyasy.com)