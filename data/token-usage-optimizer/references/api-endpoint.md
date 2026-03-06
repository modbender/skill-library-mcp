# Anthropic OAuth Usage API

Official API endpoint for Claude Code usage monitoring.

## Endpoint

```
GET https://api.anthropic.com/api/oauth/usage
```

## Headers

```
Authorization: Bearer <access-token>
anthropic-beta: oauth-2025-04-20
```

## Example Request

```bash
curl -s "https://api.anthropic.com/api/oauth/usage" \
  -H "Authorization: Bearer sk-ant-oat01-..." \
  -H "anthropic-beta: oauth-2025-04-20"
```

## Response Format

```json
{
  "five_hour": {
    "utilization": 22.0,
    "resets_at": "2026-02-20T14:00:00.364238+00:00"
  },
  "seven_day": {
    "utilization": 49.0,
    "resets_at": "2026-02-24T10:00:01.364256+00:00"
  },
  "seven_day_oauth_apps": null,
  "seven_day_opus": null,
  "seven_day_sonnet": {
    "utilization": 35.0,
    "resets_at": "2026-02-24T16:00:00.364265+00:00"
  },
  "seven_day_cowork": null,
  "iguana_necktie": null,
  "extra_usage": {
    "is_enabled": true,
    "monthly_limit": 5000,
    "used_credits": 4887.0,
    "utilization": 97.74
  }
}
```

## Fields

### `five_hour`
- **Rolling 5-hour window** session limit
- Prevents rapid bursts of usage
- Resets every 5 hours
- `utilization`: percentage (0-100)
- `resets_at`: ISO 8601 timestamp (UTC)

### `seven_day`
- **Rolling 7-day window** weekly limit
- Main quota for subscription tier
- Resets weekly
- `utilization`: percentage (0-100)
- `resets_at`: ISO 8601 timestamp (UTC)

### `seven_day_sonnet` (Optional)
- Model-specific weekly quota for Sonnet
- Not all plans have this

### `extra_usage` (Optional)
- Additional monthly credits
- `monthly_limit`: total credits per month
- `used_credits`: credits consumed
- `utilization`: percentage (0-100)

## Rate Limits

- No documented rate limits for this endpoint
- Recommended: cache responses for 5-10 minutes
- Avoid excessive polling (>1 req/min)

## Error Responses

### Authentication Error

```json
{
  "type": "error",
  "error": {
    "type": "authentication_error",
    "message": "OAuth authentication is currently not supported.",
    "details": {
      "error_visibility": "user_facing"
    }
  },
  "request_id": "req_..."
}
```

**Cause:** Invalid or expired access token

**Fix:** Use refresh token to get new access token

### Missing Beta Header

If you forget `anthropic-beta: oauth-2025-04-20`, you may get an error or outdated response format.

## Notes

- All timestamps are in UTC
- `utilization` is a float (can have decimals)
- `resets_at` format: `YYYY-MM-DDTHH:MM:SS.ssssss+00:00`
- Some fields may be `null` depending on your plan

## Subscription Tiers

Different tiers have different quota limits (not exposed in API):

- **Pro ($20/mo):** Lower limits
- **Max 100 ($100/mo):** Medium limits
- **Max 200 ($200/mo):** Higher limits

The API doesn't expose absolute quota limits, only utilization percentage.

## Best Practices

1. **Cache responses** for 5-10 minutes
2. **Use refresh token** for long-running scripts
3. **Monitor `five_hour` more frequently** than `seven_day` (it resets faster)
4. **Set alerts** at 50% (five_hour) and 80% (seven_day)
5. **Track burn rate** to optimize subscription usage
