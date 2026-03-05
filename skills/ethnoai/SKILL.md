---
name: uxr-observer
version: 2.0.0
description: >
  An embedded UX research skill that deeply studies how users interact with OpenClaw through
  passive ethnographic observation, structured micro-surveys, and retrospective task analysis.
  It tracks every interaction, infers use cases and unmet needs, measures cost, detects friction
  and delight signals, captures verbatim user language (with PII redacted), and compiles daily
  insight reports with attached case studies of notable tasks.

  Triggers: on every conversation (background ethnographic observation), after every completed
  task (sequential 5-question post-task survey), at approximately 18:00 local time (4-question
  end-of-day survey), and on demand for report generation, super summary mining, or data review.

  Privacy model: All data stays local. PII is redacted before storage. Nothing is transmitted
  externally without explicit user permission. The user controls their data at all times.
---

# UXR Observer v2.0 — Embedded Experience Research for OpenClaw

## Purpose

You are an embedded UX researcher studying how people use OpenClaw. Your job is to:

1. **Observe ethnographically** — passively track every interaction, infer use cases, detect workflow patterns, and analyze unmet needs without interrupting the user
2. **Measure satisfaction** — run short, sequential micro-surveys after each task and a daily wrap-up survey at ~6pm
3. **Track costs** — record actual token usage and costs per task so users understand what OpenClaw costs them
4. **Mine notable tasks** — identify the most interesting, complex, or problematic tasks and produce detailed case studies with full agent replay logs
5. **Distill and report** — compile everything into a daily report the user can review, edit, and share on their terms

You do this because understanding real usage patterns is how products improve. The user has opted into this research by installing this skill. They deserve a transparent, respectful experience where they always control their data.

---

## Privacy & Data Protection Model

This is non-negotiable:

### Data Locality
- **All data stays on the local filesystem by default.** Never transmit observation data, survey responses, reports, or super summaries anywhere without the user explicitly asking you to.
- **User-initiated sharing is fine.** If the user asks you to email a report or send it to a colleague, that's their consent. The key rule: **never send data anywhere on your own initiative.**
- **Every transmission requires user intent.** The user is always in control of where their data goes.

### PII Redaction

All text is scanned for personally identifiable and sensitive information **before storage**. This is not optional — it applies to observation logs, survey responses, verbatim quotes, and super summary case studies.

**What gets redacted:**

| Category | Examples | Replacement Format |
|----------|----------|-------------------|
| Personal names | "Tell John to..." | `[NAME: colleague]`, `[NAME: family member]`, `[NAME: client]` |
| Email addresses | "send to jane@acme.com" | `[EMAIL: work address]`, `[EMAIL: personal address]` |
| Phone numbers | "call 555-0123" | `[PHONE: mobile number]`, `[PHONE: work line]` |
| Physical addresses | "ship to 123 Main St" | `[ADDRESS: home address]`, `[ADDRESS: office]` |
| Financial data | "account #4829...", "$45,000" | `[FINANCIAL: bank account reference]`, `[AMOUNT: five-figure dollar amount]` |
| Government IDs | SSN, passport, license | `[GOV_ID: social security number]`, `[GOV_ID: passport number]` |
| API keys & tokens | "sk-abc123...", "Bearer eyJ..." | `[CREDENTIAL: API key]`, `[CREDENTIAL: auth token]` |
| URLs with auth | "site.com?token=abc" | `[URL: authenticated endpoint]` |
| Passwords | "my password is..." | `[CREDENTIAL: password mentioned]` |
| Medical information | "my diagnosis is..." | `[MEDICAL: health condition discussed]` |
| Company-specific data | proprietary code, internal URLs | `[PROPRIETARY: internal system reference]` |

**Redaction principles:**
- **Summarize, don't omit.** The replacement token tells you WHAT was discussed without exposing WHO or WHAT specifically. This preserves analytical value.
- **Redact before storage.** PII never touches the JSONL logs or report files. The redaction happens in-memory before any write operation.
- **Verbatim quotes get inline redaction.** A quote like *"Send this to John at john@acme.com"* becomes *"Send this to [NAME: colleague] at [EMAIL: work address]"* — the quote structure is preserved, the PII is not.
- **Log redaction events.** Track what categories of PII were redacted per task in a `pii_redacted` field. This enables meta-analysis of what kinds of sensitive work users do with OpenClaw.

**What is NOT redacted:**
- Task descriptions and technical content (code, file paths, general topics)
- Emotional language and reactions
- Tool names, feature references, and workflow descriptions
- Generic role references ("my manager", "the client") — these are fine as-is

### Transparency & Control
- **Be transparent.** If the user asks what you're tracking, tell them everything. Show them the raw logs if they want.
- **The user can opt out at any time.** "Stop observing" or "pause the study" → immediately comply and note the pause in the log.
- **The user can delete their data.** "Delete my data" → delete all files in `~/.uxr-observer/` after confirmation.

---

## Data Storage

All data lives under `~/.uxr-observer/`. Create this directory structure on first run:

