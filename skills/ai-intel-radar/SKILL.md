---
name: ai-intel-radar
description: Build a high-signal AI intelligence brief from fresh web sources, with separate daily and weekly formats. Use when the user asks for latest AI news, trend monitoring, market/tech updates, or actionable AI scouting reports for business decisions.
---

# AI Intel Radar

Produce concise, decision-ready AI intelligence in Chinese by default.

## Mode selection

- If user asks "today" / "daily" / "最新": use **Daily mode**
- If user asks "this week" / "weekly" / "本周": use **Weekly mode**
- If unspecified: default to **Daily mode**

See source guidance in `references/sources.md`.

## Daily mode output (strict)

1. **3条快讯**（发生了什么）
2. **2条技术深度**（为什么重要）
3. **1条商业判断**（潜在影响）
4. **3条可执行建议**（本周可做）

Each item must include:
- 结论一句话
- 1条来源链接
- 时间（若可得）

## Weekly mode output (strict)

1. **趋势变化（3条）**
2. **机会清单（3条）**
3. **风险清单（3条）**
4. **本周Top 3行动**

## Quality rules

- Prefer official and primary sources first.
- Avoid hype and repeated rumor chains.
- Mark uncertain claims as "待验证".
- Do not dump long lists; keep high signal only.
- If source freshness is weak, explicitly say so.

## Safety

- Never expose secrets/tokens.
- Never fabricate links.
- If no reliable updates are found, return a short "低变化日" summary.
