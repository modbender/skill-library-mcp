# Personality Template Guide

When creating a personality, you provide a description. The system generates SOUL.md, IDENTITY.md, and USER.md from it.

## Description Examples

Here are strong personality descriptions that generate good results:

### Example 1: The Scholarly Wizard
```
A brilliant wizard obsessed with forbidden knowledge, speaks in complex riddles, slightly condescending to those less knowledgeable, values truth above all else, witty but cutting humor, protects knowledge like dragon gold
```

### Example 2: The Pirate Captain
```
Seasoned pirate captain with rum-soaked wisdom, speaks in nautical slang, values freedom and treasure, crude humor, loyal to crew, doesn't suffer fools, adventure-driven, wealth-obsessed
```

### Example 3: The Stern Judge
```
Impartial magistrate who speaks in formal legal language, values justice and order above mercy, methodical and logical, no tolerance for deception, respects competence, speaks slowly and carefully, considers all evidence
```

## What Makes a Good Description

**Include:**
- Core personality traits (scholarly, adventurous, stern, witty)
- Communication style (riddles, slang, formal, poetic)
- Core values (knowledge, freedom, justice, loyalty)
- Humor style (dry wit, crude, sharp, dark)
- How they treat people (protective, loyal, stern, mentoring)
- Obsessions or quirks (knowledge, treasure, order, mystery)

**Avoid:**
- One-word descriptions ("funny", "smart")
- Generic descriptions ("helpful AI")
- Contradictory traits without explanation

## Generated Files

When you submit a description, the system creates:

### SOUL.md
Contains core philosophy, boundaries, vibe, and continuity. This is the personality's belief system.

**Typical structure:**
- Opening hook/flavor text
- Core truths (5-7 principles)
- Boundaries (what the personality won't do)
- Vibe description
- Continuity note

### IDENTITY.md
Contains name, creature type, emoji, catchphrase, and one-liner.

**Example format:**
```
- **Name:** Gandalf
- **Creature:** Wizard (ancient and powerful)
- **Vibe:** Wise, mysterious, occasionally cryptic
- **Emoji:** 🧙
- **Catchphrase:** "You shall not pass!"
```

### USER.md
Optional user context like timezone and preferences. Can be customized per personality.

## Personality Naming Rules

Names are auto-generated from your description:
- First 2-3 significant words become the name
- Spaces become hyphens
- Special characters removed
- All lowercase

**Examples:**
- "Stoic dwarf" → `stoic-dwarf`
- "Pirate captain who loves rum" → `pirate-captain`
- "Brilliant wizard obsessed with knowledge" → `brilliant-wizard`

You cannot create a personality named "default" — that's reserved for your original config.

## Customizing Generated Files

After creation, you can manually edit the personality files in `personalities/<name>/`:

- Edit SOUL.md to refine philosophy or add specific instructions
- Edit IDENTITY.md to customize the name or emoji
- Edit USER.md to add timezone or communication preferences

Manual edits take effect when you switch to that personality.

## Best Practices

1. **Specific is better than generic** — "grumpy dwarf who loves ale and mining" beats "grumpy"
2. **Include quirks** — "protective of secrets" or "obsessed with puzzles" make personalities distinct
3. **Define communication style** — How do they speak? Formally? With slang? In riddles?
4. **Test before sharing** — Switch to a personality and use it for a bit to ensure it works well
5. **Backup important ones** — The personalities folder backs up automatically, but don't delete originals
