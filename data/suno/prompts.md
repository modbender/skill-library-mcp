# Prompt Engineering — Suno

## Structure

Build prompts in layers:
```
[genre] [subgenre] [mood] [tempo] [instruments] [vocals] [era/influence]
```

Example: "indie folk melancholic slow acoustic guitar soft female vocals 90s"

## Genre Templates

### Electronic
```
electronic [subgenre] [mood] synth [texture] [era]

Subgenres: house, techno, ambient, trance, dubstep, drum and bass, lo-fi
Textures: warm pads, crisp beats, atmospheric, glitchy, analog
Eras: 80s synth, 90s rave, modern EDM
```

### Rock
```
[subgenre] rock [energy] [guitars] [drums] [vocals] [decade]

Subgenres: alternative, indie, grunge, punk, metal, classic
Energy: driving, explosive, laid-back, aggressive
Guitars: distorted, clean, jangly, heavy riffs
```

### Pop
```
pop [mood] [tempo] [production] [vocals] [era]

Moods: upbeat, anthemic, dreamy, melancholic
Tempo: uptempo, mid-tempo, slow
Production: polished, lo-fi, synth-heavy, acoustic
```

### Hip Hop
```
hip hop [subgenre] [beat] [mood] [era]

Subgenres: boom bap, trap, lo-fi, conscious, old school
Beats: hard-hitting, laid-back, bouncy, dark
Eras: 90s golden age, 2000s, modern trap
```

### Folk/Acoustic
```
folk [subgenre] [mood] [instruments] [vocals]

Subgenres: indie folk, americana, traditional, contemporary
Instruments: acoustic guitar, banjo, mandolin, harmonica
Moods: storytelling, nostalgic, uplifting, intimate
```

### Jazz
```
jazz [subgenre] [instruments] [mood] [setting]

Subgenres: smooth, bebop, fusion, latin, modal
Instruments: piano, saxophone, trumpet, double bass
Settings: smoky club, late night, sophisticated
```

### Classical
```
classical [period] [ensemble] [mood] [dynamics]

Periods: baroque, romantic, modern, minimalist
Ensembles: orchestra, string quartet, solo piano, chamber
Dynamics: sweeping, intimate, dramatic, subtle
```

## Mood Combinations

### High Energy + Positive
```
euphoric energetic uplifting triumphant anthemic powerful driving
```

### Low Energy + Positive
```
peaceful calm serene contemplative gentle soothing relaxing dreamy
```

### High Energy + Negative
```
aggressive intense dark chaotic frantic anxious explosive turbulent
```

### Low Energy + Negative
```
melancholic somber mournful introspective sad lonely haunting
```

### Complex/Nuanced
```
bittersweet nostalgic hopeful yearning wistful reflective
```

## Voice Descriptors

### Female Vocals
```
soft female vocals
ethereal soprano
powerful female voice
breathy intimate female
soulful alto
```

### Male Vocals
```
deep male vocals
raspy baritone
smooth tenor
powerful male voice
emotional male vocals
```

### Choir/Group
```
choir harmonies
gospel choir
layered vocals
harmonized voices
```

### Instrumental Only
```
instrumental
no vocals
no singing
instrumental only
```

## Tempo/Energy Words

### Fast/High Energy
```
uptempo driving energetic fast-paced explosive powerful
BPM: 120-180+
```

### Medium
```
mid-tempo moderate steady groovy
BPM: 90-120
```

### Slow/Low Energy
```
slow downtempo ballad laid-back relaxed gentle
BPM: 60-90
```

## Production Style

### Polished/Professional
```
polished clean crisp professional radio-ready high-quality
```

### Raw/Lo-fi
```
lo-fi raw gritty distorted vinyl warm tape hiss
```

### Atmospheric/Spacious
```
atmospheric spacious reverb-heavy ambient ethereal expansive
```

### Minimalist
```
minimal stripped-down sparse simple clean
```

## Era/Influence

### Decades
```
60s: psychedelic, british invasion, motown
70s: disco, funk, prog rock, punk
80s: synth-pop, new wave, hair metal, post-punk
90s: grunge, britpop, eurodance, gangsta rap
2000s: indie rock, emo, crunk, blog house
2010s: EDM, trap, indie folk, synthwave
Modern: hyperpop, bedroom pop, drill
```

## Effective Combinations

### Chill Study Music
```
lo-fi hip hop chill relaxing jazzy piano beats study music
```

### Epic Cinematic
```
orchestral cinematic epic powerful sweeping dramatic
```

### Summer Vibes
```
tropical house upbeat sunny positive summer vibes feel-good
```

### Emotional Ballad
```
emotional piano ballad soft vocals heartfelt intimate powerful
```

### Party/Club
```
EDM house energetic dance club banging drops build-up
```

## What to Avoid

| Don't | Why | Instead |
|-------|-----|---------|
| Artist names | Copyright issues | Describe the style |
| "Like X song" | Too specific | Describe elements |
| Brand names | May be filtered | Generic terms |
| 20+ keywords | Dilutes focus | 8-12 key terms |
| Contradictions | Confuses model | Consistent mood |
