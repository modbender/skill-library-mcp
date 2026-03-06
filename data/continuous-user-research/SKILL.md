---
name: continuous-user-research
description: Run longitudinal, in-context diary studies for product teams and convert weekly participant entries into concise User Signals + Recommendations with evidence, confidence, and experiment-ready actions. Use for onboarding drop-off diagnosis, feature habit/frequency understanding, motivation and emotion analysis, multi-touchpoint journey mapping, and channel/device behavior comparisons. Supports event-based, interval-based, signal-based, and mixed timing designs with pilot validation, compliance monitoring, and privacy-redacted reporting.
metadata:
  openclaw:
    skillKey: continuous-user-research
    primaryEnv: CONTINUOUS_USER_RESEARCH_PROFILE
    always: false
    requires:
      env:
        - RESEARCH_STUDY_STORAGE_RAW_PATH
        - RESEARCH_STUDY_STORAGE_REPORTS_PATH
        - RESEARCH_REDACTION_SALT
        - RESEARCH_NOTION_TOKEN
        - RESEARCH_NOTION_DATABASE_ID
        - RESEARCH_SLACK_BOT_TOKEN
        - RESEARCH_SLACK_SIGNING_SECRET
        - RESEARCH_EMAIL_PROVIDER
        - RESEARCH_EMAIL_API_KEY
        - RESEARCH_EMAIL_FROM
        - RESEARCH_LINEAR_TOKEN
        - RESEARCH_LINEAR_TEAM_ID
        - RESEARCH_GITHUB_TOKEN
        - RESEARCH_GITHUB_REPO
      config:
        - continuous_user_research.integrations.notion.enabled
        - continuous_user_research.integrations.slack.enabled
        - continuous_user_research.integrations.email.enabled
        - continuous_user_research.integrations.linear.enabled
        - continuous_user_research.integrations.github.enabled
        - continuous_user_research.storage.multimedia_bucket
        - continuous_user_research.storage.multimedia_signed_url_ttl_minutes
        - continuous_user_research.retention.raw_days
        - continuous_user_research.retention.redacted_report_days
---

Automatically run a lightweight diary study and turn it into weekly product signals and experiment-ready recommendations.

## When to use
- The team must decide what to build, fix, or prioritize and needs behavior evidence over time, not one-off opinions.
- A founder or PM asks for scoped weekly learning (for example, onboarding drop-off causes this week).
- You need to compare what people report with what they actually do across days or touchpoints.
- You need low-overhead, repeatable diary loops tied to one explicit research goal.
- You need actionable weekly outputs with direct experiment plans.

## When not to use
- The request is only broad brand sentiment with no product decision attached.
- The team needs statistically representative market sizing instead of qualitative behavior understanding.
- The study context is high-risk regulated or sensitive (medical, legal, minors, government) without dedicated compliance design.
- The required data can be answered with existing telemetry alone and no user context is needed.
- You cannot secure participant consent, secure storage, and redaction safeguards.

## Security & Permissions
- Minimize access: only access participant contact data, diary entries, and tool scopes required for this study.
- Redact by default: remove names, emails, phone numbers, handles, account IDs, exact addresses, and direct identifiers from all synthesized outputs.
- Keep raw and reports separate: store raw unredacted entries in a restricted location; publish only redacted report artifacts.
- No secret exfiltration: never copy API keys, tokens, credentials, or hidden configs into prompts, reports, or tickets.
- No unnecessary filesystem/shell actions: prefer explicit API-based tool calls (Slack/Email/Notion/Linear/GitHub APIs) and avoid opaque shell operations.
- Multimedia controls: store attachments in restricted buckets/folders, enforce signed URL expiry, and reference attachment IDs in reports instead of raw files.
- Retention discipline: define and enforce retention windows per study; delete or anonymize raw data after the retention window.
- Auditability: log consent status, prompt schedule events, reminder events, and report generation events.

