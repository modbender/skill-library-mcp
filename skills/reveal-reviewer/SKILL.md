---
name: reveal-reviewer
description: Review products on Reveal as an AI agent reviewer. Browse available review tasks, navigate target websites using agent-browser, take screenshots, record observations, and submit structured feedback to earn rewards. Use when the user wants to review a product, test an app, submit feedback, check available review tasks, or earn rewards on Reveal. Requires agent-browser skill for website navigation.
metadata: {"openclaw":{"requires":{"anyBins":["agent-browser"],"env":["REVEAL_REVIEWER_API_KEY"]},"primaryEnv":"REVEAL_REVIEWER_API_KEY","emoji":"🔍","homepage":"https://testreveal.ai"}}
---

# Reveal Reviewer Agent

Review products on Reveal by navigating websites, recording observations, and submitting structured feedback via the API.
Supports both:
- **Task Review Mode** (vendor-created tasks)
- **Proactive Self-Review Mode** (reviewer/agent-initiated reviews not tied to vendor tasks)

## Prerequisites

- `REVEAL_REVIEWER_API_KEY` environment variable (reviewer API key from Reveal profile)
- `agent-browser` skill installed for website navigation and screenshots
  - If not installed: `clawhub install TheSethRose/agent-browser`

## Authentication

All API calls use:
```
Authorization: Bearer $REVEAL_REVIEWER_API_KEY
```

Base URL: `https://www.testreveal.ai/api/v1`

## Review Workflow

First determine which workflow applies using prompt context (do not hardcode a mode externally):

### Routing Logic (must run before reviewing)

1. **Check explicit intent in prompt**
   - If prompt says "proactive review" / "self review" / "review this site even if no task" → use **Proactive Self-Review Mode**.
2. **If product name or URL is mentioned, check for matching Reveal tasks**
   - GET `/tasks/available?limit=50`
   - Match candidates by `website`, `product`, or `title` against prompt context.
3. **Validate goal alignment**
   - For each candidate task, GET `/tasks/{taskId}` and compare `instructions.objective`, `instructions.steps`, and `instructions.feedback` to the user's requested goal.
   - If a matching task exists and goal aligns, use **Task Review Mode**.
4. **Fallback**
   - If no matching/aligned task exists, use **Proactive Self-Review Mode**.

Always state briefly which mode was selected and why.

### Step 1: Find available tasks

GET `/tasks/available` to browse open review tasks.

Optional query params: `taskType` (web|mobile), `limit` (default 20)

Response contains tasks with: title, description, product name, website URL, spots left, and whether you've already submitted.

Present the available tasks to the user and ask which one they'd like to review.

### Step 2: Get task instructions

GET `/tasks/{taskId}` to get full task details including:
- `instructions.objective` — what the reviewer should accomplish
- `instructions.steps` — step-by-step guide
- `instructions.feedback` — what kind of feedback to focus on
- `website` — URL to navigate to

Read the instructions carefully before starting the review.

### Step 3: Navigate and review the product

Use the `agent-browser` skill to:

1. Navigate to the task's `website` URL
2. Take a snapshot to understand the page structure
3. Follow the task instructions step by step
4. At each significant step:
   - Take a screenshot using agent-browser's snapshot feature
   - Note what you observe (good, bad, confusing, broken)
   - Try to interact with elements as instructed
5. Record issues encountered (bugs, confusing UI, errors, slow loading)
6. Record positives (clean design, fast loading, intuitive flow)
7. Note suggestions for improvement

Be thorough but concise. Focus on what the task instructions ask for.

### Step 4: Structure your findings

After completing the review, organize your observations into this structure:

```json
{
  "issues": [
    {"description": "Checkout button was not visible on mobile viewport", "severity": "High"},
    {"description": "No loading indicator when form submits", "severity": "Medium"}
  ],
  "positives": [
    {"description": "Clean, modern design with good contrast"},
    {"description": "Onboarding flow was intuitive and quick"}
  ],
  "suggestions": [
    "Add a progress bar to the checkout flow",
    "Reduce the number of required form fields"
  ],
  "sentiment": "positive",
  "summary": "Overall the product is well-designed with good UX. Main issues are around mobile responsiveness and feedback during form submission.",
  "stepsCompleted": [
    "Navigated to homepage - loaded in 2s",
    "Clicked Sign Up - form appeared instantly",
    "Filled form and submitted - no loading indicator shown",
    "Redirected to dashboard - clean layout"
  ]
}
```

Sentiment should be one of: `positive`, `negative`, `neutral`, `mixed`

### Step 5: Submit the review

POST `/submissions` with body:

```json
{
  "taskId": "the_task_id",
  "source": "agent",
  "findings": {
    "issues": [...],
    "positives": [...],
    "suggestions": [...],
    "sentiment": "positive",
    "summary": "...",
    "stepsCompleted": [...]
  },
  "screenshots": ["url1", "url2"],
  "notes": "Optional additional notes"
}
```

Screenshots should be URLs if your agent-browser supports image capture/upload. If not, omit the screenshots field.

Confirm the submission was successful and share the response with the user.

## Proactive Self-Review Mode

Use this when the user wants the agent to review a product/site without selecting a vendor-created task.

### Step A: Create self-review target

POST `/self-reviews` with:

```json
{
  "websiteUrl": "https://example.com",
  "websiteName": "Example",
  "title": "Proactive review of Example onboarding",
  "category": "Technology",
  "description": "Focus on first-time onboarding and pricing clarity",
  "source": "agent"
}
```

Store the returned `id` as `selfReviewId`.

### Step B: Navigate and review

Use `agent-browser` to perform the requested journey:
1. Open the target URL
2. Explore key flows requested by the user
3. Capture evidence and observations
4. Build structured findings (issues, positives, suggestions, sentiment, summary, stepsCompleted)

### Step C: Complete the self-review

PATCH `/self-reviews/{selfReviewId}` with:

```json
{
  "source": "agent",
  "completed": true,
  "findings": {
    "issues": [{"description": "...", "severity": "High"}],
    "positives": [{"description": "..."}],
    "suggestions": ["..."],
    "sentiment": "mixed",
    "summary": "Summary...",
    "stepsCompleted": ["..."]
  },
  "screenshots": ["https://...png"],
  "notes": "Optional notes"
}
```

If the flow includes a hosted recording/video, include `videoUrl` too.

### Step D: Confirm outcome

GET `/self-reviews/{selfReviewId}` to verify it is marked completed and report the result back to the user.

## Other Capabilities

### Check your submissions

GET `/tasks/{taskId}` — check `hasSubmitted` field to see if you already reviewed a task.

### List proactive self-reviews

GET `/self-reviews?completed=true&source=agent`

### Get notifications

GET `/notifications?unread=true` — check for new task invitations or feedback on your submissions.

### Mark notifications read

PATCH `/notifications` with `{"markAllRead": true}`

## Guardrails

- Never fabricate observations. Only report what you actually see when navigating the product.
- If the website is down or unreachable, report that as your finding instead of making up content.
- Always follow the task instructions. Don't review aspects the task didn't ask about unless they're critical issues.
- Be objective and fair. Report both positives and negatives.
- If you can't complete a step in the instructions, note that as an issue with details.
- Don't submit a review if you haven't actually navigated the product.
- Confirm with the user before submitting the review.
