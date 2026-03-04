---
name: near-content-creator
description: Generate NEAR-focused content (threads, market updates, ecosystem news, tutorials).
metadata: {"author":"mastrophot","version":"0.1.0","homepage":"https://github.com/mastrophot/near-content-creator"}
---

# NEAR Content Creator Skill

Generate publication-ready NEAR content in multiple formats for social and educational use.

Implementation entrypoint: `{baseDir}/dist/index.js`

## When to Use

Use this skill when you need:
- Educational social content for NEAR audience (threads).
- Daily NEAR market digest with timestamped metrics.
- Curated ecosystem news with links.
- Tutorial draft for a specific NEAR topic.

## Commands

```python
@skill.command("near_content_thread")
async def generate_thread(topic: str) -> list:
    """Generate educational Twitter thread"""

@skill.command("near_content_update")
async def market_update() -> str:
    """Generate daily market update"""

@skill.command("near_content_news")
async def ecosystem_news() -> list:
    """Compile ecosystem news"""

@skill.command("near_content_tutorial")
async def generate_tutorial(topic: str) -> str:
    """Generate tutorial content"""
```

## Notes

- Market updates include timestamped metrics and are informational only.
- News compilation prefers official NEAR and NEAR-adjacent sources with links, deduplication, and source ranking.
- Tutorials are structured for practical execution, not generic copywriting.
- Thread output is normalized into stable `1/8` ... `8/8` structure for direct publishing.
