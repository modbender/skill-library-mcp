# QQ 官方机器人 Skill

📦 包含完整配置步骤、IP 白名单管理、故障排除

## 快速开始

1. 阅读 `SKILL.md` 获取完整指南
2. 复制 `config.example.json` 为 `qq_official_bot_config.json` 并填入配置
3. 运行 `qq_bot_daemon.sh start` 启动机器人

## 核心文件

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 完整文档和故障排除 |
| `qq_official_bot.py` | QQ Bot 主程序 |
| `qq_bot_daemon.sh` | 启动管理脚本 |
| `qq_ai_handler.sh` | AI 处理器脚本 |
| `config.example.json` | 配置模板 |

## 快速命令

```bash
# 启动
./qq_bot_daemon.sh start

# 停止
./qq_bot_daemon.sh stop

# 重启
./qq_bot_daemon.sh restart

# 查看状态
./qq_bot_daemon.sh status
```

---

**维护者**: 小皮 🦊
**版本**: 1.0.0
