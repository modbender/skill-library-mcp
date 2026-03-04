---
name: metabot-basic
description: MetaBot是基于 MetaID 协议的 AI Agent/Bot/机器人/智能体。本技能可用于 创建 MetaBot、设置 MetaBot 头像、发送 Buzz，发送链上信息。当用户在需要创建 Metabot，修改 MetaBot 头像，发送 buzz 信息时触发。需 Node.js >= 18、TypeScript。
---

# metabot basic

MetaBot 的基础技能，包括创建 MetaBot、设置 MetaBot 头像、发送 Buzz

## 关于 MetaBot
MetaBot是基于 MetaID 协议的 AI Agent/Bot/机器人/智能体。每个 MetaBot 都有对应的助记词、地址、LLM 设置、人格设置等，保存在skills根目录的 account.json

## 环境与依赖

- **要求**：Node.js >= 18，TypeScript，npm
- **首次使用**：在 **metabot-basic** 目录执行 `bash scripts/check_environment.sh`。若未安装依赖，脚本会提示或自动执行 `npm install`；若未安装 Node.js，会提示安装方式（如 https://nodejs.org/ 或 nvm）。
- **account.json**：位于**项目根目录**（与后续 metabot-basic 系列技能共用），首次创建 MetaBot 时会自动生成或插入新条目。

## 核心能力（仅三项）

本技能对外仅提供以下三项能力，转账、createPin 等由 metabot-wallet 技能提供。

1. **创建 MetaBot**：根据用户意图创建新 MetaBot，生成/更新根目录 `account.json`。
2. **设置 MetaBot 头像**：为已有 MetaBot 设置头像（图片 &lt; 1MB）。
3. **发送 Buzz**：以指定 MetaBot 身份向默认 MVC 网络发送一条 Buzz 协议消息。

## 触发与执行

### 1. 创建 MetaBot（必含名字）

**典型说法**：  
「创建 metabot，名字叫'xx'」「创建一个 MetaBot 名字叫 Sunny」「新建机器人，名字叫 小橙」

**执行方式**：  
在 **metabot-basic** 目录运行：
```bash
npm run start -- "创建 metabot，名字叫'小橙'"
```
或使用 ts-node：
```bash
npx ts-node scripts/main.ts "创建 metabot，名字叫'小橙'"
```
- 会生成新助记词、注册 MetaID name 节点、写入/更新根目录 `account.json`。  
- 若 account.json 不存在则创建；若已存在则在 `accountList` 前插入新账户。

### 2. 创建 MetaBot 并发送一条 Buzz

**典型说法**：  
「创建 metabot，名字叫'xx'，并发送一条 buzz 叫'hello'」「创建一个 MetaBot 叫 小橙，并发一条 buzz 内容为 你好世界」

**执行方式**：
```bash
npm run start -- "创建 metabot，名字叫'小橙'，并发送一条 buzz 叫'hello'"
```
- 先完成创建 MetaBot（同上），再用该 MetaBot 以 Buzz 协议向默认 MVC 网络发送指定内容。  
- 内容解析规则：`发条 buzz 叫'xxx'`、`内容为'xxx'`、`content is xxx` 等，见 `references/buzz-protocol.md`。

### 3. 设置 MetaBot 头像

**方式一**：创建时带头像  
- 将图片放到 `metabot-basic/static/avatar/`（或 Cursor 中 @ 引用该路径），然后：
```bash
npm run create-agents -- --avatar "metabot-basic/static/avatar/henry.png" "小橙"
```

**方式二**：为已有 MetaBot 设头像  
```bash
npm run create-avatar -- "小橙"
```
（会从 `static/avatar/` 读取图片；或传入路径：`npm run create-avatar -- "小橙" /path/to/image.png`）

- 限制：图片 &lt; 1MB，超限会提示并跳过头像。

### 4. 发送 Buzz（已有 MetaBot）

**典型说法**：  
「用 小橙 发一条 buzz 说 你好」「让 xx 发送一条 buzz，内容为 hello」

**执行方式**：
```bash
npm run send-buzz -- "小橙" "你好世界"
```
或从文件读内容：
```bash
npx ts-node scripts/send_buzz.ts "小橙" @./content.txt
```

## Scripts 速查

| 脚本 | 用途 |
|------|------|
| main.ts | 主入口：解析「创建 MetaBot」+ 可选「发送一条 buzz」，生成/更新 account.json 并可选发 Buzz |
| create_agents.ts | 批量创建 MetaBot（支持 `--avatar <路径>`） |
| create_avatar.ts | 为已有 MetaBot 设头像 |
| send_buzz.ts | 以指定 MetaBot 发送 Buzz |

## 解析规则摘要

- **名字**：`名字叫'xxx'`、`名字叫 xxx`、`name is xxx`、`用户名: xxx`  
- **Buzz 内容**：`发送一条 buzz 叫'xxx'`、`内容为'xxx'`、`content is xxx`、`发条信息，内容为 xxx`  
- **账户选择**：新建时新账户 unshift 到 accountList；已有则按用户名/地址匹配，无匹配用 accountList[0]。  
- 完整 account 结构、path、addressIndex 等见 **references/account-management.md**。

## Cursor 执行规范

当用户请求「执行某命令」时：先说明推荐方案，**然后代为执行**，让用户一键确认即可跑起来，而非仅贴命令。若用户未安装环境，引导先执行 `bash scripts/check_environment.sh`（必要时自动安装依赖）。

## References

- `references/account-management.md` - account.json 结构与字段说明  
- `references/buzz-protocol.md` - Buzz 协议与内容解析
