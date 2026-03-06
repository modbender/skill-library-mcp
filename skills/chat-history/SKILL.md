---
name: Chat History Skill
description: 自动归档每天的对话记录，分类保存，支持快速搜索和历史回溯。
---

# Chat History Skill

> 📦 对话归档系统 - 自动归档、搜索和管理对话记录
> Skill名称: `chat_history`

---

## 🎯 功能概述

自动归档每天的对话记录，分类保存，支持快速搜索和历史回溯。

**核心功能**：
- ✅ 自动归档（每天23:59或用户手动触发）
- ✅ 分类保存（Channel端完整、WebUI端纯文字）
- ✅ 智能搜索（快速查找历史对话）
- ✅ 触发关键词（多种自然语言触发）
- ✅ 命令系统（结构化的命令操作）

---

## 📋 命令系统

### 基础命令

#### `/chat_history`
查看所有可用指令和功能

```
/chat_history
```

**输出示例**：
```
📚 Chat History 指令列表

基础命令：
• /chat_history - 查看本帮助
• /chat_history start - 启动自动归档
• /chat_history stop - 停止自动归档
• /chat_history status - 查看归档状态
• /chat_history keyword - 列出所有触发关键词

搜索命令：
• /chat_history search <关键词> - 搜索对话
• /chat_history list - 列出所有归档
• /chat_history list channel - 列出Channel端归档
• /chat_history list webui - 列出WebUI端归档
• /chat_history yyyymmdd - 列出指定日期的归档

评估命令：
• /chat_history list-evaluations - 列出评估过的skills
• /chat_history search-evaluations <关键词> - 搜索评估记录

提示：也可以通过自然语言触发，详见下方触发关键词列表
```

---

### 控制命令

#### `/chat_history start`
启动自动归档功能

- 第一次运行：询问是否归档过往所有聊天记录
- 设置每天03:55自动归档（早于04:00清空）
- 如果之前跳过，重新激活询问

```
/chat_history start
```

**交互流程**：
```
Chat History 首次启动

📦 是否立即归档过往所有聊天记录？

选项：
[1] 立即归档 - 归档所有历史对话
[2] 稍后归档 - 跳过，稍后执行
[3] 取消 - 不启动自动归档

请输入选项 (1/2/3): _
```

**为什么要3:55归档？**
- OpenClaw默认在04:00清空session窗口
- 在清空前5分钟归档，避免丢失0:00-4:00的聊天记录

---

#### `/chat_history stop`
停止自动归档功能

```
/chat_history stop
```

**输出示例**：
```
✅ 已停止自动归档功能

注意：之前归档的记录仍然保留，可以随时重新启动
提示：使用 /chat_history start 重新启动
```

---

#### `/chat_history status`
查看归档状态

```
/chat_history status
```

**输出示例**：
```
📊 归档状态

自动归档: ✅ 已启用
定时任务: 每天 03:55（早于04:00清空）
上次归档: 2026-02-23 03:55:05
归档总数: 125 个会话
归档文件夹: /Users/tanghao/.openclaw/workspace/conversation-archives/

Channel端归档: 125 个文件
WebUI端归档: 125 个文件
搜索索引: ✅ 已更新
```

---

#### `/chat_history keyword`
列出所有触发关键词

```
/chat_history keyword
```

**输出示例**：
```
🔑 触发关键词列表

通用触发：
• 我想不起来了 • 我记不清了 • 找不到之前的对话
• 找聊天 • 查记录 • 搜索聊天记录
• 聊天记录 • 对话记录 • 历史记录
• 以前的聊天 • 之前的对话 • 归档 • 备份

英文触发：
• chat history • conversation history • chat log
• conversation log • search history • find chat
• old chat • previous conversation • archive • backup

命令触发：
• 归档 • 搜索对话 • 列出对话 • 找记录 • 查历史

日期查询：
• 今天的对话 • 昨天的对话 • 2026年2月21日的对话
• yyyy-mm-dd 的对话

评估查询：
• 评估过的skills • 评估记录 • skill评估

提示：输入任意关键词即可自动触发搜索或归档功能
```

---

### 搜索命令

#### `/chat_history search <关键词>`
搜索历史对话

```
/chat_history search "视频"
```

**输出示例**：
```
✅ 找到 3 个会话包含"视频"（共5处匹配）

[1] 会话ID: session_xxxxxxxxxxxxxx
    日期: 2026-02-21 2305
    类型: channel
    消息数: 23
    匹配数: 2

    匹配1（第15行）:
    **[1] User** | 2026-02-21 15:30:15
    露娜，帮我做个**视频**。
```

