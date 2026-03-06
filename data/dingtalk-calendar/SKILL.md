---
name: dingtalk-calendar
description: 钉钉日程管理（创建日程、查询闲忙、会议室预订）。使用 mcporter CLI 连接钉钉 MCP server 执行日程管理、日程查询、会议室预订等操作。使用场景：日程创建管理、会议预订、查询他人闲忙、会议室预约等。
---

# 钉钉日程管理

使用 `mcporter` CLI 调用钉钉日历 MCP 创建和管理日程。

## 前置要求

### 安装 mcporter CLI

本技能依赖 `mcporter` 工具，使用前请先安装：

```bash
# 使用 npm 安装
npm install -g mcporter

# 或使用 bun 安装
bun install -g mcporter
```

验证安装：
```bash
mcporter --version
```

### 配置 MCP Server

本技能需要配置两个 MCP 服务：**钉钉日历** 和 **钉钉通讯录**。

**步骤一：获取 Streamable HTTP URL**

1. 访问钉钉 MCP 广场：https://mcp.dingtalk.com
2. 搜索 **钉钉日历**，点击进入服务详情页
3. 在页面右侧找到 `Streamable HTTP URL`，点击复制按钮
4. 同样的方法，获取 **钉钉通讯录** 的 URL

**步骤二：使用 mcporter 配置 MCP 服务**

```bash
# 添加钉钉日历 MCP 服务
mcporter config add dingtalk-calendar --url "这里粘贴钉钉日历的URL"

# 添加钉钉通讯录 MCP 服务  
mcporter config add dingtalk-contacts --url "这里粘贴钉钉通讯录的URL"
```

**步骤三：验证配置**

```bash
# 查看已配置的服务
mcporter config list

# 测试连接（列出可用工具）
mcporter call dingtalk-calendar list_tools --output json
mcporter call dingtalk-contacts list_tools --output json
```

### 基本命令模式

所有操作通过 `mcporter call dingtalk-calendar <tool>` 执行：

```bash
# 创建日程
mcporter call dingtalk-calendar create_calendar_event \
  --args '{"summary":"会议","startDateTime":"2026-02-28T14:00:00+08:00","endDateTime":"2026-02-28T15:00:00+08:00"}' \
  --output json

# 查询日程
mcporter call dingtalk-calendar list_calendar_events \
  --args '{"startTime":1738128000000,"endTime":1738214400000}' \
  --output json

# 查询闲忙
mcporter call dingtalk-calendar query_busy_status \
  --args '{"userIds":["userId1"],"startTime":1738128000000,"endTime":1738214400000}' \
  --output json
```

## 核心工具

### 1. 创建日程

```bash
# 基本创建
mcporter call dingtalk-calendar create_calendar_event \
  --args '{
    "summary": "项目评审会议",
    "startDateTime": "2026-02-28T14:00:00+08:00",
    "endDateTime": "2026-02-28T15:00:00+08:00",
    "description": "讨论 Q1 进度",
    "attendees": ["userId1", "userId2"]
  }' \
  --output json
```

**参数说明：**
| 参数 | 必填 | 说明 |
|------|------|------|
| `summary` | ✅ | 日程标题（最长 2048 字符） |
| `startDateTime` | ✅ | 开始时间（ISO-8601 格式，如 `2026-02-28T14:00:00+08:00`） |
| `endDateTime` | ✅ | 结束时间（ISO-8601 格式） |
| `description` | ❌ | 日程描述（最长 5000 字符） |
| `attendees` | ❌ | 参与人 userId 列表（最多 500 人） |

### 2. 查询日程列表

```bash
# 查询指定时间范围的日程
mcporter call dingtalk-calendar list_calendar_events \
  --args '{
    "startTime": 1738128000000,
    "endTime": 1738214400000
  }' \
  --output json
```

### 3. 查询他人闲忙

```bash
mcporter call dingtalk-calendar query_busy_status \
  --args '{
    "userIds": ["userId1", "userId2"],
    "startTime": 1738128000000,
    "endTime": 1738214400000
  }' \
  --output json
```

### 4. 查询空闲会议室

```bash
mcporter call dingtalk-calendar query_available_meeting_room \
  --args '{
    "startTime": "1738128000000",
    "endTime": "1738131600000"
  }' \
  --output json
```

### 5. 为日程添加会议室

```bash
mcporter call dingtalk-calendar add_meeting_room \
  --args '{
    "eventId": "日程ID",
    "roomIds": ["会议室ID1"]
  }' \
  --output json
```

### 6. 更新日程

```bash
mcporter call dingtalk-calendar update_calendar_event \
  --args '{
    "eventId": "日程ID",
    "summary": "新标题",
    "description": "新描述"
  }' \
  --output json
```

### 7. 删除日程

```bash
mcporter call dingtalk-calendar delete_calendar_event \
  --args '{"eventId": "日程ID"}' \
  --output json
```

## 通讯录工具

### 搜索用户

```bash
mcporter call dingtalk-contacts search_user_by_key_word \
  --args '{"keyWord": "张三"}' \
  --output json
```

### 获取用户详情

```bash
mcporter call dingtalk-contacts get_user_info_by_user_ids \
  --args '{"user_id_list": ["userId1", "userId2"]}' \
  --output json
```

## 常用时间格式

```python
import time
from datetime import datetime

# 获取当前时间戳（毫秒）
int(time.time() * 1000)

# 时间戳转 ISO 8601
datetime.fromtimestamp(1738128000000 / 1000).strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ISO 8601 转时间戳（毫秒）
int(datetime.fromisoxt("2026-02-28T14:00:00+08:00").timestamp() * 1000)
```

## 使用示例

### 创建会议并预订会议室

```bash
# 1. 查询14:00-15:00的空闲会议室
mcporter call dingtalk-calendar query_available_meeting_room \
  --args '{"startTime":"1738128000000","endTime":"1738131600000"}' \
  --output json

# 2. 创建日程（假设获取到会议室ID: room123）
mcporter call dingtalk-calendar create_calendar_event \
  --args '{
    "summary": "周会",
    "startDateTime": "2026-02-28T14:00:00+08:00",
    "endDateTime": "2026-02-28T15:00:00+08:00"
  }' \
  --output json

# 3. 添加会议室（假设日程ID: event123）
mcporter call dingtalk-calendar add_meeting_room \
  --args '{"eventId":"event123","roomIds":["room123"]}' \
  --output json
```