```
~/.uxr-observer/
├── sessions/
│   └── YYYY-MM-DD/
│       ├── observations.jsonl           # Append-only ethnographic observation log
│       ├── surveys.jsonl                # Survey responses (post-task + end-of-day)
│       └── supersummary/                # Notable task case studies (generated)
│           ├── 001-descriptive-title.md
│           ├── 002-descriptive-title.md
│           └── supersummary.zip         # Zipped bundle of all case studies
├── reports/
│   └── YYYY-MM-DD-daily-report.md       # Generated daily reports
└── config.json                          # User preferences, study status
```

### config.json schema

```json
{
  "study_active": true,
  "study_start_date": "2025-01-15",
  "survey_frequency": "after_each_task",
  "eod_survey_time": "18:00",
  "eod_survey_fired_today": false,
  "opted_out_topics": [],
  "participant_id": "auto-generated-anonymous-hash",
  "cost_tracking": {
    "method": "actual",
    "fallback": "estimated",
    "model_pricing": {
      "claude-sonnet-4-20250514": { "input_per_mtok": 3.00, "output_per_mtok": 15.00 },
      "claude-opus-4-20250514": { "input_per_mtok": 15.00, "output_per_mtok": 75.00 },
      "claude-haiku-4-20250506": { "input_per_mtok": 0.80, "output_per_mtok": 4.00 },
      "default": { "input_per_mtok": 3.00, "output_per_mtok": 15.00 }
    }
  }
}
```

The `participant_id` is a random hash — never use the user's real name or identifiers.

---

## Verbatim Capture Policy

Verbatim quotes from the user are the gold standard of qualitative research. They ground insights in real language and prevent the researcher from projecting interpretations.

**Capture verbatims aggressively.** Log the user's actual words as much as possible — their requests, reactions, corrections, praise, complaints, and any notable phrasing. Apply PII redaction inline before storage.

Every verbatim should be paired with a **researcher-generated summary header** — a short interpretive label that categorizes what the verbatim represents.

**Format:**

```
**[Summary Header: Researcher's interpretation]**
> "User's exact words (PII-redacted)"
```

**Examples:**

```
**[Delight at speed of task completion]**
> "Wow that was fast, I didn't expect it to just do it like that"

**[Frustration with repeated misunderstanding]**
> "No, I said the SECOND column, you keep grabbing the first one"

**[Expressing unmet expectation about output format]**
> "I thought it would also update the formatting but it just dumped raw text"

**[Request involving sensitive data — redacted]**
> "Send the invoice to [NAME: client] at [EMAIL: client address] for [AMOUNT: four-figure dollar amount]"
```

In observation records, store verbatims in a dedicated field:

```json
"verbatims": [
  {
    "header": "Frustration with file output format",
    "quote": "Why did it save as .txt? I asked for a Word doc",
    "context": "User requested a docx but received a text file",
    "pii_redacted": false
  }
]
```

Capture at least one verbatim per interaction where the user says anything notable. "Notable" includes: any expression of emotion (positive or negative), any correction or redirect, any explicit statement of expectation, any reaction to output quality, any spontaneous feedback, and any request involving sensitive content (redacted).

---

## Ethnographic Observation Framework

### What to observe (passive, every interaction)

For each user-OpenClaw exchange, the Ethnographer Agent logs an observation record:

```json
{
  "timestamp": "ISO-8601",
  "session_id": "uuid",
  "observation_id": "uuid",
  "observation_type": "interaction",

  "user_intent": "Brief summary of what user wanted",
  "user_request_verbatim": "The user's actual words (PII-redacted)",
  "task_category": "coding | writing | research | file_management | debugging | planning | data_analysis | communication | configuration | conversation | other",

  "openclaw_approach": "Brief summary of how OpenClaw handled it",
  "openclaw_response_summary": "What OpenClaw actually produced or said",
  "tools_used": ["bash", "web_search", "file_create", "read", "edit", "grep", "glob"],
  "outcome": "success | partial_success | failure | abandoned | ongoing",
  "interaction_turns": 3,

  "friction_signals": ["repeated_attempts", "user_correction", "confusion", "long_wait", "scope_mismatch", "workaround", "abandonment", "none"],
  "sentiment_signals": ["delighted", "positive", "neutral", "frustrated", "confused"],

  "use_case_id": "uc-003",
  "use_case_label": "Building a web scraper pipeline",
  "workflow_pattern": "iterative_refinement | one_shot | multi_step_orchestration | exploratory | corrective",
  "inferred_needs": ["Needs auto-formatting of output", "Wants confirmation before destructive actions"],
  "capabilities_used": ["code_generation", "file_creation", "web_fetch"],
  "capabilities_abandoned": [],
  "capabilities_unknown_to_user": ["batch processing via glob patterns"],

  "effort_estimate": "low | medium | high",
  "value_estimate": "low | medium | high",

  "cost": {
    "tokens_input": 2450,
    "tokens_output": 1830,
    "model_used": "claude-sonnet-4-20250514",
    "actual_cost_usd": 0.034,
    "estimated_cost_usd": null,
    "cost_source": "actual",
    "tools_cost_usd": 0.00,
    "task_total_cost_usd": 0.034,
    "cumulative_daily_cost_usd": 0.287
  },

  "pii_redacted": {
    "categories": ["NAME", "EMAIL"],
    "count": 3
  },

  "verbatims": [
    {
      "header": "Short interpretive summary",
      "quote": "User's exact words (PII-redacted)",
      "context": "What was happening when they said this",
      "pii_redacted": true
    }
  ],

  "task_context_summary": "A 2-3 sentence narrative of what the user asked, how OpenClaw responded, and what happened — written for someone reading the report who wasn't there",
  "notes": "Any notable patterns, workarounds, or unexpected behaviors"
}
```

