---
name: security-audit-hand
version: 1.0.0
description: 自主安全审计 - 定期检查系统安全、发现风险、生成报告
runtime: prompt_only
---

# Security Audit Hand - 自主安全审计

## 🎯 核心功能

自主定期安全检查：
- 系统漏洞扫描
- 配置审计
- 权限检查
- 日志分析
- 风险报告

**灵感来源**: OpenFang 16 层安全模型

---

## 🛡️ 审计框架 (基于 OpenFang)

### 16 层安全检查

| # | 检查项 | OpenFang 实现 | 我的实现 |
|---|--------|--------------|---------|
| 1 | 沙箱隔离 | WASM 双计量 | exec 允许列表 |
| 2 | 审计追踪 | Merkle 哈希链 | 日志文件 |
| 3 | 污点追踪 | 信息流标签 | 敏感数据扫描 |
| 4 | 身份签名 | Ed25519 | ⏳ 待实现 |
| 5 | SSRF 防护 | 私有 IP 阻止 | URL 白名单 |
| 6 | 秘密零化 | Zeroizing | ⏳ 待实现 |
| 7 | 双向认证 | HMAC-SHA256 | Token 认证 |
| 8 | 能力门控 | RBAC | 工具配置文件 |
| 9 | 安全头 | CSP/HSTS | N/A |
| 10 | 端点脱敏 | 最小化信息 | ✅ 已实现 |
| 11 | 进程沙箱 | env_clear | ✅ 已实现 |
| 12 | 注入扫描 | 提示词检测 | ✅ 已实现 |
| 13 | 循环守卫 | SHA256 检测 | ✅ 已实现 |
| 14 | 会话修复 | 7 阶段验证 | ✅ 已实现 |
| 15 | 路径遍历 | 规范化 + 符号链接 | ✅ 已实现 |
| 16 | 限流 | GCRA | ⏳ 待实现 |

---

## 🔍 审计流程 (7 阶段)

### Phase 1: 状态恢复
```
1. memory_recall `security_audit_state`
2. 读取历史报告 `security_reports/`
3. 加载基线配置 `security_baseline.json`
```

### Phase 2: 系统信息收集
```bash
# 系统信息
uname -a
whoami
pwd
df -h
free -h

# 网络信息
netstat -tlnp
curl ifconfig.me

# OpenClaw 状态
openclaw gateway status
openclaw --version
```

### Phase 3: 配置审计
```json
检查 ~/.openclaw/openclaw.json:
- [ ] auth.token 是否设置
- [ ] gateway.bind 是否安全 (loopback/lan)
- [ ] tools.deny 是否配置
- [ ] session.dmScope 是否安全
- [ ] 敏感信息是否明文
```

### Phase 4: 权限检查
```bash
# 文件权限
ls -la ~/.openclaw/
ls -la ~/.openclaw/workspace/

# API Key 权限
cat ~/.openclaw/.api-keys.md | grep -E "sk-|nvapi-"

# 进程权限
ps aux | grep openclaw
```

### Phase 5: 日志分析
```bash
# 检查异常日志
grep -i "error\|fail\|unauthorized" /tmp/openclaw/*.log

# 检查频繁错误
grep -c "error" /tmp/openclaw/openclaw-*.log

# 检查敏感信息泄露
grep -E "sk-[a-zA-Z0-9]+" /tmp/openclaw/*.log
```

### Phase 6: 风险评估
```
每个风险评分 (0-100):
- 严重性：+40 (高/中/低)
- 可能性：+30 (高/中/低)
- 影响范围：+20 (系统/应用/数据)
- 可修复性：+10 (易/中/难)

风险等级:
- 🔴 高危：≥80 分
- 🟠 中危：50-79 分
- 🟡 低危：<50 分
```

### Phase 7: 生成报告
```markdown
# 安全审计报告

## 执行摘要
- 审计时间：[日期]
- 发现风险：N 个 (🔴X 🟠Y 🟡Z)
- 整体安全评分：X/100

## 发现的风险

### 🔴 高危风险 1: [名称]
**描述**: [详细说明]
**影响**: [可能的后果]
**修复建议**: [具体步骤]
**优先级**: 立即修复

### 🟠 中危风险 2: [名称]
...

## 安全评分趋势
[与历史审计对比]

## 修复计划
[按优先级排序的待办事项]
```

---

## 📊 检查清单

### 🔐 认证安全
- [ ] API Key 是否使用环境变量
- [ ] Token 是否定期轮换
- [ ] 是否启用双因素认证
- [ ] 密码是否足够复杂

### 🔒 数据安全
- [ ] 敏感文件是否加密
- [ ] 数据库是否加密
- [ ] 传输是否使用 HTTPS
- [ ] 备份是否安全

### 🛡️ 网络安全
- [ ] 防火墙是否开启
- [ ] 不必要端口是否关闭
- [ ] SSH 是否使用密钥认证
- [ ] 是否使用 VPN/Tailscale

