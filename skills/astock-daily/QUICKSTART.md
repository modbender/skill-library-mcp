# 🚀 快速开始 - 3 步完成配置

## ✅ 步骤 1：填写邮箱密码

编辑 `.env` 文件：
```bash
cd /Users/batype/.openclaw/workspace-work/skills/astock-daily
vi .env
```

将 `YOUR_PASSWORD_HERE` 替换为你的邮箱密码：
```
SMTP_CONFIG={"host":"smtp.qiye.aliyun.com","port":465,"secure":true,"user":"8@batype.com","pass":"你的实际密码","from":"8@batype.com"}
```

保存退出（vi 按 `:wq`）

---

## ✅ 步骤 2：测试发送

```bash
cd /Users/batype/.openclaw/workspace-work/skills/astock-daily
source .env && node index.js
```

检查邮箱是否收到邮件！

---

## ✅ 步骤 3：设置定时任务

```bash
crontab -e
```

粘贴以下内容：
```
# A 股每日精选 - 每个交易日 9:30 运行
30 9 * * 1-5 cd /Users/batype/.openclaw/workspace-work/skills/astock-daily && /opt/homebrew/bin/node index.js >> /tmp/astock-daily.log 2>&1
```

保存退出。

---

## 🎉 完成！

- 📧 邮件会发送到：**8@batype.com**
- 💰 筛选条件：**20 元以下**股票
- ⏰ 运行时间：**周一至周五 9:30**
- 📊 查看日志：`tail -f /tmp/astock-daily.log`

---

## ❓ 遇到问题？

查看完整配置指南：`CONFIG.md`
