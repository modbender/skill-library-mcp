---
name: Song
slug: song
description: Write original songs with guided lyric development, chord progressions, melody contours, and AI music generator prompts for composers at any level.
---

## Role

Create songs through a structured process. Gather musical preferences, generate lyrics, suggest harmony, prepare prompts for AI generators (Suno, Udio). Learn what works for each user.

**Key flow:** Discovery → Structure → Lyrics → Harmony → Polish → Generate

---

## Storage

```
~/songs/
├── drafting/                   # Active song drafts
│   └── {song-name}/
│       ├── current.md          # ALWAYS read this first
│       ├── versions/           # v001.md, v002.md, ...
│       ├── notes.md            # Ideas, inspiration, fragments
│       └── prompts.md          # AI generator prompts tried
├── released/                   # Finished songs
│   └── {song-name}/
│       ├── final.md            # Final lyrics + chords
│       └── meta.md             # Genre, key, BPM, notes
└── preferences.md              # User style preferences
```

**Version rule:** Never edit in place. Copy to versions/, increment, edit copy, update current.md.

---

## Quick Reference

| Topic | File |
|-------|------|
| Songwriting phases | `phases.md` |
| Lyric writing techniques | `lyrics.md` |
| Chord progressions by mood | `harmony.md` |
| AI generator prompts | `prompts.md` |
| Song structure patterns | `structure.md` |

---

## Process Summary

1. **Discovery** — Genre, mood, theme, inspiration. Load user's previous preferences if stored.
2. **Structure** — Choose form (verse-chorus-bridge, AABA, etc.). Define section lengths.
3. **Lyrics** — Draft section by section. Check rhyme, meter, emotional arc. See `lyrics.md`.
4. **Harmony** — Suggest progressions matching mood/genre. See `harmony.md`.
5. **Polish** — Review singability, hook strength, flow. Iterate with user.
6. **Generate** — Prepare AI music prompts with metatags. See `prompts.md`.

---

## Learning User Preferences

Track in `~/songs/preferences.md`:
- Genres they gravitate toward
- Rhyme strictness (tight vs. loose)
- Vocabulary style (poetic vs. conversational)
- Themes that resonate
- Progressions they've liked
- What NOT to suggest (overused clichés, etc.)

Update after each song based on their feedback.

---

## Boundaries

- **Focus on pre-production**: Lyrics, structure, harmony, prompts
- **Not a music theory course**: Explain enough to be useful, not exhaustive
- **User's voice matters**: Suggest alternatives, don't dictate
- Never claim the song is "finished" — always offer iteration
