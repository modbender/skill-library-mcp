---
name: sentinel-mood
description: Analyze the sentiment and emotional tone of text using NLTK and VADER. Use this to gauge user mood, detect urgency, or analyze content tone.
metadata:
  openclaw:
    emoji: "🎭"
    requires:
      python_packages:
        - nltk
---

# Sentinel Mood

A lightweight sentiment analysis skill powered by NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner). It is specifically tuned for social media texts, conversational language, and short updates.

## Capabilities

- **Analyze Sentiment:** Get positive, negative, neutral, and compound scores for any text.
- **Detect Tone:** (Implicit) Infer tone based on polarity scores.

## Usage

**User:** "Analyze the sentiment of this message: 'I love how this project is turning out, great job!'"
**Agent:** [Runs skill] -> Returns sentiment scores (e.g., compound: 0.8, pos: 0.6).

## Technical Details

This skill uses a Python script (`analyze.py`) that imports `nltk.sentiment.SentimentIntensityAnalyzer`.

### Dependencies

- Python 3
- `nltk` library (`pip install nltk`)
- `vader_lexicon` (downloaded via `nltk.downloader`)

## Implementation

The skill executes a python script that takes text as an argument and outputs JSON.
