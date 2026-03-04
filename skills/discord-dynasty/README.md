# Discord Dynasty

OpenClaw skill：明朝六部式 Discord 管理——司礼监+六部频道模板、一帖一任务、上朝/上奏/回传。需配合 [Discord skill](https://clawhub.ai/steipete/discord) 与 `channels.discord` 配置使用。架构借鉴自 [Ai Court](https://clawhub.ai/wanikua/ai-court)。

## 安装

从 ClawHub 安装（推荐）：

```bash
clawhub install discord-dynasty
```

或从本仓库复制 `discord-task-center` 目录到 OpenClaw 工作区的 `skills/discord-task-center/`。

## 依赖

- OpenClaw 已配置 **Discord**（`channels.discord` 含 token 等）
- 建议同时安装 Discord skill：`clawhub install steipete/discord`

## 功能

- **一帖 = 一任务 = 一 session**：每个论坛帖子对应一个独立任务和会话
- **新建任务**：用户说「新建任务」「开个任务：xxx」时，在论坛发帖并打上状态/属性/模型标签
- **归档任务**：用户说「归档这个任务」时，给当前帖打上「归档」标签
- **模型标签**：帖子上的模型标签决定该帖对话使用的模型（由后端按标签切换）
- **六部管理频道模板**（可选）：用户说「建六部管理频道」「按六部模板创建」时，按司礼监 + 吏户礼兵刑工结构创建整站类别与频道；详见 reference 第 10 节

## 文件说明

- **SKILL.md** — 给 OpenClaw agent 的指令（何时触发、如何响应）
- **reference.md** — Discord API 与实现参考、与 discord skill 的对应关系；**六部管理频道模板**与**多 Agent 协作协议**（上朝/上奏/回传/巡检）见第 10、11 节
- **templates/** — 明朝六部式频道模板（`six-ministries.json` 完整版、`six-ministries-minimal.json` 精简版）
- **clawhub.json** — ClawHub 展示用元数据

## License

MIT
