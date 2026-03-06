# 定时任务

## 概述

**定时任务：**
- 每日热点总结（早上10点）
- 记忆清理（每周一次）

---

## 1. 每日热点总结

### 1.1 任务描述

**时间：** 每天早上 10:00（上海时间）

**内容：**
1. 打开 X Creator Inspiration 页面
2. 抓取 Top 10 热点推文
3. 分析为什么火
4. 更新热点表格
5. 推送总结给用户

### 1.2 Cron 表达式

```
0 10 * * *  # 每天 10:00
```

### 1.3 任务配置

**使用 OpenClaw cron 系统：**

```json
{
  "name": "每日热点总结",
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "每日热点总结任务：\n\n1. 打开 https://x.com/i/jf/creators/inspiration/top_posts 获取 Top 10\n\n2. 分析每条：\n   - 内容、作者、数据\n   - 为什么火\n   - 重要性评级\n\n3. 识别重大事件：\n   - 如果是重大事件（战争、政治、大公司），创建/更新 memory/daily/hotspots/events/[事件名].md\n\n4. 更新表格文件 memory/daily/hotspots/tables/YYYY-MM-DD.md\n\n5. 删除超过7天的表格文件\n\n6. 推送总结给用户",
    "timeoutSeconds": 300
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce"
  }
}
```

### 1.4 设置方法

**方法 1: 使用 OpenClaw CLI**

```bash
openclaw cron add --config hotspot-cron.json
```

**方法 2: 使用脚本**

```bash
./scripts/setup-cron.sh
```

### 1.5 输出格式

**推送内容：**

```
# 每日热点总结 (2026-03-02)

## Top 10 热点

| 排名 | 账号 | 内容 | 数据 | 为什么火 |
|------|------|------|------|----------|
| 1 | @user1 | "热点内容" | 70M views | 原因 |
| ... | ... | ... | ... | ... |

## 重大事件

⚠️ **伊朗战争持续**（详见 events/iran-war-2026.md）

## 发推技巧

- Quote + 短评
- 自嘲
- 时机把握

## 适合你的内容

1. AI/Tech 热点评论
2. Crypto 市场分析
3. ...

---

*下次更新: 2026-03-03 10:00*
```

---

## 2. 记忆清理

### 2.1 任务描述

**时间：** 每周日 03:00

**内容：**
1. 删除30天前的评论历史
2. 删除30天前的每日日志
3. 删除7天前的热点表格

### 2.2 Cron 表达式

```
0 3 * * 0  # 每周日 03:00
```

### 2.3 清理脚本

**文件：** `scripts/cleanup-memory.sh`

```bash
#!/bin/bash

# 清理评论历史（保留30天）
find ~/memory/daily/hotspots/history/comments -mtime +30 -type f -delete

# 清理每日日志（保留30天）
find ~/memory/daily/hotspots/history/daily -mtime +30 -type f -delete

# 清理热点表格（保留7天）
find ~/memory/daily/hotspots/tables -mtime +7 -type f -delete

echo "记忆清理完成: $(date)"
```

### 2.4 设置方法

```bash
chmod +x scripts/cleanup-memory.sh
crontab -e
```

添加：
```
0 3 * * 0 ~/path/to/cleanup-memory.sh >> ~/memory/cleanup.log 2>&1
```

---

## 3. 刷推提醒

### 3.1 任务描述

**根据用户配置生成提醒：**

| 类型 | 说明 | 示例 |
|------|------|------|
| 固定时间 | 每天固定时间提醒 | 09:00, 15:00, 21:00 |
| 随机 | 每天随机N次 | 随机3次（09:00-22:00范围） |
| 随机范围 | 每天随机N-M次 | 随机2-4次 |
| 工作日/周末 | 不同配置 | 工作日20:00，周末随机3次 |

### 3.2 固定时间提醒

**用户输入：** "早上9点、下午3点、晚上9点"

**配置：**
```json
{
  "type": "fixed",
  "times": ["09:00", "15:00", "21:00"],
  "reminderEnabled": true
}
```

**Cron 任务：**
```
0 9 * * *   # 09:00
0 15 * * *  # 15:00
0 21 * * *  # 21:00
```

### 3.3 随机时间提醒

**用户输入：** "每天3次，随机时间"

**配置：**
```json
{
  "type": "random",
  "countPerDay": 3,
  "timeRange": ["09:00", "22:00"],
  "reminderEnabled": true
}
```

**实现方式：**
- 每天凌晨生成当天随机时间
- 创建一次性 cron 任务

