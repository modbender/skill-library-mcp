# Youmind Skill（API 优先）

这个 skill 用于在本地 CLI / AI 代理中直接操作 Youmind，避免手工浏览器流程。

- 列出 / 查找 / 创建 boards
- 向 board 添加链接、上传文件
- 发起新会话、继续已有会话
- 通过对话触发图片和幻灯片生成
- 从聊天消息中提取生成产物（图片/幻灯片/文档）

## 适用对象

适用于有本地 shell 执行能力的 AI 代理和开发者（Codex、Claude Code、OpenClaw 等）。

## 运行模型

- 业务能力全部通过 API 实现。
- 浏览器仅用于认证初始化 / 刷新登录态。
- 本地认证与会话信息保存在 `data/` 目录。

## 环境要求

- Python `3.10+`
- Shell 执行权限
- 可访问 `youmind.com` 的网络

首次运行时，`scripts/run.py` 会自动创建 `.venv` 并安装依赖。

## 安装

### Claude Code / Codex

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone https://github.com/p697/youmind-skill.git
cd youmind-skill
```

### OpenClaw

```bash
mkdir -p ~/.openclaw/workspace/skills
cd ~/.openclaw/workspace/skills
git clone https://github.com/p697/youmind-skill.git
cd youmind-skill
```

## 快速开始（CLI）

### 1. 首次认证

```bash
python scripts/run.py auth_manager.py setup
python scripts/run.py auth_manager.py validate
```

### 2. 列出并创建 board

```bash
python scripts/run.py board_manager.py list
python scripts/run.py board_manager.py create --name "Demo Board"
python scripts/run.py board_manager.py find --query "demo"
```

### 3. 添加资料

```bash
python scripts/run.py material_manager.py add-link --board-id <board-id> --url "https://example.com"
python scripts/run.py material_manager.py upload-file --board-id <board-id> --file /path/to/file.pdf
```

### 4. 对话与生成

```bash
python scripts/run.py chat_manager.py create --board-id <board-id> --message "Summarize key points"
python scripts/run.py chat_manager.py generate-image --board-id <board-id> --prompt "Minimal product poster"
python scripts/run.py chat_manager.py generate-slides --board-id <board-id> --prompt "6-slide project update"
```

### 5. 提取生成产物

```bash
python scripts/run.py artifact_manager.py extract --chat-id <chat-id>
python scripts/run.py artifact_manager.py extract-latest --board-id <board-id>
python scripts/run.py artifact_manager.py extract --chat-id <chat-id> --include-raw-content
```

## 能力清单

### Boards

- `list`：列出所有 boards
- `find`：按关键词搜索 boards
- `get`：按 id 获取 board 详情
- `create`：创建新 board

```bash
python scripts/run.py board_manager.py list
python scripts/run.py board_manager.py find --query "roadmap"
python scripts/run.py board_manager.py get --id <board-id>
python scripts/run.py board_manager.py create --name "My Board" --prompt "Initialize this board"
```

### Materials

- 向 board 添加 URL
- 上传本地文件到 board
- 按 ids 查询 snips
- 列出 board picks

```bash
python scripts/run.py material_manager.py add-link --board-id <board-id> --url "https://example.com"
python scripts/run.py material_manager.py add-link --board-url "https://youmind.com/boards/<id>" --url "https://example.com"
python scripts/run.py material_manager.py upload-file --board-id <board-id> --file /path/to/file.pdf
python scripts/run.py material_manager.py get-snips --ids "<snip-id-1>,<snip-id-2>"
python scripts/run.py material_manager.py list-picks --board-id <board-id>
```

### Chat

- 创建会话并发送追问
- 获取历史与详情
- 将会话标记为已读
- 通过 prompt 生成图片/幻灯片

```bash
python scripts/run.py chat_manager.py create --board-id <board-id> --message "Summarize this board"
python scripts/run.py chat_manager.py send --board-id <board-id> --chat-id <chat-id> --message "Give next steps"
python scripts/run.py chat_manager.py history --board-id <board-id>
python scripts/run.py chat_manager.py detail --chat-id <chat-id>
python scripts/run.py chat_manager.py mark-read --chat-id <chat-id>
python scripts/run.py chat_manager.py generate-image --board-id <board-id> --prompt "Blue AI poster"
python scripts/run.py chat_manager.py generate-slides --board-id <board-id> --prompt "Project review deck"
```

### Artifacts

`artifact_manager.py` 会解析 chat detail 中 assistant 的 tool block：

- `image_generate`：返回图片 URLs 和 media ids
- `slides_generate`：返回每页幻灯片的图片 URLs 和 media ids
- `write`：返回文档 page id、内容预览（加 `--include-raw-content` 可拿原始内容）

## 代理交互示例

你可以直接对代理说：

- “列出我所有的 Youmind boards”
- “找下名字里有 roadmap 的 board”
- “创建一个叫 GTM Plan 的 board”
- “把这个链接加到 board <id>：https://example.com”
- “在 board <id> 里生成一张极简海报图”
- “在 board <id> 里生成一份季度汇报 slides”
- “提取 board <id> 最近一次生成结果”

## 项目结构

```text
SKILL.md
scripts/
  run.py
  auth_manager.py
  api_client.py
  board_manager.py
  material_manager.py
  chat_manager.py
  artifact_manager.py
  ask_question.py
  cleanup_manager.py
  setup_environment.py
references/
  api_reference.md
  integration_api_discovery.md
  integration_plan_from_live_product.md
  troubleshooting.md
data/ (本地生成)
```

## 当前限制

- Youmind 后端 API 变更时，接口字段可能漂移
- 登录态可能过期，需要执行 `auth_manager.py reauth`
- 幻灯片生成目前返回的是每页图片资产，不是直接 `.pptx` 下载链接

## 排障

```bash
python scripts/run.py auth_manager.py status
python scripts/run.py auth_manager.py validate
python scripts/run.py auth_manager.py reauth
```

参考文档：

- `references/api_reference.md`
- `references/troubleshooting.md`

## 安全说明

- `data/` 目录包含会话/认证信息，禁止提交到代码仓库
- 如组织要求隔离，请使用专门的自动化账号

## License

MIT（见 `LICENSE`）
