# 🔧 DNS 解析问题修复指南

## 🕵️ 问题原因

**FlClash 代理** 劫持了 DNS 请求，将阿里云 SMTP 域名解析到了错误的测试地址：

| 域名 | 正确 IP | 错误 IP |
|------|---------|---------|
| smtp.qiye.aliyun.com | 47.246.165.89 ✅ | 198.18.0.32 ❌ |
| smtp.mxhichina.com | 47.246.165.89 ✅ | 198.18.0.35 ❌ |

**198.18.0.0/15** 是 RFC 2544 网络测试地址段，不应该用于公共 DNS 解析。

---

## ✅ 解决方案

### 方案一：修复 hosts 文件（推荐）

运行修复脚本：

```bash
cd /Users/batype/.openclaw/workspace-work/skills/astock-daily
chmod +x fix-hosts.sh
./fix-hosts.sh
```

或手动执行：

```bash
sudo sh -c 'echo "47.246.165.89 smtp.qiye.aliyun.com" >> /etc/hosts'
sudo sh -c 'echo "47.246.165.89 smtp.mxhichina.com" >> /etc/hosts'
```

### 方案二：FlClash 规则配置

在 FlClash 配置中添加直连规则：

1. 打开 FlClash
2. 进入 **规则** 或 **配置**
3. 添加以下规则：

```yaml
rules:
  - DOMAIN,smtp.qiye.aliyun.com,DIRECT
  - DOMAIN,smtp.mxhichina.com,DIRECT
  - DOMAIN-SUFFIX,aliyun.com,DIRECT
```

或者在 UI 中：
1. 找到 **规则设置**
2. 添加域名规则：`smtp.qiye.aliyun.com` → **直连**
3. 添加域名规则：`smtp.mxhichina.com` → **直连**

### 方案三：临时关闭代理

在 FlClash 中：
1. 切换到 **直连模式** (Direct Mode)
2. 或暂时关闭代理
3. 测试 SMTP 发送
4. 恢复代理模式

---

## 🧪 验证修复

```bash
# 测试 DNS 解析
ping smtp.qiye.aliyun.com
# 应该显示 47.246.165.89，而不是 198.18.0.32

# 测试 SMTP 发送
cd /Users/batype/.openclaw/workspace-work/skills/astock-daily
source .env && node index.js
```

---

## 📊 当前配置

- SMTP 服务器：`smtp.mxhichina.com:465`
- 邮箱：`8@batype.com`
- 真实 IP：`47.246.165.89`

---

## 🔍 诊断命令

```bash
# 检查 hosts 文件
grep "aliyun\|mxhichina" /etc/hosts

# 测试 DNS 解析
nslookup smtp.qiye.aliyun.com

# 通过 DoH 查询真实 IP
curl -s 'https://dns.alidns.com/resolve?name=smtp.qiye.aliyun.com'

# 检查 FlClash 进程
ps aux | grep -i flclash
```
