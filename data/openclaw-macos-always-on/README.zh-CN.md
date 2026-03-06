# OpenClaw macOS 永久在线方案

**让 OpenClaw 在 macOS 上 24/7 运行 - 即使锁屏数小时也不中断！**

[![macOS](https://img.shields.io/badge/macOS-10.15+-blue.svg)](https://www.apple.com/cn/macos/)
[![已验证](https://img.shields.io/badge/已验证-macOS%2014.4-success.svg)](https://github.com/happydog-intj/openclaw-macos-always-on)
[![许可证](https://img.shields.io/badge/许可证-MIT-green.svg)](LICENSE)

[English](README.md) | 简体中文

## 🎯 解决的问题

默认情况下，macOS 在锁屏时会暂停用户进程，导致 OpenClaw 机器人停止响应消息。本项目提供了一个**经过测试和验证**的解决方案，使用 LaunchDaemon + caffeinate 实现 24/7 运行。

**已验证可用：**
- ✅ 锁屏超过 30 分钟后仍正常工作
- ✅ macOS 14.4（以及更早版本）
- ✅ Intel 和 Apple Silicon Mac 通用

## 🚀 快速安装

一键安装命令：

```bash
curl -fsSL https://raw.githubusercontent.com/happydog-intj/openclaw-macos-always-on/master/install.sh | bash
```

或手动安装 - 查看 [SKILL.md](./SKILL.md) 获取详细说明。

## ✨ 功能对比

将 OpenClaw 从用户级 LaunchAgent 升级为系统级 LaunchDaemon，带来以下改进：

| 功能 | 之前（LaunchAgent） | 之后（LaunchDaemon + caffeinate） |
|------|-------------------|-----------------------------------|
| **锁屏后运行** | ❌ 约10分钟后暂停 | ✅ 无限期运行 |
| **注销后运行** | ❌ 停止运行 | ✅ 继续运行 |
| **开机启动** | 登录时启动 | 系统启动时启动 |
| **优先级** | 用户级 | 系统级 |
| **防止休眠** | 无 | `caffeinate -s` |

## 🔧 工作原理

解决方案使用三个关键组件：

1. **LaunchDaemon** - 系统级服务（以你的用户身份运行，但由系统 launchd 管理）
2. **caffeinate** - macOS 内置工具，阻止系统休眠，同时允许屏幕休眠
3. **增强的 KeepAlive** - 网络感知的自动重启和崩溃恢复

```xml
<!-- 关键配置 -->
<key>ProgramArguments</key>
<array>
  <string>/usr/bin/caffeinate</string>
  <string>-s</string>  <!-- 阻止系统休眠 -->
  <string>/opt/homebrew/bin/node</string>
  <string>.../openclaw/dist/index.js</string>
  <string>gateway</string>
</array>
```

## 📋 系统要求

- **macOS 10.15+**（已在 14.4 上测试）
- **管理员权限**（安装时需要 sudo）
- **已安装 OpenClaw**（`npm install -g openclaw`）

## 📖 文档

- [SKILL.md](./SKILL.md) - 完整文档和故障排除指南
- [install.sh](./install.sh) - 自动化安装脚本

## 🧪 测试方法

安装后，用不同的锁屏时长测试：

```bash
# 测试 1：立即锁屏
pmset displaysleepnow
# 用手机发送 "ping" - 应该立即收到回复

# 测试 2：锁屏 30+ 分钟
# 机器人应该仍能响应
```

## 📊 验证状态

检查 caffeinate 是否正常工作：

```bash
# 查看 caffeinate 进程
ps aux | grep caffeinate | grep -v grep

# 检查电源断言
pmset -g assertions | grep caffeinate
```

你应该看到：
```
pid XXXXX(caffeinate): PreventSystemSleep named: "caffeinate command-line tool"
  Details: caffeinate asserting on behalf of '/opt/homebrew/bin/node' (pid XXXXX)
```

## 🔄 管理命令

```bash
# 重启服务
sudo launchctl kickstart -k system/ai.openclaw.gateway

# 停止服务
sudo launchctl bootout system/ai.openclaw.gateway

# 查看日志
tail -f ~/.openclaw/logs/gateway.log

# 检查状态
sudo launchctl print system/ai.openclaw.gateway
```

## 🔓 卸载

```bash
# 停止并删除
sudo launchctl bootout system/ai.openclaw.gateway
sudo rm /Library/LaunchDaemons/ai.openclaw.gateway.plist

# 可选：恢复 LaunchAgent
mv ~/Library/LaunchAgents/ai.openclaw.gateway.plist.disabled \
   ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

## ⚡ 性能影响

- **空闲时**：约 50MB 内存，<1% CPU
- **活跃时**：约 100MB 内存，根据任务变化
- **电池影响**：会阻止系统休眠（台式机无影响，笔记本在使用电池时可能影响续航）

## 🐛 故障排除

**服务无法启动？**
```bash
tail -50 ~/.openclaw/logs/gateway.err.log
```

**锁屏后仍被暂停？**
- 验证 caffeinate 是否运行：`ps aux | grep caffeinate`
- 检查电源断言：`pmset -g assertions`
- 确保使用了最新的安装脚本

**端口冲突？**
```bash
lsof -i :18789
kill -9 <PID>
```

查看 [SKILL.md](./SKILL.md#troubleshooting) 了解更多解决方案。

## 🤝 贡献

发现问题或有改进建议？欢迎提交 Pull Request！

1. Fork 本仓库
2. 创建你的功能分支
3. 在你的 Mac 上测试
4. 提交 Pull Request

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 了解详情。

## 🙏 致谢

- 为 [OpenClaw](https://github.com/openclaw/openclaw) 构建
- 由社区测试和验证
- 特别感谢在不同 macOS 版本上测试的贡献者

## 🔗 相关项目

- [OpenClaw](https://github.com/openclaw/openclaw) - 本技能支持的 AI 助手
- [Clawhub](https://clawhub.ai) - OpenClaw 技能市场

---

**用 ❤️ 为需要 macOS 上 24/7 机器人可用性的 OpenClaw 用户打造**

## 📞 支持

遇到问题？

- 💬 [GitHub Issues](https://github.com/happydog-intj/openclaw-macos-always-on/issues)
- 📖 [完整文档](./SKILL.md)
- 🌐 [OpenClaw 文档](https://docs.openclaw.ai)

## ⭐ 如果有帮助，请给个星标！

如果这个项目帮到了你，请在 GitHub 上给个 ⭐，让更多人发现它！
