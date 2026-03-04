---
name: vajra
description: Analyze URLs, YouTube videos, tweets, or text for quality, bias, and reliability using the Vajra API (vajra.to). Use when the user asks to fact-check, analyze, evaluate, score, or assess the quality/bias/reliability of any web content, article, video, tweet, or text. Also use when asked to "vajra" something or run content through a signal filter.
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["VAJRA_API_KEY"] },
      },
  }
---

# Vajra - Signal Filter for the Internet

Vajra is a content-analysis API by [Humanity Labs](https://humanitylabs.org). It scores content for epistemic quality (1-10), detects bias, extracts key takeaways, flags questionable claims, and produces structured verdicts.

## Privacy and Data Handling

**Important:** This skill sends content to the Vajra API at `https://www.vajra.to`. Before using it:

- Content you submit (URLs, text) is transmitted to Vajra's servers for analysis.
- Analyzed content is **cached server-side**. If another user submits the same URL, they receive the cached result (0 credits). The original text you submit is **not stored** -- only the analysis output.
- Every analysis generates a **public permalink** (e.g. `vajra.to/a/ID`). These are shareable and publicly accessible.
- **Do not submit private, proprietary, or personally identifiable content** unless you understand and accept this behavior.
- Vajra's privacy policy and terms are available at [vajra.to](https://www.vajra.to).

## Setup

An API key is required. Get one free at [vajra.to/dashboard](https://www.vajra.to/dashboard) (Connections tab).

The key must be stored as the environment variable `VAJRA_API_KEY`. The agent will be prompted to set this during installation.

## Analyze Content

```bash
curl -s -X POST https://www.vajra.to/api/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $VAJRA_API_KEY" \
  -d '{"content": "URL_OR_TEXT", "type": "url"}'
```

Set `type` to `"text"` for raw text (max 50,000 chars). Default is `"url"`.

Supported content: articles, YouTube videos, X/Twitter posts, and raw text.

## Parse the Response

The response JSON contains:

```
success        - boolean
cached         - boolean (0 credits if true)
credits_used   - 0 or 1
url            - permalink to full report (e.g. https://www.vajra.to/a/UUID)
analysis.title - content title
analysis.quality_score - 1-10 rating
analysis.bias_level    - bias assessment
analysis.markdown      - full report in markdown
analysis.metadata.tldr - one-sentence summary
analysis.metadata.verdict      - reliability assessment
analysis.metadata.key_takeaways - array of takeaways
analysis.metadata.warnings      - array of warnings
```

## Present Results

When showing results to the user, format as:

```
**Title** - Quality: X/10
TLDR: [tldr]
Verdict: [verdict]
Key takeaways: [list]
Warnings: [list if any]
Full report: [permalink url]
```

## Retrieve Existing Analysis

Fetch a previously completed analysis by ID (no auth needed, public endpoint):

```bash
curl -s https://www.vajra.to/api/analysis/ANALYSIS_ID
```

## Credits and Pricing

- Cached results cost 0 credits (same URL already analyzed by any user)
- Free tier: 5 analyses/month
- Pro: 100 analyses/month ($12/mo or $79/yr)
- Analyses take 10-60 seconds depending on content length
