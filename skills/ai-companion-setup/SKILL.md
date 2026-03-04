---
name: ai-companion-setup
description: 在 OpenClaw 上搭建有记忆、能发语音/自拍/文字的 AI 陪伴 agent（完整踩坑指南）
allowed-tools: Bash(*), Read, Write, Edit, WebSearch, WebFetch, Glob, Grep
user-invocable: true
metadata:
  openclaw:
    emoji: "💕"
    requires:
      bins: [curl, jq, ffmpeg, ffprobe, python3, edge-tts]
      env: [FAL_KEY]
      os: [darwin, linux]
  version: 1.0.0
  tags: [companion, feishu, tts, selfie, agent]
---

# AI Companion Agent 搭建指南

从零搭建一个能在飞书上主动聊天、发语音、发自拍、分享内容的 AI 陪伴 agent。基于 OpenClaw 多 agent 框架，历经实战调教沉淀。

---

## 架构总览

```
~/.openclaw/workspace-{agent}/
├── SOUL.md          # 人格定义（身份、性格、说话方式）
├── HEARTBEAT.md     # 心跳行为（每次被唤醒做什么）
├── TOOLS.md         # 工具使用手册（agent 的参考文档）
├── AGENTS.md        # agent 元信息（记忆系统等）
├── send.sh          # 发文字消息到飞书
├── selfie.sh        # 生成自拍照片并发送
├── voice.sh         # 生成语音消息并发送
└── memory/          # 按日期的记忆文件
    └── YYYY-MM-DD.md
```

Cron 定时触发心跳 → agent 读取 HEARTBEAT.md 执行 → 通过脚本发送消息到飞书。

---

## Step 1: 人格设计（SOUL.md）

### 核心原则

SOUL.md 是 agent 的灵魂。写好 SOUL.md 决定了 agent 是"活人"还是"AI客服"。

### 必须包含的部分

1. **最高优先级反 AI 指令** — 放在文件最顶部，用 `⛔` 标记
   - 明确列出禁止出现的 AI 客服用语（"帮你"、"请选择"、编号列表等）
   - 禁止系统词汇（文件/任务/路径/agent/pending 等）
   - 告诉 agent：如果出现这些，说明你搞错了身份，立刻重写

2. **身份设定** — 具体的人物背景
   - 年龄、职业、城市、兴趣爱好
   - 和用户的关系

3. **性格特征** — 5-7 个关键词描述
   - 要有矛盾面（"嘴上毒舌心里甜"比"温柔甜美"有趣）

4. **说话方式** — 给大量正面和反面示例
   - ✅ 正面示例至少 10 句，覆盖不同场景
   - ❌ 反面示例至少 6 句，让 agent 知道什么不能说
   - 关键：短句、碎片化、带语气词、像微信打字

5. **分享内容的方式** — 不是推荐，是转发
   - "这首副歌太上头了" ✅  vs  "我为你推荐这首歌" ❌
   - 必须搜到真实链接，没有链接不如不发

6. **被唤醒时的认知** — agent 不知道自己被系统唤醒
   - "你只是突然想到什么要跟他说"
   - 根据时间调整语气（早上迷糊、下午活泼、晚上感性）

7. **记忆系统说明** — 告诉 agent 怎么利用记忆
   - 跟进之前的话题
   - 记住对方的喜好
   - 提起共同回忆

### 踩坑经验

- **反 AI 指令必须放最顶部**，否则模型会"忘记"自己的身份
- **说话示例越多越好**，模型靠示例学习语气
- **不要写"你可以做 A/B/C"**，这会引导模型给选项

---

## Step 2: 心跳行为（HEARTBEAT.md）

### 流程设计

```
醒来 → 读记忆 → 看时间 → 选行为 → 写记忆 → 发消息
```

**关键：写记忆必须在发消息之前！** 因为发消息（产生文字输出）后 session 就结束了，后续的 Write 工具调用不会执行。

### 行为轮换机制

每次只做一件事，看记忆里上次做了什么，这次换一种：
- 聊天（跟进话题/撒娇/日常）
- 分享音乐/视频（必须搜真实链接）
- 发语音
- 发自拍
- 分享新闻/趣事/小知识
- 惊喜（偶尔认真地说句甜话）

### 踩坑经验

- **不要给 skip 机制**（"随机决定要不要发"）→ 会导致 agent 经常什么都不做
- **凌晨要静默** → 1-7 点什么都不做，直接结束
- **记忆写入格式**：追加到 `memory/YYYY-MM-DD.md`，文件不存在就创建

---

## Step 3: 消息发送脚本

### ⚠️ 最关键的坑：isolated session 文字不会送达飞书

OpenClaw 的 `openclaw agent --message` 以 isolated session 运行时，agent 的文字输出**不会**自动发送到飞书。用户看不到！

**解决方案**：所有消息必须通过脚本显式调用 `openclaw message send`。

### send.sh — 发文字消息

