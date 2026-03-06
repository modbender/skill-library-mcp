---
name: discord-task-center
description: "Handles Discord task-center forum: create task posts, archive
  tasks by tag, and respect model tags. Supports six-ministries style channel
  template (司礼监+六部). Use when user says 新建任务、开个任务、归档任务、建六部管理频道, or when asked to
  create a task from todo/calendar. Requires Discord forum integration."
---


# Discord 任务中心 (供 OpenClaw Agent 使用)

你当前对话所在的 Discord 论坛帖子（thread）对应**一个任务**和**一个 session**。本 skill 约定你如何响应用户在任务帖内的请求：新建任务、归档任务、以及如何理解帖子上的模型标签。

## 何时遵循本 Skill

- 用户身处 **Discord 任务中心论坛**的某个帖子（thread）内与你对话；或
- 用户说 **「新建一个任务」「开个任务：xxx」**；或
- 用户说 **「归档这个任务」「归档当前任务」**；或
- 用户要求根据其**任务事项/待办/日历**主动开一个任务帖；或
- 用户说 **「建六部管理频道」「按六部模板创建频道」「创建明朝六部管理结构」**（见下文「建六部管理频道」一节）。

## 上下文约定

- **一帖 = 一任务 = 一 session**：每个论坛帖子绑定一个独立任务和会话。
- **模型标签**：帖子当前所打的「模型」标签（如 gpt-4o、claude-3-5）表示**本对话应使用的模型**。若用户或管理员在 Discord 上修改了该帖的模型标签，**下一轮对话**会由后端按新标签切换模型，你无需在回复里改模型，只需知道这一点即可。
- **标签体系**：论坛预置状态（待开始、进行中、已完成）、属性（开发、学习、工作）、归档、以及若干模型标签。每个帖子最多 5 个标签。

---

## 当用户说「新建一个任务」或「开个任务：xxx」

你要做：

1. **创建论坛帖子**：调用可用的「在任务中心论坛发帖」工具/接口（例如 Discord 插件提供的创建 forum thread 或 `createTaskPost` 等）。传入：
   - **标题**：用户给出的任务名，或从「开个任务：xxx」中提取；若未给出则根据上下文生成简短标题。
   - **首条消息**：任务描述或检查项（可选），可从用户话中提取或留空。
   - **标签**：至少包含 **待开始**（或 **进行中** 若业务默认）、一个**属性**（开发/学习/工作，按用户意图选，否则默认一个）、以及**当前会话的模型标签**（与当前帖或系统默认一致）。
2. **回复用户**：确认已创建任务，并附上新帖子的链接（若工具返回了链接）。可写：「已创建任务 [标题]，点这里进入帖子继续推进。」

若用户是从「任务事项/待办/日历」让你开任务，同样：在任务中心论坛新建一帖，打上上述标签，并在回复中说明已根据其事项创建了任务帖。

---

## 当用户说「归档这个任务」或「归档当前任务」

你要做：

1. **更新当前帖子标签**：调用可用的「修改帖子/thread 标签」工具/接口（例如更新 thread 的 `applied_tags`）。将当前帖的标签改为：**加入「归档」**，并**移除「进行中」**（若有）。其他标签（如属性、模型）可保留。
2. **回复用户**：确认已归档。可写：「已归档当前任务，之后可在论坛里用「归档」标签筛选查看。」

---

## 当用户要求「建一个任务管理频道」或首次配置

若用户要求创建专门用于任务管理的论坛频道（仅当你有创建频道权限时）：

- 使用 **GUILD_FORUM**（论坛频道），建议名称如「任务中心」或 `task-center`。
- 在频道中预置 **available_tags**：待开始、进行中、已完成、归档、开发、学习、工作、以及若干模型标签（如 gpt-4o、claude-3-5）。
- 具体 API 与字段见 [reference.md](reference.md)。

---

## 当用户要求「建六部管理频道」「按六部模板创建频道」或「创建明朝六部管理结构」

若用户要求按**明朝六部式**创建整站管理频道结构（仅当你有创建频道权限时）：

1. **读取模板**：从本 skill 的 `templates/six-ministries.json` 读取配置（若用户明确要精简版，则用 `templates/six-ministries-minimal.json`）。模板结构见 [reference.md](reference.md) 第 10 节。
2. **创建顺序**：**先司礼监 (main)，再六部**（吏→户→礼→兵→刑→工）。每个类别下：先调用 `channelCreate` 创建**类别**（Discord type=4，name 为 category.name），取得返回的频道 ID 作为 `parent_id`；再对该类别下每个 channel 调用 `channelCreate`，传入 `parent_id`、`name`、`type`（0=文本、5=公告、15=论坛），以及 `topic`、`available_tags`（仅论坛需传）。
3. **使用 discord 工具**：使用 `channelCreate`（需开启 `discord.actions.channels: true`）。若工具一次只能建一个频道，则按上述顺序循环调用，并在回复中汇总新建的类别名与频道链接/ID。
4. **回复用户**：确认已按六部模板创建完成，并说明「司礼监置顶，其下为六部；工部内含任务中心论坛」。若工具不支持 `parent_id` 或 `available_tags`，则完成能创建的部分后，提示用户在 Discord 后台手动创建类别/子频道或补全标签。**若无法读取模板文件**，请提示用户检查 skill 是否完整安装或提供正确的模板路径（如 `discord-task-center/templates/six-ministries.json`）。

**与「建一个任务管理频道」的区分**：后者只建**一个**任务中心论坛；本处建**整站**司礼监 + 六部结构（含任务中心在内）。

---

## 与 ClawHub / 官方 Discord skill 配合使用

本 skill 与 OpenClaw 的 **discord** skill 一起使用：由 discord skill 提供 `discord` 工具（发消息、thread、频道管理等），你按本 skill 的语义调用即可。

- **安装 Discord skill**（若尚未安装）：
  - ClawHub：`clawhub install steipete/discord` 或 `openclaw add @steipete/discord`
  - 需在配置中启用 `channels.discord` 并设置 bot token。
- **新建任务帖**：使用 `discord` 工具的 **threadCreate**。在论坛频道下创建 thread 时，若后端支持「论坛帖」（不传 messageId），则用 `channelId`（论坛频道 ID）、`name`（帖子标题）、首条内容（若工具支持 message/content）。若该工具支持 **applied_tags** 或创建后可用 **channelEdit** 打标签，则传入或随后编辑为：待开始 + 属性 + 模型标签。
- **归档任务**：使用 `discord` 工具的 **channelEdit**（目标为当前 thread 的 channelId），更新 **applied_tags**：在现有标签中加入「归档」、移除「进行中」。
- **建任务中心频道**：使用 **channelCreate**，`type: 15`（GUILD_FORUM），并设 `available_tags`（若工具支持）；否则需在 Discord 后台或通过其他方式预置标签。详见 [reference.md](reference.md) 的「与 ClawHub Discord skill 结合」一节。

若当前 `discord` 工具未暴露论坛帖的 `applied_tags`（创建时或 channelEdit），你在执行新建/归档时尽量完成发帖与改标题，并回复用户说明「标签需在 Discord 客户端手动勾选」或建议管理员扩展工具以支持 applied_tags。详细 API 与扩展点见 [reference.md](reference.md)。
