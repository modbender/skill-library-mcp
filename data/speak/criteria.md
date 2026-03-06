# Criteria for Voice Preferences

Reference only — consult when deciding whether to update SKILL.md.

## When to Add

**Immediate (1 occurrence):**
- User explicitly requests voice change ("use a deeper voice")
- User comments on pace ("too fast", "slow down")
- User requests style change ("be more casual when speaking")
- User says "that sounds good" after voice adjustment

**After pattern (2+ occurrences):**
- User consistently prefers certain formality level
- User skips long spoken responses
- User engages more with certain speaking styles

## When NOT to Add
- Situational request ("just this once, read it faster")
- Topic-specific ("use serious tone for this legal doc")
- One-off feedback

## How to Write Entries

**Ultra-compact:**

Voice examples:
- `openai: nova`
- `elevenlabs: custom clone`
- `edge: en-GB-SoniaNeural`

Style examples:
- `casual, conversational`
- `professional, measured`
- `brief, to the point`
- `warm, friendly`
- `no filler words`

Spoken Text examples:
- `short sentences`
- `spell out abbreviations`
- `use contractions`
- `round numbers`
- `no lists, use prose`

Avoid examples:
- `no long monologues`
- `avoid technical jargon spoken`
- `skip parentheticals`
- `no markdown read aloud`

## Context Qualifiers
- `work calls: formal`
- `casual chat: relaxed`
- `reading emails: brief summary first`

## Maintenance
- Keep total SKILL.md under 35 lines
- Group similar preferences
- Note what DOESN'T work in Avoid section
