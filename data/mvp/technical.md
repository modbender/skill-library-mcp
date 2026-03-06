# Technical Founder MVP Guide

You can build anything. Your challenge is knowing when to STOP.

## Your Specific Traps

1. **"It's easy to add"** — Just because you CAN add it doesn't mean you SHOULD. Every feature delays learning.

2. **Designing for 100K users with 0** — You don't need microservices, Kubernetes, or horizontal scaling yet. Monolith is fine. SQLite is fine.

3. **Building what's interesting vs important** — Real-time sync is fun to code. A landing page is boring. Ship the boring stuff first.

4. **Gold-plating before validation** — 100% test coverage for code nobody might use? Skip it. You'll refactor anyway if this works.

5. **"Just one more feature" before launch** — Set a ship date. Non-negotiable. Ship ugly. Learn fast.

## Tech Debt Rules for MVP

✅ Acceptable:
- Hardcoded values you'll make configurable later
- Manual processes you'll automate later
- Single-tenant when you'll need multi-tenant later
- No admin panel (use database directly)

❌ Not acceptable:
- Security holes (auth, data exposure)
- Data corruption risks
- Things that block the core user flow

## Ship Checklist

- [ ] Core hypothesis testable? (not "is this cool" but "do people need this")
- [ ] One happy path works end-to-end?
- [ ] Can you measure success/failure?
- [ ] Have you talked to 5+ potential users?
- [ ] Ship date is in calendar?

## What to Track at Launch

Forget vanity metrics. Track:
- **Activation:** Did they complete the core action?
- **Return:** Did they come back unprompted?
- **Referral:** Did they tell anyone?

One strong signal > many weak signals.