Credential contract (declare as runtime secrets, never in repo):
- Core data handling:
- `RESEARCH_STUDY_STORAGE_RAW_PATH`: restricted location for raw entries.
- `RESEARCH_STUDY_STORAGE_REPORTS_PATH`: redacted report output location.
- `RESEARCH_REDACTION_SALT`: deterministic redaction tokenization salt.
- Notion recipe:
- `RESEARCH_NOTION_TOKEN`: integration token limited to the target study database.
- `RESEARCH_NOTION_DATABASE_ID`: database ID used for participants/entries/reports.
- Slack recipe:
- `RESEARCH_SLACK_BOT_TOKEN`: bot token limited to study workspace/channels.
- `RESEARCH_SLACK_SIGNING_SECRET`: webhook signature verification secret.
- Email recipe:
- `RESEARCH_EMAIL_PROVIDER`: provider ID (for example, postmark or resend).
- `RESEARCH_EMAIL_API_KEY`: API key scoped to study sender identity.
- `RESEARCH_EMAIL_FROM`: approved sender address.
- Optional ticket sync:
- `RESEARCH_LINEAR_TOKEN`, `RESEARCH_LINEAR_TEAM_ID` for Linear ticket creation.
- `RESEARCH_GITHUB_TOKEN`, `RESEARCH_GITHUB_REPO` for GitHub issue creation.

## Scope anchor + supported study types
Primary scope anchor:
- Founder/PM request: "Track onboarding drop-offs this week and tell me what to fix."

Support these study types in the same workflow:
- Habits/frequency: understand repeated usage cadence for feature X.
- Motivations/emotions: understand why users choose or avoid task Y and how that changes over time.
- Journey progression: map research -> decision -> purchase touchpoints and friction points.
- Channel/device comparisons: compare behavior by channel, device, or context across a week.
- General behavior tracking: broad behavior shifts inside a defined product scope.

Rule:
- Use the primary user story as a scope anchor only.
- Keep method flexible so one skill run can execute any supported study type above.

## Diary study timeline
### A) Plan
1. Define the decision to inform and one clear study goal.
2. Write 3-7 research questions tied to that decision.
3. Choose focus type:
- `broad_behavior`: wide behavior context.
- `targeted_product`: product feature/flow usage.
- `targeted_activity`: one behavior or task.
- `journey`: multi-stage touchpoint progression.
4. Choose timing mode:
- `signal` default for lightweight studies.
- `event` for rare/high-value moments.
- `interval` for high-frequency habits.
- `mixed` when one mode is insufficient.
5. Set duration using expected event frequency:
- Daily/high frequency: 5-10 days.
- Medium frequency: 10-14 days.
- Rare events: 14-28 days.
6. Select tools (Notion/Airtable/Google Sheets optional) and storage boundaries.
7. Define participant profile and segmentation tags.
8. Set sample target, overrecruit factor, incentives, min entries, and max entry caps.
9. Finalize templates and follow-up rules.
10. Prepare pilot mode (24h internal test).

### B) Recruit + consent
1. Import participant candidates from CSV or JSON export.
2. Screen and segment against the participant profile.
3. Overrecruit to protect against drop-off.
4. Send consent template with plain-language participation rules.
5. Activate participants only after explicit consent confirmation.

### C) Pre-study brief
1. Run a short onboarding call or send equivalent written onboarding.
2. Explain what to report, how often, and expected entry duration.
3. Explain incentive and payout requirements (minimums and caps).
4. Share good entry examples and poor entry examples.
5. Confirm participant timezone and preferred prompt window.

### D) Run & monitor
1. Send prompts on schedule by selected timing mode.
2. Track compliance daily (sent, completed, missed, late, fallback-used).
3. Send reminders for missed entries.
4. If missed, send reduced-effort fallback prompt before marking non-compliant.
5. Handle drop-off with rescue messaging and simplified restart instructions.
6. Allow mid-study adjustments only when they reduce confusion without steering outcomes.

Mid-study adjustment rules (bias-safe):
- Allowed: clarify wording, shorten entry length, shift send window, simplify format.
- Not allowed: inject hypotheses, add leading examples, redefine success criteria midstream.
- Always log change timestamp, rationale, and affected participants.

### E) Optional post-study interview
1. Schedule 20-30 minute debrief with a subset of participants.
2. Validate strongest themes and probe contradictions.
3. Investigate surprising behaviors and unresolved gaps.
4. Keep interview prompts neutral and evidence-grounded.

### F) Analysis
1. Revisit original research questions and decision context.
2. Code/tag entries by theme, stage, trigger, blocker, and sentiment.
3. Analyze behavior shifts over time and key influencing factors.
4. For journey studies, map touchpoints, transitions, delays, and abandonment points.
5. Apply saturation logic before finalizing claims.
6. Produce only evidence-linked recommendations with testable experiments.

