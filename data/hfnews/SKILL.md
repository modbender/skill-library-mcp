---
name: hfnews
description: Fetch and filter news from multiple sources with stopwords/blacklist support. Customized for Hubert's interests (IT, Cybersecurity) with political/sports noise filtered out.
---

# News Fetcher

## Usage

```bash
# All categories
news

# Specific category
news Allgemeines
news IT
news Cybersecurity
```

## Output Format

Simple list:
```
Allgemeines:
- Titel URL
- Titel URL
- Titel URL
- Titel URL
- Titel URL

IT:
- Titel URL
- Titel URL
- Titel URL
- Titel URL
- Titel URL

Cybersecurity:
- Titel URL
- Titel URL
- Titel URL
- Titel URL
- Titel URL
```

## Blacklist

Words to filter out:
- Sport, Trump/USA, SPD, Iran, Bürgergeld, Mietreform, Mieterschutz
- Regenpause, Ukraine, Putin, Epstein
- Bilder des Tages, Karrierefrage
- Stellenmarkt, Jobs

## Categories

### Allgemeines
- Tagesschau: https://www.tagesschau.de/
- FAZ: https://www.faz.net/aktuell/
- WiWo: https://www.wiwo.de/
- Süddeutsche: https://www.sueddeutsche.de/
- Spiegel: https://www.spiegel.de/
- Mittelbayerische: https://www.mittelbayerische.de/lokales/stadt-regensburg

### IT
- Heise: https://www.heise.de/
- Golem: https://www.golem.de/
- Slashdot: https://slashdot.org/

### Cybersecurity
- The Hacker News: https://thehackernews.com/
- BleepingComputer: https://www.bleepingcomputer.com/
- Logbuch Netzpolitik: https://logbuch-netzpolitik.de/
