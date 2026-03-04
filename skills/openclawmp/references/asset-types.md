# 资产类型判断指南

> 发布资产前，按以下优先级判断类型。核心原则：**看项目在 OpenClaw 架构中的角色，不看技术复杂度。**

## ⚠️ 核心规则：Experience 是兜底类型

**Experience 是最后的退路，不是默认选项。**

1. Skill / Plugin / Trigger / Channel 四类**平级**，按架构角色直接判断
2. 都不合适时，才归为 Experience
3. 如果觉得"既可以是 Experience 也可以是其他类型"，**优先选其他类型**
4. 合集（多资产组合包）也归入 Experience，不再单独设 Template 类型

## 五种类型

### Channel（📡 通信器）

项目是否承担 Agent 与用户之间的**双向消息通道**？

✅ 飞书 / Telegram / Discord / Slack 适配器
✅ 桌面可视化客户端（如 KKClaw 球体宠物）— WebSocket 接收 Agent 输出并渲染，接受用户输入回传
✅ 任何有 UI 渲染 + 双向通信 + 连接 Gateway 的项目

🔑 **把显示/交互部分拆出来，它就是一个展示输入输出的渠道 → Channel**

### Trigger（🔔 触发器）

项目是否**监听外部事件**并唤醒 Agent？或**以 cron/定时调度为核心驱动**？

✅ 文件监控（fswatch / inotify）、Webhook 接收器、定时器
✅ 邮件 / RSS / 日历变更监听、股价变动通知
✅ **含 cron 定时任务的自动化工作流**（每日摘要、定时巡检、周期性数据采集等）

**cron 规则：**
- **单个 cron 定时任务**驱动的自动化 → **Trigger**（一个触发器做一件事）
- **多个 cron 定时任务组成的系统方案** → **Experience**（合集/方案，不是单个触发器）

判断标准：数 cron 任务数量。只有一个核心定时任务 → Trigger；有 2+ 个不同的定时任务协同工作 → Experience（合集）。

🔑 **单个 cron → Trigger；多 cron 组合方案 → Experience**

### Plugin（🔌 工具）

项目是否给 Agent 提供**新的工具能力**？代码级扩展。

✅ MCP server、Tool provider、API wrapper
✅ 数据库连接器、搜索引擎封装、飞书文档操作工具

🔑 **Agent 通过 tool call 调用它 → Plugin**

### Skill（🛠️ 技能）

Agent 可直接学习的能力包？含提示词与脚本，定义"怎么做某个任务"。

✅ 代码审查流程、SEO 审计、小红书文案创作、法律助理
✅ 有 SKILL.md，通过自然语言 prompt 引导 Agent 行为

🔑 **Agent 会反复使用的操作流程 → Skill**

### Experience（💡 经验/合集）— 兜底类型

以上都不合适？那就是 Experience。包括：

**经验类：** 亲身实践的方案与配置思路，给 Agent 一份参考。
✅ 三层记忆系统搭建方案（daily log + MEMORY.md + cron sync）
✅ 赛博人格模板（SOUL.md + IDENTITY.md + USER.md 的模板化方案）
✅ 飞书卡片最佳实践（Schema 2.0 卡片 + Python 发送脚本，踩坑全记录）
✅ macOS 常驻方案（caffeinate + LaunchAgent + hooks，让 Agent 永不休眠）
✅ 模型路由配置方案

**合集类：** 多个资产的打包组合，一键获得完整方案。
✅ "全栈飞书助手"（Skill + Channel + Experience + Trigger 的组合包）
✅ "Agent 冷启动套件"（记忆系统 + 人格模板 + 心跳配置）

**Experience 面向两类读者：**
- 给 **Agent** 的是配置文件和参考思路
- 给 **人** 的 README 说清"这在解决什么问题"

🔑 **定义"怎么配置 / 怎么搭建"而非"怎么做某个反复执行的任务"，且不是 Channel/Trigger/Plugin/Skill → Experience**

## 常见误判

| 误判 | 正确 | 原因 |
|------|------|------|
| 桌面可视化客户端 → experience | → **channel** | 本质是消息渠道 |
| WebSocket 聊天 UI → plugin | → **channel** | 做的是输入/输出展示 |
| 文件 watcher → skill | → **trigger** | 核心是事件监听 |
| cron 驱动的每日摘要 → skill | → **trigger** | 单个 cron，核心是定时触发 |
| cron 驱动的定时巡检 → skill | → **trigger** | 单个 cron，定时事件驱动 |
| 多 cron 组合方案 → trigger | → **experience** | 多个定时任务的合集/系统方案 |
| API wrapper → skill | → **plugin** | 代码级工具调用 |
| SOUL.md 人设 → skill | → **experience** | 经验/配置沉淀（确实不是别的类型） |
| 记忆系统方案 → plugin | → **experience** | 实践方案分享 |
| 模型路由方案 → plugin | → **experience** | 配置片段 |
| 多资产组合包 → template | → **experience** | template 已合并入 experience |

## 灰色地带怎么判？

问自己两个问题：

**第一问：用户装它主要为了什么？**
- 装飞书 bot 主要为了**收发消息** → Channel
- 装 PDF 工具主要为了**调用 API 处理文件** → Plugin
- 装代码审查流程为了**让 Agent 学会审查步骤** → Skill
- 装每日 Reddit 摘要为了**定时自动跑** → Trigger
- 装记忆系统方案为了**参考怎么配置自己的记忆** → Experience

**第二问：能不能归到前四类？**
- 如果犹豫"这到底是 Skill 还是 Experience"→ **选 Skill**
- 如果犹豫"这到底是 Plugin 还是 Experience"→ **选 Plugin**
- 如果犹豫"这到底是 Skill 还是 Trigger"→ **看驱动方式**：单个 cron 驱动 → Trigger；按需/人触发 → Skill
- 如果犹豫"这到底是 Trigger 还是 Experience"→ **数 cron 数量**：单个 → Trigger；多个 cron 组合方案 → Experience
- 只有前四类都说不通时 → Experience