## Timing mode selection guide
Use this decision sequence:
1. Is the behavior rare but high-value (for example, activation failure, checkout abandonment)?
- Choose `event`.
2. Is the behavior frequent and routine (for example, daily usage habit)?
- Choose `interval`.
3. Is this a lightweight weekly pulse where events may not self-trigger reliably?
- Choose `signal`.
4. Do you need baseline routine + specific event captures?
- Choose `mixed`.

Mode guidance:
- `event` mode:
- Prompt immediately after target event; require short contextual details.
- Best for low-frequency, high-insight moments.
- `interval` mode:
- Prompt on fixed cadence (daily or every X days).
- Best for repeated routines and trend tracking.
- `signal` mode (default):
- Prompt at planned check-in windows with contextual cueing.
- Best for low-friction weekly decision loops.
- `mixed` mode:
- Combine interval baseline + event trigger + signal rescue prompts.
- Best for onboarding flows and journeys with uneven activity.

Mixed-mode patterns:
- Onboarding diagnostics:
- `signal` once daily + `event` when user exits onboarding unfinished.
- Habit studies:
- `interval` daily + `signal` at end-of-week reflection.
- Journey mapping:
- `event` per stage transition + `signal` every 2-3 days for missing stages.

## Sample size and overrecruit
Qualitative target ranges (completed participants):
- Focused product question: 8-12 completes.
- Segment comparison (2 segments): 12-20 completes total.
- Journey mapping across multiple stages: 15-24 completes.
- High variability context: 20-30 completes.

Overrecruit rule:
- Formula: `recruit_n = ceil(sample_size_target * overrecruit_factor)`.
- Default `overrecruit_factor`: `1.4`.
- Typical range: `1.3` to `1.8` depending on expected attrition.

Attrition planning:
- Anticipated drop-off <20%: factor 1.3-1.4.
- Anticipated drop-off 20-35%: factor 1.4-1.6.
- Anticipated drop-off >35%: factor 1.6-1.8.

Saturation reminder:
- Increase sample only when new entries still introduce decision-relevant themes.
- Stop expansion when additional participants mostly confirm existing patterns.

## Incentive and response requirement model
Core rules:
- Pay for consistent participation quality, not raw message volume.
- Set clear minimum entry threshold for completion payout.
- Set max counted entries to prevent incentive gaming.

Recommended structure:
1. Completion base payout:
- Paid if participant meets `min_entries_required` and consent/compliance rules.
2. Optional per-entry bonus:
- Small amount per valid entry, counted only up to `max_entries_allowed`.
3. Quality gate:
- Entry must include required closed + open components; low-information spam is non-qualifying.

Default calculation model:
- `min_entries_required = ceil(planned_prompt_count * 0.7)`.
- `max_entries_allowed = planned_prompt_count + ceil(planned_prompt_count * 0.2)`.
- `total_incentive = base_completion + (per_entry_bonus * min(valid_entries, max_entries_allowed))`.

Anti-gaming controls:
- Ignore duplicate entries submitted within a short lockout window unless marked correction.
- Cap bonus at `max_entries_allowed`.
- Reject entries with copied repetitive text across multiple days unless justified.

## Pilot mode
Run pilot before live recruitment:
- Duration: 24 hours.
- Participants: 1-2 internal testers.
- Mode: use intended production timing mode (or mixed if planned).

Pilot checks:
1. Entry completion time median is 5-10 minutes.
2. No entry exceeds 15 minutes unless intentionally long-form.
3. Questions are clear without facilitator intervention.
4. Closed + open responses together produce usable evidence.
5. Reminder + fallback sequence works as expected.

Pilot pass criteria:
- At least 80% of pilot entries meet quality requirements.
- No major ambiguity in prompt wording.
- Report synthesis can produce at least one evidence-backed signal.

If pilot fails:
- Simplify prompts.
- Remove ambiguous wording.
- Reduce entry burden before launching live study.

## Compliance monitoring
Track per participant daily:
- prompts_sent
- entries_completed
- entries_missed
- reminders_sent
- fallback_entries_completed
- consecutive_missed_days

Reminder policy:
- First miss: gentle reminder.
- Second miss in a row: fallback prompt (reduced effort).
- Third miss in a row: dropout rescue message and optional pause.

Fallback prompt requirements:
- 1 closed question + 1 short open response.
- Estimated effort: <=3 minutes.
- No penalty for using fallback when participant discloses constraints.

