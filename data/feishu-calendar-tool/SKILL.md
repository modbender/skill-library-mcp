---
name: feishu-calendar-tool
description: 飞书日历管理工具 - 零配置，自动获取凭证和日历ID，支持创建、删除、查询日程
---

# 飞书日历管理工具 📅

简单高效的飞书日历事件管理工具 - **零配置启动！**

## ✨ 核心特性

- **零配置** - 自动从 `~/.openclaw/openclaw.json` 读取飞书凭证
- **自动发现** - 自动获取 user_id 和 calendar_id
- **智能缓存** - 凭证和配置缓存 24 小时
- **创建日程** - 支持创建飞书日程事件
- **删除日程** - 支持删除已创建的事件
- **查询日程** - 查看指定日期范围的日程

## 快速开始

### 零配置使用（推荐）⭐

**已配置飞书通道？无需任何配置，直接使用！**

```bash
# 创建日程
node bin/create-event.mjs \
  --title "团队会议" \
  --start "2026-02-10 14:00:00" \
  --end "2026-02-10 15:00:00"

# 查询日程
node bin/list-events.mjs

# 删除日程
node bin/delete-event.mjs --event-id "事件ID"
```

### 首次使用

如果你还没有配置飞书应用：

#### 1. 创建飞书应用

访问 [飞书开放平台](https://open.feishu.cn/app) 创建应用，获取：
- **App ID**
- **App Secret**

#### 2. 添加权限

在应用管理页添加以下权限：
- ✅ `calendar:calendar` - 读写日历
- ✅ `calendar:calendar:readonly` - 读取日历
- ✅ `contact:user.base:readonly` - 自动获取 user_id
- ✅ `contact:user.employee_id:readonly` - 读取员工目录

#### 3. 配置到 openclaw.json

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "channels": {
    "feishu": {
      "accounts": {
        "default": {
          "appId": "你的AppID",
          "appSecret": "你的AppSecret",
          "enabled": true
        }
      }
    }
  }
}
```

**完成！现在可以零配置使用了。**

## 使用方法

### 创建日程

```bash
node bin/create-event.mjs \
  --title "周会议" \
  --start "2026-02-10 17:00:00" \
  --end "2026-02-10 18:00:00" \
  --description "每周例会" \
  --location "会议室A"
```

**参数说明：**
- `--title` - 日程标题（必需）
- `--start` - 开始时间，格式：YYYY-MM-DD HH:MM:SS（必需）
- `--end` - 结束时间，格式：YYYY-MM-DD HH:MM:SS（必需）
- `--description` - 日程描述（可选）
- `--location` - 地点（可选）
- `--attendees` - 参与人，逗号分隔（可选）
- `--timezone` - 时区，默认 Asia/Shanghai（可选）

### 查询日程

```bash
# 查看未来 7 天的日程
node bin/list-events.mjs

# 查看指定日期范围
node bin/list-events.mjs \
  --start "2026-02-10" \
  --end "2026-02-17"
```

### 删除日程

```bash
node bin/delete-event.mjs --event-id "事件ID"
```

## 配置方式

### 自动查找顺序

1. **环境变量** - 如果已设置
2. **~/.openclaw/openclaw.json** - 推荐 ⭐
3. **~/openclaw/.secrets.env**
4. **~/.secrets.env**

## 验证配置

```bash
# 测试凭证加载
node bin/test-credentials.mjs

# 查看可用的日历
node bin/get-user-info.mjs
```

成功输出：
```
✅ Credentials loaded successfully!
Source: /home/user/.openclaw/openclaw.json
App ID: cli_xxxxxxxxxxxxx
```

## 自动发现功能

- **user_id** - 通过飞书 API 自动获取当前用户 ID
- **calendar_id** - 自动选择主日历（primary calendar）
- **缓存** - 结果缓存 24 小时，减少 API 调用

## 技术实现

- 使用飞书 Calendar v4 API
- 自动处理 access token 获取和刷新
- 智能错误重试机制
- 支持 Asia/Shanghai 时区

## 常见问题

### Q: 我已经配置了飞书通道，还需要重新配置吗？
A: **不需要！** 技能会自动读取 `openclaw.json` 中的凭证，直接使用即可。

### Q: 支持多个飞书账户吗？
A: 支持！在 `openclaw.json` 中配置多个账户，技能会优先使用 `default` 账户。

### Q: 如何查看我的日历 ID？
A: 运行 `node bin/get-user-info.mjs` 查看所有可用的日历。

### Q: 技能会修改我的 openclaw.json 吗？
A: **不会！** 技能只读取配置，从不修改。

## 相关链接

- [飞书开放平台](https://open.feishu.cn/app)
- [飞书日历 API 文档](https://open.feishu.cn/document/server-docs/docs/calendar-v4/event/create)

## 作者

小李子

## 许可证

MIT
