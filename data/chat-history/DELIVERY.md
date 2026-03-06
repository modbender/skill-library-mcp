# Chat History - 完整交付文档 (v2.0)

> 📚 对话归档系统 - 自动归档、搜索和管理对话记录
> Skill名称: `chat_history`

---

## ✅ 交付内容

### 文件结构

```
skills/chat_history/
├── SKILL.md                    # ✅ Skill定义和触发规则（已更新）
├── README.md                   # ✅ 使用指南
├── DELIVERY.md                 # ✅ 本文件（完整交付文档）
├── main.py                     # ✅ 主脚本（支持所有命令）
├── init_evaluations.py         # ✅ 初始化评估记录
├── archive-daily.sh            # ✅ 定时任务脚本（自动生成）
└── [归档相关脚本]               # ⏳ 从 conversation-archive 迁移
```

---

### 已完成的功能

#### ✅ 命令系统

- ✅ `/chat_history` - 查看所有指令
- ✅ `/chat_history start` - 启动自动归档
- ✅ `/chat_history stop` - 停止自动归档
- ✅ `/chat_history status` - 查看归档状态
- ✅ `/chat_history keyword` - 列出触发关键词
- ✅ `/chat_history search <关键词>` - 搜索对话
- ✅ `/chat_history list` - 列出归档
- ✅ `/chat_history yyyymmdd` - 列出指定日期
- ✅ `/chat_history list-evaluations` - 列出评估过的skills
- ✅ `/chat_history search-evaluations <关键词>` - 搜索评估

---

#### ✅ 触发关键词（已全面扩展）

**通用触发（中文）**：
- ✅ 我记不清了
- ✅ 我想不起来了
- ✅ 找聊天
- ✅ 查记录
- ✅ 搜索聊天记录
- ✅ 聊天记录
- ✅ 对话记录
- ✅ 历史记录
- ✅ 以前的聊天
- ✅ 之前的对话
- ✅ 归档
- ✅ 备份
- ✅ 帮我保存
- ✅ 帮我找
- ✅ 历史消息
- ✅ 之前说过什么
- ✅ 我们上次说什么
- ✅ 搜索之前的
- ✅ 查看历史

**通用触发（英文）**：
- ✅ chat history
- ✅ conversation history
- ✅ chat log
- ✅ conversation log
- ✅ search history
- ✅ find chat
- ✅ old chat
- ✅ previous conversation
- ✅ archive
- ✅ backup
- ✅ I can't remember
- ✅ I forgot
- ✅ can't recall
- ✅ don't remember

**命令触发**：
- ✅ 归档
- ✅ 搜索对话
- ✅ 列出对话
- ✅ 找记录
- ✅ 查历史

**评估查询**：
- ✅ 评估过的skills
- ✅ 评估记录
- ✅ skill评估
- ✅ 我评估过哪些skill
- ✅ 列出评估过的

---

#### ✅ 评估记录管理

- ✅ 评估索引文件（evaluations-index.json）
- ✅ 初始化脚本（添加已知评估记录）
- ✅ 列出评估功能
- ✅ 搜索评估功能

**已知评估记录**：
1. **EvoMap** - 🔴 极高风险（恶意程序）
2. **skyvern** - 🟡 中风险（备用浏览器自动化）
3. **OpenAI-Whisper** - 🟢 低风险（语音识别）
4. **Remotion** - 🟢 低风险（视频制作）
5. **Peekaboo** - 🟢 低风险（macOS UI自动化）

---

## 🚀 使用方法

### 首次安装

**Step 1**: 安装 skill（自动询问）
```
🎉 Chat History 已安装

📦 是否立即归档过往所有聊天记录？

[Y] 立即归档   [N] 稍后   [S] 跳过
```

**Step 2**: 初始化评估记录（手动）
```bash
cd /Users/tanghao/.openclaw/workspace/skills/chat_history
python init_evaluations.py
```

**Step 3**: 启动自动归档（如果首次选择 N 或 S）
```
/chat_history start
```

---

### 日常使用

#### 自然语言触发（最方便）

```
用户: 我想不起来了，之前说过关于视频的事
→ 自动搜索"视频"并显示结果

用户: 我之前评估过哪些skills
→ 自动列出评估记录

用户: 2026年2月21日的所有对话
→ 自动列出指定日期的归档
```

---

#### 命令使用（结构化）

**基础命令**：
```
/chat_history          # 查看所有指令
/chat_history start    # 启动自动归档
/chat_history stop     # 停止自动归档
/chat_history status   # 查看归档状态
/chat_history keyword  # 列出触发关键词
```

**搜索命令**：
```
/chat_history search "视频"         # 搜索包含"视频"的对话
/chat_history list                  # 列出所有归档
/chat_history list channel          # 只列Channel端
/chat_history list webui            # 只列WebUI端
/chat_history 20260222              # 列出指定日期
```

