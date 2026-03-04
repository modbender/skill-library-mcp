[English](README.md) | 中文

# Task Sync

**滴答清单** 与 **Google Tasks** 双向同步工具，支持智能列表。

基于 [OpenClaw](https://openclaw.ai/) 技能构建，可通过 cron 自动运行或手动执行。

## 功能特性

- **双向列表同步**：Google 任务列表与滴答清单项目按名称自动匹配或创建
- **双向任务同步**：标题、完成状态、备注/内容
- **优先级映射**：滴答清单优先级映射为 Google 任务标题前缀（`[★]` 高优先级、`[!]` 中优先级）
- **智能列表**（单向，滴答清单 -> Google）：
  - **Today**：已过期 + 今日任务
  - **Next 7 Days**：未来一周任务
  - **All**：所有活跃任务（含日期）
- **日期策略**：防止 Google Calendar 出现重复任务
- **幂等运行**：可重复执行，不会产生重复数据

## 日期策略

Google Tasks 中带日期的任务会自动显示在 Google Calendar。为防止跨列表重复，日期处理如下：

| 列表类型 | Google 中是否保留日期 | 原因 |
|----------|:--------------------:|------|
| 常规列表 | 否 | 日期转发到滴答清单后从 Google 清除 |
| "All" 智能列表 | 是 | 作为 Calendar 唯一日期来源 |
| "Today" / "Next 7 Days" | 否 | 仅作为过滤视图 |

## 架构

```text
sync.py                        主同步脚本
utils/
  google_api.py                Google Tasks API 封装（分页、Token 自动刷新）
  ticktick_api.py              滴答清单 Open API 封装
scripts/
  setup_google_tasks.py        Google OAuth 授权设置
  setup_ticktick.py            滴答清单 OAuth 授权设置
config.json                    配置文件（Token 与数据路径）
data/sync_db.json              任务/列表映射数据库（自动生成）
data/sync_log.json             同步统计日志（自动生成）
e2e_test.py                    端到端测试（15 个用例）
```

### 同步流程

```text
1. 列表同步（双向）
   Google Lists <----------> TickTick Projects
   - 按名称匹配（不区分大小写）
   - "My Tasks" <-> "Inbox"（特殊映射）
   - 未匹配列表自动创建对应项

2. 任务同步（双向，按列表对）
   Google Tasks <----------> TickTick Tasks
   - 新任务双向同步
   - 完成状态双向传播
   - 日期：Google -> TickTick（转发后清除 Google 日期）
   - 优先级：TickTick -> Google（标题前缀）
   - 备注/内容在创建时同步

3. 智能列表（单向：TickTick -> Google）
   TickTick ---------------> Google "Today" / "Next 7 Days" / "All"
   - 不再匹配的任务会自动移除
```

## 安装配置

### 前置要求

- Python 3.10+
- 已启用 Tasks API 的 Google Cloud 项目
- 滴答清单开发者应用（[developer.ticktick.com](https://developer.ticktick.com/)）

### 1. 安装依赖

```bash
pip install google-auth google-auth-oauthlib google-api-python-client requests
```

### 2. 配置 Google Tasks

```bash
python scripts/setup_google_tasks.py
```

将 Google OAuth desktop client JSON 放到 `config/google_credentials.json`
（或设置 `GOOGLE_CREDENTIALS_FILE`），按提示完成授权。
Token 会写入 `config.json` 的 `google_token` 路径；未配置时默认写入 `data/google_token.json`。

### 3. 配置滴答清单

```bash
python scripts/setup_ticktick.py
```

先用 `config/ticktick_creds.json.example` 生成 `config/ticktick_creds.json`
（或设置 `TICKTICK_CREDENTIALS_FILE`），按提示完成授权。
Token 会写入 `config.json` 的 `ticktick_token` 路径；未配置时默认写入 `data/ticktick_token.json`。

### 4. 编辑 config.json

```json
{
  "google_token": "/path/to/google/token.json",
  "ticktick_token": "/path/to/ticktick/token.json",
  "sync_db": "/path/to/data/sync_db.json",
  "sync_log": "/path/to/data/sync_log.json",
  "ticktick_api_base": "https://api.ticktick.com/open/v1"
}
```

### 5. 运行

```bash
python sync.py
```

## 自动化

配置 cron 定时同步：

```bash
# 每 10 分钟执行一次
*/10 * * * * /path/to/python /path/to/sync.py >> /path/to/sync.log 2>&1
```

也可使用 OpenClaw 内置 cron 系统。

## 测试

项目包含基于真实 API 的端到端测试：

```bash
python e2e_test.py
```

## API 参考

- [Google Tasks REST API](https://developers.google.com/workspace/tasks/reference/rest)
- [TickTick Open API](https://developer.ticktick.com/)

## 许可证

MIT