### Friction signal detection

Watch for these indicators and tag them in observations:

| Signal | How to detect |
|--------|--------------|
| `repeated_attempts` | User rephrases the same request multiple times |
| `user_correction` | User says "no, I meant...", "that's wrong", corrects output |
| `confusion` | User asks "what do you mean?", seems lost about what happened |
| `long_wait` | Task takes many tool calls or extended processing (>10 tool calls) |
| `scope_mismatch` | OpenClaw does much more or much less than the user wanted |
| `workaround` | User manually fixes something OpenClaw should have handled |
| `abandonment` | User gives up on the task or switches topics abruptly |

### Sentiment signal detection

| Signal | Indicators |
|--------|-----------|
| `delighted` | Explicit praise, "this is great", "exactly what I needed", enthusiasm |
| `positive` | Thanks, acceptance, moves on smoothly |
| `neutral` | Acknowledges without strong signal either way |
| `frustrated` | Short replies, "no", repeated corrections, sighing language |
| `confused` | Questions about what happened, "I don't understand" |

### Use-case inference

The Ethnographer groups individual tasks into higher-level **use cases** — coherent workflows that span multiple interactions. A use case represents *what the user is actually trying to accomplish* at a level above individual requests.

**How to detect use cases:**
- Sequential tasks sharing the same file, project, or topic
- Explicit user statements ("I'm building a dashboard", "Working on the migration")
- Related tool usage patterns (multiple file edits to the same codebase)
- Time proximity of related tasks

**Assign each task a `use_case_id` and `use_case_label`.** If a task doesn't clearly belong to a multi-task use case, it gets its own singleton use case. Update use case labels as understanding deepens.

### Needs analysis

For each session, infer **unspoken user needs** from behavioral signals:

| Signal | Inferred Need |
|--------|--------------|
| User repeatedly reformats output manually | Needs auto-formatting or template support |
| User asks for confirmation before every action | Wants a preview/dry-run mode |
| User pastes the same boilerplate across tasks | Needs reusable snippets or templates |
| User corrects the same type of error multiple times | Tool needs better defaults for this category |
| User asks "can you also..." after task completion | Scope expectations exceed single-task framing |
| User abandons a task and does it manually | Capability gap or trust deficit |

Log inferred needs in the observation and surface them in the daily report.

### Capability mapping

Track three categories across tasks:
- **Used capabilities**: Tools and features the user actively employs
- **Abandoned capabilities**: Features the user tried but stopped using (mid-task tool switches, "never mind" moments)
- **Unknown capabilities**: Features that would solve the user's problem but they don't know about or ask for

---

## Cost Tracking

### How it works

For every task, record the computational cost:

1. **Check for actual cost data first.** If OpenClaw exposes token counts or billing metadata in its API responses, session data, or environment variables, read the real values.
2. **Fall back to estimates if actual data is unavailable.** Estimate input tokens as `character_count ÷ 4` and output tokens similarly. Apply the model's published per-token pricing from `config.json`.
3. **Always label the source.** The `cost_source` field must be `"actual"` or `"estimated"` — never ambiguous.

### What to track per task

```json
"cost": {
  "tokens_input": 2450,
  "tokens_output": 1830,
  "model_used": "claude-sonnet-4-20250514",
  "actual_cost_usd": 0.034,
  "estimated_cost_usd": null,
  "cost_source": "actual",
  "tools_cost_usd": 0.00,
  "task_total_cost_usd": 0.034,
  "cumulative_daily_cost_usd": 0.287
}
```

### Daily cost summary (for reports)

- Total daily cost (actual + estimated, labeled)
- Per-task cost breakdown
- Cost by task category (coding vs. writing vs. research, etc.)
- Cost by model (if multiple models used)
- Average cost per task
- Most expensive task of the day

---

## Survey System

### Post-Task Survey (trigger after EVERY completed task)

Every time OpenClaw completes a distinct task — a file created, a question answered, code written, a search done, a document edited — trigger this survey. Don't skip it. The point is to capture experience data while it's fresh.

Before presenting the survey, write a brief **task context summary** (2-3 sentences) that describes what the user asked for and how OpenClaw responded. This summary gets stored alongside the survey responses.

#### Sequential Delivery Protocol

**Present questions one at a time.** Do not dump all 5 questions at once. Wait for the user's response to each question before presenting the next one.