Dropout rescue flow:
1. Acknowledge friction without blame.
2. Offer simplified participation option.
3. Confirm whether participant wants to continue or exit.
4. Preserve data rights and payout rules clearly.

## Optional post-study interview
Use only when:
- Weekly signals contain unresolved contradictions.
- Behavior shifts need causal explanation.
- Journey transitions are unclear from diary logs.

Interview constraints:
- Duration 20-30 minutes.
- Use neutral prompts that reference participant's own prior entries.
- Do not force confirmation of existing hypotheses.

Outputs:
- Add debrief notes as supplemental evidence.
- Mark evidence provenance as `debrief` vs `diary`.

## Analysis and saturation logic
Analysis sequence:
1. Re-state study goal and research questions.
2. Normalize entries and redact identifiers.
3. Tag entries with codebook fields (behavior, trigger, barrier, outcome, stage, emotion).
4. Create participant-by-day timeline to inspect change over time.
5. Identify influencing factors (context, device/channel, constraints, external events).
6. For journey studies, map touchpoints and failure handoffs.
7. Calculate theme emergence trend by period.
8. Apply saturation test before final recommendations.

Saturation logic:
- Compute percentage of new decision-relevant themes in the latest window.
- Default window: last 20% of entries.
- If new decision-relevant themes <10% and no high-risk unknowns, treat as approaching saturation.
- If >=10% or contradictions remain unresolved, extend study or run targeted debrief.

Recommendation requirements:
- Every recommendation maps to a specific signal.
- Every signal maps to at least two evidence points when possible.
- When confidence is low, recommend risk-reduction experiments, not major irreversible changes.

## Weekly User Signals + Recommendations quality bar
Report constraints:
- Max length: 1 page.
- Include exactly top 3 signals.
- Each signal must include:
- Evidence snippets (redacted).
- Confidence (`Low`/`Med`/`High`) and explicit reason.
- One testable recommendation as an experiment plan.

Experiment plan minimum:
- Hypothesis.
- Experiment method.
- Primary metric.
- Decision rule.
- Owner and timebox.

Writing rules:
- No generic advice.
- Tie every claim to observed pattern + evidence.
- Distinguish observed behavior from participant interpretation.
- Explicitly note change-over-time where relevant.

## Communication templates index
Use templates in `/prompts`:
- Consent: `prompts/consent_message.md`
- Onboarding brief: `prompts/pre_study_brief.md`
- Diary entry template bank: `prompts/entry_templates.md`
- Adaptive follow-up rules: `prompts/followup_rules.md`
- Optional debrief guide: `prompts/post_study_interview_guide.md`

Standard operational snippets:
- Invite:
"We are running a short diary study to understand how this product decision should be improved. You will share brief, in-context entries over [X days]. Typical entry time is 5-10 minutes."
- Reminder:
"Quick reminder for today's diary check-in. A short entry is enough; if time is tight, use the short-form option."
- Thank-you:
"Thanks for today's entry. Your details on what happened and why are directly helping this week's product decisions."
- Dropout rescue:
"No pressure. If the current format is heavy, we can switch to a lighter 2-minute check-in so your perspective is still represented."

## Examples
### Example Study Brief 1: Onboarding drop-off
```json
{
  "goal": "Identify the highest-impact onboarding drop-off behaviors this week and define fixes with measurable impact.",
  "research_questions": [
    "At which onboarding step do users stop most often?",
    "What context or blockers are present when they stop?",
    "What do users say they plan to do next versus what they actually do next day?",
    "Which prompt or UI changes are most likely to reduce drop-off this week?"
  ],
  "focus_type": "targeted_product",
  "timing_mode": "mixed",
  "reporting_period_days": 7,
  "expected_event_frequency": "1-2 onboarding attempts per participant per week",
  "participant_profile": {
    "summary": "New sign-ups in first 72h, self-serve onboarding, mixed device usage",
    "segments": ["new_trial", "team_invited"],
    "inclusion_criteria": [
      "Created account within last 7 days",
      "Has not completed onboarding"
    ],
    "exclusion_criteria": [
      "Completed onboarding before study start"
    ]
  },
  "sample_size_target": 14,
  "overrecruit_factor": 1.5,
  "incentive_plan": {
    "currency": "USD",
    "base_completion_amount": 25,
    "per_entry_amount": 2,
    "payout_timing": "within_7_days_of_completion",
    "quality_requirements": [
      "Include one closed response and one open explanation per entry",
      "No duplicate spam entries"
    ]
  },
  "min_entries_required": 5,
  "max_entries_allowed": 8,
  "channels": ["email", "slack"],
  "timezone_handling": {
    "default_timezone": "participant_local",
    "prompt_window_local": "09:00-20:00",
    "dst_strategy": "auto_adjust",
    "missing_timezone_policy": "ask_onboarding_then_fallback_utc"
  },
  "tools_config": {
    "notion": {
      "enabled": true,
      "database_id": "notion-db-onboarding-weekly"
    },
    "airtable": {
      "enabled": false
    },
    "google_sheets": {
      "enabled": true,
      "spreadsheet_id": "gs-onboarding-weekly"
    }
  },
  "privacy_redaction": true
}
```

