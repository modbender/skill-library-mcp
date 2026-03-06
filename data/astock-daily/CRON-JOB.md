# ⏰ OpenClaw Cron Job 配置

## 任务信息

| 字段 | 值 |
|------|-----|
| **任务 ID** | `7b941fcb-6355-4ab5-84e1-c0eba7c2cd04` |
| **任务名称** | A 股每日精选 |
| **描述** | 获取 A 股新股发行和 20 元以下精选股票，发送到邮箱 |
| **Cron 表达式** | `0 30 9 * * 1-5` |
| **时区** | Asia/Shanghai |
| **运行时间** | 每周一至周五 9:30 |
| **会话类型** | isolated（独立会话） |
| **超时时间** | 300 秒（5 分钟） |
| **下次运行** | 3 天后 |

---

## 🔧 管理命令

### 查看任务列表
```bash
openclaw cron list
```

### 查看任务详情
```bash
openclaw cron status fcb44571-0b4c-48f4-b675-49a00103e26d
```

### 立即运行测试
```bash
openclaw cron run fcb44571-0b4c-48f4-b675-49a00103e26d
```

### 暂停任务
```bash
openclaw cron disable fcb44571-0b4c-48f4-b675-49a00103e26d
```

### 启用任务
```bash
openclaw cron enable fcb44571-0b4c-48f4-b675-49a00103e26d
```

### 删除任务
```bash
openclaw cron rm fcb44571-0b4c-48f4-b675-49a00103e26d
```

### 查看运行历史
```bash
openclaw cron runs fcb44571-0b4c-48f4-b675-49a00103e26d
```

---

## 📊 运行日志

任务运行后，日志会显示在 OpenClaw 会话中。

也可以查看本地日志：
```bash
tail -f /tmp/astock-daily.log
```

---

## 📝 Cron 表达式说明

```
0 30 9 * * 1-5
│ │  │ │ │  │
│ │  │ │ │  └──── 星期一到周五
│ │  │ │ └────── 每月
│ │  │ └──────── 每月
│ │  └────────── 每天 9 点
│ └───────────── 30 分
└─────────────── 0 秒
```

---

## 🔄 修改运行时间

如果需要修改运行时间，先删除再添加：

```bash
# 删除旧任务
openclaw cron rm fcb44571-0b4c-48f4-b675-49a00103e26d

# 添加新任务（示例：改为 9:00 运行）
openclaw cron add \
  --name "A 股每日精选" \
  --description "获取 A 股新股发行和 20 元以下精选股票，发送到邮箱" \
  --cron "0 0 9 * * 1-5" \
  --tz "Asia/Shanghai" \
  --message "cd /Users/batype/.openclaw/workspace-work/skills/astock-daily && source .env && node index.js" \
  --session "isolated" \
  --timeout-seconds 120 \
  --thinking "low"
```

---

## ✅ 状态确认

任务已成功添加，下次运行时间：**3 天后**（下一个交易日 9:30）