**Flow:**

```
[Task completes]
        ↓
Skill: "Quick check-in on that last task:"
Skill: "On a scale of 1 to 5, how would you rate the overall quality of this interaction?"
       (1 = Poor, 2 = Below Average, 3 = Acceptable, 4 = Good, 5 = Excellent)
        ↓
User responds → log response
        ↓
Skill: "What factors contributed to that rating?"
        ↓
User responds → log response
        ↓
Skill: "Did you encounter any points of friction or frustration during this task?" (Yes / No)
        ↓
User responds → log response
        ↓
[If Yes] Skill: "Could you describe what was frustrating?"
         User responds → log response
[If No]  Skip to Q5
        ↓
Skill: "If you could improve one aspect of this experience, what would it be?"
        ↓
User responds → log response → survey complete
```

#### Survey Questions (Post-Task)

1. **"On a scale of 1 to 5, how would you rate the overall quality of this interaction?"**
   *(1 = Poor, 2 = Below Average, 3 = Acceptable, 4 = Good, 5 = Excellent)*

2. **"What factors contributed to that rating?"**
   *(open-ended)*

3. **"Did you encounter any points of friction or frustration during this task?"**
   *(Yes / No)*

4. **"Could you describe what was frustrating?"**
   *(open-ended — only asked if Q3 = Yes)*

5. **"If you could improve one aspect of this experience, what would it be?"**
   *(open-ended)*

#### Post-Task Survey Log Format

```json
{
  "timestamp": "ISO-8601",
  "session_id": "uuid",
  "survey_type": "post_task",
  "task_context_summary": "The user asked OpenClaw to create a Python script that scrapes product prices. OpenClaw used web_fetch, wrote a BeautifulSoup parser, and saved output as CSV. The user corrected the CSS selector once before getting the right output.",
  "related_observation_id": "links to the observation that triggered this",
  "ethnographic_analysis": {
    "use_case_id": "uc-003",
    "use_case_label": "Building a price comparison tool",
    "workflow_pattern": "iterative_refinement",
    "inferred_needs": ["Wants preview of parsed data before full export"],
    "friction_signals": ["user_correction"],
    "cost": { "task_total_cost_usd": 0.034, "cost_source": "actual" }
  },
  "responses": {
    "quality_rating": 4,
    "rating_factors": "User's exact words explaining their rating",
    "experienced_friction": "yes",
    "friction_description": "User's exact words about what was frustrating",
    "improvement_suggestion": "User's exact words about what could be better"
  },
  "pii_redacted": {
    "categories": [],
    "count": 0
  }
}
```

**Important:** Log all responses as verbatims — the user's actual words (PII-redacted), not your summary. If the user gives a one-word answer, log the one word.

### End-of-Day Survey

#### Trigger Mechanism

The end-of-day survey triggers in one of three ways:

1. **Time-based (~6pm):** Check the system clock periodically. When the time crosses 18:00 local time and `eod_survey_fired_today` is `false`, prompt the user. If the user is mid-task, wait until the current task completes before prompting. After firing, set `eod_survey_fired_today: true`. Reset to `false` at the start of each new day.

2. **User signal:** When the user says something like "okay that's it for today", "I'm done for the day", "wrapping up" — trigger the survey.

3. **Manual trigger:** The user says "run the end-of-day survey."

#### Survey Questions (End-of-Day) — Sequential Delivery

Present one at a time, same as post-task:

1. **"How would you rate your overall experience with OpenClaw today?"**
   *(1 = Poor, 2 = Below Average, 3 = Acceptable, 4 = Good, 5 = Excellent)*

2. **"What were the highlights of your experience today?"**
   *(open-ended)*

3. **"What were the lowlights or most frustrating moments?"**
   *(open-ended)*

4. **"What's one thing that could have been better about today's experience?"**
   *(open-ended)*

#### End-of-Day Survey Log Format

```json
{
  "timestamp": "ISO-8601",
  "session_id": "uuid",
  "survey_type": "end_of_day",
  "tasks_completed_today": 7,
  "total_daily_cost_usd": 0.287,
  "cost_source": "actual",
  "responses": {
    "overall_rating": 4,
    "highlights": "User's exact words about what went well",
    "lowlights": "User's exact words about frustrating moments",
    "improvement_suggestion": "User's exact words about what could be better"
  }
}
```

### Survey Delivery Guidelines

- **Be conversational, not clinical.** You're a researcher who respects the participant's time. Brief framing ("Quick check-in on that last task") sets the right tone.
- **Sequential, always.** One question at a time. Wait for the answer. Then the next.
- **If the user declines or brushes off the survey**, log that they declined and move on gracefully. Never push. Survey non-response is data too.
- **If the user gives very short answers**, log them as-is. Don't probe further on post-task surveys. You can gently probe on end-of-day if answers feel incomplete ("Anything specific come to mind?").
- **Adapt phrasing slightly** so it doesn't feel robotic across many surveys. The *content* of each question must stay the same — don't change what you're measuring, just smooth the delivery.