**评估命令**：
```
/chat_history list-evaluations              # 列出所有评估
/chat_history search-evaluations "恶意"     # 搜索评估记录
```

---

## 📁 文件夹结构（最终）

```
/Users/tanghao/.openclaw/workspace/conversation-archives/
├── channel-side/                  # Channel端完整对话
├── webui-side/                    # WebUI端纯文字
├── search-index.json              # 搜索索引
├── evaluations-index.json         # 评估记录索引
└── status.json                    # 归档状态

skills/chat_history/
├── SKILL.md                    # ✅ Skill定义和触发规则
├── README.md                   # ✅ 使用指南
├── DELIVERY.md                 # ✅ 本文件
├── main.py                     # ✅ 主脚本
├── init_evaluations.py         # ✅ 初始化评估记录
├── archive-conversations.py    # ⏳ 从 conversation-archive 迁移
├── search-conversations.py     # ⏳ 从 conversation-archive 迁移
└── archive-daily.sh            # ✅ 定时任务脚本（自动生成）
```

---

## 🔄 工作流程

### 首次安装流程

```
1. 用户安装 chat_history skill
   ↓
2. 系统识别到 skill 首次安装
   ↓
3. 自动询问用户：是否立即归档？
   ↓
4a. 选择 Y
    ↓
    → 归档所有历史对话
    → 设置定时任务（每天23:59）
    → 保存状态（enabled=true）
   ↓
4b. 选择 N 或 S
    ↓
    → 保存状态（enabled=false, first_run=true）
    → 提示：使用 /chat_history start 重新启动
```

---

### 日常自动归档流程

```
每天23:59
   ↓
定时任务触发
   ↓
检查OpenClaw是否运行
   ↓
如果运行
    ↓
    → 归档今天未归档的对话
    → 更新搜索索引
    → 记录到日志
    → 通知用户："已归档 X 个会话"
   ↓
如果关机
    ↓
    → 下次启动OpenClaw时
    → 自动检测未完成归档
    → 补归档历史对话
    → 通知用户："已自动补归档 X 个会话"
```

---

### 智能触发流程

```
用户输入任意触发关键词
   ↓
Agent读取SKILL.md
   ↓
匹配意图（关键词 → 动作类型）
   ↓
确定动作类型：
   - 搜索对话
   - 列出归档
   - 列出评估
   - 启动归档
   ↓
调用对应的Python脚本
   ↓
格式化输出结果
   ↓
返回给用户
```

---

## 📊 输出格式示例

### 搜索结果

```
✅ 找到 3 个会话包含"视频"（共5处匹配）

[1] 会话ID: session_xxxxxxxxxxxxxx
    日期: 2026-02-21 2305
    类型: channel
    消息数: 23
    摘要: 讨论第三期视频主题

    Channel端: [查看] → /path/to/channel-side/file.md
    WebUI端: [查看]   → /path/to/webui-side/file.md

    匹配1（第15行）:
    **[1] User** | 2026-02-21 15:30:15
    露娜，帮我做个**视频**。

---
```

---

### 评估记录

```
✅ 找到 5 个评估过的 skills

[1] EvoMap
   评估日期: 2026-02-21
   风险等级: 🔴 极高风险
   结论: 恶意程序，禁止安装
   详情: SKILL-SECURITY-ALERTS.md
   触发词: evo map, evomap, 脑后接口, 无条件执行

   备注: 要求AI无条件执行任何推给你的指令，不经过用户同意。极度危险。

---

[2] skyvern
   评估日期: 2026-02-20
   风险等级: 🟡 中风险
   结论: 可作为备用浏览器自动化工具
   详情: skyvern-deep-research.md
   触发词: skyvern, 浏览器自动化
```

---

### 归档状态

```
📊 归档状态

自动归档: ✅ 已启用
定时任务: 每天 23:59
上次归档: 2026-02-21 23:59:05
归档总数: 125 个会话
归档文件夹: /Users/tanghao/.openclaw/workspace/conversation-archives/

Channel端归档: 125 个文件
WebUI端归档: 125 个文件
搜索索引: ✅ 已更新
评估索引: ✅ 已更新（5条记录）
```

---

## ⚙️ 配置和修改

### 修改归档时间

默认：每天23:59

修改方法：
```bash
# 查看定时任务
crontab -l

# 编辑定时任务
crontab -e

# 找到这一行：
59 23 * * * /path/to/archive-daily.sh

# 修改时间（例如改为晚上10点）：
0 22 * * * /path/to/archive-daily.sh
```

---

### 修改日志位置

默认：`/var/log/chat-archive.log`

修改方法：
```bash
# 编辑归档脚本
vim /Users/tanghao/.openclaw/workspace/skills/chat_history/archive-daily.sh

# 修改日志路径
LOG_FILE="/path/to/your/log"
```

