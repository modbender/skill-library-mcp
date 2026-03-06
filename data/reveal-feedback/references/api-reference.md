# Reveal REST API v1 Reference

Base URL: `https://www.testreveal.ai/api/v1`
Auth: `Authorization: Bearer <REVEAL_API_KEY>`

## Products

### GET /products
List vendor's products.
Query params: `limit` (int, default 20, max 50)
Response: `{ "data": { "products": [...], "total": n } }`

### GET /products/{id}
Get product details with review task count and total submissions.

### GET /products/{id}/analytics
Get product analytics.
Response fields: `productId`, `productName`, `reviewTasks`, `totalSubmissions`, `analyzedSubmissions`, `averageCompletionRate` (int, percent), `sentimentDistribution` (object), `topIssues` (array of {issue, mentions}), `topPositives` (array of {positive, mentions})

## Review Tasks

### GET /review-tasks
List review tasks.
Query params: `status` (active|completed|all), `productId`, `limit` (max 50)
Response: `{ "data": { "reviewTasks": [...], "total": n } }`

Each task: `id`, `title`, `description`, `status`, `taskType` (web|mobile), `productId`, `product`, `website`, `requiredReviewers`, `completedReviews`, `submissionCount`, `createdAt`

### POST /review-tasks
Create a review task.
Required body fields: `title` (string), `productId` (string), `instructions` (object with `objective`, `steps`, `feedback`)
Optional: `description`, `website`, `taskType` (web|mobile), `requiredReviewers` (int, default 5)

### GET /review-tasks/{id}
Get full task details including instructions and store URLs.

### PATCH /review-tasks/{id}
Update a task. Body: `status`, `title`, `description`, `requiredReviewers` (all optional)

## Submissions

### GET /review-tasks/{id}/submissions
Get all submissions for a task.
Query params: `status` (pending|completed|all)

Each submission: `index`, `status`, `videoUrl`, `submittedAt`, `notes`, `hasAnalysis`, `sentiment`, `issueCount`, `positiveCount`, `visualSummaryUrl`, `transcript`, `analysis` (object with `issues`, `positives`, `suggestions`, `sentiment`, `usabilityFriction`, `visualEvents`, `userExperience`)

## Insights

### GET /insights/{productId}
Aggregated AI insights across all submissions for a product.
Response: `totalAnalyzedSubmissions`, `sentimentDistribution`, `topIssues` (array of {text, mentions}), `topPositives`, `topSuggestions`, `uniqueIssues`, `uniquePositives`

## Webhooks

### GET /webhooks
List registered webhooks.

### POST /webhooks
Register a webhook.
Body: `url` (string, HTTPS required), `events` (array of: review.submitted, review.analyzed, task.completed, video.generated)
Response includes `secret` for HMAC-SHA256 signature verification via `X-Reveal-Signature` header.

### DELETE /webhooks?id={webhookId}
Delete a webhook.

## Notifications

### GET /notifications
Query params: `unread` (true|false, default true), `limit` (max 50)

### PATCH /notifications
Mark as read. Body: `{ "notificationId": "..." }` or `{ "markAllRead": true }`

## Error format

All errors: `{ "error": { "code": "ERROR_CODE", "message": "human readable" } }`
Common codes: UNAUTHORIZED (401), NOT_FOUND (404), VALIDATION_ERROR (400)
