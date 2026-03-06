---
name: islamic-daily-reflection
version: 1.0.0
description: Daily Islamic reflections with Python script. Provides formatted spiritual guidance with calendar awareness (Ramadan, Jummah, Dhul Hijjah). Authentic Quran/Hadith references and practical daily challenges.
author: clinicode
---

# Islamic Daily Reflection

## CRITICAL: Always Run the Script

When user requests a reflection, you MUST execute the Python script:
```bash
python scripts/reflection.py
```

**Display the complete output exactly as returned by the script.**

The script provides:
- ✅ Formatted output with ═══ borders
- ✅ Hijri calendar awareness
- ✅ Ramadan/Jummah/Regular reflections
- ✅ Actionable daily challenges
- ✅ Quran/Hadith references

**DO NOT generate your own reflection. ALWAYS run the script.**

## User Commands

Users may ask:
- "daily reflection"
- "islamic reminder"
- "inspire me"
- "motivate me islamically"
- "friday reflection"
- "ramadan reflection"

For ALL of these: run `python scripts/reflection.py`

## Script Output Format

The script returns formatted text like:
```
═══════════════════════════════════════
📅 Thursday, 13 February 2026 | 25 Sha'ban 1447

🤲 Patience in Small Trials

[Reflection content...]

💡 Today's Action (X min):
[Actionable challenge...]

📖 [Quran/Hadith reference]
═══════════════════════════════════════
```

Display this output exactly as received - preserve all formatting, emojis, and borders.

## Technical Details

The script (`scripts/reflection.py`):
- Detects current date (Gregorian + Hijri)
- Selects appropriate reflection type:
  - Ramadan days 1-30 (specific reflections)
  - Jummah (Friday reflections)
  - Regular days (30 rotating themes)
- Formats with consistent structure
- No external dependencies (uses stdlib only)

## Reflection Themes

**Regular days rotate through:**
Patience, Gratitude, Tawakkul, Taqwa, Ikhlas, Humility, Contentment, Hope, Khashyah, Love for Allah, Brotherhood, Honesty, Justice, Mercy, Forgiveness, Charity, Good Character, Dhikr, Knowledge, Kindness to Parents, Neighbors, Promises, Avoiding Backbiting, Controlling Anger, Thankful in Trials, Dua, Quran Reading, Tahajjud, Fasting, Remembering Death

**Special occasions:**
- Ramadan (Month 9): Day-specific reflections
- Dhul Hijjah (Month 12, Days 1-10): Hajj themes
- Jummah (Fridays): Friday-specific
- Muharram (Day 10): Ashura

## Version

1.0.0 - Python script with pre-written reflections