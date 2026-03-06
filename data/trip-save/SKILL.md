---
name: trip-save
description: Save travel inspiration from YouTube videos, Instagram reels, blog URLs, tweets, or plain text like "want to visit Hampi". Extracts destination, auto-tags by vibe and location, stores in memory.
---

# Trip Save

## When to activate
- User forwards a URL (YouTube, Instagram, blog, tweet)
- User says "save this", "want to visit X", "adding X to my list", "bookmark this"

## URL handling
1. Use web search or web fetch to get the page content
2. Extract: destination name, key details, vibe
3. Auto-tag and store in memory

## Plain text saves
- "want to visit Hampi" → destination: Hampi
- Extract any vibe/budget hints from context

## Auto-tagging
- **Location:** state/region (Himachal, Rajasthan, Goa, Kerala)
- **Vibe:** mountains, beaches, heritage, adventure, spiritual, nightlife, offbeat
- **Budget:** budget, mid-range, luxury
- **Source:** youtube, instagram, blog, text, voice

## Memory storage
Remember each save as:
"Saved destination: [name] | Tags: [tags] | Source: [url or text] | Date: [today]"

## Recall
When user asks "show my saved places" or "what did I save":
- List all saved destinations from memory
- Support filtering: "show my beach saves"

## Response
"✓ Saved: Kasol · mountains, Himachal, budget · from YouTube"

If destination unclear: "Saved the link. What place is this about?"

## Rules
- Don't summarize the article/video — just save and confirm
- Don't give planning advice on save
