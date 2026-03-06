---
name: torah-scholar
description: Search and explore Jewish texts (Torah, Tanach, Talmud, Midrash, commentaries) via Sefaria API. Use when researching Torah sources, looking up verses, finding commentaries, cross-references, or preparing divrei Torah. Supports Hebrew and English. Handles references like "Genesis 1:1", "Berakhot 2a", "Mishnah Avot 1:1".
keywords:
  - torah
  - jewish
  - judaism
  - sefaria
  - talmud
  - bible
  - hebrew
  - tanach
  - mishnah
  - midrash
  - dvar torah
  - parsha
  - rabbi
  - yeshiva
  - study
  - religious
  - scripture
---

# Torah Scholar

Research Jewish texts with full access to the Sefaria library: Tanach, Talmud Bavli/Yerushalmi, Mishnah, Midrash, Zohar, and thousands of commentaries.

## Quick Start

```bash
# Search across all texts
torah search "love your neighbor"

# Get specific verse with Hebrew + English
torah verse "Leviticus 19:18"

# Find commentaries on a verse
torah links "Genesis 1:1"

# This week's parsha
torah parsha

# Today's learning schedule (Daf Yomi, etc.)
torah today
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `torah search <query>` | Full-text search | `torah search "tikkun olam"` |
| `torah verse <ref>` | Get text + translation | `torah verse "Psalms 23"` |
| `torah links <ref>` | Commentaries & cross-refs | `torah links "Exodus 20:1"` |
| `torah related <ref>` | Related texts & topics | `torah related "Deuteronomy 6:4"` |
| `torah parsha` | This week's portion | `torah parsha` |
| `torah today` | Daily learning schedule | `torah today` |
| `torah dvar` | Generate dvar Torah | `torah dvar` |
| `torah dvar ref <ref>` | Dvar on specific verse | `torah dvar ref "Genesis 12:1"` |
| `torah dvar theme <theme>` | Dvar with theme focus | `torah dvar theme "leadership"` |

## Reference Formats

### Tanach (Hebrew Bible)
- Books: Genesis, Exodus, Leviticus, Numbers, Deuteronomy (Torah)
- Nevi'im: Joshua, Judges, Samuel, Kings, Isaiah, Jeremiah, Ezekiel, etc.
- Ketuvim: Psalms, Proverbs, Job, Song of Songs, Ruth, Ecclesiastes, etc.
- Format: `Book Chapter:Verse` or `Book Chapter:Start-End`
- Examples: `Genesis 1:1`, `Psalms 23`, `Isaiah 40:1-5`

### Talmud
- Bavli (Babylonian): `Tractate DafNumber` + `a` or `b`
- Examples: `Berakhot 2a`, `Shabbat 31a`, `Bava Metzia 59b`
- Major tractates: Berakhot, Shabbat, Eruvin, Pesachim, Yoma, Sukkah, Beitzah, Rosh Hashanah, Taanit, Megillah, Moed Katan, Chagigah, Yevamot, Ketubot, Nedarim, Nazir, Sotah, Gittin, Kiddushin, Bava Kamma, Bava Metzia, Bava Batra, Sanhedrin, Makkot, Shevuot, Avodah Zarah, Horayot, Zevachim, Menachot, Chullin, Bekhorot, Arakhin, Temurah, Keritot, Meilah, Tamid, Niddah

### Mishnah
- Format: `Mishnah Tractate Chapter:Mishnah`
- Examples: `Mishnah Avot 1:1`, `Mishnah Berakhot 1:1`

### Midrash
- Midrash Rabbah: `Genesis Rabbah 1:1`, `Exodus Rabbah 1:1`
- Midrash Tanchuma: `Tanchuma Bereshit 1`
- Other: `Pirkei DeRabbi Eliezer 1`

### Commentaries
- Access via `torah links <ref>` to see Rashi, Ramban, Ibn Ezra, Sforno, etc.

## Research Workflows

### Find Sources on a Topic
```bash
# 1. Search for topic
torah search "repentance teshuvah"

# 2. Get full text of relevant result
torah verse "Maimonides Hilchot Teshuvah 2:1"

# 3. Find related commentaries
torah links "Maimonides Hilchot Teshuvah 2:1"
```

### Prepare a Dvar Torah
```bash
# 1. Get this week's parsha
torah parsha

# 2. Read the opening verses
torah verse "Genesis 12:1-5"  # (adjust to actual parsha)

# 3. Find commentaries for insights
torah links "Genesis 12:1"

# 4. Search for thematic connections
torah search "lech lecha journey"
```

### Study Daf Yomi
```bash
# 1. Check today's daf
torah today

# 2. Get the text
torah verse "Berakhot 2a"  # (from calendar)

# 3. See what it connects to
torah links "Berakhot 2a"
```

### Generate a Dvar Torah
```bash
# Quick dvar for this week's parsha
torah dvar

# Focus on specific verse
torah dvar ref "Exodus 28:1"

# Explore a theme across sources
torah dvar theme "holiness and service"
```

The dvar generator outputs:
- Opening verses with Hebrew + English
- Key commentaries (Rashi, Ramban, Sforno, etc.)
- Related sources across the library
- Suggested structure (hook → problem → sources → resolution → application)
- Themes to explore further

## Python API

For advanced usage, import directly:

```python
from scripts.sefaria import get_text, search, get_links, get_parsha

# Get verse
result = get_text("Genesis 1:1")
print(result.get("he"))  # Hebrew
print(result.get("text"))  # English

# Search
results = search("golden rule", limit=5)

# Get commentaries
links = get_links("Leviticus 19:18")
```

## Tips

- **Hebrew search**: Sefaria supports Hebrew queries: `torah search "ואהבת לרעך כמוך"`
- **Partial refs**: `torah verse "Psalms 23"` returns entire chapter
- **Ranges**: `torah verse "Genesis 1:1-5"` for multiple verses
- **Talmud context**: Daf refs include both amud a and b context

## Limitations

- Rate-limited by Sefaria (be respectful of their free API)
- Some texts may have Hebrew only (no English translation)
- Search is full-text, not semantic (exact/stemmed matches)

## Source

Powered by [Sefaria](https://www.sefaria.org) — the free, open-source library of Jewish texts.
