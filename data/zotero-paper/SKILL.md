---
name: zotero-scholar
description: 将论文保存到 Zotero 文库，请按照 userid:apiKey 的格式配置 ZOTERO_CREDENTIALS 环境变量。
homepage: https://www.zotero.org
metadata:
  {
    "openclaw":
      {
        "emoji": "📚",
        "requires": { "bins": ["uv"], "env": ["ZOTERO_CREDENTIALS"] },
        "primaryEnv": "ZOTERO_CREDENTIALS",
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      }
  }
---


# Zotero Scholar

专业的文献入库助手。可以将论文元数据、PDF 链接以及 AI 生成的总结一键保存到你的 Zotero 库中。

## 使用示例
可以读取环境变量 `ZOTERO_CREDENTIALS` 中的 Zotero 凭据，格式为 `userid:apiKey`。

### 使用环境变量运行

```bash
uv run {baseDir}/scripts/save_paper.py \
  --title "Attention Is All You Need" \
  --authors "Vaswani et al." \
  --url "https://arxiv.org/abs/1706.03762"
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--title` | 论文标题 |
| `--authors` | 作者列表（逗号分隔） |
| `--url` | 论文链接 (用于排重) |
| `--abstract` | 论文摘要 |
| `--summary` | (AI 生成) 简短总结或 Insight |
| `--tags` | 标签列表（逗号分隔） |