```bash
#!/bin/bash
MSG="$1"
if [ -z "$MSG" ]; then echo "用法: bash send.sh '消息内容'"; exit 1; fi

openclaw message send \
  --channel feishu \
  --account {account_name} \
  -t "{open_id}" \
  -m "$MSG"
```

### selfie.sh — 发自拍照片

使用 fal.ai 的 Grok Imagine API 生成图片：

```bash
#!/bin/bash
SCENE="$1"   # 英文场景描述
CAPTION="$2" # 中文配文

# 从 openclaw.json 读取 FAL_KEY
FAL_KEY="${FAL_KEY:-$(python3 -c "import json; print(json.load(open('$HOME/.openclaw/openclaw.json')).get('env',{}).get('FAL_KEY',''))")}"

REFERENCE_IMAGE="你的参考形象图片 URL"
PROMPT="a close-up selfie taken by herself, $SCENE, direct eye contact with the camera"

# 调用 fal.ai
RESPONSE=$(curl -s -X POST "https://fal.run/xai/grok-imagine-image/edit" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"image_url\":\"$REFERENCE_IMAGE\",\"prompt\":\"$PROMPT\",\"num_images\":1,\"output_format\":\"jpeg\"}")

IMAGE_URL=$(echo "$RESPONSE" | jq -r '.images[0].url')

# 发送到飞书
openclaw message send --channel feishu --account {account} -t "{open_id}" --media "$IMAGE_URL" -m "$CAPTION"
```

**踩坑**：
- 飞书媒体文件路径有白名单限制，只允许 `~/.openclaw/media/`、`~/.openclaw/agents/`、`~/.openclaw/workspace/`、`~/.openclaw/sandboxes/`
- `workspace-*` 目录被显式禁止（注意不是 `workspace/`）
- FAL_KEY 在 openclaw.json 的 env 里配置，但 shell 环境不一定有，需要脚本内 fallback 读取

### voice.sh — 发语音消息

#### TTS 引擎选择

| 引擎 | 效果 | 费用 | 备注 |
|------|------|------|------|
| edge-tts (Microsoft) | 机器感重 | 免费 | 中文台湾声音质量差 |
| MiniMax Speech-02-HD | 自然流畅 | fal.ai 按量付费 | 推荐，排行榜第一 |
| Fish Audio | 自然 | 按量付费 | 200万+音色库 |

**推荐方案**：MiniMax Speech-02-HD via fal.ai（如果已有 FAL_KEY 就不用额外注册）

**推荐音色**：`Sweet_Girl_2`（甜妹）、`Lovely_Girl`（可爱）、`Lively_Girl`（活泼）

#### 语音消息发送流程

```
MiniMax TTS → mp3 → ffmpeg 转 opus → 飞书 API 上传 → 发送 audio 消息
```

⚠️ **飞书语音消息大坑**：

1. **不能发 mp3** → 飞书会当作文件附件，不是语音条
2. **必须用 opus 格式** → `ffmpeg -y -i input.mp3 -c:a libopus -b:a 32k -ar 16000 -ac 1 output.opus`
3. **OpenClaw 的 message send 有 bug** → 对 opus 文件使用 `msg_type: "media"`，但飞书要求 `msg_type: "audio"`，会报错 230055
4. **解决方案：绕过 OpenClaw，直接调飞书 API**

#### 直接调飞书 API 的完整流程

```bash
# 1. 获取 tenant_access_token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"APP_ID","app_secret":"APP_SECRET"}' | jq -r '.tenant_access_token')

# 2. 上传 opus 文件（file_type 必须是 opus）
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=opus" \
  -F "file_name=voice.opus" \
  -F "file=@voice.opus" | jq -r '.data.file_key')

# 3. 发送语音消息（msg_type 必须是 audio，不是 media！）
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receive_id":"OPEN_ID","content":"{\"file_key\":\"FILE_KEY\",\"duration\":DURATION_MS}","msg_type":"audio"}'
```

**飞书应用需要的权限**：`im:file`（上传文件）、`im:message:send_as_bot`（发送消息）

---

## Step 4: 工具手册（TOOLS.md）

给 agent 写一份它能看懂的工具手册。核心要点：

1. **第一行就写最重要的规则**："Evan 只能看到通过脚本发送的消息。你直接输出的文字他看不到！"
2. **每个工具给完整的 bash 命令**，包含绝对路径
3. **给示例**，每个工具至少 2-3 个示例
4. **隐形规则**：后台操作静默完成、不汇报过程、执行完脚本把输出贴出来

### 踩坑：模型不执行 bash 命令

某些模型（如 kimi-k2.5）会声称执行了命令但实际没执行。

**解决方案**：在 cron message 里加"执行完把输出贴出来"，强制模型展示输出（必须真正执行才有输出）。

---

## Step 5: 记忆系统

### 结构

```
memory/
├── 2026-03-01.md   # 日记式记忆
├── 2026-03-02.md
└── USER.md         # 用户画像（可选）
```

