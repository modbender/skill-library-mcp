# Business Profile & Phone Numbers — WhatsApp Business API

## Business Profile

### Get Profile

```bash
curl "https://graph.facebook.com/v21.0/$WHATSAPP_PHONE_NUMBER_ID/whatsapp_business_profile?fields=about,address,description,email,profile_picture_url,websites,vertical" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

Response:

```json
{
  "data": [
    {
      "about": "Your trusted partner",
      "address": "123 Business St, City",
      "description": "We help businesses grow with innovative solutions.",
      "email": "support@example.com",
      "profile_picture_url": "https://...",
      "websites": ["https://example.com"],
      "vertical": "RETAIL"
    }
  ]
}
```

### Update Profile

```bash
curl -X POST "https://graph.facebook.com/v21.0/$WHATSAPP_PHONE_NUMBER_ID/whatsapp_business_profile" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "about": "Your trusted partner since 2020",
    "address": "456 New Address, City",
    "description": "We help businesses grow with innovative AI solutions.",
    "email": "hello@example.com",
    "websites": ["https://example.com", "https://blog.example.com"],
    "vertical": "TECH"
  }'
```

### Business Verticals

| Vertical | Description |
|----------|-------------|
| UNDEFINED | Not specified |
| OTHER | Other category |
| AUTO | Automotive |
| BEAUTY | Beauty & cosmetics |
| APPAREL | Clothing & fashion |
| EDU | Education |
| ENTERTAIN | Entertainment |
| EVENT_PLAN | Event planning |
| FINANCE | Financial services |
| GROCERY | Groceries |
| GOVT | Government |
| HOTEL | Hotels & lodging |
| HEALTH | Healthcare |
| NONPROFIT | Non-profit |
| PROF_SERVICES | Professional services |
| RETAIL | Retail |
| TRAVEL | Travel |
| RESTAURANT | Restaurant & food |
| NOT_A_BIZ | Not a business |

---

## Phone Numbers

### Get Phone Number Details

```bash
curl "https://graph.facebook.com/v21.0/$WHATSAPP_PHONE_NUMBER_ID?fields=display_phone_number,verified_name,quality_rating,messaging_limit_tier" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

Response:

```json
{
  "display_phone_number": "+1 234 567 8900",
  "verified_name": "My Business",
  "quality_rating": "GREEN",
  "messaging_limit_tier": "TIER_1K",
  "id": "123456789"
}
```

### List All Phone Numbers

```bash
curl "https://graph.facebook.com/v21.0/$WHATSAPP_BUSINESS_ACCOUNT_ID/phone_numbers" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

---

## Quality Rating

| Rating | Meaning | Action |
|--------|---------|--------|
| GREEN | High quality | Continue as normal |
| YELLOW | Medium quality | Review messaging practices |
| RED | Low quality | Risk of restrictions |

Quality is based on:
- User blocks/reports
- Template quality
- Engagement rates

---

## Messaging Limit Tiers

| Tier | Unique Users/Day | Requirements |
|------|------------------|--------------|
| TIER_1K | 1,000 | New accounts |
| TIER_10K | 10,000 | Good standing for 7 days |
| TIER_100K | 100,000 | Good standing, verified business |
| TIER_UNLIMITED | Unlimited | Consistent high quality |

**Note:** Limits apply to business-initiated conversations only. Replies within 24h window don't count.

---

## Business Verification

### Check Verification Status

```bash
curl "https://graph.facebook.com/v21.0/$WHATSAPP_BUSINESS_ACCOUNT_ID?fields=account_review_status" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

### Verification Levels

| Level | Benefits |
|-------|----------|
| Unverified | Basic features, limited templates |
| Official Business Account (OBA) | Green checkmark, higher limits |

### Get Verified

1. Complete business profile with accurate info
2. Submit verification documents via Business Manager
3. Wait for Meta review (1-5 business days)

---

## Two-Step Verification

### Enable

```bash
curl -X POST "https://graph.facebook.com/v21.0/$WHATSAPP_PHONE_NUMBER_ID" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pin": "123456"}'
```

### Disable

```bash
curl -X DELETE "https://graph.facebook.com/v21.0/$WHATSAPP_PHONE_NUMBER_ID" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

---

## Display Name

### Request Name Change

```bash
curl -X POST "https://graph.facebook.com/v21.0/$WHATSAPP_PHONE_NUMBER_ID/request_code" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code_method": "SMS",
    "language": "en"
  }'
```

Display name changes require re-verification.

---

## Common Traps

- **Profile pic not updating** — Changes can take 24h to propagate
- **Vertical locked** — Can only change before verification
- **Quality degraded** — Review sent messages for spam-like patterns
- **Tier not increasing** — Need 7+ days of good quality
