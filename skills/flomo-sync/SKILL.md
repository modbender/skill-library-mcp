---
name: flomo-sync
description: 将 flomo 所有记录 memo 同步/备份到本地 Markdown 文件的工具。使用 scripts/flomo-sync.py 脚本通过 flomo API 拉取 memo，支持增量同步、附件下载、多文件输出。当用户需要备份 flomo、同步 flomo memo 到本地、导出 flomo 笔记为 Markdown 时使用。
---

# flomo-sync

将 flomo 所有 memo 增量同步为本地 Markdown 文件。

## 前置入参要求（必须）

执行本技能前，必须先明确并拿到以下入参：

- 当前项目主路径（绝对路径），例如 `/Users/xxx/project-name`
- flomo token（来自项目主路径下 `.flomo.config`，避免在对话中明文暴露）

`--dir` 必须基于“当前项目主路径”传入绝对路径，禁止使用相对路径（如 `./output`、`../backup`）。

## 快速开始

### 1. 安装依赖（Python 3.10+）

```bash
pip install requests markdownify
```

### 2. 配置 token

在项目主路径下创建 `.flomo.config`，并包含 `token=<access_token>`。

**安全建议（强烈推荐）**：
- 优先使用 `.flomo.config` 保存 token，不要在对话中直接粘贴 token，避免泄露给 LLM。
- 执行同步时优先使用 `python scripts/flomo-sync.py`（自动从 `.flomo.config` 读取）。

#### `.flomo.config` 格式说明

- **通用规则**：一行一个 `key=value`；以 `#` 开头的行为注释；空行忽略。
- **flomo-sync 所需**：`token=<access_token>`；支持带或不带 `Bearer ` 前缀，例如：
  - `token=1023456|AA000000ABCDEFGHIJKHLMNOP000000000000000`
  - `token=Bearer 1023456|AA000000ABCDEFGHIJKHLMNOP000000000000000`
- **获取 token**：在浏览器打开 [https://v.flomoapp.com](https://v.flomoapp.com) 登录后，按 `F12` → Network → 点击任意请求 → Headers → 复制 `Authorization` 的值（形如 `Bearer 1023456|...`）。备用：Application → Local Storage → `me` → 复制 `access_token`。
- 同一文件可同时包含 `url=` 供 flomo-add 使用（与 flomo-add 共用一配置文件）。

### 3. 运行同步

```bash
# 基本用法（文档规范：必须传 --dir 且为绝对路径）
python scripts/flomo-sync.py --dir /abs/path/to/output

# 推荐：以当前项目主路径作为基准拼接输出目录
# 例：当前项目主路径=/Users/yourname/my-project
python scripts/flomo-sync.py --dir /Users/yourname/my-project/output/flomo-sync

# 临时排障：仅在本地终端通过命令行传入 token（不要在对话中提供 token）
# token 含 | 必须用单引号
python scripts/flomo-sync.py --token '1023456|AA000000...' --dir /abs/path/to/output

# 自定义输出目录
python scripts/flomo-sync.py --dir /Users/yourname/Desktop/flomo-sync

# 只拉取指定日期后更新的 memo
python scripts/flomo-sync.py --after 2024-01-01 --dir /abs/path/to/output

# 不下载附件到本地（保留远程 URL）
python scripts/flomo-sync.py --no-download --dir /abs/path/to/output
```

> 文档规范要求：执行同步时必须传 `--dir` 且使用绝对路径。实现层面为兼容保留兜底：未传 `--dir` 时，默认写入当前执行目录。

### 运行输出示例（含条目级进度）

```text
==================================================
flomo → Markdown 同步工具
==================================================

after=2024-01-01（来源: 命令行 --after）

  第 1 页（游标 updated_at=1704067200 slug=''）… 拉取 93 条
    页内处理 [########################] 93/93
    → 已处理，累计 93 条
  第 2 页（游标 updated_at=1709155652 slug='MTI3MTMwMzQ0'）… 拉取 27 条
    页内处理 [########################] 27/27
    → 已处理，累计 120 条

✅ 完成！新增 12 条，更新 3 条，跳过 105 条（耗时 2.1s）
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--token` | flomo access_token（可从 `.flomo.config` 读取）。支持 `Bearer <token>` 格式 | — |
| `--dir` | 输出目录绝对路径（文档规范：必传）。必须基于“当前项目主路径”确定 | —（未传时实现默认当前执行目录） |
| `--after YYYY-MM-DD` | 仅拉取该日期后更新的 memo | 自动读取 `.flomo.lock` |
| `--no-download` | 不下载附件，保留远程 URL | 否（默认下载） |

## 输出格式

每条 memo 生成独立 `.md` 文件，命名格式为 `{日期}_{标签}_{内容前6字}_{slug}.md`：

```markdown
---
slug: MTI3MTMwMzQ0
created_at: 2024-07-11 00:20:04
updated_at: 2024-07-11 00:20:04
tags: [英语/如何学习]
source: android
---

#英语/如何学习

你不是学不会，你只是不学

**附件:**
![photo.png](images/2024/07/11/MTI3MTMwMzQ0_photo.png)
```

## 增量同步机制

脚本自动维护 `.flomo.lock` 文件，记录上次同步的最大 `updated_at` 时间戳。下次运行时自动从该时间点（减 1 天容错）开始拉取，无需手动指定 `--after`。

## 常见问题

- **`sign 错误`**：token 无效或过期，重新从浏览器获取
- **`请先登录`**：未传入 token 或 token 不完整
- **附件处理**：图片（`.png/.jpg/.gif` 等）以 `![name](path)` 嵌入，音频（`.m4a/.mp3` 等）以 `[name](path)` 链接；加 `--no-download` 保留原始远程 URL

## 文件说明

```
skills/flomo-sync/
├── SKILL.md
├── scripts/
│   └── flomo-sync.py       # 主脚本
└── assets/                 # 预留
```

运行后会在输出目录产生：

```
output/
├── images/YYYY/MM/DD/      # 本地附件
├── {日期}_{标签}_{摘要}_{slug}.md  # 每条 memo（独立模式）
└── flomo_export.md          # 合并文件（--single 模式）
```
