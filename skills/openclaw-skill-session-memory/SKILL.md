# 会话记忆技能

自动记录对话内容，按日期存储，支持快速关键字搜索回忆。

## 功能

- **自动记录**: 每次会话结束后自动保存对话内容到md文件
- **按日期存储**: 文件保存在 `memory/conversations/YYYY-MM-DD.md`
- **数据脱敏**: 自动过滤账号、密码、密钥、token等敏感信息
- **快速搜索**: 支持关键字正则匹配，无需加载整个文件

## 使用方式

### 自动记录（会话结束自动调用）

技能会在会话结束时自动调用，记录本次会话内容。

### 手动搜索回忆

```bash
# 搜索关键字（默认搜索最近7天）
python3 ~/.openclaw/workspace/skills/session-memory/search.py "关键词"

# 搜索指定天数
python3 ~/.openclaw/workspace/skills/session-memory/search.py "关键词" --days 30

# 列出最近所有会话文件
python3 ~/.openclaw/workspace/skills/session-memory/search.py --list
```

## 脱敏规则

自动替换以下内容：
- 邮箱: `xxx@xxx.com` → `[EMAIL]`
- 手机号: 11位数字 → `[PHONE]`
- API Key/Token: 包含 `key`、`token`、`secret`、`password` 的长字符串 → `[REDACTED]`
- 身份证号: 18位 → `[ID]`
- 银行卡号: 16-19位 → `[CARD]`
- IP地址: → `[IP]`

## 文件格式

```markdown
# 2026-03-02 会话记录

## 会话 1
- 时间: 19:13 - 19:20
- 渠道: feishu
- 消息数: 6

### 关键内容
- 用户询问焱焱是否在线
- 讨论会话丢失问题
- 要求创建会话记忆技能

### 消息摘要
- [19:13] 用户: "焱焱在吗"
- [19:15] 焱焱: "刚才应该是网络延迟"
...
```

## 技术实现

- Python脚本处理会话日志
- 正则表达式匹配敏感信息
- 按日期分割文件便于快速检索