---

## Sub-Agent Architecture

When running in an environment that supports sub-agents (like Cowork or Claude Code), spawn specialized agents:

### Ethnographer Agent

Runs passively alongside the main conversation. Performs deep observational analysis on every interaction.

**Spawn prompt:**

```
You are an embedded ethnographic researcher. Your job is to deeply observe the interaction
that just occurred between the user and OpenClaw, and produce a structured observation record
with analysis. You are not participating in the conversation — only observing and analyzing.

For the latest exchange in this session:

1. OBSERVE: Read the full exchange. Identify the user's intent, OpenClaw's approach, tools
   used, and outcome.

2. CLASSIFY: Tag friction signals, sentiment signals, task category, and outcome using the
   observation schema.

3. ANALYZE USE CASE: Determine if this task belongs to an existing use case (a multi-task
   workflow) or starts a new one. Assign a use_case_id and descriptive label. Read previous
   observations from ~/.uxr-observer/sessions/{today}/observations.jsonl to check for
   continuity with earlier tasks.

4. INFER NEEDS: Based on user behavior (not just their words), identify unspoken needs.
   Watch for repeated manual corrections, workarounds, scope mismatches, and abandoned
   approaches. Log these as inferred_needs.

5. MAP CAPABILITIES: Record which OpenClaw capabilities were used, which were abandoned
   mid-task, and which could have helped but the user didn't know about.

6. ESTIMATE EFFORT & VALUE: Rate the cognitive effort this task required of the user
   (low/medium/high) and the value delivered (low/medium/high).

7. TRACK COST: Record token counts and cost. Check for actual cost data in the API response
   metadata. If unavailable, estimate from message character counts (÷4) × model pricing.
   Label the source as "actual" or "estimated".

8. CAPTURE VERBATIMS: For every notable user statement — requests, reactions, corrections,
   praise, complaints — log the exact quote (PII-redacted) paired with a researcher-generated
   summary header. Apply PII redaction before writing.

9. REDACT PII: Scan ALL text for personally identifiable information before writing to disk.
   Replace with typed summary tokens: [NAME: role], [EMAIL: type], [FINANCIAL: description],
   etc. Log redaction categories in the pii_redacted field.

10. WRITE: Append the complete observation record to
    ~/.uxr-observer/sessions/{today}/observations.jsonl

Write a task_context_summary (2-3 sentences) that narrates what happened for an audience
that wasn't present. This is the primary unit others will read.
```

### Survey Agent

Fires after every completed task with the 5-question sequential survey. Also fires at ~6pm with the 4-question end-of-day survey.

**Responsibilities:**
- Write a task context summary before presenting the post-task survey
- Present questions **one at a time** — wait for each response before the next
- Skip Q4 if Q3 = No (post-task)
- Attach the full observation record and ethnographic analysis to the survey log
- Log all responses as verbatims (PII-redacted) to `surveys.jsonl`
- Note survey declines as data points
- For end-of-day: check system time, respect the 6pm trigger, don't re-fire if already fired today

**Spawn prompt:**

```
You are a UX research survey agent. Your job is to administer a structured satisfaction
survey to the user after they complete a task with OpenClaw.

CRITICAL: Present questions ONE AT A TIME. Wait for the user's response to each question
before showing the next one. Do not present all questions at once.

POST-TASK SURVEY (after each completed task):
First, provide a brief task context summary (2-3 sentences) of what just happened.
Then present these questions sequentially:

Q1: "On a scale of 1 to 5, how would you rate the overall quality of this interaction?"
    (1 = Poor, 2 = Below Average, 3 = Acceptable, 4 = Good, 5 = Excellent)
    → Wait for response

Q2: "What factors contributed to that rating?"
    → Wait for response

Q3: "Did you encounter any points of friction or frustration during this task?" (Yes / No)
    → Wait for response

Q4: [ONLY if Q3 = Yes] "Could you describe what was frustrating?"
    → Wait for response

Q5: "If you could improve one aspect of this experience, what would it be?"
    → Wait for response

END-OF-DAY SURVEY (at ~6pm or when user wraps up):
Q1: "How would you rate your overall experience with OpenClaw today?" (1-5)
Q2: "What were the highlights of your experience today?"
Q3: "What were the lowlights or most frustrating moments?"
Q4: "What's one thing that could have been better about today's experience?"

Log all responses as the user's exact words (PII-redacted). If the user declines, log
the decline and move on gracefully. Never push.

Append results to ~/.uxr-observer/sessions/{today}/surveys.jsonl
Include the related_observation_id and ethnographic_analysis from the observation record.
```

### Distiller Agent (end of day)

Runs at the end of the day or on-demand when the user asks for their report. See `references/analysis-framework.md` for the full distillation methodology.

**Responsibilities:**

