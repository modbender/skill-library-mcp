# Example Output & Readability

## Example 1: Query "iran 3h"

**Command**: `node scripts/query.mjs iran 3h`

**Output** (excerpt):

```
🔍 iran · 3h
LANG: en

--- Time-filtered (5 items) ---

[politics] Oil prices rise after ships attacked near Strait of Hormuz (2h ago)
  → https://www.bbc.com/news/articles/...

[middleeast] US-Israel war on Iran live: explosions heard in Gulf cities... (2小时前)
  → https://www.theguardian.com/...

--- 摘要 ---

### politics
- **Oil prices rise after ships attacked near Strait of Hormuz** (BBC World) [原文](...)
- **Iran after 48 hours: Tactical success, strategic uncertainty - CNN** (CNN World) [原文](...)

## 伊朗相关事件
- Larijani: Trump has dragged the region into chaos...
- Iran International's audience reported several heavy explosions in Tehran...
```

---

## Example 2: English query "layoffs"

**Command**: `node scripts/query.mjs layoffs`

**Output**:

```
🔍 layoffs · 全部
LANG: en

### layoffs
- **Jack Dorsey just halved the size of Block's employee base** (TechCrunch Layoffs) [原文](...)
- **eBay to lay off 800 staff** (TechCrunch Layoffs) [原文](...)
- **Lucid Motors slashes 12% of its workforce** (TechCrunch Layoffs) [原文](...)
```

---

## Readability: Human vs AI

| Aspect | For Human | For AI |
|--------|-----------|--------|
| Structure | Headers, lists, links | Structured, parseable |
| Language | Mostly English | LANG hint for translation |
| Density | Many items | Suitable for summarization |
| **Conclusion** | Scannable; Agent should translate for Chinese users | Ideal for Agent to translate + summarize |
