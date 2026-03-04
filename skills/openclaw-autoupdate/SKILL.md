---
name: openclaw-autoupdate
description: OpenClaw静默更新技能。安全自动化更新OpenClaw到最新版本。
---

# OpenClaw 静默更新

## 功能

- 检查当前版本
- 获取最新版本  
- 执行更新
- 重启Gateway
- 验证服务状态

## 使用方式

```bash
~/.openclaw/workspace/skills/openclaw-autoupdate/scripts/silent-update.sh
```

## 配置文件

无需额外配置，脚本直接使用系统已有的openclaw CLI。

## 安全说明

**本技能仅使用以下安全的命令：**
- `openclaw gateway status` - 查看状态
- `openclaw gateway stop` - 停止服务
- `npm install -g openclaw` - 全局更新
- `openclaw gateway start` - 启动服务
- 纯文件读写操作

**为什么被误报：**
- VirusTotal将"npm全局安装"行为标记为可疑
- 这是安全扫描器的常见误报
- 实际上脚本只使用openclaw官方CLI

## 源代码哈希

```
SHA256: eee24f574b4bf559e6e2c487f8bf180d2176c8c2e5f435b510b017415ee155c3
```

**验证方法：**
```bash
shasum -a 256 scripts/silent-update.sh
```

## 审计日志

脚本执行时会记录详细日志到 `~/.openclaw/logs/autoupdate.log`

---

*发布者：@jimmieting*
*版本：v1.0.2*
