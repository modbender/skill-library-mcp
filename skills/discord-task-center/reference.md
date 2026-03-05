# Discord 任务中心 — API 与实现参考

本文档为 SKILL.md 的补充，提供 Discord API 与实现细节，便于开发时查阅。

## 1. 创建论坛频道 (GUILD_FORUM)

**Endpoint**: `POST /channels`（需带 `guild_id`，通常通过 body 传入）

**Body 要点**:
- `type`: `15`（GUILD_FORUM）
- `name`: 频道名，1–100 字符
- `topic`: 可选，0–4096 字符（论坛/媒体频道）
- `available_tags`: 可选，论坛可用标签数组，**最多 20 个**

**Forum Tag 对象**（available_tags 每项）:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | snowflake | 标签 ID（创建时由 Discord 生成，更新频道时仅新建项可不带） |
| name | string | 标签名，0–20 字符 |
| moderated | boolean | 是否仅 MANAGE_THREADS 权限者可添加/移除 |
| emoji_id | ?snowflake | 服务器自定义 emoji ID（与 emoji_name 二选一） |
| emoji_name | ?string | Unicode emoji |

更新论坛频道时，`available_tags` 中若只改现有标签，可只传 `name` 等需改字段。

**权限**: Bot 需 `MANAGE_CHANNELS`。

---

## 2. 在论坛中发帖（创建 Thread）

**Endpoint**: `POST /channels/{channel.id}/threads`  
（channel.id = 论坛频道 ID）

**Body（JSON 或 multipart/form-data）**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 帖子标题，1–100 字符 |
| message | object | 是 | 首条消息，见下表 |
| applied_tags | array of snowflake | 否 | 要打上的标签 ID 列表，**最多 5 个** |
| auto_archive_duration | integer | 否 | 60 / 1440 / 4320 / 10080（分钟） |
| rate_limit_per_user | ?integer | 否 | 0–21600 秒 |

**message 对象**（Forum and Media Thread Message Params）:
- 至少提供其一：`content`、`embeds`、`sticker_ids`、`components`、`files[n]`
- `content`: 字符串，最多 2000 字符
- `embeds`: 最多 10 个 rich embed

**权限**: 当前用户/Bot 需在频道有 `SEND_MESSAGES`（论坛中 `CREATE_PUBLIC_THREADS` 被忽略）。

**返回**: 新建的 channel（thread）对象，以及首条 message 对象（嵌套）。

---

## 3. 修改帖子（含标签）

**Endpoint**: `PATCH /channels/{channel.id}`  
（channel.id = thread ID，即帖子 ID）

**Body（Thread 适用字段）**:
| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 1–100 字符 |
| applied_tags | array of snowflake | 该帖当前应有的标签 ID 列表，**最多 5 个**（全量覆盖） |
| archived | boolean | 是否归档 |
| locked | boolean | 是否锁定 |
| auto_archive_duration | integer | 60 / 1440 / 4320 / 10080 |

仅更新标签时，只传 `applied_tags` 即可；归档任务时通常同时传 `applied_tags`（加入「归档」、移除「进行中」等）。

**权限**: 修改标签/归档/锁定等需 `MANAGE_THREADS`；仅改 name 等部分字段时也可能需该权限（视 Discord 规则而定）。若只把 thread 从 archived 改为未归档且未锁定，仅需 `SEND_MESSAGES`。

---

## 4. 获取频道/帖子信息

- **获取论坛频道（含 available_tags）**: `GET /channels/{channel.id}`  
  返回的 channel 对象中带 `available_tags`（标签 id、name、emoji 等），用于解析「模型标签」「状态」「归档」等对应关系。
- **获取帖子（thread）**: `GET /channels/{thread.id}`  
  返回的 channel 对象中带 `applied_tags`（当前帖子的标签 ID 列表）。

实现「根据模型标签切换模型」时：在用户于某帖内发起对话时，调用 `GET /channels/{thread.id}`，从 `applied_tags` 与论坛的 `available_tags` 解析出模型名/ID，再选择对应模型处理本次对话。

---

## 5. 标签数量与限制

- 每个论坛频道 **available_tags 最多 20 个**。
- 每个帖子 **applied_tags 最多 5 个**。  
  设计标签体系时需控制：状态(1) + 属性(1) + 归档(0 或 1) + 模型(1) 通常不超过 5 个；若需更多维度，可合并或精简。

---

## 6. 可选：创建频道请求示例

```json
{
  "name": "task-center",
  "type": 15,
  "topic": "任务看板：一帖一任务，用标签筛选状态/属性/模型。",
  "available_tags": [
    { "name": "待开始" },
    { "name": "进行中" },
    { "name": "已完成" },
    { "name": "归档" },
    { "name": "开发" },
    { "name": "学习" },
    { "name": "工作" },
    { "name": "gpt-4o" },
    { "name": "claude-3-5" }
  ]
}
```

创建后，从返回的 channel 或再次 GET channel 取得每个 tag 的 `id`，在发帖与修改帖子时用这些 id 填入 `applied_tags`。

---

## 7. OpenClaw 对接要点小结

