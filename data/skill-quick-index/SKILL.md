---
name: skill-quick-index
version: 1.0.1
description: Build a wide-trigger, precise-match index for local OpenClaw skills (L1-L3), then quickly route by intent/category/keywords.
---

# Skill Quick Index

Create and use a fast local index so users can trigger skills with natural language (broad keywords) and still get precise skill routing.

## What this skill does

1. Scans local skills in `~/.openclaw/workspace/skills/*/SKILL.md`
2. Builds a category + keyword index for L1/L2/L3 routing
3. Supports quick lookup from any user phrase
4. Produces recommended skills with priority order

## Files

- `index/skill_index.json` — index database
- `scripts/skill_lookup.py` — local query tool
- `README.md` — usage docs

## Usage

```bash
python3 scripts/skill_lookup.py "打开网页并截图"
python3 scripts/skill_lookup.py "ocr识别图片文字"
python3 scripts/skill_lookup.py "自动化工作流"
```

## Matching strategy

- Exact skill trigger > category keyword > generic intent
- Multi-keyword query returns intersected/re-ranked skills
- Keeps L0 out of normal routing unless explicitly requested

## Typical triggers

- Browser: 浏览器 / 网页 / 抓取 / 截图 / 登录 / 表单
- Docs: word / docx / csv / 报告 / 导出
- AI Agent: evomap / agent / 协作 / 节点
- Media: ocr / 字幕 / youtube / 语音转文字
- Team: codingteam / 子代理 / 任务分解
