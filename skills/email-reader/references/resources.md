# 邮件管理参考资料

## himalaya 配置示例

### Gmail
```
--imap-host imap.gmail.com
--imap-port 993
--smtp-host smtp.gmail.com
--smtp-port 587
--username your@gmail.com
--password "app-password"
```

### QQ 邮箱
```
--imap-host imap.qq.com
--imap-port 993
--smtp-host smtp.qq.com
--smtp-port 587
--username your@qq.com
--password "auth-code"
```

## 常用命令速查

```bash
# 列出账户
himalaya envelope list accounts

# 列出最近邮件
himalaya list -w 50 | head -20

# 标记为已读
himalaya envelope mark <id> --seen

# 标记为重要
himalaya envelope mark <id> --flagged

# 删除邮件
himalaya envelope delete <id>

# 搜索邮件
himalaya search "keyword"

# 发送邮件（使用模板）
himalaya send \
  --from "you@example.com" \
  --to "recipient@example.com" \
  --subject "主题" \
  --body "内容"
```

## IMAP/SMTP 端口

| 服务 | IMAP | SMTP |
|------|------|------|
| Gmail | 993 | 587 |
| Outlook | 993 | 587 |
| QQ | 993 | 465/587 |
| 网易 | 993 | 465 |

## OAuth2 配置（Gmail）

1. 前往 Google Cloud Console
2. 创建 OAuth 2.0 凭据
3. 下载 JSON 文件
4. 使用 `--oauth2` 参数