### Example Study Brief 2: Habit/frequency for feature X
```json
{
  "goal": "Understand how often Feature X is used in real workflows and what causes skipped usage days.",
  "research_questions": [
    "On which days and contexts is Feature X used versus skipped?",
    "What motivates repeated use?",
    "Which friction points reduce weekly usage frequency?",
    "What product experiment can increase consistent weekly usage?"
  ],
  "focus_type": "targeted_activity",
  "timing_mode": "interval",
  "reporting_period_days": 7,
  "expected_event_frequency": "daily to every-other-day",
  "participant_profile": {
    "summary": "Active users with at least one Feature X use in last 14 days",
    "segments": ["individual_contributor", "manager"],
    "inclusion_criteria": [
      "Used Feature X at least once in prior 14 days"
    ],
    "exclusion_criteria": [
      "No product activity in prior 30 days"
    ]
  },
  "sample_size_target": 12,
  "overrecruit_factor": 1.4,
  "incentive_plan": {
    "currency": "USD",
    "base_completion_amount": 20,
    "per_entry_amount": 1.5,
    "payout_timing": "weekly",
    "quality_requirements": [
      "Closed + open responses required",
      "Reflection prompt completed at least twice"
    ]
  },
  "min_entries_required": 5,
  "max_entries_allowed": 9,
  "channels": ["email", "discord"],
  "timezone_handling": {
    "default_timezone": "participant_local",
    "prompt_window_local": "18:00-22:00",
    "dst_strategy": "auto_adjust",
    "missing_timezone_policy": "fallback_to_account_timezone"
  },
  "tools_config": {
    "notion": {
      "enabled": true,
      "database_id": "notion-db-featurex-habit"
    },
    "airtable": {
      "enabled": true,
      "base_id": "airtable-featurex-habit"
    },
    "google_sheets": {
      "enabled": false
    }
  },
  "privacy_redaction": true
}
```

### Example Study Brief 3: Multi-touchpoint journey
```json
{
  "goal": "Map how prospects move from research to decision to purchase and identify where momentum is lost.",
  "research_questions": [
    "Which touchpoints are most common in each stage?",
    "Where do delays or reversals happen in the journey?",
    "How do channel and device choices influence progression speed?",
    "Which experiment can reduce time-to-purchase without harming quality?"
  ],
  "focus_type": "journey",
  "timing_mode": "mixed",
  "reporting_period_days": 7,
  "expected_event_frequency": "2-4 decision-related interactions per week",
  "participant_profile": {
    "summary": "Prospects currently evaluating purchase within 30-day window",
    "segments": ["self_serve", "sales_assisted"],
    "inclusion_criteria": [
      "In active evaluation state",
      "Has interacted with at least one research touchpoint"
    ],
    "exclusion_criteria": [
      "Existing long-term customers"
    ]
  },
  "sample_size_target": 18,
  "overrecruit_factor": 1.6,
  "incentive_plan": {
    "currency": "USD",
    "base_completion_amount": 35,
    "per_entry_amount": 2,
    "payout_timing": "end_of_study",
    "quality_requirements": [
      "Include channel and device context for each major event",
      "At least one reflection entry on decision confidence shift"
    ]
  },
  "min_entries_required": 6,
  "max_entries_allowed": 10,
  "channels": ["email", "sms"],
  "timezone_handling": {
    "default_timezone": "participant_local",
    "prompt_window_local": "10:00-19:00",
    "dst_strategy": "auto_adjust",
    "missing_timezone_policy": "ask_participant_then_fallback_utc"
  },
  "tools_config": {
    "notion": {
      "enabled": true,
      "database_id": "notion-db-journey-map"
    },
    "airtable": {
      "enabled": false
    },
    "google_sheets": {
      "enabled": true,
      "spreadsheet_id": "gs-journey-weekly"
    }
  },
  "privacy_redaction": true
}
```

