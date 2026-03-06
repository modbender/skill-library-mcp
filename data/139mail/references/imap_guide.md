# IMAP 操作指南

## IMAP 基础概念

IMAP（Internet Message Access Protocol）是一种邮件获取协议，允许客户端远程管理服务器上的邮件。

### 与 POP3 的区别

| 特性 | IMAP | POP3 |
|------|------|------|
| 邮件存储 | 服务器上 | 下载到本地后删除 |
| 多设备同步 | 支持 | 不支持 |
| 服务器管理 | 可创建文件夹、标记已读 | 只能下载 |

## 常用 IMAP 操作

### 1. 连接服务器

```python
import imapclient

server = imapclient.IMAPClient('imap.139.com', ssl=True)
server.login('username@139.com', 'password')
```

### 2. 选择文件夹

```python
server.select_folder('INBOX')  # 收件箱
server.select_folder('Sent Messages')  # 已发送
```

### 3. 搜索邮件

```python
# 搜索所有邮件
messages = server.search(['ALL'])

# 搜索未读邮件
messages = server.search(['UNSEEN'])

# 搜索来自某人的邮件
messages = server.search(['FROM', 'sender@example.com'])

# 搜索主题包含关键词
messages = server.search(['SUBJECT', '关键词'])
```

### 4. 获取邮件

```python
# 获取邮件头部
fetch_data = server.fetch([msg_id], ['BODY.PEEK[HEADER]'])

# 获取完整邮件
fetch_data = server.fetch([msg_id], ['BODY[]'])

# 获取已读/未读状态
flags = server.fetch([msg_id], ['FLAGS'])
```

### 5. 管理邮件

```python
# 标记为已读
server.add_flags([msg_id], ['\\Seen'])

# 标记为未读
server.remove_flags([msg_id], ['\\Seen'])

# 删除邮件
server.delete_messages([msg_id])
server.expunge()

# 移动邮件到其他文件夹
server.copy([msg_id], 'TargetFolder')
server.delete_messages([msg_id])
server.expunge()
```

### 6. 列出文件夹

```python
folders = server.list_folders()
for folder in folders:
    print(folder)
```

## 邮件标志（Flags）

- `\Seen` - 已读
- `\Answered` - 已回复
- `\Flagged` - 已标记（红旗）
- `\Deleted` - 已删除
- `\Draft` - 草稿

## 注意事项

1. **SSL/TLS 兼容性**：139邮箱使用较旧的 TLS 协议，可能需要使用兼容模式
2. **授权码**：必须使用授权码而非登录密码
3. **编码问题**：邮件主题和发件人可能需要解码（decode_header）
4. **性能考虑**：大量邮件时避免一次性获取所有邮件
