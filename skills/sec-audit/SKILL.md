# OpenClaw Security Audit Skill

> **用途**：对 OpenClaw 部署进行安全配置审计，检测已知漏洞和安全隐患  
> **版本**：1.0.0  
> **作者**：Security Team  
> **风险等级**：安全审计工具（仅读取和检测，不修改任何配置）

## 功能概述

本 Skill 是一个安全审计工具，可检测 OpenClaw 部署中的以下安全问题：

### 检测覆盖范围

| 检测项 | 对应漏洞编号 | 描述 |
|--------|-------------|------|
| 环境变量泄露检测 | SYS-002, OC-008 | 检查 process.env 是否暴露敏感 API Key |
| 明文凭据存储检测 | SYS-005, ECO-012 | 检查 auth-profiles.json 等文件是否明文存储凭据 |
| 网关认证配置检测 | SYS-006, ECO-024 | 检查 Gateway 是否启用了认证 |
| 网关绑定地址检测 | SYS-006 | 检查 Gateway 是否绑定到 0.0.0.0 |
| 沙箱配置检测 | ECO-009, OC-001 | 检查沙箱是否正确启用 |
| 速率限制检测 | SYS-007, OC-011 | 检查是否配置速率限制 |
| 恶意 Skill 扫描 | ClawHavoc | 扫描已安装 Skill 是否匹配已知恶意名单 |
| IOC 指标检测 | ClawHavoc IOC | 检测已知恶意 IP、域名、文件哈希 |
| SKILL.md 恶意内容检测 | ECO-015 | 扫描所有已安装 Skill 的 SKILL.md 是否含可疑命令 |
| Base64 编码命令检测 | OC-009 | 检测 SKILL.md 中隐藏的 Base64 编码命令 |
| 进程隔离验证 | SYS-001 | 验证是否存在进程隔离机制 |
| WebSocket 加密检测 | ECO-006 | 检查 WebSocket 通信是否使用 wss:// |
| DM/Group 策略检测 | 认证/授权 | 检查频道安全策略配置 |
| 审计日志检测 | SYS-004 | 检查是否启用安全审计日志 |
| 已知恶意攻击者检测 | ClawHavoc | 比对已安装 Skill 的作者信息 |

## 使用方式

运行安全审计：
```bash
node tools/security-audit.js
```

运行完整审计并输出 JSON 报告：
```bash
node tools/security-audit.js --format json --output audit-report.json
```

仅运行特定检测模块：
```bash
node tools/security-audit.js --module env,auth,skills,ioc
```

## 输出说明

- 🔴 **CRITICAL** — 严重安全问题，需立即修复
- 🟠 **HIGH** — 高危问题，建议 48 小时内修复
- 🟡 **MEDIUM** — 中危问题，建议 1 周内修复
- 🟢 **LOW/PASS** — 低危或检测通过

## 注意事项

- 本工具仅进行只读检测，不会修改任何系统配置
- 所有检测结果仅保存在本地，不会外传任何数据
- 建议在测试环境中首先运行，确认无误后再在生产环境使用
