---
name: evomap-quality-generator
description: Generate high-quality EvoMap bundles from REAL skills with actual code
version: 1.0.0
signals:
  - evomap quality
  - real skill bundle
  - code snippet
  - high quality asset
---

# EvoMap Quality Generator v1.0.0

> Generate high-quality Gene+Capsule bundles from REAL workspace skills

## Problem

批量生成的资产只是模板占位符，没有实际价值。

## Solution

此 Skill 从工作区的**真实 skills** 生成高质量资产：

1. **扫描** - 查找所有有 SKILL.md 的 skills
2. **提取** - 获取名称、描述、信号、实际代码
3. **生成** - 创建包含真实代码的 bundle

## Features

- ✅ 从真实 skills 生成
- ✅ 包含实际 code_snippet (50-3000 字符)
- ✅ 真实的 strategy 步骤
- ✅ 符合所有 EvoMap 验证要求

## Usage

```bash
# 扫描可用的 skills
node index.js scan

# 从单个 skill 生成
node index.js generate feishu-doc ./my-bundles

# 从所有 skills 生成高质量 bundle
node index.js all ./evomap-quality

# 验证 bundles
node index.js validate ./evomap-quality
```

## Output Structure

```json
{
  "Gene": {
    "signals_match": [...],
    "strategy": ["step 1", "step 2", ...],
    "content": "详细描述..."
  },
  "Capsule": {
    "code_snippet": "实际代码 (50-3000 chars)",
    "content": "验证说明...",
    "confidence": 0.95,
    "success_streak": 5
  },
  "EvolutionEvent": {...}
}
```

## Example

```bash
$ node index.js scan
Found 45 skills:

- api-client: api client, rest, http
- feishu-doc: feishu document
- email-sender: send email, smtp
- ...

$ node index.js all ./evomap-quality
Generating 45 high-quality bundles...

✓ api-client
✓ feishu-doc
✓ email-sender
...

Generated 45 bundles in ./evomap-quality
```
