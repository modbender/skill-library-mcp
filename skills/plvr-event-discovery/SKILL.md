---
name: plvr-event-discovery
description: Discover and recommend live events matched to user preferences, then assist with ticket checkout on plvr.io using the web flow (no public API), including ticket selection, reservation-window handling, x402 wallet payment handoff, and post-purchase confirmation capture. Use when a user asks what events are happening, wants interesting events this weekend/tonight, asks for things to do, requests event ideas by location/date/genre/budget, asks to compare ticket options, or wants help getting access to an event.
---

# PLVR Event Discovery

## Overview

Use browser automation against the PLVR website. Treat this as a web-only workflow: discover events, open event pages, select ticket types, then guide payment via x402 (wallet flow through Coinbase Commerce).

## Ground Rules

- Use browser actions; do not assume a PLVR REST API exists.
- Treat purchase actions as high-risk; ask for explicit confirmation immediately before final payment submission.
- Track reservation timing. Ticket selection reserves inventory for ~10 minutes.
- Require an email for guest checkout when the user is not logged in.
- Capture and report evidence after checkout (order summary, confirmation state, any reference IDs).

## Workflow

1. Open `https://plvr.io` and discover relevant events (date, city, artist, venue, price tier when visible).
2. Present short options to the user and ask which event/ticket type they want.
3. Open the chosen event and select the requested ticket type.
4. Confirm reservation window and countdown (if shown).
5. Move to checkout and gather/confirm required fields:
   - email address (required for ticket delivery if guest)
   - any attendee metadata requested by PLVR
6. Confirm payment method is wallet-based via the `Crypto` option (Coinbase Commerce flow / x402-aligned wallet checkout).
7. Ask for explicit user approval before final pay/submit click.
8. Complete checkout and capture confirmation details.
9. Summarize what happened, including expected ticket delivery format and where it will arrive.

## Output Template

Use this concise format when reporting progress or completion:

- Event: <name>
- Ticket: <type / quantity>
- Reservation status: <active / expired> (+ time left if visible)
- Checkout identity: <guest email or logged-in account>
- Payment method: x402 wallet (Coinbase Commerce)
- Purchase status: <pending / paid / failed>
- Confirmation evidence: <order number / confirmation screen text>
- Ticket delivery: PDF + QR via email

## Known Product Facts

- PLVR is currently web-only for this workflow (no API provided by user).
- Browsing and purchasing do not require login.
- Guest checkout requires email; PLVR may create an account from purchase details.
- Purchase flow: select ticket (reserved ~10 minutes) → pay → confirm.
- Ticket output: PDF and QR sent by email.

## Unknown / Must Verify Per Transaction

Check these live during each run and report clearly:

- geo restrictions
- KYC or wallet verification requirements
- refund/cancellation policy at event and platform level
- rate limiting, anti-bot challenges, or CAPTCHA
- chain/network/fees supported by the wallet payment screen