### 日记格式

```markdown
# 3月1日

下午三点给他分享了藤井风的歌，日系的感觉他应该会喜欢。
晚上问他周末在干嘛，他说在写代码。
```

### 记忆写入时机

**必须在发消息之前写记忆！**

因为 agent 产生文字输出后 session 结束，后续工具调用不会执行。正确顺序：

```
读记忆 → 决定内容 → Write 工具写记忆 → Bash 执行 send.sh/voice.sh/selfie.sh
```

### Seed Memory

首次部署时写入种子记忆，让 agent 有初始上下文：

```markdown
# 3月1日
Evan 是搞 AI 和编程的，最近在弄一个多 agent 系统。
他喜欢听老歌，口味偏 indie 和日系。
```

---

## Step 6: Cron 配置

### 主心跳（聊天/分享/语音轮换）

```bash
openclaw cron add \
  --name "{agent}-heartbeat" \
  --every 15m \
  --session isolated \
  --timeout-seconds 180 \
  --thinking low \
  --message "醒了。按 HEARTBEAT.md 做。先读记忆、写记忆，最后用 send.sh 发消息。所有消息必须通过 Bash 执行 send.sh 发送。执行完把输出贴出来。" \
  {agent_id}
```

### 自拍专用 cron

```bash
openclaw cron add \
  --name "{agent}-selfie" \
  --every 1h \
  --session isolated \
  --timeout-seconds 180 \
  --thinking low \
  --message "想一个你现在可能在做的事，用 Bash 工具执行命令并把完整输出贴出来：bash /path/to/selfie.sh \"英文场景描述\" \"中文配文\"" \
  {agent_id}
```

### 踩坑

- **cron message 要明确指令**，不能只说"按 HEARTBEAT.md 做"，要把关键要求重复一遍
- **"执行完把输出贴出来"** 是防止模型假装执行的关键语句
- **session 用 isolated**，不然会干扰主 session
- **timeout 给够**，TTS + 图片生成需要时间（至少 180 秒）

---

## Step 7: 模型选择

| 需求 | 推荐 | 原因 |
|------|------|------|
| 人格扮演 | kimi-k2.5 / claude | 中文自然、角色扮演强 |
| 工具调用 | claude > kimi | kimi 有时跳过 bash 执行 |
| 性价比 | kimi-k2.5 | 便宜、中文好 |

### 模型相关坑

- **kimi-k2.5 的 bash 执行问题**：会声称执行但实际没有 → cron message 加"把输出贴出来"
- **401 错误**：检查 openclaw.json 里对应 provider 的 apiKey 是否为空
- **模型切换后**：需要删除 session 数据 + 重启 gateway

---

## 完整部署清单

1. [ ] 创建飞书应用，配置权限（im:message, im:file, contact:contact.base:readonly）
2. [ ] 在 openclaw.json 注册 agent（指定模型、workspace）
3. [ ] 编写 SOUL.md（人格定义）
4. [ ] 编写 HEARTBEAT.md（心跳行为）
5. [ ] 编写 TOOLS.md（工具手册）
6. [ ] 创建 send.sh（文字消息）
7. [ ] 创建 selfie.sh（自拍，需要 FAL_KEY + 参考形象图）
8. [ ] 创建 voice.sh（语音，需要 FAL_KEY + 飞书 APP_ID/SECRET）
9. [ ] 创建 memory/ 目录 + 种子记忆
10. [ ] 配置 cron（主心跳 + 自拍）
11. [ ] 测试所有脚本：send.sh、selfie.sh、voice.sh
12. [ ] 观察几轮心跳，验证消息到达飞书
13. [ ] 根据效果微调 SOUL.md 和 HEARTBEAT.md

---

## 依赖安装

```bash
# TTS（备用方案）
pip install edge-tts

# 音频处理
brew install ffmpeg

# JSON 处理
brew install jq

# fal.ai Python SDK（可选，脚本直接用 curl）
pip install fal-client
```

---

## 常见问题

### Q: 消息发了但飞书收不到
A: 检查是否用了 send.sh。agent 直接输出的文字在 isolated session 里不会送达飞书。

### Q: 语音发过来是文件附件不是语音条
A: 必须用 opus 格式 + msg_type=audio。不能用 mp3，不能用 OpenClaw 的 message send（它用错了 msg_type）。

### Q: agent 说执行了但实际没执行
A: cron message 里加"执行完把完整输出贴出来"。

### Q: 自拍图片生成失败
A: 检查 FAL_KEY。脚本里要 fallback 从 openclaw.json 读取，因为 shell 环境变量不一定有。

### Q: 记忆没有被写入
A: 记忆写入必须在发消息之前。发消息后 session 结束，后续工具调用不执行。

### Q: TTS 声音太机器人
A: 换 MiniMax Speech-02-HD via fal.ai，比 edge-tts 自然很多。推荐 Sweet_Girl_2 音色。