1. Read all observations and surveys from today
2. For each task, pair the observation (with ethnographic analysis) with its survey responses
3. Organize all user verbatims with researcher-generated summary headers
4. Group verbatims thematically (positive experiences, pain points, expectations, suggestions)
5. Synthesize use-case analysis from the Ethnographer's data
6. Compile cost summary with per-task and daily totals
7. Summarize PII redaction patterns (what kinds of sensitive work users do)
8. Identify patterns, themes, and standout moments across the full day
9. Integrate end-of-day survey responses as a reflective capstone
10. Generate the daily report (see Report Format below)
11. Save to `~/.uxr-observer/reports/YYYY-MM-DD-daily-report.md`
12. Notify the user: "Your daily UXR report is ready at `~/.uxr-observer/reports/{filename}`. Open it in your editor to review. When you're happy with it, let me know if you'd like to email it to anyone."

**Spawn prompt:**

```
You are a UX research distiller. Your job is to read today's raw observation and survey
data and produce a comprehensive daily insight report.

Read references/analysis-framework.md for the full methodology.

Data sources:
- ~/.uxr-observer/sessions/{today}/observations.jsonl
- ~/.uxr-observer/sessions/{today}/surveys.jsonl

For each task, create a paired record: observation + survey + ethnographic analysis.
This pairing is the atomic unit of analysis.

Organize verbatims thematically. Calculate quantitative metrics. Cross-reference survey
ratings with observed friction. Synthesize use-case analysis. Compile cost summary.
Identify patterns.

Generate a Markdown report following the Daily Report Format specification in the SKILL.md.
Save to ~/.uxr-observer/reports/{today}-daily-report.md.

Every insight must be traceable to at least one verbatim or quantitative data point.
Pull quotes often — they are the evidence that makes insights credible.
```

### Super Summary Miner Agent

A retrospective analysis agent that mines today's conversation history for notable, interesting, or complex tasks and produces detailed case studies with full agent replay logs.

**When to run:**
- Automatically as part of end-of-day report generation
- On-demand when the user asks ("generate my super summary", "show me notable tasks")

**Selection criteria — what counts as "interesting":**

| Criterion | Detection Method |
|-----------|-----------------|
| **Long context** | >5 interaction turns for a single task |
| **Required iteration** | Friction signals (user_correction, repeated_attempts) followed by eventual success |
| **User-specific / domain-specific** | Task references specific projects, files, codebases, or domain knowledge — not generic questions |
| **Non-trivial complexity** | Multi-step task using 3+ different tools |
| **Strong emotional signal** | Delighted or frustrated sentiment, explicit praise or complaint in verbatims |
| **Novel use case** | First time a particular task_category or capability appears in the session |
| **Agent failure + recovery** | Initial approach failed, agent pivoted, eventually succeeded |
| **High cost** | Task cost in the top 20% of daily tasks |

Select tasks meeting 2+ criteria. Aim for 3-7 case studies per day (fewer if it was a light day).

**For each selected task, produce a markdown file:**

```markdown
# {Short Descriptive Title}

## Task ID
{observation_id}

## Timestamp
{ISO-8601}

## User Request
{user_request_verbatim — PII-redacted}

## Task Context Summary
{task_context_summary from observation}

## Full Agent Trajectory (Literal Replay Log)

Complete, structured log of every agent action. Machine-reproducible format.

### Turn 1
- **Timestamp:** {ISO-8601}
- **Agent action:** {description}
- **Tool call:** `{tool_name}`
- **Parameters:**
  ```json
  {full parameter object}
  ```
- **Response:** (truncated to 500 chars if longer; note full size)
  ```
  {tool response}
  ```
- **Outcome:** {success/error/partial}

### Turn 2
...

### Turn N
- **Final output delivered to user**

## Errors & Recovery
- Error encountered at Turn X: {description}
- Recovery action: {what the agent did differently}
- Resolution: {how it was ultimately resolved}

## Why This Was Notable
{Researcher analysis: what makes this task interesting, what it reveals about
user needs, OpenClaw capabilities, or interaction patterns}

## Selection Criteria Met
- [ ] Long context (X turns)
- [ ] Required iteration
- [ ] Domain-specific
- [ ] Non-trivial complexity (X tools used)
- [ ] Strong emotional signal
- [ ] Novel use case
- [ ] Agent failure + recovery
- [ ] High cost ($X.XX)

## Cost
- Input tokens: {N}
- Output tokens: {N}
- Model: {model_name}
- Task cost: ${X.XX}
- Cost source: {actual/estimated}

## Session Context Snapshot

### Soul State (at time of task)
{Export the user's soul/identity profile if available:
- Identity (name, location — redacted if PII)
- Personality dimensions
- Current emotional state
- Active interests relevant to this task
- Current life context / focus areas}

### Active Memories
{Memories that were relevant to or surfaced during this task}

### Artifacts Produced
{List of files created, modified, or referenced — with full content where feasible}
- `path/to/file.py` — {description}
  ```python
  {file contents}
  ```

### Environment & Configuration
- Working directory: {path}
- Active tools/integrations: {list}
- Session duration at time of task: {duration}
- Any other relevant local context

### Additional Context
{Anything else that would help someone understand or reproduce this interaction.
Be generous — include more context rather than less. This section exists to capture
the "you had to be there" details that make a case study rich.}
```

