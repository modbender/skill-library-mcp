---
name: geepers-etymology
description: Look up word etymology, historical sound changes, language family trees, and word evolution through the dr.eamer.dev etymology and diachronic linguistics API. Use for language history research, writing, or exploring how words have changed over time.
---

# Dreamer Etymology

Access etymology and historical linguistics data at `https://api.dr.eamer.dev`.

## Authentication

```bash
export DREAMER_API_KEY=your_key_here
```

## Endpoints

### Word Etymology
```
GET https://api.dr.eamer.dev/v1/etymology/word?word=serendipity
```
Returns origin language, root words, historical forms, and first known use.

### Explore Word History
```
GET https://api.dr.eamer.dev/v1/etymology/explore?word=knight&lang=en
```
Returns full etymology chain, related words, and language family context.

### Sound Change Rules (Diachronica)
```
GET https://api.dr.eamer.dev/v1/etymology/sound-changes?from=proto-indo-european&to=english
```
Returns documented phonological changes between proto-languages and descendants.

## When to Use
- Researching word origins and historical meaning shifts
- Understanding cognates across related languages
- Exploring how pronunciation has changed over centuries
- Writing that benefits from etymological depth

## Don't Use When
- You need standard dictionary definitions (use a dictionary API)
- You need very recent neologisms (data focuses on documented historical forms)
