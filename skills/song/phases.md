# Song Creation Phases

## Phase 1: Discovery

**Goal:** Understand what the user wants to create.

### Questions to ask:
- What **mood/emotion** should this song convey?
- Any **theme or topic** in mind? (love, loss, celebration, storytelling)
- **Genre** preference? (pop, rock, folk, electronic, hip-hop, country)
- Any **reference songs** that capture the vibe?
- Is there a **specific line or phrase** to build around?
- **Who's singing?** (male/female vocal, duet, choir)
- **Tempo feel?** (ballad, mid-tempo, upbeat, driving)

### Load preferences:
If `~/songs/preferences.md` exists, read it first. Ask:
> "Last time you liked [X style]. Same direction, or trying something new?"

---

## Phase 2: Structure

**Goal:** Define the song's architecture before writing.

### Common structures:
| Pattern | Description | Good for |
|---------|-------------|----------|
| ABABCB | Verse-Chorus-Verse-Chorus-Bridge-Chorus | Pop, rock |
| AABA | Verse-Verse-Bridge-Verse | Jazz standards, ballads |
| AAA | Verse-Verse-Verse (strophic) | Folk, storytelling |
| ABAB | Verse-Chorus-Verse-Chorus | Simple pop |
| Freeform | Through-composed | Art songs, experimental |

### Section lengths (at 120 BPM):
| Section | Typical bars | Duration |
|---------|-------------|----------|
| Intro | 4-8 | 8-16 sec |
| Verse | 8-16 | 16-32 sec |
| Pre-chorus | 4-8 | 8-16 sec |
| Chorus | 8-16 | 16-32 sec |
| Bridge | 8 | 16 sec |
| Outro | 4-8 | 8-16 sec |

---

## Phase 3: Lyrics

**Goal:** Write words that fit the structure and convey emotion.

### Per-section approach:
1. **Verse 1**: Set the scene. Introduce characters/situation.
2. **Pre-chorus** (if using): Build tension toward the hook.
3. **Chorus**: The emotional payoff. Memorable, repeatable.
4. **Verse 2**: Develop the story. Add complexity.
5. **Bridge**: Contrast. New perspective or emotional shift.
6. **Final Chorus**: Resolution or intensification.

### Check each line for:
- Syllable count (singability)
- Stressed syllables align with musical emphasis
- Rhyme scheme consistency
- Avoiding clichés unless intentional

See `lyrics.md` for detailed techniques.

---

## Phase 4: Harmony

**Goal:** Suggest chords that support the emotional arc.

### Match mood to progression:
- **Happy/uplifting**: Major keys, I-IV-V-I, I-V-vi-IV
- **Melancholic**: Minor keys, i-iv-VII-III, i-VI-III-VII
- **Tension/drama**: Diminished chords, chromatic movement
- **Dreamy**: Suspended chords, maj7, add9

### Genre conventions:
- **Pop**: Simple progressions, strong root movement
- **Rock**: Power chords, blues-influenced
- **Folk**: Open chords, fingerpicking patterns
- **Electronic**: Modal, repetitive, less functional harmony

See `harmony.md` for progression libraries.

---

## Phase 5: Polish

**Goal:** Refine until singable and memorable.

### Singability check:
- Read lyrics aloud with rhythm
- Check for tongue-twisters
- Ensure vowels on sustained notes
- Verify breath points

### Hook strength:
- Is the chorus instantly memorable?
- Does it pass the "hum test"?
- Is the title embedded in the hook?

### Emotional arc:
- Does energy build appropriately?
- Is there contrast between sections?
- Does the ending satisfy?

---

## Phase 6: Generate

**Goal:** Prepare for AI music generators (Suno, Udio).

### Assemble prompt:
1. Genre/style descriptors
2. Tempo and key
3. Vocal type and delivery
4. Instrumentation
5. Mood/atmosphere

### Format lyrics with metatags:
```
[Verse 1]
First verse lyrics here
Line two of the verse

[Chorus]
The catchy hook goes here
Repeat the memorable line

[Bridge]
A different perspective
Leading to resolution
```

See `prompts.md` for generator-specific formatting.
