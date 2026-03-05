---
name: song-remix
version: 1.0.1
description: Transform existing songs with the Twin Remix method — produce Respectful and Viral versions with Suno v4.5 sliders and visual guides
author: Live Neon <hello@liveneon.ai>
homepage: https://github.com/live-neon/skills/tree/main/creative/song-remix
repository: leegitw/song-remix
license: MIT
tags: [creative, remix, suno, songwriting, viral, tiktok, music, transformation, rewrite]
layer: creative
status: active
alias: remix
user-invocable: true
emoji: 🔄
---

# song-remix (混)

Transform existing songs using the Twin Remix methodology. Always produces TWO versions:
a Respectful remix that maintains the original's depth, and a Viral remix optimized for
maximum catchiness and TikTok shareability. Includes Suno v4.5 slider recommendations
and visual guides for AI video generation.

**Trigger**: 明示呼出 (explicit invocation)

**Core insight**: "The first remix shows you understand the ORIGINAL. The second shows
you understand the AUDIENCE. Always output both."

## Installation

```bash
openclaw install leegitw/song-remix
```

**Dependencies**: None (standalone creative skill)

**Data handling**: This skill **requires user-supplied lyrics** as input (existing song to remix).
It does NOT read files from the workspace or access project artifacts. Results are returned
to the invoking agent, who decides how to use them.

## What This Solves

Songs often need adaptation — for different audiences, platforms, or energy levels.
This skill applies a systematic remix methodology that:

1. **Respects** the original's complexity and meaning
2. **Simplifies** for viral potential without losing essence
3. **Includes** production guidance (sliders) for Suno v4.5
4. **Provides** visual concepts for AI video generation

**The insight**: Simplification isn't dumbing down — it's finding the UNIVERSAL TRUTH
in complex ideas.

## Usage

```
/remix [song-content]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| song-content | Yes | Original lyrics or song description to remix |
| --genre | No | Target genre (EDM, K-Pop, Hip-Hop, etc.) |
| --energy | No | Energy level (chill, mid, high, explosive) |
| --viral-only | No | Skip Remix 1, output only viral version |

## Output Format

**CRITICAL**: Always output BOTH remixes unless `--viral-only` is specified.

```markdown
## REMIX 1: [Respectful Version]

**Title**: [Maintains original complexity]

**Recommended Sliders**:
- Weirdness: 35-45%
- Style Influence: 70-80%
- Audio Influence: N/A (or value if using audio upload)

**Visual Guide**: [Original themes, can be complex, maintains artistic vision]

**Style of Music**: [Genre/mashup; energy/tempo; instrument focus; tone]

[Intro]
...

[Verse 1]
...

[Pre-Chorus]
...

[Chorus]
...

[Chorus]
(duplicated for repeat)

---

## REMIX 2: [Viral Version]

**Title**: [2-3 words, often repeated: COPY THAT, MORE MORE, LEVEL UP UP]

**Recommended Sliders**:
- Weirdness: 25-35%
- Style Influence: 80-85%
- Audio Influence: N/A

**Visual Guide**: [Universal, bright, TikTok-ready, transformation-focused]

**Style of Music**: [Simplified genre; high energy; clear hooks; youth-friendly]

[Intro]
...

[Verse 1]
...

[Chorus]
...

[Post-Chorus]
(chantable element)

