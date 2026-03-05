# iMessage Skill

## 简介

iMessage Skill 让 OpenClaw 能够通过 macOS 的 Messages 应用发送和接收 iMessage 消息。

**安全增强版特性**：
- ✅ 可信联系人名单
- ✅ 发送前确认机制
- ✅ 每日发送限制
- ✅ 安全事件日志
- ✅ **接收消息控制 OpenClaw**（远程控制）

## ⚠️ 安全警告

**重要提示**：
- 本 Skill 可以发送短信/iMessage，请谨慎使用
- 首次使用需要配置可信联系人名单
- 向非可信联系人发送消息需要手动确认
- **远程控制功能默认关闭**，需要手动启用并配置管理员
- 建议仅将常用联系人添加到可信名单
- 所有发送操作都会被记录到安全日志

## 系统要求

- **仅支持 macOS** - 需要 macOS 10.14 或更高版本
- **需要 Messages 应用** - 系统自带的 Messages 应用必须可用
- **需要辅助功能权限** - 首次使用需要授予终端/脚本编辑器辅助功能权限
- **iMessage 已登录** - 需要在 Messages 应用中登录 Apple ID

## 功能特性

### 消息发送
- 💬 **发送文本消息** - 向指定手机号或邮箱发送 iMessage
- 🖼️ **发送图片** - 发送图片文件给联系人

### 消息接收
- 📨 **查看最近消息** - 获取最近的聊天记录
- 👥 **联系人列表** - 查看最近的联系人

### 远程控制（新功能）
- 📱 **接收控制命令** - 通过 iMessage 控制 OpenClaw
- 🔐 **管理员权限** - 只有管理员可以执行控制命令
- 🛡️ **命令白名单** - 只允许执行指定命令
- 🚫 **命令黑名单** - 禁止执行危险命令

### 安全管理
- 🔒 **可信名单** - 管理可信联系人，免确认发送
- ✅ **发送确认** - 向非可信联系人发送前需要确认
- 📊 **发送限制** - 每日最多发送 100 条消息
- 📝 **安全日志** - 记录所有发送操作到 security.log
- 📋 **控制日志** - 记录所有控制命令到 control.log

## 安装

### 1. 安装 Skill

```bash
npx clawhub install imessage
```

### 2. 授予权限

首次使用时，系统会提示授予辅助功能权限：

1. 打开 **系统设置** → **隐私与安全性** → **辅助功能**
2. 添加并启用 **终端**（或你使用的脚本编辑器）
3. 确保 **Messages** 应用也在列表中

### 3. 确保 iMessage 已登录

打开 Messages 应用，确认已登录你的 Apple ID。

## 使用方法

### 可信联系人管理

```bash
# 添加可信联系人（免确认发送）
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py trust phone=+8613800138000

# 移除可信联系人
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py untrust phone=+8613800138000

# 查看所有可信联系人
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py list_trusted
```

### 管理员管理

```bash
# 添加管理员（可远程控制 OpenClaw）
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py admin phone=+8613800138000

# 移除管理员
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py unadmin phone=+8613800138000
```

### 远程控制管理

```bash
# 启用远程控制
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py enable_control

# 禁用远程控制
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py disable_control
```

### 发送文本消息

```bash
# 发送给可信联系人（无需确认）
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py send phone=+8613800138000 message="你好"

# 发送给非可信联系人（需要确认）
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py send phone=+8613900139000 message="测试消息"
# 系统会提示：是否继续发送? (yes/no):
```

### 发送图片

```bash
# 发送图片（同样需要安全检查）
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py send_image phone=+8613800138000 image=/Users/username/Pictures/photo.jpg
```

### 查看最近消息

```bash
# 查看所有最近消息
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py recent limit=10

# 查看特定联系人的消息
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py recent phone=+8613800138000 limit=5

# 检查并执行控制命令
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py recent check_control=true
```

### 查看联系人列表

```bash
# 获取最近联系人（显示可信和管理员状态）
python3 ~/.openclaw/workspace/skills/imessage/scripts/main.py contacts limit=20
```

## 远程控制功能

### 工作原理

1. **发送控制命令**：管理员发送以 `!` 开头的消息
2. **Skill 检测命令**：在获取消息时自动检测控制命令
3. **权限验证**：检查发送者是否是管理员
4. **执行命令**：执行允许的命令并回复结果

### 可用命令

管理员可以通过 iMessage 发送以下命令：

```
!status - 查看 OpenClaw 状态
!help - 显示帮助信息
!list - 列出已安装的 Skills
!info - 显示系统信息
!echo <消息> - 回显消息
```

### 使用示例

1. **管理员发送命令**：
   ```
   !status
   ```

