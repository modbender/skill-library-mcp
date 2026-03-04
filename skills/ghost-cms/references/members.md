# Members & Subscribers

Managing subscriber tiers, member access, and subscription status.

## Listing Members

### All Members

```bash
curl "${GHOST_URL}/ghost/api/admin/members/?limit=15" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Filter by Status

**Paid members only:**
```bash
curl "${GHOST_URL}/ghost/api/admin/members/?filter=status:paid" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

**Free members only:**
```bash
curl "${GHOST_URL}/ghost/api/admin/members/?filter=status:free" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

**Comped members:**
```bash
curl "${GHOST_URL}/ghost/api/admin/members/?filter=status:comped" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Recent Members

```bash
curl "${GHOST_URL}/ghost/api/admin/members/?order=created_at%20desc&limit=10" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Search Members

```bash
curl "${GHOST_URL}/ghost/api/admin/members/?search=keyword" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Searches name and email fields.

## Member Structure

```json
{
  "members": [{
    "id": "member_id_here",
    "email": "member@example.com",
    "name": "Member Name",
    "status": "free",
    "created_at": "2026-01-31T12:00:00.000Z",
    "subscribed": true,
    "labels": ["vip", "newsletter-subscriber"],
    "tiers": [],
    "newsletters": [{
      "id": "newsletter_id",
      "name": "Newsletter Name"
    }]
  }]
}
```

## Managing Subscription Tiers

### List All Tiers

```bash
curl "${GHOST_URL}/ghost/api/admin/tiers/" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Returns:
```json
{
  "tiers": [{
    "id": "tier_id",
    "name": "Premium",
    "slug": "premium",
    "description": "Access to all premium content",
    "active": true,
    "type": "paid",
    "currency": "usd",
    "monthly_price": 500,
    "yearly_price": 5000,
    "benefits": [
      "Early access to posts",
      "Exclusive content",
      "Community access"
    ]
  }]
}
```

### Create Subscription Tier

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/tiers/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "tiers": [{
      "name": "Premium Plus",
      "slug": "premium-plus",
      "description": "Extended premium access",
      "active": true,
      "type": "paid",
      "currency": "usd",
      "monthly_price": 1000,
      "yearly_price": 10000,
      "benefits": [
        "All Premium benefits",
        "1-on-1 consultations",
        "Private Discord access"
      ]
    }]
  }'
```

Prices are in **cents** (500 = $5.00).

### Update Tier

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/tiers/${TIER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "tiers": [{
      "monthly_price": 1200,
      "benefits": [
        "Updated benefit 1",
        "Updated benefit 2"
      ]
    }]
  }'
```

## Managing Individual Members

### Add Member

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/members/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "members": [{
      "email": "newmember@example.com",
      "name": "New Member",
      "subscribed": true,
      "labels": ["imported"]
    }]
  }'
```

### Update Member

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "members": [{
      "name": "Updated Name",
      "labels": ["vip", "active"]
    }]
  }'
```

### Give Complimentary Subscription

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "members": [{
      "comped": true,
      "tiers": [{"id": "tier_id_here"}]
    }]
  }'
```

Makes a free member into a comped paid member with tier access.

### Remove Member

```bash
curl -X DELETE "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

## Member Labels

Labels help organize and segment members.

### Add Labels

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "members": [{
      "labels": ["existing-label", "new-label"]
    }]
  }'
```

**Note:** Labels are **replaced**, not appended. Include existing labels to keep them.

### List Members by Label

```bash
curl "${GHOST_URL}/ghost/api/admin/members/?filter=label:vip" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

## Newsletter Subscriptions

### Subscribe Member to Newsletter

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "members": [{
      "newsletters": [
        {"id": "newsletter_id_here"}
      ]
    }]
  }'
```

### Unsubscribe from Newsletter

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "members": [{
      "newsletters": []
    }]
  }'
```

## Member Content Access

### Check Member's Tier Access

```bash
curl "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.members[0].tiers'
```

### Posts Accessible to Member

Determine what content a member can see based on their tier:

1. Get member's tiers
2. Query posts filtered by `visibility:public` OR member's tier IDs
3. Return accessible posts

```bash
# Get member tiers
MEMBER_TIERS=$(curl -s "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq -r '.members[0].tiers[].id' | paste -sd "," -)

# Query posts (simplified - actual implementation needs proper filter syntax)
curl "${GHOST_URL}/ghost/api/admin/posts/?filter=visibility:[public,members,paid]" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

## Subscription Management

### Active Subscriptions

```bash
curl "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/?include=subscriptions" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Returns member with subscription details:
- Plan
- Status (active, canceled, past_due)
- Current period end
- Cancel at period end

### Cancel Subscription

Subscription cancellation is typically handled through:
- Member portal (member self-service)
- Stripe dashboard (if using Stripe)
- Ghost Admin UI

API support for cancellation is limited; use Stripe API for advanced subscription management.

## Bulk Operations

### Import Members (CSV)

Ghost Admin provides CSV import UI. For API-based import:

```bash
# Read CSV, POST each member
while IFS=, read -r email name; do
  curl -X POST "${GHOST_URL}/ghost/api/admin/members/" \
    -H "Authorization: Ghost ${GHOST_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"members\": [{
        \"email\": \"$email\",
        \"name\": \"$name\"
      }]
    }"
  sleep 0.5  # Rate limiting
done < members.csv
```

### Bulk Label Update

```bash
# Add "campaign-2026" label to all free members
MEMBERS=$(curl -s "${GHOST_URL}/ghost/api/admin/members/?filter=status:free&limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq -r '.members[].id')

for MEMBER_ID in $MEMBERS; do
  # Get current labels
  CURRENT_LABELS=$(curl -s "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
    -H "Authorization: Ghost ${GHOST_KEY}" | \
    jq -c '.members[0].labels')
  
  # Add new label
  NEW_LABELS=$(echo $CURRENT_LABELS | jq '. + ["campaign-2026"] | unique')
  
  # Update member
  curl -X PUT "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
    -H "Authorization: Ghost ${GHOST_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"members\": [{
        \"labels\": $NEW_LABELS
      }]
    }"
done
```

## Common Workflows

### New Subscriber Welcome

When a new subscriber signs up:
1. Webhook triggers (member.added)
2. Send welcome email (via newsletter or custom)
3. Assign "new-subscriber" label
4. Add to onboarding newsletter series

### Tier Upgrade

Member upgrades from free to paid:
1. Webhook triggers (member.subscription.updated)
2. Update labels ("free" → "paid", add "premium")
3. Send welcome-to-premium email
4. Grant access to exclusive Discord/community

### Churn Prevention

Identify at-risk members:
1. Query members with `last_seen_at` > 30 days ago
2. Filter for paid members
3. Send re-engagement email
4. Offer limited-time discount or exclusive content

## Member Portal

Ghost provides a member portal for self-service:
- Subscription management
- Newsletter preferences
- Profile updates
- Billing history

Portal URL: `${GHOST_URL}/portal`

Configure portal settings in Ghost Admin → Settings → Portal.

## Best Practices

- **Use labels** - Segment members for targeted communication
- **Respect privacy** - Don't expose member emails unnecessarily
- **Automate onboarding** - Welcome new members with automated flows
- **Monitor churn** - Track subscription cancellations and reasons
- **Offer comp access** - Strategically give free premium access for loyalty/value
- **Communicate changes** - Notify members before tier pricing/benefit changes
- **Sync with CRM** - Integrate with external tools for advanced member management