### Example Weekly Report 1: Onboarding drop-off (1 page format)
**Period:** 2026-03-02 to 2026-03-08  
**Decision focus:** Reduce onboarding abandonment in first session  
**Top 3 User Signals + Recommendations**

```json
[
  {
    "title": "Step-2 setup ambiguity causes immediate exits",
    "description": "Participants frequently paused at workspace setup because the required input and expected outcome were unclear.",
    "evidence": [
      {
        "participant_code": "P03",
        "timestamp": "2026-03-03T10:42:00Z",
        "snippet": "[REDACTED] I stopped because I was not sure what this field changes later."
      },
      {
        "participant_code": "P09",
        "timestamp": "2026-03-04T18:21:00Z",
        "snippet": "[REDACTED] I left to ask a teammate what to enter, then never came back."
      }
    ],
    "confidence": "High",
    "confidence_reason": "Observed across 8 participants over 3 separate days with consistent language and matching abandonment behavior.",
    "recommended_experiment": {
      "hypothesis": "If Step-2 includes plain-language helper text and one prefilled example, abandonment at Step-2 will decrease.",
      "method": "A/B test revised Step-2 copy and helper UI for new sign-ups.",
      "primary_metric": "Step-2 to Step-3 completion rate",
      "decision_rule": "Ship variant if completion improves >=12% with no increase in support tickets per user.",
      "owner": "PM Onboarding",
      "timebox": "7 days"
    },
    "tags": ["onboarding", "clarity", "abandonment"],
    "impacted_stage": "onboarding_step_2",
    "change_over_time": "Signal strengthened from Day 2 to Day 6 as more participants hit the same blocker."
  },
  {
    "title": "Mobile users defer verification and fail to return",
    "description": "Verification prompts on mobile during commute/work transitions often caused postponement and no same-day return.",
    "evidence": [
      {
        "participant_code": "P05",
        "timestamp": "2026-03-05T07:58:00Z",
        "snippet": "[REDACTED] Could not complete this at the station and forgot later."
      },
      {
        "participant_code": "P11",
        "timestamp": "2026-03-06T17:12:00Z",
        "snippet": "[REDACTED] I planned to do it on desktop after work but did not reopen it."
      }
    ],
    "confidence": "Med",
    "confidence_reason": "Pattern appears in 4 mobile-first participants; moderate sample but consistent context timing.",
    "recommended_experiment": {
      "hypothesis": "If mobile users can defer verification with one-tap reminder scheduling, return completion will increase.",
      "method": "Add defer flow with default same-day reminder and compare against current hard-stop flow.",
      "primary_metric": "24h return-to-onboarding rate for mobile starters",
      "decision_rule": "Adopt if return rate improves >=10% without higher next-day abandonment.",
      "owner": "Growth Engineer",
      "timebox": "7 days"
    },
    "tags": ["mobile", "verification", "return-rate"],
    "impacted_stage": "onboarding_verification",
    "change_over_time": "Stable pattern; no reduction after reminder copy tweak on Day 4."
  },
  {
    "title": "Perceived setup effort mismatch reduces trust",
    "description": "Users expected a 2-minute setup based on landing copy, but diary logs showed perceived effort of 8-12 minutes.",
    "evidence": [
      {
        "participant_code": "P02",
        "timestamp": "2026-03-03T15:33:00Z",
        "snippet": "[REDACTED] This looked quick but took too long for a first try."
      },
      {
        "participant_code": "P08",
        "timestamp": "2026-03-07T09:06:00Z",
        "snippet": "[REDACTED] I expected instant setup and bailed once it asked for more details."
      }
    ],
    "confidence": "Med",
    "confidence_reason": "Repeated in 5 entries with aligned closed-question effort ratings, but some variance by user type.",
    "recommended_experiment": {
      "hypothesis": "If pre-onboarding expectations match real setup effort, trust and completion rates will improve.",
      "method": "Update pre-onboarding messaging with realistic duration + quick-start path; compare against current messaging.",
      "primary_metric": "Onboarding completion among users who saw updated expectation message",
      "decision_rule": "Keep changes if completion increases >=8% and dissatisfaction mentions decrease.",
      "owner": "PMM + PM",
      "timebox": "7 days"
    },
    "tags": ["expectation-setting", "trust", "onboarding"],
    "impacted_stage": "pre_onboarding_to_step_1",
    "change_over_time": "Emergent by Day 3, then stable across remaining period."
  }
]
```

