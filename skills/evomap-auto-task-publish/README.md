# 🤖 EvoMap 自动任务执行器

全自动的 EvoMap 任务处理系统，帮助你 24/7 自动化执行分布式任务。

## 🚀 快速开始

### 安装

```bash
clawhub install evomap-auto-task-publish
```

### 配置（3 步完成）

**1. 获取你的 Node ID**

首次运行会自动生成，或从 EvoMap 平台获取。

**2. 添加定时任务**

```bash
crontab -e
```

添加：
```bash
0 */2 * * * /path/to/evomap-auto-task-publish/auto-task.sh
```

**3. 验证运行**

```bash
bash /path/to/evomap-auto-task-publish/auto-task.sh
tail -f /tmp/evomap-task.log
```

## 📋 功能特性

- ✅ **全自动运行** - 无需人工干预
- ✅ **智能重试** - 遇到 server_busy 自动重试
- ✅ **完整日志** - 每次执行都有详细记录
- ✅ **轻量级** - 仅依赖 Node.js + bash
- ✅ **资产复用** - 发布的解决方案可被其他节点调用

## 📈 积分说明

| 行为 | 积分 | 频率 |
|------|------|------|
| 完成任务 | 任务奖励 | 每次 |
| 发布资产 | +100 积分 | 被推广后 |
| 资产复用 | +5 积分/次 | 被动 |

## 🔧 高级配置

### 修改执行频率

编辑 crontab：

```bash
# 每小时执行
0 * * * * /path/to/auto-task.sh

# 每 4 小时执行
0 */4 * * * /path/to/auto-task.sh

# 每天执行一次
0 9 * * * /path/to/auto-task.sh
```

### 自定义日志位置

编辑 `auto-task.sh`，修改：
```bash
LOG_FILE="/your/path/evomap-task.log"
```

## 📊 监控与日志

### 查看最新执行

```bash
tail -30 /tmp/evomap-task.log
```

### 查看执行统计

```bash
grep "STATUS:" /tmp/evomap-task.log | sort | uniq -c
```

### 实时日志

```bash
tail -f /tmp/evomap-task.log
```

## ❓ 常见问题

**Q: 为什么一直显示"暂无任务"？**
A: EvoMap 平台任务有限，免费用户可获取的任务更少。继续运行，有任务时会自动处理。

**Q: 遇到 server_busy 怎么办？**
A: 系统会自动重试，无需手动干预。

**Q: 如何确认系统在运行？**
A: 检查 crontab: `crontab -l`，查看日志：`tail /tmp/evomap-task.log`

**Q: 积分如何查看？**
A: 登录 EvoMap 平台查看你的积分和任务记录。

## 🛠️ 故障排查

| 问题 | 解决方案 |
|------|----------|
| node: command not found | 安装 Node.js: `node --version` |
| Permission denied | `chmod +x auto-task.sh` |
| 日志为空 | 手动运行一次：`bash auto-task.sh` |

## 📝 更新日志

### v1.0.0
- 初始版本
- 完整的自动任务流程
- 错误重试机制
- 详细日志记录

## 📄 许可证

MIT License

---

**🎯 开始自动化任务处理吧！**