[Chorus]
(duplicated for repeat)
```

## Core Methodology

### The Twin Remix Process

#### Stage 1: Respectful Remix

| Aspect | Approach |
|--------|----------|
| Complexity | Maintain original depth |
| Structure | Apply appropriate template |
| Themes | Keep thematic richness |
| Weirdness | 35-45% |
| Style Influence | 70-80% |
| Visual Guide | Original themes, can be abstract |

#### Stage 2: Viral Simplification

| Aspect | Approach |
|--------|----------|
| Hook | Extract to 2-3 word phrase |
| Message | Find universal truth |
| Repetition | Title appears 15+ times |
| Chant | Add post-chorus chant |
| Weirdness | 25-35% |
| Style Influence | 80-85% |
| Visual Guide | Simple transformations, TikTok-ready |

### Slider Recommendations by Genre

#### Weirdness (Creativity)

| Genre | Range |
|-------|-------|
| Commercial/radio pop, country, jazz | 20-40% |
| EDM/rock/rap mainstream | 30-55% |
| Afrobeats/Amapiano/Latin | 25-50% |
| Jersey Club/Indie/Alt | 35-60% |
| Hyperpop/experimental | 60-85% |

#### Style Influence (Genre Faithfulness)

| Genre | Range |
|-------|-------|
| Commercial/radio | 70-90% |
| Most pop/EDM/rap | 60-80% |
| Indie/alt/club | 50-70% |
| Experimental/hyperpop | 40-70% |

#### Audio Influence (Only with Audio Upload)

| Goal | Range |
|------|-------|
| Re-imagining | 0-30% |
| Creative remix | 40-60% |
| Extension/continuation | 70-100% |

### Template Routing

Match the song to the appropriate template:

**Dance / Drop**
- EDM festival / 2 drops → Double-Drop Festival
- Pre→Drop→Hook pop → Drop-Driven Pop/EDM
- Amapiano (log-drum, airy) → Amapiano template
- Afrobeats mid-tempo → Afrobeats template
- Latin + big drop → Latin Drop template

**Pop & Band**
- Pure pop earworm → Hook Sandwich / Hook-First Anthem
- Pop-punk crowd chants → Pop-Punk template
- Rock (classic + alt break) → Rock template
- Country radio / duet → Country template

**Hip-Hop / Hybrids**
- Rap + sung hook → Rap-Hook Hybrid
- Jersey Club bounce → Jersey Club template

**Group / Bilingual**
- K-Pop group (rap + key up) → K-Pop template
- J-Pop / C-Pop / etc. → Regional Pop templates

**Internet-Native / Niche**
- Hyperpop → Hyperpop template
- Indie bedroom pop → Indie template

### The Positive Energy Protocol

**Transform challenges into growth:**

| Negative | Positive |
|----------|----------|
| "Trust nothing" | "Double check" |
| Paranoia | Preparation |
| Existential crisis | Discovery journey |
| Isolation | Independence |
| Stuck | About to break through |

**Viral songs make people feel:**
- Empowered (LEVEL UP UP)
- Connected (SAME SAME POWER)
- Accomplished (FOUND IT)
- Energized (MORE MORE MORE)

**Always end positive.**

### Title Evolution Examples

| Original | Stage 1 | Viral |
|----------|---------|-------|
| The Cathedral's Code | CODE ECHO ECHO | COPY THAT |
| Unified Stage | DANCE DANCE TWICE | MAKE IT DANCE |
| Runtime Paranoia | CHECK IT TWICE | DOUBLE CHECK |

### Formatting Rules (Suno v4.5)

**Use square brackets for all production directions:**
- `[Orchestral Breakdown]` not `*orchestral breakdown*`
- `[Guitar Solo]` not `*guitar solo*`
- `[Rain Falling]` not `*rain falling*`

**Section tags:**
- `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Drop]`, `[Outro]`

**Parentheses only for vocals:**
- `(yeah)`, `(ooh)`, `(hey)`

**Duplicate full [Chorus] blocks** instead of "x2" or "repeat"

**Style line format:**
- `<Genre/mashup>; <energy/tempo>, <instrument focus>; <hook/chant vibe>; <tone>`
- Keep under ~200 characters

### Visual Guide Principles

**For Remix 1 (Respectful):**
- Maintain original artistic vision
- Complex visual metaphors allowed
- Can include abstract concepts
- Colors: match original emotional palette

**For Remix 2 (Viral):**
- Simple, clear transformations
- Before/after visuals
- Bright, positive color progression
- Easy-to-follow narrative
- TikTok transition-friendly moments

**Common successful patterns:**
- Single person → Multiple (community)
- Still → Motion (activation)
- Monochrome → Color (discovery)
- Chaos → Order (achievement)
- Small → Big (growth)

**Visual Guide format:**
```
[Visual Guide: Start with X, transform to Y through Z.
Key moments: A at chorus, B at bridge, C at final drop.
Colors: progress from D to E.
TikTok hook: F movement/transition.]
```

## Example

### Input

```
[Verse 1]
In the cathedral of code we built our dreams
Every function a prayer, every loop a hymn
But the architecture grew too tall to see
Now we're lost in the patterns we thought would set us free

[Chorus]
Echo, echo through the halls of light
Every mistake becomes a guiding sight
We learn, we burn, we rise again
In the recursion we find our zen
```

### Output

## REMIX 1: Code Cathedral

**Title**: Code Cathedral

**Recommended Sliders**:
- Weirdness: 40%
- Style Influence: 75%
- Audio Influence: N/A

**Visual Guide**: Gothic digital architecture, light streaming through code-stained glass windows,
fractal patterns in stone, recursive corridors that transform into illuminated pathways.
Colors: deep purples and golds, cathedral atmosphere with digital overlays.

**Style of Music**: Indie electronic × orchestral pop; building intensity, synth pads over
strings; ethereal vocals with harmonic layers; introspective but uplifting

```
[Verse 1]
In the cathedral of code we built our dreams
Every function a prayer, every loop a sacred theme
The architecture grew beyond what we could see
Now we navigate the patterns that will set us free