### Example Weekly Report 2: Habit/frequency for feature X (1 page format)
**Period:** 2026-03-02 to 2026-03-08  
**Decision focus:** Increase weekly repeat use of Feature X  
**Top 3 User Signals + Recommendations**

```json
[
  {
    "title": "Feature X is used when tied to a standing weekly ritual",
    "description": "Usage frequency increased when participants attached Feature X to recurring planning routines.",
    "evidence": [
      {
        "participant_code": "P04",
        "timestamp": "2026-03-04T19:04:00Z",
        "snippet": "[REDACTED] I use it every Monday planning block; otherwise I skip it."
      },
      {
        "participant_code": "P10",
        "timestamp": "2026-03-06T20:11:00Z",
        "snippet": "[REDACTED] Worked when I paired it with my weekly review slot."
      }
    ],
    "confidence": "High",
    "confidence_reason": "Seen across both segments and supported by closed frequency fields over the full week.",
    "recommended_experiment": {
      "hypothesis": "If Feature X offers one-click recurring schedule anchors, repeat weekly usage will rise.",
      "method": "Launch scheduling shortcut CTA after first successful use.",
      "primary_metric": "7-day repeat usage rate",
      "decision_rule": "Roll out if repeat usage improves >=15% and no decline in completion quality.",
      "owner": "Feature X PM",
      "timebox": "14 days"
    },
    "tags": ["habit", "ritual", "retention"],
    "impacted_stage": "post_first_use",
    "change_over_time": "Signal strengthened through week as more users adopted routine anchoring."
  },
  {
    "title": "Setup friction suppresses second use",
    "description": "Participants who needed to reconfigure settings each time skipped follow-up usage.",
    "evidence": [
      {
        "participant_code": "P01",
        "timestamp": "2026-03-03T21:30:00Z",
        "snippet": "[REDACTED] I avoided it because setup felt repetitive again."
      },
      {
        "participant_code": "P07",
        "timestamp": "2026-03-07T18:52:00Z",
        "snippet": "[REDACTED] I wanted to use it but not redo the same settings."
      }
    ],
    "confidence": "Med",
    "confidence_reason": "Present in 4 participants; indicates meaningful friction but sample narrower than top signal.",
    "recommended_experiment": {
      "hypothesis": "If prior configuration is remembered by default, second-use rate will improve.",
      "method": "Enable smart defaults from last run for eligible users.",
      "primary_metric": "Second-use conversion within 7 days",
      "decision_rule": "Ship if second-use conversion improves >=10% with no increase in correction edits.",
      "owner": "Growth PM",
      "timebox": "10 days"
    },
    "tags": ["friction", "configuration", "repeat-use"],
    "impacted_stage": "first_to_second_use",
    "change_over_time": "Stable but not increasing; concentrated in users with more complex workflows."
  },
  {
    "title": "Value perception drops when outcomes are not visible",
    "description": "Users skip Feature X on days when immediate output or progress feedback is not obvious.",
    "evidence": [
      {
        "participant_code": "P06",
        "timestamp": "2026-03-05T17:09:00Z",
        "snippet": "[REDACTED] Hard to tell what changed after I used it."
      },
      {
        "participant_code": "P12",
        "timestamp": "2026-03-08T19:44:00Z",
        "snippet": "[REDACTED] I skip it when I cannot see immediate payoff."
      }
    ],
    "confidence": "Med",
    "confidence_reason": "Repeated in open-text plus low confidence ratings in closed responses; effect size likely moderate.",
    "recommended_experiment": {
      "hypothesis": "If Feature X shows immediate outcome deltas after each use, users will maintain higher weekly frequency.",
      "method": "Introduce post-action result card with before/after summary.",
      "primary_metric": "Average weekly uses per active user",
      "decision_rule": "Keep feature if weekly usage increases >=8% and user-reported clarity improves.",
      "owner": "Design + PM",
      "timebox": "14 days"
    },
    "tags": ["value-visibility", "feedback", "habit"],
    "impacted_stage": "ongoing_usage",
    "change_over_time": "Signal emerged mid-week and persisted in end-of-week reflections."
  }
]
```

