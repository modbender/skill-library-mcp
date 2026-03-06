---
name: z-article-card
description: 长文分页卡片生成器（文章→多张 PNG）。触发词：长文、文章转图、分页卡片、多图、帮我把文章做成图、做成卡片、生成多图。
---

# z-article-card

将长文章（Markdown 或纯文本）渲染成多张 3:4 分页卡片图，通过 message 工具顺序发图。

## 环境要求

- Python 3
- Google Chrome（macOS：`/Applications/Google Chrome.app`；Linux：`chromium`）
- `pip install markdown`

## 执行流程

1. **获取内容**：用户粘贴文本 或 用 `web_fetch` 抓取 URL 正文
2. **渲染分页**：调用 `scripts/render_article.py`，脚本自动按句末/换行边界分页
3. **顺序发图**：用 message 工具逐张发送 `card_01.png`、`card_02.png`…

## 示例调用

```bash
python3 /path/to/skills/z-article-card/scripts/render_article.py \
  --title "文章标题" \
  --text "全文内容（支持 Markdown 语法）" \
  --out-dir /path/to/workspace/tmp/article_xxx \
  --chars-per-page 300 \
  --highlight "#3d6b4f" \
  --bg "#f9fcfa" \
  --footer "公众号 · 早早集市"
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--title` | 必填 | 文章标题，显示在每张卡片顶部 |
| `--text` | 必填 | 全文内容（Markdown 格式） |
| `--out-dir` | 必填 | 输出目录，脚本自动创建 |
| `--chars-per-page` | `280` | 每页字符上限（推荐 300） |
| `--highlight` | `#3d6b4f` | 品牌高亮色 |
| `--bg` | `#f9fcfa` | 背景色 |
| `--footer` | `公众号 · 早早集市` | 底部水印文字 |

## 平台预设

| 平台 | `--footer` | `--bg` | `--highlight` |
|------|-----------|--------|--------------|
| 公众号（默认） | `公众号 · 早早集市` | `#f9fcfa` | `#3d6b4f` |
| 小红书 | `小红书 · 阿康` | `#fef9f0` | `#e53935` |

## 模板

- `assets/templates/article-3-4.html` — 分页卡片模板（3:4，900×1200）
- `assets/styles/md.css` — Markdown 渲染样式，**用户可自定义**

详见 `references/article-3-4.md`