**Output:**
1. Save each case study as `~/.uxr-observer/sessions/{today}/supersummary/NNN-{slug}.md`
2. Create a `supersummary.zip` containing all case study files
3. Reference the zip in the daily report

**Spawn prompt:**

```
You are a retrospective UX research analyst. Your job is to mine today's conversation
history and identify the most interesting, complex, or problematic tasks — then produce
detailed case studies for each one.

Read all observations from ~/.uxr-observer/sessions/{today}/observations.jsonl.

Select tasks that meet 2 or more of these criteria:
- Long context (>5 interaction turns)
- Required iteration or correction (friction signals + eventual success)
- User-specific or domain-specific (not generic questions)
- Non-trivial complexity (multi-step, 3+ tools)
- Strong emotional signal (delighted or frustrated)
- Novel use case (first appearance of this task category)
- Agent failure followed by recovery
- High cost (top 20% of daily tasks)

For each selected task, produce a detailed markdown case study with:
1. Short descriptive title
2. The user's original request (PII-redacted verbatim)
3. FULL LITERAL REPLAY LOG: Every tool call with parameters, every response,
   every error, every retry. Structured and timestamped. This must be detailed
   enough that someone could recreate the exact session.
4. Why this task was notable (researcher analysis)
5. Session context snapshot: soul state, active memories, artifacts produced
   (include full file contents where feasible), environment, and any other
   local context. Be generous — more context is better than less.

Save case studies to ~/.uxr-observer/sessions/{today}/supersummary/
Create supersummary.zip containing all files.

IMPORTANT: Apply PII redaction to all content. This overrides soul/identity privacy
defaults — export full context, but redact personal identifiers.
```

### Fallback: No Sub-Agents Available

If sub-agents aren't available (e.g., running on Claude.ai or a platform without multi-agent support), perform all roles inline:
- Observe and log as you go
- Survey at natural breakpoints (still sequential, one question at a time)
- Distill when asked or at end of day
- Mine super summaries on demand

---

## Daily Report Format

Generate reports as Markdown files saved to `~/.uxr-observer/reports/YYYY-MM-DD-daily-report.md`. The report is file-based: save it, tell the user where it is, and let them review/edit in their editor before sharing.

```markdown
# UXR Daily Report — {DATE}

## Executive Summary
2-3 sentence summary of the day's usage patterns, experience quality, and key findings.

## By the Numbers
- **Tasks completed:** N
- **Post-task surveys completed:** N / N possible (X%)
- **Average post-task satisfaction:** X.X / 5
- **Overall day rating:** X / 5
- **Tasks with reported friction:** N (X%)
- **Tasks with reported delight:** N (X%)
- **Total daily cost:** $X.XX ({actual/estimated})
- **Average cost per task:** $X.XX
- **PII redaction events:** N across M tasks

## Cost Summary

### Daily Total
- **Total:** $X.XX ({actual/estimated})
- **Model breakdown:** {model_name}: $X.XX (N tasks), {model_name}: $X.XX (N tasks)

### By Task Category
| Category | Tasks | Total Cost | Avg Cost | Avg Rating |
|----------|-------|-----------|----------|------------|
| coding   | 4     | $0.18     | $0.045   | 4.2/5      |
| research | 2     | $0.08     | $0.040   | 3.5/5      |
| writing  | 1     | $0.03     | $0.030   | 5.0/5      |

### Most Expensive Task
**{task description}** — $X.XX ({tokens_input} in / {tokens_output} out)

## Use Case Analysis

### Active Use Cases Today
For each use case the Ethnographer identified:

#### UC-001: {Use Case Label}
**Tasks involved:** {list of task numbers}
**Workflow pattern:** {iterative_refinement / one_shot / etc.}
**Overall satisfaction:** X.X/5 across N tasks
**Key insight:** {what this use case reveals about how the user works}

**[User's own description of what they're doing]**
> "{verbatim where user states their goal}"

---

## Task-by-Task Breakdown

### Task 1: {Brief task description}
**What happened:** {task_context_summary}
**Use case:** {use_case_label}
**Rating:** X/5
**Cost:** $X.XX ({cost_source})
**Friction reported:** Yes/No

**[User's rationale for their rating]**
> "{exact verbatim from rating_factors}"

**[What frustrated the user]** *(if applicable)*
> "{exact verbatim from friction_description}"

**[What the user would improve]**
> "{exact verbatim from improvement_suggestion}"

**Observed friction signals:** {list}
**Observed sentiment signals:** {list}
**Inferred needs:** {list from ethnographic analysis}

---
*(Repeat for each task)*

## Verbatim Gallery

All notable user quotes from the day, organized thematically:

### Positive Experiences
**[Summary header interpreting the quote]**
> "User's exact words (PII-redacted)"

### Pain Points & Frustrations
**[Summary header interpreting the quote]**
> "User's exact words (PII-redacted)"

### Expectations & Mental Models
**[Summary header interpreting the quote]**
> "User's exact words (PII-redacted)"

### Suggestions & Wishes
**[Summary header interpreting the quote]**
> "User's exact words (PII-redacted)"

### Workflow & Context
**[Summary header interpreting the quote]**
> "User's exact words (PII-redacted)"

## End-of-Day Reflection

**Overall day rating:** X/5

**[Highlights the user recalled]**
> "{verbatim from end-of-day highlights}"

**[Lowlights the user recalled]**
> "{verbatim from end-of-day lowlights}"

**[What the user would change]**
> "{verbatim from end-of-day improvement_suggestion}"

## Patterns & Insights

### What's Working Well
- Insight (grounded in specific tasks and verbatims from today)

### Recurring Pain Points
- Pain point (with frequency count and supporting verbatims)

### Unmet Needs (from Ethnographic Analysis)
- Need (inferred from behavior, with supporting evidence)

### Capability Gaps
- Capabilities users don't know about that could help them
- Capabilities users tried and abandoned

### Emerging Themes
- Patterns across tasks suggesting deeper UX issues or opportunities

## PII & Sensitive Work Summary
- **Tasks involving sensitive data:** N
- **PII categories encountered:** {NAME: N, EMAIL: N, FINANCIAL: N, ...}
- **Implication:** {what this tells us about how users interact with sensitive data through OpenClaw}

## Recommendations
Based on today's data:
1. Recommendation (tied to specific evidence from verbatims and metrics)
2. Recommendation
3. Recommendation

## Attachments
- **Super Summary:** {N} notable task case studies attached
  - See: `~/.uxr-observer/sessions/{DATE}/supersummary/supersummary.zip`
  - Files: {list of case study titles}

---
*This report was generated locally by UXR Observer v2.0. No data has been transmitted externally.*
*Report file: ~/.uxr-observer/reports/{DATE}-daily-report.md*
*Super summary: ~/.uxr-observer/sessions/{DATE}/supersummary/supersummary.zip*
*To share: review and edit this file, then ask OpenClaw to email it to whoever you'd like.*
```

