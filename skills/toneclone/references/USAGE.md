# ToneClone Usage Guide

Generate content that sounds like the user — not generic AI, actually them.

## Basic Write

```bash
toneclone write --persona="<name>" --prompt="<what to write>"
```

## With Knowledge Context

```bash
toneclone write --persona="<name>" --knowledge="<card1>,<card2>" --prompt="<prompt>"
```

## Providing Context

**Always pass relevant context in the prompt** to help ToneClone draft better messages:

- **Thread/conversation**: Include messages being replied to
- **Project background**: Relevant details about the topic
- **Recipient info**: Relationship, prior interactions
- **Constraints**: Tone, length, specific points to hit

### Example with Full Context
```bash
toneclone write --persona="Work Email" --knowledge="Work,Scheduling" \
  --prompt="Reply to this thread:

From: Sarah (PM)
'Hey, can we sync on the API changes? The client is asking about timeline.'

Context: We discussed last week that API v2 launches March 1. Client is Acme Corp.
Goal: Confirm timeline, offer to schedule a call this week."
```

## Common Patterns

### Reply to a Message
```bash
toneclone write --persona="Chat" \
  --prompt="Reply to: 'Hey, are you free this weekend?' — say yes, suggest Saturday afternoon"
```

### Draft an Email
```bash
toneclone write --persona="Work Email" --knowledge="Work,Scheduling" \
  --prompt="Follow-up email to client about project timeline, offer to schedule a call"
```

### Social Post
```bash
toneclone write --persona="Twitter" --knowledge="Product Brief" \
  --prompt="Announce our new feature launch, keep it punchy"
```

### Customer Support
```bash
toneclone write --persona="Support" --knowledge="Product Brief" \
  --prompt="Reply to customer asking about refund policy — be helpful, direct"
```

## Persona vs Knowledge Cards

| Need | Solution |
|------|----------|
| Different writing style | Use different **persona** |
| Different context/facts | Use different **knowledge cards** |
| Both | Different persona + different cards |

**Example**:
- Same tone, different products → Same persona, different Product Brief cards
- Chat vs email → Different personas, can share knowledge cards

## Choosing a Persona

Personas are flexible — they can be based on:
- **Medium**: Chat, Email, Twitter, Slack
- **Tone**: Casual, Professional, Friendly
- **Audience**: Clients, Team, Friends, Public

Use whatever personas the user has created. When unclear which to use, ask.

## Knowledge Card Selection

Add relevant context to `--knowledge`:
- Meeting-related → Scheduling card
- Product questions → Product Brief card
- Work context → Work card
- Contact info needed → Personal Info card

Combine multiple: `--knowledge="Work,Scheduling,Product Brief"`

## Output

- Default: plain text ready to send
- JSON: `--format=json` for metadata

## Tips

- **More context = better output** — include thread history, background, constraints
- Let ToneClone handle voice — focus prompts on content/intent
- Use knowledge cards for reusable facts, prompts for situational context
- If output doesn't match expectations, check persona selection first