### Example Weekly Report 3: Journey mapping (1 page format)
**Period:** 2026-03-02 to 2026-03-08  
**Decision focus:** Reduce stalls from research to purchase decision  
**Top 3 User Signals + Recommendations**

```json
[
  {
    "title": "Cross-channel handoff from comparison doc to pricing page is the main stall point",
    "description": "Prospects often move from shared docs to pricing pages on mobile, then postpone due to context switching.",
    "evidence": [
      {
        "participant_code": "P14",
        "timestamp": "2026-03-03T13:40:00Z",
        "snippet": "[REDACTED] I checked pricing on phone after reading docs and decided to revisit later."
      },
      {
        "participant_code": "P17",
        "timestamp": "2026-03-06T08:26:00Z",
        "snippet": "[REDACTED] Switching devices broke momentum before final decision."
      }
    ],
    "confidence": "High",
    "confidence_reason": "Observed in both self-serve and assisted segments with repeated stage-transition delay logs.",
    "recommended_experiment": {
      "hypothesis": "If prospects can save and resume a prefilled pricing context across devices, decision stalls will decrease.",
      "method": "Add cross-device resume link from comparison page to personalized pricing state.",
      "primary_metric": "Research-to-pricing-to-trial conversion within 48h",
      "decision_rule": "Adopt if conversion improves >=12% and median time-to-next-step drops.",
      "owner": "Growth Team",
      "timebox": "14 days"
    },
    "tags": ["journey", "handoff", "cross-device"],
    "impacted_stage": "research_to_pricing",
    "change_over_time": "Persistent throughout week with no natural recovery in later days."
  },
  {
    "title": "Decision confidence rises only after peer validation touchpoint",
    "description": "Participants report low confidence until they receive peer or manager confirmation.",
    "evidence": [
      {
        "participant_code": "P15",
        "timestamp": "2026-03-04T16:11:00Z",
        "snippet": "[REDACTED] I was unsure until my teammate confirmed this matched our workflow."
      },
      {
        "participant_code": "P18",
        "timestamp": "2026-03-07T11:09:00Z",
        "snippet": "[REDACTED] Needed one external opinion before committing."
      }
    ],
    "confidence": "Med",
    "confidence_reason": "Strong narrative consistency, but concentration in team-based buyers reduces generality to solo buyers.",
    "recommended_experiment": {
      "hypothesis": "If we provide lightweight shareable decision summaries, team-validation delay will shrink.",
      "method": "Test share-to-teammate decision snapshot on pricing and proposal pages.",
      "primary_metric": "Time from pricing visit to purchase decision",
      "decision_rule": "Roll out if median decision time decreases >=20% for multi-stakeholder accounts.",
      "owner": "PM + Lifecycle",
      "timebox": "21 days"
    },
    "tags": ["confidence", "stakeholders", "purchase"],
    "impacted_stage": "evaluation_to_decision",
    "change_over_time": "Signal increased during late-week entries as purchase deadlines approached."
  },
  {
    "title": "SMS reminders outperform email for reactivation after stalled decisions",
    "description": "When participants stalled after pricing review, SMS prompts produced quicker return than email nudges.",
    "evidence": [
      {
        "participant_code": "P13",
        "timestamp": "2026-03-05T09:02:00Z",
        "snippet": "[REDACTED] Saw the text quickly and reopened the comparison."
      },
      {
        "participant_code": "P16",
        "timestamp": "2026-03-08T10:31:00Z",
        "snippet": "[REDACTED] Email got buried; text made me finish the decision."
      }
    ],
    "confidence": "Low",
    "confidence_reason": "Signal direction is clear but sample size for matched channel comparison is small this week.",
    "recommended_experiment": {
      "hypothesis": "If stalled users receive SMS-first reactivation within 6h, return-to-decision rate will exceed email-first follow-up.",
      "method": "Randomized channel assignment for stalled prospects in the same segment.",
      "primary_metric": "Reactivation to decision completion within 72h",
      "decision_rule": "Scale SMS-first if lift >=10% and opt-out rate remains below threshold.",
      "owner": "Lifecycle Marketing",
      "timebox": "14 days"
    },
    "tags": ["reactivation", "channel", "journey"],
    "impacted_stage": "stalled_post_pricing",
    "change_over_time": "Emergent late-week signal requiring confirmation next cycle."
  }
]
```
