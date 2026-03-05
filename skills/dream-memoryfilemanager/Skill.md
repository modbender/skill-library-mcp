---
name: dream
description: >-
  主动维护 MEMORY.md 的记忆蒸馏技能。触发场景：
  (1) 每日 03:30 定时蒸馏（空闲时执行，忙则顺延至 06:00）；
  (2) 用户说 "dream" / "复盘" / "整理记忆" / "你记得我什么"；
  (3) 用户要求收录内容到 Obsidian 索引。
version: 0.2.1
metadata:
  openclaw:
    emoji: "🌙"
    homepage: https://github.com/teman2050/dream-skill
requires:
  bins:
    - jq
    - wc
config:
  - DREAM_VAULT_PATH
install:
  - kind: brew
    formula: jq
    bins: [jq]
---

# Dream — 主动记忆蒸馏 v5

## 核心定位

**OpenClaw 原生已经解决了捕获和搜索问题：**
- 捕获：compaction flush 自动把重要内容写入 `memory/YYYY-MM-DD.md`
- 搜索：`openclaw memory search` 提供向量 + BM25 混合搜索

**Dream 填补的空白：**
- 原生不会主动维护 MEMORY.md（只靠 AI 偶尔手动写，内容只增不减）
- 原生对 MEMORY.md 的 20,000 字符上限没有任何主动处理：超限后直接静默截断，
  AI 不会收到警告，只是安静地丢失后半段上下文，用户很难察觉
  Dream 在 18,000 字符时主动触发压缩，将过期内容移入 ledger，
  确保 MEMORY.md 始终在有效范围内、内容始终是最新最相关的
- 原生没有永久档案（ledger）
- 原生没有 Re-emergence 检测机制

Dream 的职责是**蒸馏者**，不是捕获者，也不造重复的搜索轮子。

---

## 文件分工

```
OpenClaw 原生（Dream 只读）
└── memory/YYYY-MM-DD.md     ← compaction flush 自动写入，Dream 读取作为原材料

Dream 主动维护
├── MEMORY.md                ← 每日蒸馏更新，每次对话全量注入 context，精简为王
│                               硬上限 18,000 字符（原生截断线 20,000，留 2,000 余量）
│
{DREAM_VAULT_PATH}/
├── ledger.md                ← 永久档案，只追加，永不删除
├── ledger-index.json        ← 结构化索引，供 ledger 检索用
├── meta/
│   ├── removed-entries.json ← 曾从 MEMORY.md 移除的条目摘要（Re-emergence 用）
│   ├── last-review.txt      ← 上次蒸馏完成时间
│   └── dream-state.txt      ← active | hibernating | pending
└── obsidian-index/
    ├── _index.md            ← 内容主索引（按日期倒序）
    └── topics/<topic>.md    ← 按主题分类
```

**不存在的文件（刻意省略）：**
- ~~cache.md~~ → 由 `memory/YYYY-MM-DD.md` 原生承担
- ~~自建搜索索引~~ → 由 `openclaw memory search` 原生承担

---

## MEMORY.md 结构规范

Dream 维护的 MEMORY.md 分三个区块，总字符数强制控制在 15,000 以内：

```markdown
## 当前状态
<!-- 正在进行的项目、未完成的决策、近期重要变化 -->
<!-- 变化最快，每次蒸馏都检查是否需要更新 -->

## 稳定认知
<!-- 技术栈、工作环境、决策风格、核心偏好、反复验证的价值判断 -->
<!-- 变化慢，只在有新证据时更新 -->

## 关系与背景
<!-- 重要的人、正在进行的合作、关键外部上下文 -->
<!-- 按需更新 -->

## Dream
<!-- Dream 技能自动维护，勿手动编辑 -->
<!-- ledger 最近 5 条入档摘要，让 AI 知道最近什么内容被永久保存了 -->
```

**不写入 MEMORY.md 的内容：**
- 可以实时观察到的信息（用 Mac、喜欢深色主题）
- 流水账细节（这些在 memory/YYYY-MM-DD.md 里，可随时 search）
- 已完成/已过期的状态（移入 ledger 后从 MEMORY.md 删除）

---

## 实时捕获（对话中，不等复盘）

对话过程中发现以下内容时，**直接写入 MEMORY.md 对应区块**（不等 03:30），
同时记录到当日 `memory/YYYY-MM-DD.md`：

**立即写入 MEMORY.md 的情况：**
- 用户明确纠正了 AI 的判断（"不对，我其实..."）→ 更新【稳定认知】
- 用户宣布重要决策结果（"我决定了..."）→ 更新【当前状态】
- 用户描述正在进行的新项目 → 更新【当前状态】

