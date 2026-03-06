---
name: feishu-send-message
description: |
  通过 API 向飞书用户发送消息。当你需要通过手机号或任意用户 ID（open_id、user_id、union_id）向飞书用户发送消息时使用。自动尝试所有 ID 类型以找到有效的那个。

  **新增**：消息长度指南和长内容多部分发送最佳实践！
---

# 飞书消息发送工具

单个工具 `feishu_send_message`，用于向飞书用户发送消息。

## ⚠️ 关键：正确用法

**这是一个 Python 脚本，不是 JSON 工具调用。**

### 命令行用法（正确）：
```bash
python send_message.py <标识符> <消息>

# 示例：
python send_message.py "+8613560824490" "你好！"
python send_message.py "3b3ee7d1" "天气预报"
python send_message.py "ou_xxx" "你的消息"
```

### ❌ 错误（会失败）：
```bash
python send_message.py --json-file message.json    # 不支持 --json-file！
python send_message.py --action send xxx           # 不支持 --action！
```

脚本接受**恰好 2 个位置参数**：
1. `identifier` - 手机号或用户 ID（open_id/user_id/union_id）
2. `message` - 要发送的文本消息

## 功能说明

1. 从 OpenClaw 配置读取飞书凭证
2. 自动获取 tenant_access_token
3. 支持多种用户 ID 格式（手机号、open_id、user_id、union_id）
4. 自动尝试所有可用的 ID 类型以找到有效的那个
5. 通过飞书 API 发送文本消息

## 支持的标识符格式

- **手机号**：`+8613560824490` 或 `13560824490`
- **open_id**：`ou_xxx`（当前应用中的用户 ID）
- **user_id**：`ou_xxx`（飞书中的企业用户 ID）
- **union_id**：`on_xxx`（跨应用的用户 ID）

**智能查找顺序**：
1. **本地配置优先**（`~/.openclaw/workspace/configs/feishu-users.json`）- 最快，无需 API 调用
2. **手机号查找** - 调用 API 获取所有 ID，然后尝试每个
3. **直接 ID** - 尝试该 ID，然后回退到其他类型

## 前置条件

从 `~/.openclaw/openclaw.json`：
- `appId`：飞书应用 ID（如 `cli_a98251e3d1f8900c`）
- `appSecret`：飞书应用密钥
- `domain`：（可选）API 域名 - `feishu`（中国版）或 `lark`（国际版）

首次查找后，用户 ID 会保存到 `~/.openclaw/workspace/configs/feishu-users.json`。

## API 端点

1. **获取 tenant_access_token**：
   ```
   POST https://open.{domain}/open-apis/auth/v3/tenant_access_token/internal
   ```

2. **通过手机号获取用户 ID**：
   ```
   POST https://open.{domain}/open-apis/contact/v3/users/batch_get_id
   ```

3. **发送消息**：
   ```
   POST https://open.{domain}/open-apis/im/v1/messages?receive_id_type={user_id|union_id|open_id}
   ```

## 消息类型

### 发送富文本消息（推荐 ✅）
用于格式化的消息。支持：
- ✅ 标题：`# 标题`
- ✅ 链接：`[文本](链接)`
- ✅ 表情符号：原样保留
- ✅ 换行：分隔段落
- ✅ 列表：`- 事项`

**示例**：
```bash
# 卡片格式 ✅
python send_message.py "+8613560824490" "# 🌤️ 天气通知

东莞天气预报

- 天气：多云 ☁️
- 气温：12-22℃

详情请查看 [天气预报](https://weather.com.cn)

祝你有美好的一天！"
```

### 发送纯文本消息
用于简单消息。支持：
- ✅ 换行（`\n`）
- ✅ 表情符号（🌤️ ☁️ 😊）

**示例**：
```bash
# 简单消息
python send_message.py "+8613560824490" "✅ 任务完成！
感谢你的使用～"
```

### 卡片格式支持的功能

