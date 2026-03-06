# 🔧 SMTP 问题解决方案

## ❌ 当前问题

你的网络环境 DNS 被重定向到测试网络（RFC 2544），导致：
- `smtp.mxhichina.com` → `198.18.0.35` (测试地址)
- `smtp.qiye.aliyun.com` → `198.18.0.32` (测试地址)

这不是密码或配置问题，是网络限制。

---

## ✅ 解决方案

### 方案一：使用系统邮件（当前可用）

技能已经配置为自动降级到 sendmail。如果 macOS 系统邮件已配置，邮件会正常发送。

**检查是否收到邮件**：查看邮箱 8@batype.com 是否有今天发送的测试邮件。

### 方案二：配置 hosts 文件（推荐）

手动指定 SMTP 服务器的真实 IP 地址：

```bash
# 获取真实 IP（在正常网络环境下）
ping smtp.mxhichina.com
# 假设得到：47.118.78.123

# 编辑 hosts 文件
sudo vi /etc/hosts

# 添加：
47.118.78.123 smtp.mxhichina.com
```

### 方案三：使用其他网络

切换到正常网络环境（如手机热点），SMTP 应该可以正常工作。

### 方案四：使用 QQ 邮箱转发

如果你有 QQ 邮箱，可以配置转发：

```bash
# 使用 QQ 邮箱 SMTP
export SMTP_CONFIG='{"host":"smtp.qq.com","port":465,"secure":true,"tls":{"rejectUnauthorized":false},"user":"your-qq@qq.com","pass":"授权码","from":"your-qq@qq.com"}'
```

---

## 📊 当前状态

| 项目 | 状态 |
|------|------|
| 数据获取 | ✅ 成功 |
| 邮件生成 | ✅ 成功 |
| SMTP 发送 | ❌ DNS 问题 |
| sendmail | ✅ 可用（需系统配置） |

---

## 🧪 测试系统邮件

```bash
echo "测试" | mail -s "测试邮件" 8@batype.com
```

如果收到邮件，说明系统邮件正常，技能可以直接使用！
