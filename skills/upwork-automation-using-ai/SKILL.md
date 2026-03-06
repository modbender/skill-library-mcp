---
name: upwork-automation-using-ai
description: "Automate Upwork job search and proposal drafting in one browser
  session using the Browser Relay/Browser Automation workflow. Use when the user
  wants to: (1) open/login Upwork, (2) find top matching jobs from explicit
  criteria, (3) filter out disqualifiers, (4) open the best job, and (5) fill
  proposal fields without submitting. Also use when the user asks to persist in
  the same tab/session across steps."
---


# Upwork Automation Using AI

## Workflow

1. Keep one active browser session/tab unless user explicitly asks to switch.
2. Open Upwork and ensure login state.
3. If logged out, run login automation:
   - go to Upwork login page
   - prefer "Continue with Google" when user asks for Gmail login
   - fill email/password only from user-provided credentials for this run
   - complete required next step (password, captcha/2FA/manual checkpoint)
   - verify logged-in indicators before continuing
4. Collect/confirm criteria:
   - allowed job types/stack
   - minimum client quality thresholds
   - disqualifiers
   - proposal constraints (submit or draft-only)
5. Search jobs and shortlist visible matches.
6. Reject jobs with any disqualifier.
7. Pick the best remaining job (or top N if user asks).
8. Open job detail and click Apply.
9. Detect proposal location:
   - if same tab, continue
   - if new tab/window, switch to it (or ask user to activate once if tool cannot switch)
10. Fill proposal fields completely.
11. Stop before submission unless user explicitly says submit.

## Hard Rules

- Do not submit proposal unless user explicitly says to submit now.
- Stay in the same tab/session unless user requests switching.
- After clicking Apply, immediately check whether proposal opened in same tab.
- If proposal opens in a new tab/window, auto-switch to that tab when the tool supports tab targeting.
- If auto-switch is not supported by the active tool, instruct user to activate the new tab once, then continue there.
- If a modal blocks actions, close modal first, then continue.
- Validate on-page state with screenshot/text checks before risky clicks.
- Never persist credentials to skill files or notes; use credentials only for the active run.

## Job Filtering Rubric

Treat a job as valid only if all required checks pass.

Required:
- Job type matches user scope (ecommerce stack or general development)
- Posted within time window (default <= 3 days unless user changes)
- Client quality meets thresholds (e.g., avg hourly >= $10 if visible)
- Fixed budget >= $100 when fixed-price budget is visible

Disqualify when any is true:
- Individual-only hiring restriction
- Urgent/start-today pressure language
- No/poor payment history when user disallows it
- Requires screen share, onsite reporting, strict time tracking, or skill tests (if disallowed)

If uncertain from visible data:
- mark as "needs manual review"
- do not claim it fully passed

## Proposal Drafting Template

Use concise, specific structure:

1. Direct fit opening (stack + outcome)
2. Delivery plan (milestones/timeline)
3. Relevant proof (similar builds)
4. Communication cadence
5. Clear CTA

Prefer concrete numbers and short bullets over long paragraphs.

## Execution Notes (Browser Reliability)

- Prefer deterministic selectors and verify each transition with screenshot/get_text.
- If generic selectors misfire, target by nearby unique text.
- If automation cannot switch to newly opened tab, ask user to bring proposal tab active and confirm.
- Keep browser open at end and report exact completion status:
  - job selected
  - proposal fields filled
  - submission state (not submitted)

## Output Format to User

After completing work, respond with:

- Selected job: <title>
- Why selected: <criteria match summary>
- Fields filled: <key fields>
- Submission: Not submitted
- Next action: “Review and tell me ‘submit now’ if you want me to send it.”