**代码：**
```python
import random
from datetime import datetime, timedelta

def generate_random_times(count, time_range):
    """生成随机时间点"""
    start_hour = int(time_range[0].split(":")[0])
    end_hour = int(time_range[1].split(":")[0])
    
    times = []
    for _ in range(count):
        hour = random.randint(start_hour, end_hour - 1)
        minute = random.randint(0, 59)
        times.append(f"{hour:02d}:{minute:02d}")
    
    # 排序
    times.sort()
    return times

# 示例
times = generate_random_times(3, ["09:00", "22:00"])
# ["10:23", "14:47", "19:15"]
```

### 3.4 随机范围提醒

**用户输入：** "每天随机2-4次"

**配置：**
```json
{
  "type": "random_range",
  "minPerDay": 2,
  "maxPerDay": 4,
  "timeRange": ["09:00", "22:00"]
}
```

**实现：**
- 每天随机决定次数（2-4次）
- 生成随机时间点

### 3.5 工作日/周末提醒

**用户输入：** "工作日晚上8点，周末随机3次"

**配置：**
```json
{
  "type": "weekday_weekend",
  "weekday": {
    "type": "fixed",
    "times": ["20:00"]
  },
  "weekend": {
    "type": "random",
    "countPerDay": 3,
    "timeRange": ["09:00", "22:00"]
  }
}
```

**Cron 任务：**
```
# 工作日 20:00
0 20 * * 1-5

# 周末随机（每天生成）
```

### 3.6 推送内容

```
# 刷推提醒

今天还没刷推，要刷一下吗？

配额状态：
- 关注: 0/10
- 点赞: 0/30
- 评论: 0/10

回复"刷推"或"刷推 [时间]"开始。
```

---

## 4. 任务管理

### 4.1 查看所有任务

```bash
openclaw cron list
```

### 4.2 暂停任务

```bash
openclaw cron disable --name "每日热点总结"
```

### 4.3 恢复任务

```bash
openclaw cron enable --name "每日热点总结"
```

### 4.4 手动运行

```bash
openclaw cron run --name "每日热点总结"
```

### 4.5 删除任务

```bash
openclaw cron remove --name "每日热点总结"
```

---

## 5. 任务状态检查

### 5.1 检查脚本

**文件：** `scripts/check-cron.sh`

```bash
#!/bin/bash

echo "=== Cron 任务状态 ==="
echo ""

# 检查每日热点
if openclaw cron list | grep -q "每日热点总结"; then
    echo "✓ 每日热点总结: 已启用"
else
    echo "✗ 每日热点总结: 未启用"
fi

# 检查记忆清理
if crontab -l | grep -q "cleanup-memory"; then
    echo "✓ 记忆清理: 已启用"
else
    echo "✗ 记忆清理: 未启用"
fi

echo ""
echo "=== 最近运行记录 ==="
openclaw cron runs --name "每日热点总结" --limit 5
```

### 5.2 运行检查

```bash
chmod +x scripts/check-cron.sh
./scripts/check-cron.sh
```

---

## 6. 故障处理

### 6.1 任务未运行

**检查：**
1. OpenClaw 是否运行
2. Cron 服务是否正常
3. 任务是否启用

**解决：**
```bash
# 检查 OpenClaw 状态
openclaw status

# 检查 cron 服务
systemctl status cron  # Linux
launchctl list | grep cron  # macOS

# 重新启用任务
openclaw cron enable --name "每日热点总结"
```

### 6.2 任务运行失败

**查看日志：**
```bash
openclaw cron runs --name "每日热点总结"
```

**常见错误：**
- 浏览器连接失败 → 检查 OpenClaw Browser Relay
- 页面加载超时 → 增加 timeoutSeconds
- 数据解析失败 → 检查页面结构是否变化

---

## 7. 设置脚本

**文件：** `scripts/setup-cron.sh`

```bash
#!/bin/bash

echo "=== 设置定时任务 ==="

# 1. 创建热点总结任务
echo "创建每日热点总结任务..."
openclaw cron add --name "每日热点总结" \
  --schedule "0 10 * * *" \
  --tz "Asia/Shanghai" \
  --payload "hotspot-cron.json"

# 2. 设置记忆清理
echo "设置记忆清理..."
chmod +x scripts/cleanup-memory.sh
(crontab -l 2>/dev/null; echo "0 3 * * 0 $(pwd)/scripts/cleanup-memory.sh >> ~/memory/cleanup.log 2>&1") | crontab -

# 3. 验证
echo ""
echo "=== 验证 ==="
./scripts/check-cron.sh

echo ""
echo "✓ 定时任务设置完成"
```

---

## 8. 任务时间表

| 任务 | 时间 | 频率 | 说明 |
|------|------|------|------|
| 每日热点总结 | 10:00 | 每天 | 抓取 Top 10，更新表格 |
| 记忆清理 | 03:00 | 每周日 | 删除过期文件 |
| 刷推提醒 | 20:00 | 每天 | 提醒用户刷推（可选） |

---

*文档版本: 1.0*
*更新: 2026-03-02*