- **Session ↔ Thread**: 以 `thread.id` 为唯一键绑定 session 与任务。
- **新建任务**: 调用 `POST /channels/{forum_channel_id}/threads`，传 `name`、`message`、`applied_tags`（待开始 + 属性 + 模型标签）。
- **归档任务**: 调用 `PATCH /channels/{thread.id}`，`applied_tags` 设为当前标签中加入「归档」、移除「进行中」等。
- **对话时选模型**: 请求时带 `thread_id`，后端 `GET /channels/{thread.id}` 取 `applied_tags`，与 `available_tags` 映射得到模型，再调用 OpenClaw/LLM 对应模型。

---

## 8. 与 ClawHub / 官方 Discord skill 结合

### 8.1 ClawHub 上的 Discord 相关 skill

- **steipete/discord**（官方/社区 Discord skill）
  - 来源：ClawHub 搜索 "discord" 或 [clawhub.ai/steipete/discord](https://clawhub.ai/steipete/discord)，亦见 [openclawskills.best](https://openclawskills.best/skills/steipete/discord/)、[SkillHub openclaw-discord](https://www.skillhub.club/skills/openclaw-openclaw-discord)。
  - 安装：`clawhub install steipete/discord` 或 `openclaw add @steipete/discord`（以当前 OpenClaw/ClawHub 文档为准）。
  - 依赖：配置 `channels.discord`（如 `token`、`enabled`）；metadata 中 `requires.config: ["channels.discord"]`。

### 8.2 discord skill 提供的能力（与本 skill 的对应）

| 本 skill 需求           | discord 工具 action      | 说明 |
|-------------------------|---------------------------|------|
| 新建任务帖              | `threadCreate`            | 论坛频道下创建 thread：`channelId`=论坛频道 ID，`name`=帖子标题；若支持首条内容则传 message/content。官方文档中 threadCreate 含 `messageId` 多为「从消息创建」；论坛帖为「无 messageId」创建，需网关/实现支持。 |
| 给新帖打标签            | `channelEdit` 或创建时参数 | 若 threadCreate 支持 `applied_tags` 则创建时传入；否则创建后用 `channelEdit`，`channelId`=新 thread ID，`applied_tags`=标签 ID 数组（待开始+属性+模型）。 |
| 归档任务（改标签）      | `channelEdit`             | `channelId`=当前帖子（thread）ID，`applied_tags`=当前标签中加入「归档」、移除「进行中」。 |
| 建任务中心论坛频道     | `channelCreate`           | `type: 15`（GUILD_FORUM），`name`、`topic`、`available_tags`（若工具支持）。需开启 `discord.actions.channels: true`。 |
| 读当前帖/频道信息       | `channelInfo`              | `channelId`=thread ID，可拿到 `applied_tags`；后端用此选模型。 |

**说明**：当前公开的 discord skill 文档中，`threadCreate` 示例为 `channelId` + `name` + `messageId`（从一条消息建 thread）。Discord 论坛帖的创建是「在论坛频道下 POST thread，带 name、message、applied_tags，无 messageId」。若 OpenClaw 网关已支持论坛帖创建（见 [docs.openclaw.ai Discord Forum channels](https://docs.openclaw.ai/channels/discord) 中的 `openclaw message thread create --target channel:<forumId>`），则 agent 调用 threadCreate 时对论坛频道不传 messageId 即可；是否支持 `applied_tags` 以实际工具 schema 为准。若不支持，可在网关或插件层扩展「创建论坛帖时传 applied_tags」及「channelEdit 写 thread 的 applied_tags」。

### 8.3 推荐组合用法

1. 安装并配置 **discord** skill（`channels.discord` 配置好 token、guild 等）。
2. 将 **discord-task-center** 与本 skill 同放在工作区 `skills/` 下（如 `skills/discord-task-center/`）。
3. Agent 在任务帖内收到「新建任务/归档任务」时，先应用本 skill 的语义，再调用 discord 的 `threadCreate` / `channelEdit` 等；若工具暂无 applied_tags，则完成发帖/改标题后提示用户手动在 Discord 勾选标签。

---

## 9. OpenClaw 侧使用说明

- **Skill 放置位置**：OpenClaw 从工作区 `skills/` 目录加载 skill（对应运行时的 `/skills`）。将本 skill 目录（含 `SKILL.md` 与 `reference.md`）放到 OpenClaw 工作区的 `skills/discord-task-center/` 下即可被加载。
- **可选 frontmatter 门控**：若希望仅在配置了 Discord 任务中心时才加载本 skill，可在 `SKILL.md` 的 frontmatter 中加入 `metadata`（单行 JSON），例如：
  ```yaml
  metadata: { "openclaw": { "requires": { "config": ["discord.taskCenterForumId"] } } }
  ```
  具体 config 路径以你的 `openclaw.json` 中 Discord 集成配置为准。
- **Agent 指令**：SKILL.md 正文是写给 OpenClaw agent 的指令（何时触发、如何响应新建/归档、模型标签的含义）；本 reference 供实现工具/插件或排查 API 时查阅。
