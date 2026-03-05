---
name: reveal-feedback
description: Interact with Reveal feedback infrastructure to manage products, create review tasks, read AI-analyzed user feedback, get sentiment insights, view submissions, manage notifications, and register webhooks. Use when the user asks about product feedback, user reviews, testing tasks, sentiment analysis, top issues, review submissions, marketing videos, or anything related to their Reveal account.
metadata: {"openclaw":{"requires":{"env":["REVEAL_API_KEY"]},"primaryEnv":"REVEAL_API_KEY","emoji":"📊","homepage":"https://testreveal.ai"}}
---

# Reveal Feedback Infrastructure

Reveal is a universal feedback platform where human reviewers screen-record themselves using products and provide AI-analyzed feedback. This skill connects to the Reveal REST API to manage the full feedback lifecycle.

## Authentication

All API calls require the `REVEAL_API_KEY` environment variable. The key is a vendor API key generated from the Reveal dashboard under Settings → API Keys.

Every request uses this header:
```
Authorization: Bearer $REVEAL_API_KEY
```

Base URL: `https://www.testreveal.ai/api/v1`
(Override with `REVEAL_BASE_URL` env var if set.)

## Capabilities

### 1. Check dashboard overview

Fetch products, active review tasks, and unread notifications to give the user a quick status update.

Steps:
1. GET `/products` to list vendor products
2. GET `/review-tasks?status=active` to list active tasks
3. GET `/notifications?unread=true&limit=5` to get unread notifications
4. Summarize: product count, active tasks with submission progress, and recent notifications

### 2. Get feedback insights for a product

Fetch AI-aggregated insights: top issues, top positives, sentiment distribution, and suggestions.

Steps:
1. GET `/products` to find the product ID matching the user's request
2. GET `/insights/{productId}` to get aggregated insights
3. Present: sentiment breakdown, top issues ranked by frequency, top positives, unique issue count

### 3. Get product analytics

Fetch quantitative metrics for a product.

Steps:
1. GET `/products/{productId}/analytics`
2. Present: total submissions, analyzed count, average completion rate, sentiment distribution, top issues, top positives

### 4. View review submissions

Get individual review submissions with transcripts, AI analysis, sentiment, and issue counts.

Steps:
1. GET `/review-tasks?status=active&limit=5` to find the relevant task (or use a task ID if provided)
2. GET `/review-tasks/{taskId}/submissions` to get all submissions
3. For each submission, present: status, sentiment, issue count, positive count, transcript preview

### 5. Create a review task

Create a new user-testing task so reviewers can test a product.

Steps:
1. GET `/products` to find the product matching the user's description
2. Extract from the user's message: title, objective, steps, feedback focus, reviewer count
3. POST `/review-tasks` with body:
```json
{
  "title": "extracted title",
  "productId": "matched product ID",
  "requiredReviewers": 5,
  "instructions": {
    "objective": "what the reviewer should accomplish",
    "steps": "step-by-step instructions",
    "feedback": "what feedback to focus on"
  }
}
```
4. Confirm creation with task ID and details

### 6. Update a review task

Close, pause, or modify an existing review task.

Steps:
1. PATCH `/review-tasks/{taskId}` with fields to update (status, title, description, requiredReviewers)
2. Confirm the update

### 7. List products

Show all products registered on the vendor's Reveal account.

Steps:
1. GET `/products?limit=50`
2. Present each product: name, category, platform support (web/mobile), website

### 8. Get notifications

Check for new activity on Reveal.

Steps:
1. GET `/notifications?unread=true&limit=20`
2. Present notification messages with timestamps
3. If user says to mark as read: PATCH `/notifications` with `{"markAllRead": true}`

### 9. Register a webhook

Set up real-time event notifications.

Steps:
1. POST `/webhooks` with body:
```json
{
  "url": "https://user-provided-url",
  "events": ["review.submitted", "review.analyzed", "task.completed", "video.generated"]
}
```
2. Return the webhook ID and signing secret. Instruct user to store the secret securely.

### 10. List webhooks

Steps:
1. GET `/webhooks`
2. Present each webhook: URL, subscribed events, active status

## Response format

All API responses follow this structure:
- Success: `{ "data": { ... } }`
- Error: `{ "error": { "code": "ERROR_CODE", "message": "description" } }`

## Guardrails

- Never expose or log the API key in responses to the user
- If an API call fails with 401, tell the user their API key may be invalid or expired
- If a product is not found, suggest listing products first
- When creating review tasks, always confirm the details with the user before sending the POST
- Do not fabricate feedback data — only report what the API returns
