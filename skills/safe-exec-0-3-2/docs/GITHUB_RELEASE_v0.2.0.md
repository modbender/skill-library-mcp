# 🚀 SafeExec v0.2.0 - 全局开关功能发布

## 🎉 新版本发布

SafeExec v0.2.0 现已发布！此次更新引入了**全局开关功能**，让用户可以更灵活地控制安全保护。

---

## ✨ 新功能

### 🎯 全局开关（重点功能）

- ✅ **--enable** - 启用 SafeExec 保护
- ✅ **--disable** - 禁用 SafeExec 保护（绕过检查）
- ✅ **--status** - 查看当前保护状态
- ⚙️ 配置文件驱动（`safe-exec-rules.json`）
- 📊 审计日志记录 `bypassed` 事件

**使用示例**:
```bash
# 查看状态
safe-exec --status

# 临时禁用（批量操作）
safe-exec --disable
rm -rf /tmp/cache/*
rm -rf /var/log/old/*
safe-exec --enable  # 重新启用

# 启用后恢复保护
safe-exec --enable
```

---

## 🔧 改进

### Bug 修复
- 🐛 **修复 jq `//` 操作符问题** - 正确处理 `false` 值
- 🔧 **明确 true/false 检查** - 避免条件判断错误

### 配置管理
- 📝 `safe-exec-rules.json` 新增 `enabled` 字段
- 🔄 状态持久化
- 📊 更好的配置验证

---

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/safe-exec.git ~/.openclaw/skills/safe-exec

# 添加执行权限
chmod +x ~/.openclaw/skills/safe-exec/*.sh

# 创建符号链接
ln -sf ~/.openclaw/skills/safe-exec/safe-exec.sh ~/.local/bin/safe-exec

# 验证安装
safe-exec --status
```

---

## 🚀 快速开始

### 基础使用

```bash
# 1. 查看状态
safe-exec --status
# 输出: ✅ 已启用

# 2. 执行危险命令（会被拦截）
safe-exec "rm -rf /tmp/test"
# 输出: 🚨 命令已拦截，等待批准

# 3. 批准请求
safe-exec-approve req_xxx
```

### 高级使用

```bash
# 临时禁用保护
safe-exec --disable

# 执行多个危险命令
rm -rf /tmp/cache/*
rm -rf /var/log/old/*

# 重新启用
safe-exec --enable
```

---

## 🔒 安全特性

- ✅ **10+ 危险模式检测** - Fork bomb、磁盘破坏、系统目录写入等
- ✅ **Zero-trust 架构** - 默认拦截，明确批准
- ✅ **完整审计追踪** - 记录所有操作
- ✅ **5分钟超时** - 自动过期保护
- ✅ **灵活配置** - 自定义规则

---

## 📊 版本对比

| 功能 | v0.1.3 | v0.2.0 |
|------|--------|--------|
| 危险命令拦截 | ✅ | ✅ |
| 批准工作流 | ✅ | ✅ |
| 审计日志 | ✅ | ✅ |
| 超时保护 | ✅ | ✅ |
| 全局开关 | ❌ | ✅ **新增** |
| 状态查询 | ❌ | ✅ **新增** |
| 绕过模式 | ❌ | ✅ **新增** |

---

## 📚 文档

- 📖 [README](README.md) - 项目概览和功能介绍
- 📘 [USAGE](USAGE.md) - 完整使用指南
- 📗 [GLOBAL_SWITCH_GUIDE](GLOBAL_SWITCH_GUIDE.md) - 开关功能详解
- 📙 [CHANGELOG](CHANGELOG.md) - 版本历史
- 📕 [CONTRIBUTING](CONTRIBUTING.md) - 贡献指南

---

## 🐛 Bug 修复

### 关键修复：jq `//` 操作符问题

**问题**: jq 的 `//` 操作符将 `false` 视为 falsy 值

**影响**: 无法正确切换 SafeExec 的启用/禁用状态

**修复**:
```bash
# 修复前（错误）
enabled=$(jq -r '.enabled // true' "$RULES_FILE")

# 修复后（正确）
enabled=$(jq -r 'if .enabled == true then "true" else "false" end' "$RULES_FILE")
```

---

## ⚠️ 安全警告

**禁用 SafeExec 时的风险**:

- ⚠️ 所有命令将直接执行，无安全检查
- ⚠️ 无撤销机制
- ⚠️ 仅在可信环境中禁用

**建议**:
- ✅ 默认保持启用
- ⏰ 禁用后尽快重新启用
- 📝 记录禁用原因
- 📊 定期检查审计日志

---

## 🙏 致谢

感谢 OpenClaw 社区的支持和反馈！

特别感谢用户提出的需求：
> "让用户可以开启/关闭 SafeExec，开启后所有对话中的危险命令均进行拦截"

这个功能现已完整实现！✨

---

## 📮 联系方式

- **GitHub**: https://github.com/yourusername/safe-exec
- **Issues**: https://github.com/yourusername/safe-exec/issues
- **Discord**: https://discord.gg/clawd

---

**完整更新日志**: [CHANGELOG.md](CHANGELOG.md)

**下载统计**: （发布后更新）

**Star ⭐️ 这个项目支持我们！**

---

## 🔄 升级指南

### 从 v0.1.x 升级到 v0.2.0

1. **拉取最新代码**:
   ```bash
   cd ~/.openclaw/skills/safe-exec
   git pull origin master
   git fetch --tags
   ```

2. **更新配置文件**:
   ```bash
   # 如果 enabled 字段不存在，会自动添加
   safe-exec --status  # 自动初始化
   ```

3. **验证功能**:
   ```bash
   safe-exec --status   # 应显示状态
   safe-exec --enable   # 启用保护
   safe-exec --disable  # 禁用保护
   ```

**无需额外配置！** 升级无缝兼容。

---

**SafeExec v0.2.0 - 更灵活的安全保护** 🛡️✨
