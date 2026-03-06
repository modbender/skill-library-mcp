# 飞书日历 API 调用示例
# 获取今天的日程

## 步骤说明

### 1. 获取 Access Token

使用 web_fetch 工具调用飞书认证接口：

```javascript
{
  "url": "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "app_id": "cli_xxxxxxxxxxxx",
    "app_secret": "xxxxxxxxxxxxx"
  }
}
```

### 2. 从响应中提取 tenant_access_token

返回格式：
```json
{
  "code": 0,
  "msg": "ok",
  "tenant_access_token": "t-xxx",
  "expire": 7200
}
```

### 3. 获取日历列表

```javascript
{
  "url": "https://open.feishu.cn/open-apis/calendar/v4/calendars?page_size=100",
  "headers": {
    "Authorization": "Bearer t-xxx"
  }
}
```

### 4. 获取特定日历的事件

```javascript
{
  "url": "https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events?start_time=2026-03-01T00:00:00+08:00&end_time=2026-03-01T23:59:59+08:00",
  "headers": {
    "Authorization": "Bearer t-xxx"
  }
}
```

## 响应格式

日历列表示例：
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "calendar_list": [
      {
        "calendar_id": "feishu.cn_xxx",
        "summary": "我的日历",
        "description": "",
        "is_primary": true
      }
    ]
  }
}
```

事件列表示例：
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "items": [
      {
        "event_id": "xxx",
        "summary": "会议标题",
        "description": "会议描述",
        "start_time": {
          "timestamp": "1709251200",
          "timezone": "Asia/Shanghai"
        },
        "end_time": {
          "timestamp": "1709254800",
          "timezone": "Asia/Shanghai"
        },
        "location": {
          "name": "会议室"
        }
      }
    ]
  }
}
```

## 注意事项

1. Token 需要提取 `tenant_access_token` 字段
2. 时间戳是 Unix 时间戳（秒）
3. 主日历的 `is_primary` 为 true
4. 需要处理分页（如果有大量事件）
