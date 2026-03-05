---
name: daily-paper-digest
description: 每日 AI 论文速递，自动聚合 arXiv 和 HuggingFace 的最新论文并推送到聊天应用。
version: 1.0.0
metadata:
  openclaw:
    emoji: "📚"
    homepage: https://github.com/your-username/daily-paper-digest
    requires:
      bins:
        - python3
        - pip3
    install:
      - kind: uv
        package: arxiv
      - kind: uv
        package: requests
      - kind: uv
        package: beautifulsoup4
      - kind: uv
        package: feedparser
---

# 📚 每日 AI 论文速递

每天自动从 arXiv 和 HuggingFace 抓取最新 AI 论文，格式化后推送到你的聊天应用（飞书、Slack、Discord 等）。

## 工具（Tools）

### `fetch_daily_papers`

获取今日最新论文速递。

**用法：**
```bash
python3 main.py
```

**参数：**
- 无（自动读取 `config/sources.json` 中的配置）

**返回：**
- 格式化的论文列表，包含标题、作者、摘要、链接

---

### `search_arxiv_papers`

搜索特定主题的 arXiv 论文。

**用法：**
```bash
python3 arxiv_fetcher.py
```

**参数（在代码中修改）：**
- `query`：搜索关键词，如 "large language model"
- `max_results`：最大返回数量（默认 5）

**返回：**
- 匹配的论文列表

---

### `fetch_huggingface_papers`

获取 HuggingFace 每日热门论文。

**用法：**
```bash
python3 huggingface_fetcher.py
```

**参数：**
- 无（直接爬取 `https://huggingface.co/papers`）

**返回：**
- 热门论文列表，含点赞数

---

## 配置

编辑 `config/sources.json` 来自定义信息源和过滤规则：

```json
{
  "sources": [
    {
      "name": "arxiv",
      "enabled": true,
      "categories": ["cs.AI", "cs.CL", "cs.CV", "cs.LG"],
      "max_results": 10
    },
    {
      "name": "huggingface",
      "enabled": true,
      "max_results": 10
    }
  ],
  "filter": {
    "keywords": ["LLM", "transformer"],
    "exclude_keywords": []
  }
}
```

### arXiv 常用分类

| 代码 | 含义 |
|------|------|
| `cs.AI` | 人工智能 |
| `cs.CL` | 计算语言学/NLP |
| `cs.CV` | 计算机视觉 |
| `cs.LG` | 机器学习 |
| `cs.NE` | 神经网络 |
| `cs.RO` | 机器人 |
| `stat.ML` | 统计机器学习 |

---

## 安装与使用

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 2. 运行测试

```bash
python3 test.py
```

### 3. 获取今日论文

```bash
python3 main.py
```

### 4. 定时自动运行（配合 OpenClaw 调度器）

在 OpenClaw 中配置 Cron 表达式（例如每天 9:00）：
```
0 9 * * *
```

---

## 在 OpenClaw 中触发

在聊天应用中发送以下任意内容即可触发：

- `论文速递`
- `今日论文`
- `最新论文`
- `/papers`
- `/digest`

---

## 依赖

- `arxiv` — arXiv 官方 Python 客户端
- `requests` — HTTP 请求
- `beautifulsoup4` — HTML 解析
- `feedparser` — RSS/Atom 解析

---

## 示例输出

```
╔══════════════════════════════════════════════════════════╗
║           🎓 AI 论文每日速递 - 2026年02月20日           ║
╚══════════════════════════════════════════════════════════╝

📊 今日共收录 15 篇论文

============================================================
📄 论文 1
============================================================

📌 标题: Attention Is All You Need
👥 作者: Ashish Vaswani, Noam Shazeer 等 8 人
🏷️  来源: ARXIV | 日期: 2026-02-20

📝 摘要:
The dominant sequence transduction models are based on...

🔗 arXiv: http://arxiv.org/abs/1706.03762
📥 PDF: http://arxiv.org/pdf/1706.03762
```

---

## 文件结构

```
daily-paper-digest/
├── SKILL.md                 ← 本文件（ClawHub 规范）
├── main.py                  ← 主程序
├── arxiv_fetcher.py        ← arXiv 模块
├── huggingface_fetcher.py  ← HuggingFace 模块
├── requirements.txt        ← Python 依赖
└── config/
    ├── sources.json        ← 默认配置
    └── sources_llm.json    ← LLM 专用配置
```