**只写 memory/YYYY-MM-DD.md，等待 03:30 蒸馏：**
- 情绪事件、偏好讨论、观点表达
- 单次出现、重要性尚不确定的信息

写入前检查 MEMORY.md 字符数（`dream-tools.sh --check-size`），
超过 16,000 字符时先压缩最旧的【当前状态】条目，再写入。

---

## 操作指令

### `dream review` — 每日蒸馏（核心）

**全程自动，静默执行（03:30 触发时不推送任何消息）。**

执行步骤：

**Step 1 — 前置检查**
```
dream-tools.sh --check-idle   → busy? 写 pending，15分钟后重试，上限 06:00
dream-tools.sh --check-size   → 读取 MEMORY.md 当前字符数
```

**Step 2 — 读取原材料**

读取自上次蒸馏以来新增的 `memory/YYYY-MM-DD.md` 文件（增量，不重复处理）。
若无新文件，跳过蒸馏，只更新 `last-review.txt`。

**Step 3 — AI 蒸馏判断**

对每条日记内容，按以下规则判断操作：

| 判断 | 条件 | 操作 |
|------|------|------|
| 更新 MEMORY.md | 比现有条目有新进展或修正 | 替换对应行 |
| 新增到 MEMORY.md | 跨 2 个以上日期出现，或单次但明显重要 | 追加到对应区块 |
| 仅入 ledger | 重要但已完成/过期，不需要常驻上下文 | 从 MEMORY.md 删除并入档 |
| 忽略 | 口水话、单次低价值、已有高度相似条目 | 丢弃 |

**Re-emergence 检查**（每次蒸馏必做）：
对照 `meta/removed-entries.json`，若日记中出现与曾被移除条目语义相似（>70%）的内容，
该条目重新写入 MEMORY.md 并标注 `[re-emerged]`，优先级提升，下次蒸馏不轻易移除。
同时在 ledger 追加一条 re-emergence 事件记录。

**Step 4 — 字符上限保护（写入前执行）**

```
目标写入后大小 > 15,000 字符？
  → 压缩【当前状态】中最旧的已完成条目：移入 ledger，从 MEMORY.md 删除
  → 压缩【稳定认知】中重复度最高的条目：合并相似条目
  → 直到预估写入后 ≤ 18,000 字符
```

**Step 5 — 原子写入 MEMORY.md**
```
dream-tools.sh --atomic-write MEMORY.md <tmpfile>
# 先写 .tmp，验证格式和字符数（≤ 18,000）后 mv 替换
```

**Step 6 — 入档操作**

对本次蒸馏中判断"仅入 ledger"的条目：
```
dream-tools.sh --ledger-append <id> <category> <content>
# 追加区块到 ledger.md，更新 ledger-index.json
```

ledger 条目格式：
```markdown
---
ID: a3f8c201
入档时间: 2026-02-27 03:31
类别: [决策]
内容: 决定用 Obsidian 替代 Notion，原因是数据本地化和 Git 同步
来源: memory/2026-02-27.md，首次出现
---
```

**Step 7 — 更新 meta**
- 追加今日到 `active-days.json`（去重）
- 更新 `last-review.txt`
- 更新 `## Dream` 区块：ledger 最近 5 条一句话摘要（覆盖）

**Step 8 — 复盘日志（按月归档）**
```
# 追加到 meta/review-YYYY-MM.md
### YYYY-MM-DD 03:30
更新: N条 | 新增: N条 | 入档: N条 | Re-emergence: N条 | 忽略: N条
MEMORY.md 字符数: N → N
```

手动触发时额外输出简报：
```
🌙 蒸馏完成
MEMORY.md: N 字符（上限 15,000）
本次：更新 N 条 | 新增 N 条 | 入档 N 条
永久档案共 N 条记录
```

---

### 搜索：全部委托原生，不自建

```bash
# 日常搜索（memory/ 目录 + MEMORY.md，向量+BM25混合）
openclaw memory search "<关键词>"

# 深度检索（含永久档案）
# Step 1: 先用原生搜索 memory 部分
openclaw memory search "<关键词>"
# Step 2: 再检索 ledger
dream-tools.sh --ledger-search "<关键词>"
# Step 3: 合并输出，标注来源
```

`dream search <关键词>` 命令封装以上两步，输出时明确区分来源：
```
🔍 "Obsidian" 检索结果：

── OpenClaw Memory ──
· memory/2026-02-27.md: 决定用 Obsidian 替代 Notion...
· MEMORY.md [稳定认知]: 主力笔记工具 Obsidian...

── 永久档案 ──
· [a3f8c201] 2026-02-27 [决策] 决定用 Obsidian 替代 Notion（入档得分 22）

── Obsidian 内容索引 ──
· OpenClaw + Obsidian 集成笔记 (2026-02-15)
```

