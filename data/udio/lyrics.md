# Lyrics Guide — Udio

How to write and format lyrics for optimal Udio generation.

## Section Tags

Udio recognizes structural tags that guide song arrangement:

| Tag | Purpose | Typical Length |
|-----|---------|----------------|
| `[Intro]` | Opening, often instrumental | 4-8 bars |
| `[Verse]` | Story/narrative content | 8-16 bars |
| `[Verse 1]`, `[Verse 2]` | Numbered verses | 8-16 bars |
| `[Pre-Chorus]` | Build before chorus | 4-8 bars |
| `[Chorus]` | Hook, memorable | 8-16 bars |
| `[Bridge]` | Contrast section | 4-8 bars |
| `[Outro]` | Ending section | 4-8 bars |
| `[Instrumental]` | No vocals | Variable |
| `[Break]` | Stripped down moment | 4-8 bars |
| `[Drop]` | Electronic music climax | 8-16 bars |

## Basic Song Structure

### Pop/Rock Standard
```
[Intro]

[Verse 1]
First verse lyrics here
Second line of verse
Third line continues
Fourth line wraps up

[Chorus]
Catchy hook repeated
Main message here
Memorable and singable
Hook again

[Verse 2]
Story continues here
Building on verse one
New details emerge
Leading to chorus

[Chorus]
Catchy hook repeated
Main message here
Memorable and singable
Hook again

[Bridge]
Different perspective
Change in melody
Building tension
Back to chorus

[Chorus]
Catchy hook repeated
Main message here
Final emotional peak
Resolution

[Outro]
```

### Electronic/Dance
```
[Intro]

[Build]
Tension rising here
Energy increasing

[Drop]
[Instrumental]

[Breakdown]
Stripped back moment
Breathe before next drop

[Build]
Rising again
Here it comes

[Drop]
[Instrumental]

[Outro]
```

### Ballad
```
[Intro]
[Instrumental]

[Verse 1]
Slow emotional opening
Setting the scene
Personal and intimate
Drawing listener in

[Chorus]
Emotional core revealed
Main theme expressed
Powerful and moving
Heart of the song

[Verse 2]
Story deepens here
More vulnerability
Building to climax
Emotional stakes rise

[Chorus]
Emotional core revealed
Main theme expressed
Even more powerful
Building intensity

[Bridge]
Breaking point moment
Highest emotion
Resolution beginning
Catharsis

[Chorus]
Final statement
Resolution achieved
Peaceful or powerful
Closing sentiment

[Outro]
Gentle fade
```

## Writing Effective Lyrics

### Line Length
- **Short lines work best:** 4-8 syllables per line
- **Consistent rhythm:** Similar syllable counts across lines
- **Natural breaks:** End lines where you'd naturally pause

### Rhyme Schemes
| Scheme | Pattern | Example |
|--------|---------|---------|
| AABB | Lines 1-2 rhyme, 3-4 rhyme | day/way, night/light |
| ABAB | Alternating rhymes | day/night/way/light |
| ABCB | Only 2nd and 4th rhyme | day/night/way/light |
| Free | No strict pattern | Varies |

### Emotional Words
Words that translate well to sung emotion:
- Heart, soul, fire, rain, night, light
- Love, pain, hope, fear, dream
- Forever, never, always, away
- Fall, rise, break, heal

### Avoid
- Long compound words (hard to sing)
- Technical jargon (doesn't flow)
- Tongue twisters
- Too many syllables per line

## Vocal Direction Tags

Add in brackets to guide vocal performance:

| Tag | Effect |
|-----|--------|
| `[soft]` | Quieter, intimate |
| `[powerful]` | Belting, loud |
| `[whispered]` | Breathy, quiet |
| `[spoken]` | Spoken word |
| `[harmonies]` | Layered vocals |
| `[falsetto]` | High register |
| `[ad-lib]` | Improvised vocals |

Example:
```
[Verse 1]
[soft]
Walking through the rain alone
Memories of what we'd known

[Chorus]
[powerful]
But I won't let you go
No I won't let you go
```

## Instrumental Indicators

### No Vocals
```
[Instrumental]
```
or
```
[Instrumental Break]
```

### Solo Sections
```
[Guitar Solo]
[Piano Solo]
[Saxophone Solo]
```

### Specific Instrumental Moments
```
[Strings Swell]
[Beat Drop]
[Bass Line]
```

## Ending Lyrics

To indicate song ending:
```
[Outro]
Fading away now
Fading away
[fade out]
```

Or for definite endings:
```
[Outro]
This is where it ends
Final words
[end]
```

## Language Tips

### English (Default)
Works best. Model trained primarily on English lyrics.

### Other Languages
Include language indicator in prompt:
```
Prompt: "spanish flamenco passionate vocals"
Lyrics: Spanish text
```

Languages with good support:
- Spanish
- French
- Japanese
- Korean
- Portuguese
- German

### Phonetic Writing
For non-native languages, phonetic spelling can help:
```
[Verse]
Arigatou gozaimasu
Watashi no kokoro
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Wall of text | Model can't parse structure | Add section tags |
| No line breaks | Rushed delivery | Break into short lines |
| Over-rhyming | Sounds forced | Use ABCB or free verse |
| Too many words | Crammed singing | Fewer syllables per line |
| Missing chorus | No hook | Add memorable repeated section |
| Abrupt ending | Cut off feeling | Add `[Outro]` with conclusion |