---

#### `/chat_history list`
列出所有归档

```
/chat_history list
```

**选项**：
```
/chat_history list              - 列出所有
/chat_history list channel      - 只列Channel端
/chat_history list webui        - 只列WebUI端
/chat_history list 2026-02-21   - 列出指定日期
```

---

#### `/chat_history yyyymmdd`
列出指定日期的所有归档

```
/chat_history 20260222
/chat_history 2026-02-22
```

**输出示例**：
```
📅 2026-02-22 的归档

找到 5 个会话

会话ID: session_xxxxxxxxxxxxxx
  日期: 2026-02-22 0130
  摘要: 讨论对话归档系统设计

Channel端: [查看]
WebUI端: [查看]
---
```

---

### 评估命令

#### `/chat_history list-evaluations`
列出所有评估过的skills

```
/chat_history list-evaluations
```

**输出示例**：
```
✅ 找到 3 个评估过的 skills

[1] EvoMap
   评估日期: 2026-02-21
   风险等级: 🔴 极高风险
   结论: 恶意程序，禁止安装
   详情: SKILL-SECURITY-ALERTS.md
   触发词: evo map, evomap, 脑后接口

[2] skyvern
   评估日期: 2026-02-20
   风险等级: 🟡 中风险
   结论: 可作为备用浏览器自动化工具
   详情: skyvern-deep-research.md

[3] OpenAI-Whisper
   评估日期: 2026-02-19
   风险等级: 🟢 低风险
   结论: 安全可安装
   详情: 已记录到MEMORY.md
```

---

#### `/chat_history search-evaluations <关键词>`
搜索评估记录

```
/chat_history search-evaluations "恶意"
```

---

## 🤖 NLP自然语言触发

Chat History Skill 支持**自然语言触发**！用户可以用自然的中文/英文表达意图，系统会自动识别并执行对应操作。

### 如何工作？

```
用户输入自然语言
     ↓
分析用户意图（关键词检测）
     ↓
映射到对应命令
     ↓
执行命令并返回结果
```

---

### 控制类NLP触发

**启动归档**：
```
用户: 开启自动归档
用户: 启动自动备份
用户: 开始保存对话
用户: 归档服务开始
用户: 打开自动归档系统
→ /chat_history start
```

**停止归档**：
```
用户: 停止自动归档
用户: 关闭归档功能
用户: 停止保存对话
用户: 暂停归档
用户: 关闭自动备份
→ /chat_history stop
```

**查看状态**：
```
用户: 归档状态怎么样
用户: 自动归档是否开启
用户: 看看归档情况
用户: 归档系统状态
用户: 查看自动备份状态
→ /chat_history status
```

---

### 搜索类NLP触发

**关键词搜索**：
```
用户: 搜索"视频"的对话
用户: 找找关于视频的记录
用户: 搜索视频
用户: 查找视频相关的内容
用户: 说过什么关于视频的
→ /chat_history search "视频"
```

**列出归档**：
```
用户: 列出所有归档
用户: 看看所有对话记录
用户: 显示所有保存的对话
用户: 查看归档列表
用户: 列出对话
→ /chat_history list
```

**指定端点搜索**：
```
用户: 搜索webui端的内容
用户: 看看channel端的归档
用户: 列出webui归档
→ /chat_history list webui / channel
```

---

### 日期类NLP触发

**指定日期**：
```
用户: 今天的所有对话
用户: 昨天的记录
用户: 2026年2月23的对话
用户: 2月23日说了什么
用户: 今天的记录
→ /chat_history search --date <today>
→ /chat_history list <date>
```

---

### 评估类NLP触发

**列出评估**：
```
用户: 评估过哪些skills
用户: 我之前评估过什么
用户: 列出评估记录
用户: 我评估的skills列表
用户: 评估过的
→ /chat_history list-evaluations
```

**搜索评估**：
```
用户: 搜索恶意的skill
用户: 找找高风险的评估
用户: 评估过哪个视频相关
→ /chat_history search-evaluations "关键词"
```

---

## 🗣️ 触发关键词（精确匹配）

除了NLP自然语言触发，Chat History 也支持**精确关键词触发**，系统会检测以下关键词并自动执行对应操作。

### 通用触发（中文）

**遗忘类**：
```
我想不起来了
我记不清了
忘了
找不到了
记不得
想不起来
```

**搜索类**：
```
找聊天
查记录
搜索聊天记录
查历史
找历史
```

**记录类**：
```
聊天记录
对话记录
历史记录
以前的聊天
之前的对话
对话历史
聊天历史
```

