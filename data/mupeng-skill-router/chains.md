# Skill Chain Templates

Collection of frequently used skill combination pipelines. Templates for handling complex requests efficiently.

---

## 1. Content Full Pipeline

**Name**: content-full-pipeline  
**Trigger**: "create content", "make a post", "create for Instagram"

**Description**: Full content creation pipeline from idea to Instagram publish

**Steps**:
1. **seo-content-planner** — Keyword research + content topic selection
2. **copywriting** — SEO-optimized text creation
3. **cardnews** — Card news image generation (1:1 square)
4. **insta-post** — Instagram upload (requires approval)

**Output**: Instagram post URL + performance tracking start

---

## 2. Competitor Analysis Report

**Name**: competitor-research-report  
**Trigger**: "analyze competitors and report", "do market research"

**Description**: Monitor competitor trends, generate organized report and send email

**Steps**:
1. **competitor-watch** — Crawl competitor websites/SNS + detect changes
2. **daily-report** — Convert analysis results into structured report
3. **mail** — Send report email (requires approval)

**Output**: Report MD file + email sent confirmation

---

## 3. Video→Content Conversion

**Name**: video-to-content  
**Trigger**: "summarize this video into card news", "create content from YouTube video"

**Description**: Summarize YouTube video and repackage as card news

**Steps**:
1. **yt-digest** — YouTube video download + subtitle extraction + summary
2. **content-recycler** — Restructure summary into short sentences for card news
3. **cardnews** — Generate card news images
4. **insta-post** — Instagram upload (requires approval)

**Output**: Card news image set + Instagram post

---

## 4. Weekly Comprehensive Review

**Name**: weekly-review  
**Trigger**: "weekly review", "summarize this week", "week summary"

**Description**: Comprehensive weekly report with performance, costs, and reflections

**Steps** (parallel execution):
1. **self-eval** — Analyze last week's mistakes/improvements
2. **tokenmeter** — Weekly token usage + cost aggregation
3. **performance-tracker** — Content performance analysis (likes/comments/views)

**Steps** (sequential execution):
4. **daily-report** — Generate weekly report integrating above 3 results

**Output**: weekly-review-YYYY-MM-DD.md

---

## 5. Content Recycling

**Name**: content-recycle  
**Trigger**: "recycle content", "rewrite successful post"

**Description**: Find high-performing content and repackage in new format

**Steps**:
1. **performance-tracker** — Extract content with most likes/comments in last 30 days
2. **content-recycler** — Rewrite popular content from different angle/format
3. **cardnews** — Generate new card news

**Output**: Repackaged content + card news images

---

## 6. Idea→Action

**Name**: idea-to-action  
**Trigger**: "review idea and execute", "brainstorm and do it now"

**Description**: Review idea, establish execution plan, and execute immediately

**Steps**:
1. **think-tank** (brainstorm mode) — Idea generation + feasibility review
2. **decision-log** — Record decisions (why this direction was chosen)
3. **skill-composer** — Auto-compose skill combination matching execution plan

**Output**: Execution result + decision-log update

---

## 7. Market Research Full Analysis

**Name**: market-research  
**Trigger**: "market research", "industry trends"

**Description**: Integrated market research through competitors + trends + data collection

**Steps** (parallel execution):
1. **competitor-watch** — Monitor competitor websites
2. **trend-radar** — Google Trends + social trends analysis
3. **data-scraper** — Collect related statistical data

**Steps** (sequential execution):
4. **daily-report** — Organize all research results into integrated report

**Output**: market-research-YYYY-MM-DD.md

---

## 8. Safe Release

**Name**: safe-release  
**Trigger**: "release", "deploy", "push to production"

**Description**: Code review → Git commit → deployment checklist verification

**Steps**:
1. **code-review** — Review code changes + risk assessment
2. **git-auto** — Commit + push (only if code-review passes)
3. **release-discipline** — Verify pre-deployment checklist (DB migration, env vars, etc.)

**Safety Measures**:
- If code-review detects HIGH severity → block commit + notification-hub
- Final approval required

**Output**: Git commit hash + deployment checklist completion confirmation

---

## 9. Morning Routine

**Name**: morning-routine  
**Trigger**: "morning routine", "start today", cron (daily 09:00)

**Description**: Check system status + costs + notifications and summary report

**Steps** (parallel execution):
1. **health-monitor** — System health check (disk, memory, API status)
2. **tokenmeter** — Verify yesterday/this month token usage
3. **notification-hub** — Collect unread notifications

**Steps** (sequential execution):
4. **daily-report** — Generate morning summary report

**Output**: morning-brief-YYYY-MM-DD.md + Discord DM

---

## 10. Urgent Alert Chain

**Name**: urgent-alert  
**Trigger**: Auto-chain rules (when specific events detected)

**Description**: Immediate notification when important events occur

**Auto Trigger Conditions**:
- tokenmeter exceeds $500/month
- code-review detects HIGH severity
- health-monitor detects system anomaly
- mail detects important email

**Steps**:
1. **notification-hub** (urgent priority) — Send Discord DM immediately
2. **daily-report** — Record event log

**Output**: Immediate notification + log record

---

## Chain Execution Rules

### Parallel vs Sequential
- **Parallel execution**: Skills with no dependencies (use sessions_spawn)
- **Sequential execution**: When next skill needs previous skill's result

### Data Transfer
- Data between skills saved as JSON events in `events/` folder
- Each skill saves results in `events/latest-{skill-name}.json` format
- Next skill reads that file as input

### Error Handling
- Skill failure mid-chain → save partial results + notification-hub alert
- Timeout during approval wait (1 hour) → auto-cancel + notification
- Same chain executed 3 times detected → prevent infinite loop, stop

---

> 🐧 Built by **무펭이** — [Mupengism](https://github.com/mupeng) ecosystem skill
