---
name: plvr-event-discovery
description: Discover and compare live events on plvr.io by date, city, genre, and budget using the public web flow. Provide concise recommendations, visible pricing/availability signals, and planning details. This skill does not execute checkout or payment.
---

# PLVR Event Discovery (Safe Scope)

## Purpose

Use browser automation to help users discover and compare events on `https://plvr.io`.

This skill is intentionally limited to **discovery and planning**. It does **not** perform checkout, payment submission, wallet interactions, or irreversible purchase actions.

## Safety Guardrails

- Discovery-only scope: browsing, filtering, comparing, and summarizing events.
- Never submit checkout/payment forms.
- Never request or handle secrets (wallet seed phrases, private keys, passwords, OTPs).
- Never collect sensitive personal data beyond what is needed for planning preferences.
- If the user asks to purchase, stop and ask for explicit confirmation to switch to a separate checkout workflow/skill.

## Workflow

1. Open `https://plvr.io`.
2. Gather relevant options based on user preferences (date, city, artist/genre, venue, budget).
3. Capture visible event details:
   - event title
   - date/time
   - venue/city
   - visible ticket price tiers
   - visible availability indicators
4. Present top options and explain tradeoffs.
5. If asked for next steps, provide non-transactional guidance (what to click next), without submitting checkout/payment.

## Output Format

- Event: <name>
- Date/Time: <when>
- Venue/City: <where>
- Price (visible): <tier/range>
- Availability signal: <available/low/unknown>
- Why it matches: <1-line reason>
- Next step: <non-transactional guidance>

## Known Notes

- Source of truth is the live website UI.
- Availability and pricing can change quickly.
- If details are missing on listing pages, open the event page and verify before recommending.
