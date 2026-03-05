---
name: cache-cleanup
description: 清理过期缓存文件、auto-flush 文件、旧日志，释放磁盘空间。
---

# Cache Cleanup

清理各类缓存和临时文件，释放磁盘空间。

## 能力轮廓

- **输入**：缓存目录
- **输出**：清理报告
- **核心**：扫描 → 分类 → 清理

## 工作流

```
1. 扫描缓存目录
2. 识别过期文件（按类型设定过期时间）
3. 统计大小
4. 清理
5. 报告
```

## 目标目录

| 目录 | 类型 | 过期时间 |
|------|------|----------|
| ~/.npm/_cache/ | NPM 缓存 | 7 天 |
| ~/.cache/ | 通用缓存 | 7 天 |
| /tmp/ | 临时文件 | 1 天 |
| ~/.openclaw/logs/ | 日志文件 | 14 天 |
| ~/.openclaw/browser/ | 浏览器缓存 | 3 天 |
| ~/.openclaw/sandbox/ | 沙箱 | 7 天 |
| ~/.openclaw/sandbox-neko/ | 猫娘沙箱 | 7 天 |
| ~/.openclaw/canvas/ | Canvas 缓存 | 3 天 |

## 清理规则

| 类型 | 规则 |
|------|------|
| 日志 | .log, .jsonl > 14 天 |
| 缓存 | 所有 > 7 天 |
| 临时 | 所有 > 1 天 |
| 浏览器 | 所有 > 3 天 |

## 磁盘告警

- 磁盘使用 > 80% 时增强清理
- 清理前检查磁盘使用率

## 主动性

- 每3天执行一次
- 磁盘使用率高时主动清理

## 使用方式

```bash
# 手动执行
~/.openclaw/workspace/skills/cache-cleanup/cleanup.sh

# 配置定时任务（每3天凌晨2点）
cron job add cache-cleanup "0 2 */3 * *" ~/.openclaw/workspace/skills/cache-cleanup/run.sh
```
