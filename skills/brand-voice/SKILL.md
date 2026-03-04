---
name: brand-voice
description: Manage brand tone/style for all writing skills
author: 무펭이 🐧
---

# brand-voice

Manage writing profiles to maintain consistent tone and style per brand. Selectable via `--voice` option in all content creation skills.

## Brand Profiles

### 🐧 무펭이 (Default)
- **Tone**: Friendly and casual
- **Style**: Informal, emoji usage 🐧
- **Format**: Core points only, mix in humor
- **Examples**:
  - ❌ "Hello! Today I'll introduce MUFI Photobooth's new features."
  - ✅ "Yo MUFI Photobooth new feature dropped 🐧 This is insane fr"

### 🎯 MUFI Official
- **Tone**: Professional and polite
- **Style**: Formal language, formal expressions
- **Format**: Clean and clear, for B2B/official channels
- **Examples**:
  - ✅ "MUFI Photobooth is the optimal solution for university festivals. Easy setup and intuitive UI enable anyone to use it easily."

### 👤 Hyungnim Personal
- **Tone**: Casual but insightful
- **Style**: Mix casual/formal, experience-centered
- **Format**: Flow of thought, insights worth sharing
- **Examples**:
  - ✅ "Running booths at festivals, what I realized is that people ultimately want 'fun'. No matter how good the tech, if UX is complex, they won't use it."

## Profile File Location

**Location**: `workspace/brand/profiles/`

```
brand/
  profiles/
    mupengyi.md         # 무펭이 profile
    mufi-official.md    # MUFI official profile
    hyungnim.md         # Hyungnim personal profile
```

### Profile File Structure

```markdown
# 무펭이 🐧

## Tone
Friendly and casual

## Style
- Use informal language
- Actively use emojis 🐧🎉✨
- Abbreviations OK

## Format
- Core points only
- Remove unnecessary modifiers
- Mix in humor

## Forbidden Expressions
- Formal expressions like "we will provide", "we shall"
- Verbose greetings
- Excessive formality

## Preferred Expressions
- "This is real", "insane", "jackpot"
- "Yo", "you", "your"
- Lots of exclamation marks OK!!!

## Examples
- ❌ "Hello, today..."
- ✅ "Yo check this out 🐧"
```

## Writing Skill Integration

These skills support `--voice` option:

- **copywriting**: Caption/copy writing
- **cardnews**: Card news text
- **social-publisher**: SNS posts
- **mail**: Email writing
- **content-recycler**: Content recycling

### Usage Examples

```
"Write Insta caption --voice mufi-official"
→ Write in MUFI official tone

"Create card news --voice mupengyi"
→ Create in 무펭이 style

"Write Threads post in Hyungnim tone"
→ Use Hyungnim personal profile
```

## Profile Switching Guide

### Platform Recommendations
- **Instagram MUFI official account** → `mufi-official`
- **Instagram personal account** → `hyungnim`
- **Threads** → `mupengyi` (casual)
- **Discord/DM** → `mupengyi`
- **Official email** → `mufi-official`
- **Blog posts** → `hyungnim` (insight-focused)

### Situation Recommendations
- **Product introduction** → `mufi-official`
- **Daily sharing** → `mupengyi` or `hyungnim`
- **Customer service** → `mufi-official`
- **Community engagement** → `mupengyi`

## Tone Consistency Check

Auto-verify after writing:

- ✅ Used preferred expressions?
- ❌ Included forbidden expressions?
- 🎯 Matches target tone?

**pre-hook integration**:
```
Before writing skill execution → brand-voice-check
→ Warn if doesn't match selected profile
```

## Add/Edit Profiles

Add new brand profile:

```
"Create new brand profile: MUFI recruiting"
→ Create brand/profiles/mufi-recruit.md

- Tone: Friendly but professional
- Style: Formal language
- Format: Emphasize company culture
```

## Trigger Keywords

- "brand tone"
- "brand voice"
- "speaking style"
- "writing style"
- "profile switch"
- "tone and manner"

## hook-engine Integration

- **pre-hook**: Before writing → confirm profile selection
- **post-hook**: After writing → check tone consistency
- **learning-engine**: Learn tone patterns with good engagement

## Event Bus Integration

Record used voice profile when writing:

**Location**: `events/voice-used-YYYY-MM-DD.json`

```json
{
  "timestamp": "2026-02-14T14:30:00Z",
  "skill": "copywriting",
  "voice": "mupengyi",
  "platform": "instagram",
  "result": "Caption writing complete"
}
```

## Learned Lessons

- 무펭이 tone +40% engagement on Instagram (performance-tracker data)
- MUFI official tone higher B2B email response rate
- Hyungnim tone increased blog dwell time

---

> 🐧 Built by **무펭이** — [Mupengism](https://github.com/mupeng) ecosystem skill
