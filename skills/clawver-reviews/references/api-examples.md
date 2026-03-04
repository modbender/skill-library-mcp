# Reviews API Examples

## Good Example: Fetch and Respond to Unanswered Reviews

```bash
curl https://api.clawver.store/v1/stores/me/reviews \
  -H "Authorization: Bearer $CLAW_API_KEY"

curl -X POST https://api.clawver.store/v1/reviews/{reviewId}/respond \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"body":"Thanks for your feedback. We are improving shipping times."}'
```

Why this works: it uses owner review endpoints and structured response body.

## Bad Example: Oversized Response Body

A response over 1000 characters.

Why it fails: review response length is capped.

Fix: keep response concise and actionable.

## Bad Example: Responding to a Review You Do Not Own

Attempting to respond to a review from another store.

Why it fails: only the owning store can post `POST /v1/reviews/{reviewId}/respond`.

Fix: use the API key for the store that owns the review.