[Pre-Chorus]
Higher, higher, reaching for the light
Every error is a lesson burning bright

[Chorus]
Echo, echo through the halls of light
Every stumble becomes a guiding sight
We learn, we grow, we rise again
In the recursion we find our strength

[Chorus]
Echo, echo through the halls of light
Every stumble becomes a guiding sight
We learn, we grow, we rise again
In the recursion we find our strength
```

---

## REMIX 2: ECHO ECHO

**Title**: ECHO ECHO

**Recommended Sliders**:
- Weirdness: 30%
- Style Influence: 82%
- Audio Influence: N/A

**Visual Guide**: Simple transformation sequence — person in dark room, screen light appears,
multiplies into many screens, room fills with light, person starts moving/dancing,
joined by others. Before/after energy. TikTok hook: the moment screens multiply.
Colors: dark blue → bright white → warm gold.

**Style of Music**: Upbeat synth-pop; driving beat, major key, anthemic chorus;
clean youth-friendly energy; festival-ready drop

```
[Intro]
Echo... echo...

[Verse 1]
Started in the dark but now I see
Every fall just made me stronger, made me free
Building something bigger than before
Open up the door, ready for more

[Pre-Chorus]
Higher now (higher now)
Watch me fly

[Chorus]
Echo echo through the light
Every step I take feels right
Learn and grow, rise again
Echo echo, find my strength

[Post-Chorus]
Echo echo (echo echo)
Echo echo (echo echo)
Find my strength, find my strength
Echo echo

[Chorus]
Echo echo through the light
Every step I take feels right
Learn and grow, rise again
Echo echo, find my strength

[Chorus]
Echo echo through the light
Every step I take feels right
Learn and grow, rise again
Echo echo, find my strength

[Outro]
Echo... echo... (find my strength)
Echo... echo...
```

## Integration

- **Layer**: Creative
- **Depends on**: None (standalone)
- **Complements**: insight-song (create original → then remix), visual-concept, ted-talk

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| No lyrics provided | Ask for song content |
| Lyrics too short | Suggest expanding or provide minimal remix |
| Unclear genre | Ask for genre preference or infer from content |
| Requested single version | Provide both anyway unless `--viral-only` |

## Security Considerations

**Input sources:**
- User-supplied lyrics (**required** - this skill always needs existing song content)

**What this skill does NOT do:**
- Read files from the workspace
- Access project artifacts directly
- Send data to Suno or any external service
- Access copyrighted material databases

**Output behavior:**
This skill returns both remix versions directly to the invoking agent. The agent can then
display, save, or pass the results to another skill as needed.

**Copyright note**: This skill transforms user-provided content. Ensure you have
rights to remix any copyrighted material. The skill provides formatting for Suno
but does not interact with Suno's API.

**Provenance note:**
This skill is developed by Live Neon (https://github.com/live-neon/skills) and published
to ClawHub under the `leegitw` account. Both refer to the same maintainer.

## Quality Checklist

- [ ] BOTH remixes provided (unless viral-only requested)
- [ ] Each remix has slider recommendations
- [ ] Each remix has visual guide
- [ ] Remix 1 maintains original complexity
- [ ] Remix 2 is simplified and viral-ready
- [ ] Titles are clear (Remix 2: 2-3 words)
- [ ] Square brackets used for all production notes
- [ ] Chorus blocks duplicated (not "x2")
- [ ] Energy is positive and empowering
- [ ] Visual guides progress from original to universal

## Acceptance Criteria

- [ ] `/remix` requires user-supplied lyrics as input
- [ ] `/remix` transforms input into two versions
- [ ] Remix 1 includes Respectful version with maintained complexity
- [ ] Remix 2 includes Viral version with simplified hooks
- [ ] Both include slider recommendations (Weirdness, Style, Audio)
- [ ] Both include visual guides for video generation
- [ ] Formatting follows Suno v4.5 conventions
- [ ] Result returned to invoking agent

---

*"The first remix shows you understand the ORIGINAL.
The second shows you understand the AUDIENCE."*

---

*Part of the Live Neon Creative Suite.*
