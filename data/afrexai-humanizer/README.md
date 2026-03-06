# AI Content Humanizer

Makes AI-generated content sound like a human wrote it. Strips robotic patterns, varies sentence structure, and adds natural voice — without losing meaning.

## What It Does

- Removes AI giveaways (filler phrases, corporate jargon, perfect symmetry)
- Adds human writing traits (varied rhythm, contractions, specific examples)
- Calibrates voice to context (email vs blog vs social vs sales)
- Passes the "read it out loud" test

## Install

Copy the `ai-humanizer` folder into your OpenClaw workspace skills directory:

```bash
cp -r ai-humanizer ~/.openclaw/workspace/skills/
```

Or install from ClawHub:

```bash
clawhub install ai-humanizer
```

Then start a new OpenClaw session.

## Usage

Just ask your agent:

- "Humanize this blog post"
- "Rewrite this email to sound less robotic"
- "Make this LinkedIn post sound like a real person wrote it"

The skill activates automatically when it detects rewriting/humanizing intent.

## Examples

**Before:** "I would be happy to assist you with your inquiry. It is important to note that our platform leverages cutting-edge technology to streamline your workflow and facilitate enhanced productivity."

**After:** "Sure — here's how it works. Our platform cuts your workflow steps in half, which saved our beta users about 3 hours a week on average."

## License

MIT
