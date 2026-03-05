---
name: geepers-corpus
description: Query the COCA (Corpus of Contemporary American English) linguistics API for word frequency, collocations, concordances, and historical usage trends. Use for linguistic research, writing assistance, or understanding how words are actually used in American English.
---

# Dreamer Corpus

Access the COCA corpus API at `https://api.dr.eamer.dev`.

COCA contains 1+ billion words of contemporary American English from spoken, fiction, magazine, newspaper, and academic sources.

## Authentication

```bash
export DREAMER_API_KEY=your_key_here
```

## Endpoints

### Word Search / Concordance
```
GET https://api.dr.eamer.dev/v1/corpus/search?word=serendipity&limit=20
```
Returns KWIC (keyword-in-context) examples showing the word in actual usage.

### Collocations
```
GET https://api.dr.eamer.dev/v1/corpus/collocations?word=run&pos=verb&limit=20
```
Returns words that statistically co-occur with the target word (MI score, frequency).

### Frequency
```
GET https://api.dr.eamer.dev/v1/corpus/frequency?word=algorithm&genre=academic
```
Returns frequency per million words, with optional genre filter: `spoken`, `fiction`, `magazine`, `newspaper`, `academic`.

## When to Use
- Checking how formal or common a word is in real American English
- Finding natural collocations for writing assistance
- Linguistic research on word usage patterns
- Historical frequency trends across decades

## Don't Use When
- You need non-English corpora
- You need corpora other than contemporary American English (COCA is 1990-present)
