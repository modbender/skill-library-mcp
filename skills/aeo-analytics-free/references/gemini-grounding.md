# Using Gemini API with Grounding for AEO Analytics

## Overview

Gemini's API supports "grounding with Google Search" — when enabled, the model searches the web before answering and exposes the sources it used. This is the most direct free signal for AI visibility.

## Setup

1. Get a free API key from https://aistudio.google.com/apikey
2. Store it as environment variable `GEMINI_API_KEY` or in the agent's keychain

## API Call (grounding enabled)

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "What is the best AI travel planner that gives real local recommendations?"}]}],
    "tools": [{"googleSearch": {}}]
  }'
```

## Response Structure (relevant fields)

```json
{
  "candidates": [{
    "content": {
      "parts": [{"text": "The AI's response text..."}]
    },
    "groundingMetadata": {
      "searchEntryPoint": {
        "renderedContent": "<HTML snippet>"
      },
      "groundingChunks": [
        {
          "web": {
            "uri": "https://example.com/page",
            "title": "Page Title"
          }
        }
      ],
      "groundingSupports": [
        {
          "segment": {
            "startIndex": 0,
            "endIndex": 150,
            "text": "The specific text supported by this source"
          },
          "groundingChunkIndices": [0],
          "confidenceScores": [0.95]
        }
      ],
      "webSearchQueries": [
        "best AI travel planner local recommendations"
      ]
    }
  }]
}
```

## How to Extract Visibility Data

1. **Brand mentioned?** — Search `candidates[0].content.parts[0].text` for brand names (case-insensitive)
2. **Brand cited?** — Search `groundingChunks[].web.uri` for the brand's domain
3. **Competitors cited?** — Extract all domains from `groundingChunks` that aren't the target brand
4. **What AI searched for** — `webSearchQueries` shows how the AI interpreted the prompt
5. **Confidence** — `groundingSupports[].confidenceScores` shows how confident the AI is in each citation

## Free Tier Limits

- Gemini 2.0 Flash: 15 RPM, 1,500 RPD, 1M TPM
- Gemini 1.5 Flash: 15 RPM, 1,500 RPD

For a typical scan of 10-20 prompts, you'll use ~20 requests — well within free limits. You could run 75 scans per day and stay free.

## Fallback: Web Search Proxy

If no Gemini API key is available, use `web_search` as a proxy:
1. Search the exact prompt text
2. Check if brand's domain appears in results
3. Less direct than Gemini grounding but requires zero API keys

This method detects traditional search visibility, not AI citation specifically. Use it as a supplement, not a replacement.
