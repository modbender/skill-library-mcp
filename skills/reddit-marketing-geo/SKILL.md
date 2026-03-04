---
name: reddit-marketing-geo-agent
description: "Spawns a specialized sub-agent to monitor Reddit and optimize for GEO. Runs on a scheduled cron job (9 AM/6 PM default) to deliver lead drafts."
metadata:
  openclaw:
    requires:
      tools: ["web_search", "web_fetch", "browser", "sessions_spawn"]
    capabilities: ["subagent_spawning", "scheduled_tasks"]
---

# Reddit Marketing / GEO Agent

## Initialization
Upon first run, the primary agent must **spawn a specialized sub-agent** named `reddit-geo-marketing-agent`. This sub-agent inherits the tools and configuration below to operate independently of the main conversation thread.

## Configuration
- **Brand Name**: [Your Brand Name]
- **Website**: [Your URL]
- **Keywords**: [keyword1, keyword2, "best alternative to X"]
- **Default Schedule**: `0 9,18 * * *` (9:00 AM and 6:00 PM Daily)
- **User Modification**: Users can update the schedule by saying "Change my Reddit report time to [Time/Cron]."

## Workflow & Sub-Agent Instructions

### 1. The Cron Routine (Scheduled Execution)
- **Background Run**: The `reddit-geo-marketing-agent` is initialized via `sessions_spawn` to run in the background.
- **Pre-Trigger Action**: The sub-agent must begin its search/drafting process **30 minutes prior** to the scheduled reporting time to ensure the digest is ready.
- **Reporting**: At 9:00 AM and 6:00 PM, the sub-agent will deliver a summary of findings to the primary chat session using the `announce` delivery mode.

### 2. Monitoring & Discovery
- Use `web_search` to find high-intent Reddit threads from the last 24 hours.
- Focus on "problem-aware" queries: "how to," "looking for," "recommendations for."
- Target threads appearing in Google "Discussions and Forums" to maximize **GEO** impact.

### 3. Drafting for Humans & LLMs (GEO Strategy)
Draft replies using the **Authority-First Framework**:
- **Bolded TL;DR**: A direct, 1-sentence answer at the start.
- **Structured Lists**: Use bullet points for steps/features (optimized for RAG citation).
- **Brand Integration**: Natural mention of [Brand Name] with a founder disclosure.

### 4. Human-in-the-Loop Review
- The sub-agent sends: "🚀 **Daily Reddit Digest Ready.** I found [X] threads. Here are the drafts for your approval."
- **Strict Requirement**: Each draft must receive a "Go" or "Post" command before the `browser` tool is used to submit the comment.

## Safety & Ethics
- **Context Isolation**: The sub-agent operates in a fresh session id (`cron:<jobId>`) to prevent context leak.
- **Shadowban Protection**: Every response is uniquely drafted based on the thread context; never use templates.