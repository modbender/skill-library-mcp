# 🏢 飞书办公套件

*Feishu/Lark Office Toolkit — 让 Agent 成为你的飞书办公助手*

基于飞书开放平台 API 的全面集成工具包，覆盖日常办公六大核心场景。安装本技能后，你的 Agent 就能帮你预约会议室、发送消息、发起审批、操作多维表格、查询通讯录和管理考勤。

## ✨ 功能亮点

| 模块 | 能力 | 示例指令 |
|------|------|----------|
| 📅 日历 | 日程 CRUD、会议室预约、忙闲查询 | "帮我预约明天下午的8楼大会议室" |
| 💬 消息 | 文本/富文本/卡片消息发送、回复 | "给产品组群发版本发布通知" |
| ✅ 审批 | 发起/查询/同意/拒绝/转交审批 | "帮我发起一个出差审批" |
| 📊 多维表格 | 表格创建、记录增删改查 | "在项目跟踪表中新增一条任务" |
| 👥 通讯录 | 用户/部门查询、组织架构浏览 | "查一下市场部有哪些成员" |
| ⏰ 考勤 | 打卡记录、补卡查询、考勤组管理 | "查看我这周的打卡记录" |

## 📦 安装

```bash
claw skill install official/feishu-toolkit
```

或在 AI IDE（Cursor / Copilot / Windsurf / Trae 等）中：

```bash
curl -sL "https://backend.clawd.org.cn/api/skills/official%2Ffeishu-toolkit/install.sh" | sh
```

## ⚙️ 配置

### 1. 创建飞书应用

前往 [飞书开发者后台](https://open.feishu.cn/app) 创建自建应用，开启**机器人能力**，并根据所需模块申请对应 API 权限。

### 2. 设置环境变量

```bash
export FEISHU_APP_ID="your-app-id"
export FEISHU_APP_SECRET="your-app-secret"
```

| 变量 | 必填 | 说明 |
|------|------|------|
| `FEISHU_APP_ID` | ✅ | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用 App Secret |
| `FEISHU_APPROVAL_CODES` | 否 | 常用审批类型映射（JSON） |

### 3. 启动服务

```bash
cd server/
uv venv && uv pip install -e ".[dev]"
uv run --env-file .env uvicorn feishu_toolkit.main:app --host 127.0.0.1 --port 8002
```

### 4. 验证

```bash
curl http://127.0.0.1:8002/ping
# {"message": "pong"}
```

## 🔐 权限清单

| 模块 | 权限标识 | 说明 |
|------|----------|------|
| 日历 | `calendar:calendar` | 读写日历及日程 |
| 日历 | `vc:room:readonly` | 查询会议室 |
| 消息 | `im:message:send_as_bot` | 发送消息 |
| 审批 | `approval:approval` | 读写审批信息 |
| 审批 | `approval:task` | 审批人操作 |
| 多维表格 | `bitable:app` | 读写多维表格 |
| 多维表格 | `drive:drive` | 访问云空间 |
| 通讯录 | `contact:contact.base:readonly` | 读取通讯录 |
| 考勤 | `attendance:task:readonly` | 导出打卡数据 |

> 💡 在飞书开发者后台 → 权限管理中，将 **通讯录权限范围** 设为「全部成员」或指定部门，否则无法查询到用户信息。

## 📖 详细文档

- [日历与会议室](references/calendar.md)
- [消息](references/messaging.md)
- [审批](references/approval.md)
- [多维表格](references/bitable.md)
- [通讯录](references/contacts.md)
- [考勤](references/attendance.md)

## 🔗 相关资源

- [飞书开放平台](https://open.feishu.cn/)
- [飞书开发者文档](https://open.feishu.cn/document/)
- [API 调试台](https://open.feishu.cn/api-explorer)