### 📁 文件安全
- [ ] 敏感文件权限是否正确 (600)
- [ ] 是否有世界可读文件
- [ ] 是否有 SUID/SGID 文件
- [ ] 临时文件是否清理

### 🧩 应用安全
- [ ] OpenClaw 是否最新版本
- [ ] Skills 是否来自可信源
- [ ] 是否配置工具黑名单
- [ ] 是否启用会话维护

---

## 📋 报告模板

```markdown
# 安全审计报告

**审计日期**: 2026-03-02
**审计范围**: OpenClaw 系统 + 服务器配置
**审计工具**: security-audit-hand v1.0

---

## 执行摘要

| 指标 | 值 |
|------|------|
| 整体安全评分 | 75/100 |
| 发现风险数 | 5 个 |
| 🔴 高危 | 0 个 |
| 🟠 中危 | 2 个 |
| 🟡 低危 | 3 个 |
| 上次审计 | 2026-02-26 |

---

## 发现的风险

### 🟠 中危风险 1: API Key 明文存储

**文件**: `~/.openclaw/openclaw.json`

**问题**: API Key 以明文形式存储在配置文件中

**影响**: 如果配置文件泄露，攻击者可使用 API Key

**修复建议**:
```bash
# 1. 使用环境变量
export DASHSCOPE_API_KEY="sk-xxx"

# 2. 或使用加密存储
openclaw secrets add dashscope_api_key

# 3. 修改配置文件
{
  "models": {
    "providers": {
      "dashscope": {
        "apiKey": "${DASHSCOPE_API_KEY}"
      }
    }
  }
}
```

**优先级**: 本周内修复

---

### 🟠 中危风险 2: Gateway 绑定到 LAN

**配置**: `gateway.bind = "lan"`

**问题**: Gateway 监听所有网络接口 (0.0.0.0)

**影响**: 同一网络内的设备可访问 Gateway

**修复建议**:
```json5
// 如果不需要远程访问
{
  gateway: {
    bind: "loopback"  // 仅监听 127.0.0.1
  }
}

// 如果需要远程访问，使用 Tailscale
{
  gateway: {
    bind: "lan",
    tailscale: {
      mode: "on"
    }
  }
}
```

**优先级**: 本周内修复

---

### 🟡 低危风险 1: 未配置工具黑名单

**问题**: `tools.deny` 未配置

**影响**: 默认允许所有工具，可能误用危险工具

**修复建议**:
```json5
{
  tools: {
    deny: ["group:runtime"],  // 禁止 exec/bash
  }
}
```

---

## 安全评分趋势

```
2026-02-26: 70/100
2026-03-02: 75/100 (+5)
```

**改进**:
- ✅ 配置了会话维护
- ✅ 启用了循环检测
- ⏳ 待修复：API Key 存储

---

## 修复计划

### 立即修复 (本周)
- [ ] API Key 改用环境变量
- [ ] Gateway 绑定改为 loopback

### 短期修复 (本月)
- [ ] 配置工具黑名单
- [ ] 启用 Tailscale 远程访问
- [ ] 配置定期安全审计

### 长期改进 (下季度)
- [ ] 实现 Merkle 审计日志
- [ ] 添加污点追踪
- [ ] 实现秘密零化

---

## 附录

### 审计命令
```bash
openclaw security audit
openclaw doctor
openclaw gateway status --deep
```

### 参考文档
- OpenFang Security Model: 16 layers
- OpenClaw Security: /gateway/security
- Server Hardening: /skills/healthcheck
```

---

## 🔧 配置选项

```toml
# 审计频率
audit_schedule = "weekly"  # daily/weekly/monthly

# 风险阈值
high_risk_threshold = 80
medium_risk_threshold = 50

# 报告设置
report_format = "markdown"
save_history = true
history_retention_days = 90

# 通知设置
notify_on_high_risk = true
notify_channel = "feishu"
```

---

## 📊 仪表盘指标

```json
{
  "security_audit_score": 75,
  "security_audit_last_date": "2026-03-02",
  "security_high_risks": 0,
  "security_medium_risks": 2,
  "security_low_risks": 3,
  "security_reports_generated": 1,
  "security_fixes_applied": 0
}
```

---

## 🎯 使用示例

### 激活 Hand
```
openfang hand activate security-audit
```

### 手动触发审计
```
帮我做一次全面的安全审计
```

### 查看安全评分
```
现在的安全评分是多少？
```

### 定期检查
```
每周一早上 9 点自动审计
```

---

## 📝 从 OpenFang 借鉴

1. ✅ 16 层安全模型 (完整采用)
2. ✅ 自主定期审计 (适配实现)
3. ✅ 风险评分系统 (直接采用)
4. ✅ 审计报告模板 (优化适配)
5. ✅ 仪表盘指标 (简化实现)

---

*此 Skill 受 OpenFang Security Model 启发创建*
