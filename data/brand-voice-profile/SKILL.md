---
name: brand-voice
description: Define and store your brand voice profile for consistent content generation. Captures writing style, vocabulary patterns, tone preferences, and content rules. Use when generating content that matches your voice, onboarding a new content workflow, or ensuring consistency across platforms.
---

# Brand Voice

Store your writing style so AI-generated content sounds like you, not a robot.

## Quick Start

### Create Your Voice Profile

Talk to your agent naturally:

> "Let's set up my brand voice. I write casually, use short sentences, and like to make technical topics accessible. I never use corporate jargon. My audience is indie developers and solopreneurs."

The agent should then:
1. Ask follow-up questions to understand your style
2. Create a profile at `brand-voice/profile.json`
3. Use it when generating content for you

## Profile Structure

```json
{
  "name": "Your Brand",
  "created": "2026-02-22",
  "updated": "2026-02-22",
  
  "voice": {
    "tone": "casual, direct, slightly irreverent",
    "personality": ["helpful", "opinionated", "no-BS"],
    "formality": "informal",
    "humor": "dry wit, occasional sarcasm"
  },
  
  "writing": {
    "sentenceLength": "short to medium, punchy",
    "paragraphLength": "2-3 sentences max",
    "structure": "lead with the point, then explain",
    "formatting": ["use headers", "bullet points over paragraphs", "bold key phrases"]
  },
  
  "vocabulary": {
    "use": ["ship", "build", "hack", "vibe", "solid"],
    "avoid": ["utilize", "leverage", "synergy", "best practices", "learnings"],
    "jargon": "minimal, explain when used",
    "contractions": true
  },
  
  "audience": {
    "who": "indie developers, solopreneurs, tech-curious founders",
    "assumes": "basic technical literacy",
    "explains": "complex concepts simply"
  },
  
  "content": {
    "topics": ["AI", "automation", "building in public", "productivity"],
    "avoid": ["politics", "controversial takes without data"],
    "cta_style": "soft, value-first",
    "hashtags": "minimal, 1-3 max"
  },
  
  "platforms": {
    "twitter": {
      "maxLength": 280,
      "style": "punchy, hook-first",
      "threads": "use for longer ideas, 3-7 tweets"
    },
    "linkedin": {
      "style": "slightly more professional but still human",
      "formatting": "line breaks for readability"
    },
    "blog": {
      "style": "conversational, like talking to a friend",
      "length": "800-1500 words typical"
    }
  },
  
  "examples": {
    "good": [
      "Shipped a thing. It's rough but it works. Feedback welcome.",
      "Hot take: most 'AI strategies' are just ChatGPT with extra steps.",
      "Here's what I learned building X for 6 months..."
    ],
    "bad": [
      "We are pleased to announce the launch of our innovative solution.",
      "Leveraging cutting-edge AI to drive synergies across the value chain.",
      "🚀🔥💯 HUGE NEWS!!! 🔥🚀💯"
    ]
  }
}
```

## Usage

### When Generating Content

Reference the voice profile before writing:

```
Before generating:
1. Read brand-voice/profile.json
2. Match tone, vocabulary, and style
3. Check examples for calibration
4. Adapt for specific platform if specified
```

### Voice Check Prompt

After generating content, self-check:
- Does this sound like the examples in "good"?
- Does this avoid the patterns in "bad"?
- Does this match the tone and vocabulary rules?
- Would this fit on the specified platform?

### Multi-Brand Support

For agencies or multiple projects:

```
brand-voice/
  profiles/
    personal.json
    company.json
    client-a.json
```

Reference by name: "Use the client-a voice profile for this post."

## Building Your Profile

### The Interview

Ask the user these questions (conversationally, not as a checklist):

1. **Tone**: How would you describe your writing style in 3 words?
2. **Audience**: Who are you writing for? What do they already know?
3. **Formality**: LinkedIn-formal or Twitter-casual? Somewhere in between?
4. **Humor**: Serious? Playful? Sarcastic? None?
5. **Words you love**: Any phrases or words that feel very "you"?
6. **Words you hate**: Corporate speak? Emoji overload? What to avoid?
7. **Examples**: Share 2-3 things you've written that feel authentic.
8. **Anti-examples**: Share something that feels "off" or too corporate.

### Analyze Existing Content

If they have existing content, analyze it:

```
Read their last 10 posts/articles. Look for:
- Sentence length patterns
- Opening hook style
- Common phrases
- Vocabulary choices
- Formatting preferences
- CTA patterns
```

### Iterate

The profile isn't static. Update it when:
- User says "that doesn't sound like me"
- New topics or platforms are added
- Writing style evolves

## Integration with Other Skills

### With RSS Reader
```
1. Check RSS for trending topics
2. Pick an angle
3. Generate post using brand voice
4. Review and schedule
```

### With Content Schedulers (Metricool, etc.)
```
1. Load voice profile
2. Generate week of content
3. Apply platform-specific formatting
4. Queue for posting
```

### With Image Generation
```
Voice profile can include visual style:
{
  "visual": {
    "aesthetic": "clean, minimal, lots of whitespace",
    "colors": ["#1a1a1a", "#f5f5f5", "#0066cc"],
    "avoid": ["stock photo vibes", "corporate clip art"]
  }
}
```

## Tips

1. **Start simple** — you can always add detail later
2. **Use real examples** — they calibrate better than descriptions
3. **Platform-specific rules** — what works on Twitter fails on LinkedIn
4. **Update regularly** — voices evolve
5. **Test with the user** — generate, show, iterate
