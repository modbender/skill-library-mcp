# Torah Scholar 📜

**Search and explore Jewish texts with AI agents** — powered by the Sefaria API.

[![ClawHub](https://img.shields.io/badge/ClawHub-torah--scholar-blue)](https://clawhub.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<a href="https://www.sefaria.org"><img src="assets/powered-by-sefaria-dark.png" alt="Powered by Sefaria" width="200"></a>

## Overview

Torah Scholar is an OpenClaw/MCP skill that gives AI agents access to the world's largest open-source library of Jewish texts:

- **Tanach** (Torah, Nevi'im, Ketuvim)
- **Talmud** (Bavli & Yerushalmi)
- **Mishnah & Midrash**
- **Commentaries** (Rashi, Ramban, Ibn Ezra, Sforno, and hundreds more)
- **Kabbalah** (Zohar)
- **Halacha** (Shulchan Aruch, Mishneh Torah)

All texts available in **Hebrew and English**.

## Features

| Command | Description |
|---------|-------------|
| `torah search <query>` | Full-text search across all texts |
| `torah verse <ref>` | Get text with Hebrew + English translation |
| `torah links <ref>` | Find commentaries and cross-references |
| `torah related <ref>` | Discover related texts and topics |
| `torah parsha` | This week's Torah portion |
| `torah today` | Daily learning schedule (Daf Yomi, etc.) |
| `torah dvar` | Generate dvar Torah outlines with sources |

## Quick Start

### Installation

```bash
# Via ClawHub
clawhub install torah-scholar

# Or copy to OpenClaw skills directory
cp -r torah-scholar ~/.openclaw/skills/
```

### Usage Examples

```bash
# Search for a concept
torah search "love your neighbor"

# Get a specific verse
torah verse "Genesis 1:1"
torah verse "Berakhot 2a"

# Find commentaries
torah links "Leviticus 19:18"

# This week's parsha
torah parsha

# Generate a dvar Torah
torah dvar
torah dvar ref "Esther 4:14"
torah dvar theme "faith"
```

## Reference Formats

| Text Type | Format | Example |
|-----------|--------|---------|
| Torah | Book Chapter:Verse | `Genesis 1:1` |
| Prophets | Book Chapter:Verse | `Isaiah 40:1` |
| Writings | Book Chapter:Verse | `Psalms 23` |
| Talmud Bavli | Tractate Daf+Side | `Berakhot 2a` |
| Mishnah | Mishnah Tractate Ch:M | `Mishnah Avot 1:1` |
| Midrash | Midrash Name Section | `Genesis Rabbah 1:1` |

## Dvar Torah Generator

Generate structured Torah insights with sources:

```bash
torah dvar
```

**Output includes:**
- Opening verses (Hebrew + English)
- Key commentaries (Rashi, Ramban, etc.)
- Related sources across the library
- Suggested dvar structure
- Themes to explore

## API

For programmatic access:

```python
from scripts.sefaria import get_text, search, get_links

# Get verse
result = get_text("Genesis 1:1")
print(result["he"])   # Hebrew
print(result["text"]) # English

# Search
results = search("golden rule", limit=10)

# Get commentaries
links = get_links("Exodus 20:1")
```

## Use Cases

- **Torah Study** — Quick access to texts and commentaries
- **Dvar Torah Prep** — Generate outlines with sources
- **Research** — Cross-reference and explore connections
- **Education** — Build Torah learning tools
- **Content Creation** — Source-backed Jewish content

## Requirements

- Python 3.8+
- Internet connection (Sefaria API)
- No API key required

## Credits

- **Sefaria** — The incredible open-source Jewish library
- **OpenClaw** — AI agent framework

## License

MIT License — Use freely, contribute back!

## Links

- [Sefaria](https://www.sefaria.org)
- [Sefaria API Docs](https://developers.sefaria.org)
- [ClawHub](https://clawhub.com)
- [OpenClaw](https://github.com/openclaw/openclaw)

---

**Built with ❤️ for the Jewish community**

*"The study of Torah is equal to all the other commandments." — Mishnah Peah 1:1*
