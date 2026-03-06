---
name: knowledge-base-collector
description: Collect and organize a personal knowledge base from URLs (web/X/WeChat) and screenshots. Use when the user says they want to save an URL, ingest a link, archive content to KB, tag/classify notes, store screenshots, or search their saved knowledge in Telegram. Supports WeChat via a connected macOS node when cloud fetch is blocked.
---

## Summary

- Ingest: web URLs, X/Twitter links, WeChat Official Account links (mp.weixin.qq.com), and screenshots
- Store: writes to a shared KB folder with per-item `content.md` + `meta.json` and a global `index.jsonl`
- Organize: tag-first classification with richer tags (e.g. `#agent`, `#coding-agent`, `#claude-code`, `#mcp`, `#rag`, `#prompt-injection`, `#security`, `#pricing`, `#database`)
- WeChat: cloud fetch may be blocked; when a macOS node (e.g. Reed-Mac) is online, prefer node-side fetch to improve success rate; otherwise create a placeholder entry
- Search: designed to support Telegram Q&A / search flows on top of the index and content

把用户发来的链接/截图沉淀到共享知识库（KB），并做标签化整理。

## 默认 KB 位置
- KB Root（可改）：`/home/ubuntu/.openclaw/kb`
- 索引：`kb/20_Inbox/urls/index.jsonl`
- 每条内容目录：`kb/20_Inbox/urls/<YYYY-MM>/<item>/content.md + meta.json`

> 目标：**先入库不丢**，再迭代“摘要/标签/检索”。

## 你要做的事（按输入类型）

### 1) 普通网页 / X(Twitter) / 公众号 URL 入库
运行脚本：

```bash
python3 /home/ubuntu/.openclaw/skills/knowledge-base-collector/scripts/ingest_url.py "<URL>" --tags "#optional" --note "context"
```

行为：
- 自动识别来源（web/x/wechat）
- 优先用 `r.jina.ai` 抽取正文（无需登录）
- 公众号遇到风控会写占位条目：`status=blocked_verification` + tag `#needs-manual`
- 对同一 URL 做 key 去重（已存在则跳过）

#### WeChat 更高成功率（推荐路径）
当云端抓取命中“环境异常/验证”时：
- 如果有已连接的 macOS 节点（例如 `Reed-Mac`）且该节点能访问该文章，可用 `nodes.run` 在节点上执行抓取（requests+bs4），然后写入 KB。
- 注意：这条路径依赖节点在线与网络环境；无法承诺 100%。

### 2) 截图/图片入库（含 OCR 文本）
脚本：

```bash
python3 /home/ubuntu/.openclaw/skills/knowledge-base-collector/scripts/ingest_image.py /path/to/image.jpg \
  --text-file /path/to/ocr.txt \
  --title "..." --tags "#ai #product" --note "..."
```

说明：
- `ingest_image.py` 负责“落盘+索引”。OCR 可用：
  - 本机 tesseract（若安装了 `tesseract-ocr` + `chi_sim`）
  - 或用多模态 LLM 抽取文字后写入 `--text-file`

## Telegram 里直接问（检索）
推荐先用脚本（本机/服务器）：

```bash
python3 /home/ubuntu/.openclaw/skills/knowledge-base-collector/scripts/search_kb.py --q "claude code" --limit 10
python3 /home/ubuntu/.openclaw/skills/knowledge-base-collector/scripts/search_kb.py --tags "#claude-code #coding-agent" --limit 20
python3 /home/ubuntu/.openclaw/skills/knowledge-base-collector/scripts/search_kb.py --source wechat --since 7d --q "Elys"
```

## 公众号待补抓队列（占位条目）

```bash
python3 /home/ubuntu/.openclaw/skills/knowledge-base-collector/scripts/wechat_backlog.py --limit 30
```

## 周报/主题报告候选清单（给 LLM 写总结用）

```bash
python3 /home/ubuntu/.openclaw/skills/knowledge-base-collector/scripts/weekly_digest.py --days 7 --limit 30
```

## 重要注意事项（安全/隐私）
- 截图/网页可能包含 token/验证码/密钥：入库前应做脱敏（替换为 `REDACTED`）。
- 公众号抓取受风控影响：建议允许“占位入库”，后续再补全。