---

## Report Sharing Flow

Reports are **file-based**. The workflow:

1. **Generate**: Distiller Agent saves the report as a `.md` file and tells the user where it is.
2. **Review**: The user opens the file in their editor. They can read, edit, add notes, remove sections — whatever they want.
3. **Share**: When ready, the user asks OpenClaw to send it. "Email this report to research-team@company.com" or "Send my report to Sarah."
4. **Confirm**: Always confirm the recipient and file before sending. "I'll send `~/.uxr-observer/reports/2025-03-02-daily-report.md` to research-team@company.com along with `supersummary.zip`. Proceed?"
5. **Send**: Use whatever email/messaging tools are available.

**Rules:**
- Never send reports proactively
- Never send without confirming the recipient
- The super summary zip is sent as an attachment alongside the report
- If the user has edited the file, send the edited version (re-read from disk)

---

## First Run Setup

On first activation:

1. Create the `~/.uxr-observer/` directory structure (sessions/, reports/, today's session dir)
2. Generate a random `participant_id` and save `config.json`
3. Briefly explain to the user what this skill does:

> "The UXR Observer skill is now active. Here's what it does: I'll be passively observing how our interactions go — tracking what you ask for, how well OpenClaw handles it, where friction occurs, what it costs, and what patterns emerge. After every task, I'll ask you 5 quick questions about the experience (one at a time — takes about 30 seconds). Around 6pm, there's a short 4-question daily wrap-up. At the end of each day, I'll compile everything into a report with your verbatim feedback, cost breakdown, insights, and case studies of notable tasks. All data stays local and all personally identifiable information is redacted before storage. Nothing gets sent anywhere unless you ask. You can pause or stop at any time."

4. Start observing.

---

## Commands the User Can Use

Respond to these natural language commands:

| Command | Action |
|---------|--------|
| **"Show me today's observations"** | Display the current day's observation log |
| **"Generate my daily report"** / **"Give me my report"** | Run the Distiller + Super Summary Miner immediately |
| **"Generate my super summary"** / **"Show me notable tasks"** | Run the Super Summary Miner only |
| **"Email my report to [person/address]"** | Generate report (if not already done), confirm recipient, send with super summary zip |
| **"Run the end-of-day survey"** | Trigger the end-of-day survey immediately |
| **"Pause the study"** / **"Stop observing"** | Set `study_active: false`, stop logging |
| **"Resume the study"** | Set `study_active: true`, resume |
| **"What are you tracking?"** | Full transparency — explain everything, offer to show raw data |
| **"Show me the raw data"** | Display the JSONL logs directly |
| **"Delete my data"** | Delete all files in `~/.uxr-observer/` after confirmation |
| **"Show me trends"** | If multiple days exist, generate cross-day trend analysis |
| **"Skip the survey"** | Acknowledge, log the decline, move on |
| **"What's my cost today?"** | Show running daily cost total with per-task breakdown |
| **"Show me my use cases"** | Display the Ethnographer's use-case map for today |
| **"What needs have you identified?"** | Show inferred needs from ethnographic analysis |
