---
name: podcast-to-substack
description: Publish podcast episodes from RSS + Notion to Substack with reliable Apple Podcasts embedding and image extraction, then generate LinkedIn-ready companion posts. Use when asked to run or improve podcast-to-substack workflows, fix Notion image fetch failures, prevent Substack embed-as-text issues, or cross-post episode summaries to LinkedIn.
---

# Podcast Substack + LinkedIn

Run this workflow when handling Realist podcast episode publishing.

## Inputs
- RSS feed URL
- Notion data source/database ID with episode scripts
- Notion API key (`NOTION_API_KEY` or `~/.config/notion/api_key`)
- Substack publish access

## Workflow
1. Fetch recent episodes:
```bash
python3 scripts/fetch_rss.py "$RSS_URL" 3
```
2. Fetch episode script + images from Notion (recursive block traversal, image downloads included):
```bash
python3 scripts/fetch_notion_episode.py "EPISODE_NUMBER"
```
3. Build Substack draft content from script text.
4. Publish with stable embed behavior using the playbook in `references/substack-embed-playbook.md`.
5. Generate LinkedIn post copy from the same content:
```bash
python3 scripts/render_linkedin_post.py --json-file episode.json
```
6. Post or queue the LinkedIn copy.

## Non-negotiable rules
- Do not use iframe code or markdown links for podcast embeds in Substack.
- Prefer duplicating the existing Substack draft template that already has a working embed block.
- If creating a fresh post, use `/embed` and confirm the player card renders before publishing.
- Use top-level Apple Podcasts show URL for reliable fallback.

## References
- Substack embed behavior: `references/substack-embed-playbook.md`
- LinkedIn formatting: `references/linkedin-playbook.md`
