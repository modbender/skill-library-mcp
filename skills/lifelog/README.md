# LifeLog 生活记录系统

[English](./README_EN.md) | 中文

> ⚠️ **声明**：本技能及其文档由 AI 生成，仅供参改。

自动将日常生活记录到 Notion，支持智能日期识别和自动汇总分析。

## 功能特点

- 🤖 **智能日期识别** - 自动识别"昨天"、"前天"等日期，记录到对应日期
- 🔁 **补录标记** - 非当天记录的内容会标记为"🔁补录"
- 📝 **实时记录** - 随时记录生活点滴，自动保存到 Notion
- 🌙 **自动汇总** - 每天凌晨自动运行 LLM 分析，生成情绪状态，主要事件、位置、人员
- 🔍 **智能过滤** - 自动过滤纯工作指令、测试消息等不需要记录的内容

## 效果预览

![LifeLog Preview](./assets/preview.png)

## 快速开始

### 1. 安装

通过 ClawHub 安装：
```bash
clawhub install lifelog
```

或手动下载：
```bash
git clone https://github.com/421zuoduan/lifelog.git
```

### 2. 配置 Notion

1. **创建 Integration**
   - 访问 https://www.notion.so/my-integrations
   - 点击 **New integration**
   - 填写名称（如 "LifeLog"）
   - 复制生成的 **Internal Integration Token**

2. **创建 Database**
   - 在 Notion 中创建新 Database
   - 添加以下字段（全部为 rich_text 类型）：
     | 字段名 | 类型 | 说明 |
     |--------|------|------|
     | 日期 | title | 日期，如 2026-02-22 |
     | 原文 | rich_text | 原始记录内容 |
     | 情绪状态 | rich_text | LLM 分析后的情绪描述 |
     | 主要事件 | rich_text | LLM 分析后的事件描述 |
     | 位置 | rich_text | 地点列表 |
     | 人员 | rich_text | 涉及的人员 |
   - 点击 Database 右上角的 **...** → **Connect to** → 选择你的 Integration

3. **获取 Database ID**
   - URL 中提取：`https://notion.so/{workspace}/{database_id}?v=...`
   - database_id 是 32 位字符串（带 `-`）

4. **修改脚本配置**
   - 编辑 `scripts/` 目录下的脚本，替换：
     ```bash
     # ===== 配置区域 =====
     NOTION_KEY="你的Notion_API_Key"
     DATABASE_ID="你的Database_ID"
     # ====================
     ```

### 3. 使用方式

```bash
# 记录今天的事情
bash scripts/lifelog-append.sh "今天早上吃了油条"

# 记录昨天的事情（自动识别日期）
bash scripts/lifelog-append.sh "昨天去超市买菜了"

# 记录前天的事情
bash scripts/lifelog-append.sh "前天和朋友吃饭了"

# 记录具体日期的事情
bash scripts/lifelog-append.sh "2月22日和家人去爬山了"
```

### 4. 设置定时汇总（可选）

```bash
openclaw cron add \
  --name "LifeLog-每日汇总" \
  --cron "0 5 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "运行 LifeLog 每日汇总"
```

## 支持的日期表达

- 今天/今日/今儿 → 当天
- 昨天/昨日/昨儿 → 前一天
- 前天 → 前两天
- 明天/明儿 → 后一天
- 后天 → 后两天
- 具体日期：2026-02-22、2月22日

## 脚本说明

| 脚本 | 功能 | 使用示例 |
|------|------|----------|
| `lifelog-append.sh` | 实时记录用户消息 | `bash lifelog-append.sh "消息内容"` |
| `lifelog-daily-summary-v5.sh` | 拉取指定日期原文 | `bash lifelog-daily 2026-02-summary-v5.sh-22` |
| `lifelog-update.sh` | 写回分析结果 | `bash lifelog-update.sh "<page_id>" "<情绪>" "<事件>" "<位置>" "<人员>"` |

## 自动汇总工作流

1. 用户发送生活记录 → 调用 `lifelog-append.sh` → 写入 Notion 原文
2. 定时任务触发（每天5点）→ 调用 `lifelog-daily-summary-v5.sh` → 拉取昨日原文
3. LLM 分析原文内容 → 调用 `lifelog-update.sh` → 填充情绪状态、主要事件、位置、人员字段

## 过滤规则

系统会自动过滤以下内容，**不会**记录到 Notion：

| 类型 | 示例 |
|------|------|
| 纯工作指令 | "帮我写代码"、"部署服务"、"git push" |
| 测试消息 | "测试一下"、"试一下" |
| 系统消息 | "设置记录"、"配置Notion" |
| 太短的确认 | 单字或词（如"好"、"嗯"） |

**注意**：包含情绪表达的即便是工作相关也会记录，如"写了代码累死了"会被记录。

## 故障排除

### API 请求失败
- 检查 Notion API Key 是否正确
- 确保 Integration 已连接到 Database

### 日期识别不准确
- 确保使用支持的日期表达格式
- 检查系统时区是否正确

### 定时任务不运行
- 检查 cron 任务状态：`openclaw cron list`
- 查看任务运行日志：`openclaw cron runs --id <job_id>`

## 常见问题

**Q: 如何查看今天的记录？**
A: 在 Notion 中搜索今天的日期即可。

**Q: 可以同时记录多条消息吗？**
A: 可以，多次调用会自动追加到同一天的记录中。

**Q: 补录的内容和当天记录有什么区别？**
A: 补录的内容会在时间戳后标记"🔁补录"，方便区分。

## ClawHub

本技能已发布到 ClawHub：https://clawhub.com/s/lifelog

## License

MIT
