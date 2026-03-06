# Prompt Crafting — Udio

## Prompt Structure

The most effective Udio prompts follow a layered structure:

```
[Primary Genre] [Subgenre] [Mood 1] [Mood 2] [Instruments] [Voice] [Era/Influence]
```

### Layer Breakdown

| Layer | Purpose | Examples |
|-------|---------|----------|
| Primary Genre | Base style | electronic, rock, jazz, classical |
| Subgenre | Narrow focus | ambient, shoegaze, bebop, baroque |
| Mood | Emotional tone | melancholic, euphoric, tense |
| Instruments | Sonic palette | acoustic guitar, synths, strings |
| Voice | Vocal style | female soprano, male baritone, choir |
| Era/Influence | Reference point | 80s, vintage, modern, [Artist] style |

## Example Prompts by Genre

### Electronic
```
electronic ambient downtempo dreamy synth pads warm analog 90s IDM
```
```
techno dark industrial aggressive 808 kicks distorted synths warehouse
```
```
house deep melodic progressive female vocals ethereal sunset vibes
```

### Rock
```
indie rock shoegaze dreampop reverb guitars female vocals ethereal 90s
```
```
alternative rock grunge raw emotional male vocals distorted power chords
```
```
post-rock cinematic building crescendo instrumental atmospheric guitars
```

### Hip Hop
```
hip hop boom bap jazz samples vinyl crackle old school 90s golden era
```
```
trap dark 808s hi-hats aggressive flow modern production
```
```
lo-fi hip hop chill beats study music rain sounds nostalgic
```

### Jazz
```
jazz bebop upright bass brushed drums piano trio intimate club setting
```
```
jazz fusion electric piano rhodes funky bass 70s progressive
```
```
smooth jazz saxophone mellow late night easy listening
```

### Classical / Orchestral
```
orchestral cinematic epic strings brass percussion film score adventure
```
```
classical piano solo romantic era emotional expressive rubato
```
```
chamber music string quartet intimate baroque counterpoint
```

### Pop
```
pop upbeat catchy hooks synth pop female vocals danceable modern
```
```
indie pop quirky playful acoustic elements male vocals intimate
```
```
r&b pop smooth vocals 2000s production slick beats sensual
```

## Modifier Stacks

### Tempo Modifiers
| Slow | Medium | Fast |
|------|--------|------|
| slow, downtempo, ballad | mid-tempo, groove | upbeat, fast-paced, energetic |
| 60-80 BPM feel | 90-120 BPM feel | 130+ BPM feel |

### Mood Combinations
| Energy | Mood Stack |
|--------|------------|
| High positive | euphoric energetic uplifting triumphant |
| Low positive | peaceful calm serene contemplative |
| High negative | aggressive chaotic intense furious |
| Low negative | melancholic sad dark somber |
| Complex | bittersweet nostalgic hopeful yearning |

### Production Descriptors
| Style | Descriptors |
|-------|-------------|
| Clean | polished crisp modern professional studio |
| Raw | lo-fi tape warm analog vintage imperfect |
| Atmospheric | ambient reverb spacious ethereal floating |
| Dense | layered complex rich full wall of sound |

## Negative Prompts

While Udio doesn't have explicit negative prompts, you can steer away from unwanted elements:

**Instead of:** "no vocals"
**Use:** "instrumental only" or "no singing purely instrumental"

**Instead of:** "not loud"
**Use:** "soft quiet intimate whisper"

## Artist References

You can reference artists for style guidance:
```
in the style of [Artist Name]
[Artist Name] influence
reminiscent of [Artist Name]
```

Note: Results vary. The model interprets references broadly.

## Iteration Strategy

### When Result is Close
1. Keep the working prompt structure
2. Swap one element (mood OR instrument OR voice)
3. Try 3-5 seeds with each variation

### When Result is Wrong
1. Identify what's off (genre, mood, tempo, voice)
2. Strengthen the correct elements
3. Add explicit counter-descriptors

### Example Iteration
```
Original: indie rock dreamy guitars
Problem: Too aggressive

Iteration 1: indie rock dreamy soft guitars gentle
Iteration 2: indie pop dreamy acoustic warm intimate
Iteration 3: dream pop ethereal floating shimmering guitars whispered
```
