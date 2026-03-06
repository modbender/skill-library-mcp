---
name: arxiv-translate
description: Download Chinese translations of arXiv papers.
---

# arxiv-translate

Download Chinese translations of arXiv papers.

## Usage

```
arxiv-translate 2601.06798
```

or with full URL:

```
arxiv-translate https://arxiv.org/abs/2601.06798
```

## What it does

1. Extracts the arXiv ID from input (supports both ID and full URL)
2. Generates the translation service URL: `https://hjfy.top/arxiv/{id}`
3. Provides the user with a clickable link to access the translation
4. Explains that translations are generated on-demand and may take a moment

## Notes

- Translations are generated on-demand by the service
- The first access may take some time as the translation is being processed
- This skill provides a direct link; the user visits the site to download