---

### `dream index <内容>` — 收录到 Obsidian 索引

1. URL/标题哈希去重，已存在跳过
2. 提取元数据：标题、来源、日期、主题标签（≤5个）、一句话摘要
3. Append 到 `obsidian-index/_index.md` 和对应 `topics/<topic>.md`
4. 若内容明显反映用户偏好，同时写入当日 `memory/YYYY-MM-DD.md` 一条记录，等待下次蒸馏

---

### `dream status` — 状态总览（只读 meta，低 IO）

```
🌙 Dream 状态 — YYYY-MM-DD HH:MM
MEMORY.md: N 字符 / 18,000 上限（N%）
永久档案: N 条记录
上次蒸馏: YYYY-MM-DD HH:MM（N 小时前）
系统状态: active / hibernating（沉睡 N 天）/ pending（顺延中，已等 N 分钟）
Obsidian 索引: N 条
待蒸馏日记: N 个文件（自上次蒸馏后新增）
```

---

### `dream forget <描述>` — 从 memory 中清除

在 `memory/YYYY-MM-DD.md` 和 MEMORY.md 中语义搜索匹配条目并清除。
无需确认，直接执行。

**Re-emergence 机制：**
清除时将条目摘要写入 `meta/removed-entries.json`，记录清除时间和内容哈希。
后续对话中若该内容再次出现，自动触发 re-emergence，重新写入 MEMORY.md 并提升优先级。
被遗忘后又出现的内容，比从未被遗忘的内容更值得保留。

ledger 中的记录不受 `dream forget` 影响，永久保留。
执行时告知：「已从记忆中清除，永久档案不受影响。」

---

### `dream init` — 冷启动引导

1. 创建 `{DREAM_VAULT_PATH}` 目录结构
2. 若 MEMORY.md 为空或不存在，询问 5 个种子问题：
   工具偏好、工作环境、近期最重要的项目、核心价值判断、最重要的人际关系
3. 将回答直接写入 MEMORY.md 对应区块（不等蒸馏）
4. 写入 `dream-state.txt` = `active`

---

### `dream wakeup` — 休眠唤醒

连续 7 个日历天无活跃后首次对话自动触发：
1. 输出 ledger 最近 3 条 + MEMORY.md 当前快照摘要
2. 恢复 active 状态，不删除任何内容

---

## 辅助脚本 `dream-tools.sh`

```bash
dream-tools.sh --check-idle
# 查询 openclaw agent status，返回 idle / busy

dream-tools.sh --check-size
# 返回 MEMORY.md 当前字符数（用 wc -c）

dream-tools.sh --hash "<内容>"
# 返回 8 位 MD5 短哈希，用于 ID 生成和去重

dream-tools.sh --atomic-write <target-file> <tmp-file>
# 验证 tmp-file 格式和字符数后 mv 替换 target-file

dream-tools.sh --ledger-append <id> <category> <content> [<note>]
# 向 ledger.md 追加区块，同时更新 ledger-index.json

dream-tools.sh --ledger-search "<keyword>"
# 在 ledger-index.json 中检索，返回匹配条目

dream-tools.sh --dedup-index "<url-or-hash>"
# 检查 obsidian-index 是否已有该条目，返回 exists / new
```

依赖：`jq`（JSON）、`wc`（字符计数）、`md5sum`（哈希）。
不依赖 Python / Node。

---

## 定时触发（SOUL.md 中加入）

```
每天 03:30 执行 dream review --scheduled
```

顺延逻辑：
- 03:30 检测 idle → busy → 写 pending → 15 分钟后重试
- 重试窗口：03:45 / 04:00 / ... / 06:00
- 06:00 强制执行，不再顺延
- 全程静默，不推送消息，结果写入 meta/review-YYYY-MM.md

---

## 休眠保护

| 条件 | 行为 |
|------|------|
| 连续 7 日历天无活跃 | 写入 hibernating，03:30 心跳直接跳过，零 IO |
| 首次新对话 | 触发 `dream wakeup`，不删除任何内容 |

---

## IO 原则

- 所有写入先写 `.tmp`，原子替换，防崩溃
- ledger / obsidian-index 只追加，不重写
- status 只读 meta 目录小文件，不触碰 ledger / MEMORY.md 正文
- 休眠状态 03:30 心跳直接跳过，零文件操作
- 写入 MEMORY.md 前强制检查字符数，不允许超过 18,000