| 功能 | 支持 |
|------|------|
| 标题 `#` | ✅ |
| 链接 `[文本](链接)` | ✅ |
| 表情符号 | ✅ |
| 换行 | ✅ |
| 列表 `-` | ✅ |
| **粗体** `**text**` | ❌ 不支持 |
| *斜体* `*text*` | ❌ 不支持 |
| 代码 `` `code` `` | ❌ 不支持 |

### 自动检测
脚本自动选择正确的格式：
- 当检测到 `# ` 或 `](` 时使用 `post` 格式
- 纯消息使用 `text` 格式

## 配置

无需额外配置 - 自动从 OpenClaw 配置读取。

## 错误处理

- **缺少凭证**：返回错误
- **无效标识符**：尝试检测并使用正确格式
- **API 错误**：自动尝试其他 ID 类型
- **最终失败**：返回带详细信息的错误

## 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| "id not exist" | 用户不在应用可见范围 | 将用户添加到应用的可见范围 |
| "invalid user_id" | ID 类型错误 | 改用手机号 |
| 权限被拒绝 | 缺少机器人权限 | 在飞书控制台添加 `im:message:send_as_bot` |
| `Invalid ids: [--json-file]` | 参数格式错误 | 使用位置参数：`python script.py <id> <msg>` |
| HTTP 400 + `example value is {ou_xxx}` | open_id 格式无效 | 确认 ID 是该应用正确的用户 ID |
| HTTP 400（无具体错误） | 消息过长 | 将内容拆分为多条消息 |

## 使用示例

**发送天气卡片格式消息**（推荐）：
```bash
python send_message.py "+8613560824490" "# 🌤️ 东莞天气预报

更新于：2月7日 05:30

详细预报：
- 天气：多云 ☁️
- 气温：12℃ ~ 22℃
- 风力：无持续风向 <3级

小贴士：
早晚温差大，记得添衣哦~ 😊

查看详情 [天气预报](https://weather.com.cn)"
```

**发送简单消息**：
```bash
python send_message.py "+8613560824490" "你好，来自 OpenClaw！"
```

**发送带标题和链接的消息**：
```bash
python send_message.py "+8613560824490" "# 重要通知
这是标题内容
详见链接：[天气预报](https://weather.com.cn)"
```

**直接发送至 ID**：
```bash
python send_message.py "ou_9a013a756733f6910ebd9e3a1fe350fb" "你好！"
```

## ⚠️ 重要：消息长度限制

**飞书消息限制**：
- **文本消息**：无严格限制，但建议 < 5000 字符
- **富文本（post）**：建议总共 < 20000 字符
- **如果消息太长**：飞书 API 可能返回 HTTP 400 或截断

**长内容最佳实践**：

1. **拆分为多条消息**
   ```bash
   # 第1部分
   python send_message.py "3b3ee7d1" "# 报告 - 第1部分（共3部分）
   ...内容...
   （待续...）"

   # 第2部分（确认收到后）
   python send_message.py "3b3ee7d1" "# 报告 - 第2部分
   ...更多内容...
   （待续...）"
   ```

2. **使用文件作为内容来源**
   ```bash
   # 从文件读取（避免 CLI 参数问题）
   python send_message.py "3b3ee7d1" "$(cat long_message.txt)"
   ```

3. **发送前检查字符数**
   - 如果内容 > 3000 字符，考虑拆分
   - 使用 `wc -c` 或 `Measure-Object -Line` 检查长度

## 🐛 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 消息被截断 | 太长 | 拆分为多条消息 |
| 特殊字符错误 | CLI 引号问题 | 使用文件输入或更简单的文本 |
| "id not exist" | 用户不在应用可见范围 | 将用户添加到应用可见范围 |
| "invalid user_id" | ID 类型错误 | 改用手机号 |
| 权限被拒绝 | 缺少机器人权限 | 在飞书控制台添加 `im:message:send_as_bot` |
| HTTP 400 | 消息过长 | 拆分内容或减少格式 |

- `feishu.cn` - 中国版（默认）
- `larksuite.com` - 国际版

通过配置中的 `channels.feishu.domain` 或 `channels.feishu.accounts.main.domain` 设置。
