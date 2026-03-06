# API Error Codes & Troubleshooting

## Common Error Codes

- `401 unauthorized` - API key missing, malformed, or invalid
- `402 subscription_required` - workspace/account needs an active subscription
- `403 tier_not_allowed` - current plan tier does not include the attempted capability
- `422 invalid_payload` - request shape or enum values are invalid
- `429 rate_limited` - too many requests in a short window

---

## Troubleshooting

**"GENVIRAL_API_KEY is required"**
Export the environment variable: `export GENVIRAL_API_KEY="your_public_id.your_secret"`

**"No rendered image URLs found"**
The slideshow has not been rendered yet. Run `render` first.

**API returns 401, 402, or 403**
- `401`: verify API key format (`public_id.secret`) and token validity
- `402 subscription_required`: activate or upgrade subscription
- `403 tier_not_allowed`: your tier does not permit that feature

**Render takes too long**
Each slide takes 2-5 seconds. For 5 slides, expect up to 25 seconds.

**`update-slideshow` returns 422**
- Check for `null` values (omit fields instead of setting `null`)
- Check that `background_filters` has all 10 sub-fields
- Check that no slide has an `index` field
- Check that every slide has at minimum `image_url` and `text_elements`
