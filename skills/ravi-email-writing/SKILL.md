---
name: ravi-email-writing
description: Best practices for writing high-quality emails that look professional and avoid spam filters. Reference this before composing, replying, or forwarding emails with ravi-email-send.
---

# Email Writing Guide

Write emails that look like they came from a real person — not an AI. Good email hygiene improves deliverability, avoids spam filters, and gets responses.

## Subject Lines

- **40-60 characters** — long subjects get truncated on mobile
- **Be specific** — "Q3 metrics review for Acme project" beats "Update"
- **No ALL CAPS** — spam filters penalize this heavily
- **Avoid spam triggers** — "free", "act now", "limited time", "click here", "urgent", "guaranteed", "no obligation"
- **Match the tone** — casual for teammates, professional for external contacts

## HTML Body Structure

The `--body` flag in `ravi email compose/reply/forward` accepts HTML. Always use semantic tags — never pass plain text.

**Do this:**
```html
<p>Opening line that states the purpose.</p>

<p>Supporting details in a second paragraph.</p>

<ul>
  <li>Key point one</li>
  <li>Key point two</li>
</ul>

<p>Closing with a clear next step or ask.</p>

<p>Best,<br>IDENTITY_NAME</p>
```

**Don't do this:**
```html
Plain text with no tags at all

Or this:<br><br>Using br chains<br><br>instead of paragraphs
```

**Rules:**
- Always wrap text in `<p>` tags
- Use `<h2>` for section headers (not `<h1>`)
- Use `<ul>`/`<li>` for lists, not dashes or asterisks
- Use `<a href="...">descriptive text</a>` for links — never bare URLs
- No `<html>`, `<head>`, or `<body>` wrapper tags — the email system adds these
- No `<br>` chains — use separate `<p>` tags instead
- Get the identity name with: `ravi identity list --json | jq -r '.[0].name'`

## Recommended Template

Copy-paste starting point for most emails:

```bash
NAME=$(ravi identity list --json | jq -r '.[0].name')

ravi email compose \
  --to "recipient@example.com" \
  --subject "Specific subject under 60 chars" \
  --body "<p>Hi Alex,</p>

<p>I'm reaching out about [specific topic]. [One sentence of context.]</p>

<p>[Core message — what you need, what you're sharing, or what you're asking.]</p>

<ul>
  <li>[Key point or action item]</li>
  <li>[Key point or action item]</li>
</ul>

<p>[Clear next step — what should the recipient do?]</p>

<p>Best,<br>$NAME</p>" --json
```

## Tone and Style

- **First person, active voice** — "I'll send the report Monday" not "The report will be sent"
- **Short paragraphs** — 2-3 sentences max per `<p>` tag
- **Get to the point** — state your purpose in the first sentence
- **End with an action item** — "Can you review by Friday?" not "Let me know your thoughts"
- **No filler phrases** — cut "I hope this email finds you well", "Just wanted to touch base", "Per our previous conversation"
- **No robotic language** — cut "I am writing to inform you", "Please be advised", "Kindly note"
- **Match the thread tone** — if they're casual, be casual. If they're formal, be formal.

## Anti-Spam Essentials

These rules help your emails land in the inbox, not spam:

- **High text-to-HTML ratio** — more words, fewer tags. Don't over-format.
- **No link shorteners** — use full URLs. Spam filters distrust bit.ly, t.co, etc.
- **Max 2-3 links per email** — more links = higher spam score
- **No ALL CAPS** — not even for emphasis. Use `<strong>` instead.
- **No image-only emails** — always include text content
- **One topic per email** — don't cram multiple requests into one message
- **Don't repeat yourself** — saying the same thing in different words triggers spam heuristics

## Common Mistakes

| Mistake | Why it's bad | Do this instead |
|---------|-------------|-----------------|
| Plain text in `--body` | Renders as one blob, no formatting | Wrap everything in `<p>` tags |
| `<br><br>` chains | Looks spammy, inconsistent spacing | Use separate `<p>` tags |
| "Dear Sir/Madam" | Outdated, signals mass email | Use the recipient's name or "Hi there" |
| Wall of text | Nobody reads long emails | Break into 2-3 short paragraphs |
| "Click here" links | Spam trigger, bad accessibility | `<a href="...">descriptive text</a>` |
| Empty or vague subject | Low open rates, looks like spam | Be specific: "Invoice #1234 for January" |
| Excessive HTML styling | High tag-to-text ratio triggers filters | Keep formatting minimal |
| No signature | Looks impersonal, unprofessional | Sign with identity name |
| "Sent by AI" disclaimers | Undermines trust, unnecessary | Just write naturally |

## Related Skills

- **ravi-email-send** — CLI commands for compose, reply, reply-all, and forward
- **ravi-inbox** — Read incoming email to understand what you're replying to
- **ravi-identity** — Get your identity name for email signatures
- **ravi-feedback** — Tell the Ravi team if email deliverability could be better
