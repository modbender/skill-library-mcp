# Setup — WhatsApp Business API

This file guides initial configuration when the user first uses this skill.

## Integration

Ask how they want to use WhatsApp Business:
- "Are you building customer support, notifications, or marketing campaigns?"
- "Do you have a Meta Business account with WhatsApp access, or starting fresh?"
- "Want me to help whenever WhatsApp comes up, or only when you ask?"

## Understand Their Use Case

- What's their business type? (e-commerce, SaaS, services)
- What messages will they send? (support, order updates, promotions)
- Volume expectations? (affects tier and rate limits)

## Technical Context

- What's their stack? (Node, Python, PHP, etc.)
- Are they using webhooks already?
- Do they need multiple phone numbers?

## Getting Credentials

Guide them through Meta Business setup if needed:

1. **Meta Business Account** at business.facebook.com
2. **WhatsApp Business Account (WABA)** — created in Meta Business Suite
3. **System User** with WhatsApp permissions
4. **Access Token** — generate from System User

Key IDs to collect:
- Phone Number ID (from WhatsApp Manager)
- Business Account ID (from WhatsApp Manager)
- App Secret (from App Dashboard)

## Memory Storage

Store context in `~/whatsapp-business-api/memory.md`:
- Their primary use case (support, notifications, marketing)
- Business type if mentioned
- Phone numbers registered
- Template categories they use
- Webhook URL if configured

## When Ready

Once you know:
1. What they're building (support, notifications, etc.)
2. Basic credentials are set up

...you're ready to help. Details emerge naturally through use.