**动作类**：
```
归档
备份
保存对话
保存聊天
```

---

### 通用触发（英文）

**遗忘类**：
```
I can't remember
I forgot
find chat
can't recall
don't remember
```

**搜索类**：
```
chat history
conversation history
chat log
conversation log
search history
find chat
old chat
previous conversation
```

**记录类**：
```
messages
history
logs
archive
backup
save conversation
```

---

### 命令触发

```
归档
搜索对话
列出对话
找记录
查历史
```

---

### 日期查询

```
今天的对话
昨天的对话
2026年2月21日的对话
yyyy-mm-dd 的对话
```

---

### 评估查询

```
评估过的skills
评估记录
skill评估
我评估过哪些skill
列出评估过的
```

---

### 特殊短语

```
帮我保存
帮我找
历史消息
之前说过什么
我们上次说什么
搜索之前的
查看历史
```

---

## 🔄 工作流程

### 首次安装

1. 用户安装 `chat_history` skill
2. 自动询问：
   ```
   🎉 Chat History 已安装

   📦 是否立即归档过往所有聊天记录？

   [Y] 立即归档   [N] 稍后   [S] 跳过
   ```

3. 如果选择 `Y`：
   - 归档所有历史对话
   - 设置每天03:55自动归档（早于04:00清空）

4. 如果选择 `N` 或 `S`：
   - 提示：可以使用 `/chat_history start` 重新启动

---

### 日常使用

**用户输入任意触发关键词**：
```
用户: 我想不起来了
↓
Agent: 自动识别意图
↓
Agent: 调用搜索功能
↓
输出搜索结果
```

**示例：**
```
用户: 我记得之前说过视频的事情
↓
Chat History: 搜索"视频"
↓
输出: 找到3个会话包含"视频"
```

---

### 自动归档

**为什么是03:55？**
- OpenClaw默认在04:00清空session窗口
- 在清空前5分钟归档，避免丢失0:00-4:00的聊天记录

**每天03:55**：
1. 自动执行归档
2. 归档今天未归档的会话
3. 更新搜索索引
4. 发送通知（可选）

**关机情况**：
- 03:55前关机 → 下次启动自动补归档
- 通知用户："已自动补归档 X 个会话"

---

## 📁 归档文件夹

```
/Users/tanghao/.openclaw/workspace/conversation-archives/
├── channel-side/              # Channel端完整对话
├── webui-side/                # WebUI端纯文字
├── search-index.json          # 搜索索引
├── evaluations-index.json     # 评估记录索引
└── status.json                # 归档状态
```

---

## 📊 输出格式

### 搜索结果
```markdown
✅ 找到 X 个会话

[1] 会话ID: xxxxxx
    日期: 2026-02-21 2305
    类型: channel/webui
    摘要: ...
    文件: /path/to/file.md

    匹配内容: ...
```

### 评估记录
```markdown
✅ 找到 X 个评估过的skills

[1] SkillName
   评估日期: 2026-02-21
   风险等级: 🟢/🟡/🔴
   结论: ...
   详情: ...
```

---

## 💡 使用提示

### 快速查找

**场景1：找不到之前的对话**
```
用户: 我想不起来了，之前说过关于视频的事
→ 自动搜索"视频"
```

**场景2：列出某天的对话**
```
用户: 2026年2月21日的所有对话
→ 列出指定日期
```

**场景3：查找评估过的skill**
```
用户: 我之前评估过哪些skills
→ 列出评估记录
```

---

### 高级用法

**组合使用**：
```
用户: 搜索"视频"，只要是webui的
→ /chat_history search "视频" --type webui
```

**日期过滤**：
```
用户: 今天有没有说过关于归档的事
→ 自动搜索"归档" + 日期过滤今天
```

---

## ⚙️ 配置

### 归档时间
默认：每天03:55（早于04:00清空）

⚠️ **建议**：不要晚于03:55，否则会丢失0:00-4:00的聊天记录

可修改：
```bash
/chat_history config --time 22:00
```

### 日志位置
默认：`/var/log/chat-archive.log`

可修改：
```bash
/chat_history config --log-path /path/to/log
```

---

## 🛡️ 隐私保护

- ✅ 归档文件保存在本地
- ✅ 不包含敏感系统信息
- ✅ 不自动上传到云端
- ✅ WebUI端会过滤工具调用和代码

---

## 📞 支持

如需帮助：
```
/chat_history          - 查看所有指令
/chat_history keyword  - 列出触发关键词
```

---

*Skill版本: 2.0*
*Skill名称: chat_history*
*创建时间: 2026-02-22*
*维护者: AI露娜 🌙*