2. **Skill 自动回复**：
   ```
   OpenClaw 状态
   [OpenClaw 状态输出]
   ```

### 安全机制

- **默认禁用**：远程控制功能默认关闭
- **管理员权限**：只有 admin_contacts 中的联系人可以执行命令
- **命令白名单**：只允许执行 allowed_commands 中的命令
- **命令黑名单**：禁止执行 blocked_commands 中的命令（如 delete、rm 等）
- **命令前缀**：必须以 `!` 开头才识别为控制命令

## 安全配置

编辑 `~/.openclaw/workspace/skills/imessage/config.json`：

```json
{
  "trusted_contacts": [
    "+8613800138000"
  ],
  "admin_contacts": [
    "+8613800138000"
  ],
  "require_confirmation": true,
  "max_daily_messages": 100,
  "enable_logging": true,
  "enable_remote_control": false,
  "allowed_commands": ["status", "help", "list", "info", "echo"],
  "blocked_commands": ["delete", "rm", "remove", "uninstall", "exec", "eval"],
  "command_prefix": "!"
}
```

### 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `trusted_contacts` | 可信联系人列表 | [] |
| `admin_contacts` | 管理员列表（可远程控制） | [] |
| `require_confirmation` | 是否需要发送确认 | true |
| `max_daily_messages` | 每日最大发送数 | 100 |
| `enable_logging` | 是否启用安全日志 | true |
| `enable_remote_control` | 是否启用远程控制 | false |
| `allowed_commands` | 允许的命令列表 | ["status", "help", "list", "info", "echo"] |
| `blocked_commands` | 禁止的命令列表 | ["delete", "rm", "remove", "uninstall"] |
| `command_prefix` | 命令前缀 | "!" |

## 安全机制说明

### 可信名单机制

1. **可信联系人**：添加到 `trusted_contacts` 的联系人，发送消息时无需确认
2. **非可信联系人**：不在名单中的联系人，发送前需要手动确认
3. **自动拒绝**：非交互式环境（如脚本）无法向非可信联系人发送

### 发送确认流程

```
发送请求 → 检查可信名单 → 是 → 直接发送
                ↓ 否
         交互式环境? → 是 → 提示确认 → 用户确认 → 发送
                ↓ 否
              拒绝发送
```

### 远程控制安全流程

```
接收消息 → 检测命令前缀 → 是 → 检查远程控制启用
                              ↓ 否
                         检查管理员权限
                              ↓ 否
                         检查命令黑名单
                              ↓ 是
                         检查命令白名单
                              ↓ 否
                         执行命令 → 发送回复
```

### 安全日志

所有操作记录在 `security.log`：

```json
{"timestamp": "2026-02-16 10:30:00", "user": "username", "event": "SEND_MESSAGE", "details": {"phone": "+8613800138000", "trusted": true}}
{"timestamp": "2026-02-16 10:35:00", "user": "username", "event": "ADD_ADMIN_CONTACT", "details": {"phone": "+8613800138000"}}
{"timestamp": "2026-02-16 10:40:00", "user": "username", "event": "REMOTE_CONTROL_ENABLED", "details": {}}
```

控制命令记录在 `control.log`：

```json
{"timestamp": "2026-02-16 10:45:00", "event": "CONTROL_COMMAND_EXECUTED", "details": {"phone": "+8613800138000", "command": "status", "success": true}}
```

## 故障排除

### "不在可信名单中，无法自动发送"
- 使用 `trust` 命令将联系人添加到可信名单
- 或在交互式环境中手动确认发送

### "您没有权限控制 OpenClaw"
- 该联系人不在 `admin_contacts` 列表中
- 使用 `admin` 命令添加管理员

### "远程控制功能未启用"
- 远程控制默认关闭
- 使用 `enable_control` 命令启用

### "已达到每日发送限制"
- 今日发送数量已达到 `max_daily_messages` 限制
- 请明天再试，或修改配置增加限制

### "无法访问 Messages 数据库"
- 检查是否授予了终端辅助功能权限
- 确保 Messages 应用已打开并登录

### "发送失败"
- 检查手机号/邮箱格式是否正确
- 确认 iMessage 服务已启用
- 检查网络连接

## 隐私声明

- 本 Skill 仅在本地操作，不会上传任何数据
- 消息内容仅存储在你的 Mac 上
- 需要你的明确授权才能访问 Messages 数据库
- 安全日志和控制日志仅保存在本地，不会外泄

## 版本信息

- **版本**: 1.0.2
- **作者**: MaxStorm Team
- **许可证**: MIT
- **源码**: https://github.com/maxstorm/imessage-skill

---

**注意**: 本 Skill 仅用于个人自动化用途，请遵守 Apple 的服务条款，不要用于发送垃圾信息。