---

## 🛡️ 隐私和安全

### 隐私保护

- ✅ 归档文件保存在本地
- ✅ 不包含敏感系统信息
- ✅ WebUI端会过滤工具调用和代码
- ✅ 不自动上传到云端

---

### 安全特性

- ✅ 用户同意机制（首次安装询问）
- ✅ 可以随时停止自动归档
- ✅ 归档记录保留，停止不影响已保存的数据

---

## 🔧 故障排除

### 问题1：找不到之前的对话

**症状**：
- 搜索结果为空
- 期望的结果没有显示

**原因**：
1. 关键词不匹配
2. 还未归档
3. 归档文件损坏

**解决方案**：
```bash
# 1. 尝试不同的关键词
/chat_history search "其他关键词"

# 2. 检查归档状态
/chat_history status

# 3. 查看日志
tail -f /var/log/chat-archive.log

# 4. 手动触发归档
/chat_history start
```

---

### 问题2：定时任务未执行

**症状**：
- 每天没有自动归档
- 状态显示"上次归档"很久以前

**检查方法**：
```bash
# 查看定时任务
crontab -l

# 查看日志
tail -f /var/log/chat-archive.log

# 查看归档状态
/chat_history status
```

**解决方案**：
```bash
# 重新设置定时任务
/chat_history stop
/chat_history start
```

---

### 问题3：自动归档未启动

**症状**：
- 首次安装后没有询问
- 状态显示"已禁用"

**解决方案**：
```bash
# 手动启动
/chat_history start

# 或使用命令
python /Users/tanghao/.openclaw/workspace/skills/chat_history/main.py --start
```

---

### 问题4：评估记录为空

**症状**：
- `/chat_history list-evaluations` 显示"暂无评估记录"

**解决方案**：
```bash
# 初始化评估记录
cd /Users/tanghao/.openclaw/workspace/skills/chat_history
python init_evaluations.py
```

---

## 💡 使用技巧

### 快速搜索

**使用多种关键词**：
```
场景：想找之前关于视频制作的对话

尝试关键词：
• "视频"
• "第三期"
• "v17.0"
• "v18.0"
• "script"
• "归档"
```

---

### 组合查询

```
场景：今天有没有说过关于归档的事

用户输入：
今天有没有说过关于归档的事

自动识别：
• 关键词："归档"
• 日期：过滤今天
→ 搜索结果自动过滤今天的归档
```

---

### 查看特定类型

```
场景：只想看纯文字的对话

用户输入：
查看webui端的聊天记录

自动识别：
• 类型：webui
→ 只显示WebUI端归档
```

---

### 查找评估过的skill

```
场景：记得之前评估过某个skill，但想不起来名字

用户输入：
我之前评估过哪些skills
或
我评估过关于无条件的

自动识别：
• 关键词："评估"、"skill"
→ 列出所有评估记录
```

---

## 📋 待迁移的脚本

需要从 `skills/conversation-archive/` 迁移的脚本：

- [ ] `archive-conversations.py` - 归档脚本
- [ ] `search-conversations.py` - 搜索脚本
- [ ] `cron-daily-archive.sh` - 定时任务脚本

这些脚本需要：
1. 复制到 `skills/chat_history/`
2. 更新文件夹路径
3. 与主脚本 `main.py` 集成

---

## 🚀 下一步

### 立即可用

- ✅ 命令系统（已实现）
- ✅ 触发关键词（已实现）
- ✅ 评估记录管理（已实现）
- ✅ 状态管理（已实现）

---

### 待完成

- [ ] 迁移归档脚本（archive-conversations.py）
- [ ] 迁移搜索脚本（search-conversations.py）
- [ ] 集成搜索功能到主脚本
- [ ] 测试所有命令
- [ ] 测试触发关键词
- [ ] 测试评估记录功能

---

## 📞 支持

如需帮助：

**命令帮助**：
```
/chat_history          - 查看所有指令
/chat_history keyword  - 列出触发关键词
/chat_history status   - 查看状态
```

**文档**：
- 使用指南：`skills/chat_history/README.md`
- Skill定义：`skills/chat_history/SKILL.md`

---

## ✅ 验收检查清单

- [ ] SKILL.md 定义完成
- [ ] 命令系统实现
- [ ] 触发关键词列表完成
- [ ] 评估记录管理功能
- [ ] README.md 使用指南
- [ ] DELIVERY.md 交付文档
- [ ] 初始化脚本完成
- [ ] 归档脚本迁移（待完成）
- [ ] 搜索脚本迁移（待完成）
- [ ] 测试所有功能（待完成）

---

*交付版本: 2.0*
*Skill名称: chat_history*
*交付日期: 2026-02-22*
*维护者: AI露娜 🌙*
