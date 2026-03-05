---
name: dnfm-tracker
description: DNFM 周本进度追踪。用于查询/更新新超越本、老超越本、周本、雷龙、团本进度。支持周五自动重置新超越本等刷新逻辑。支持自定义总量和启用/禁用副本。自动从 /root/.openclaw/workspace/dnfm-tracker/progress.json 读写数据。
---

# DNFM 周本追踪

## 快速使用

**查询进度：**
```
tracker.py --status
```

**更新进度：**
```
tracker.py --update <事件> <数量>
```

## 可用事件

| 输入 | 默认总量 | 刷新日 |
|------|---------|--------|
| 新超越本 | 5 | 周五 |
| 老超越本 | 10 | 周三 |
| 周本 | 10 | 周三 |
| 雷龙 | 18 | 周一 |
| 团本 | 16 | 周一 |

## 常用命令

**显示进度：**
```
tracker.py              # 简洁进度
tracker.py --status     # 详细进度
tracker.py --config     # 查看配置
tracker.py --events     # 查看所有可用事件
```

**更新进度：**
```
tracker.py --update 老超越本 7
# ✅ 老超越本: 7/10，剩 3 个
```

**设置总量（根据你的号数）：**
```
tracker.py --set-total 雷龙 10
# ✅ 雷龙 总量: 18 → 10
```

**启用/禁用副本：**
```
tracker.py --disable 团本   # 禁用团本
tracker.py --enable 团本    # 启用团本
```

## 数据文件

- 进度文件：`/root/.openclaw/workspace/dnfm-tracker/progress.json`
- 配置文件：`/root/.openclaw/workspace/dnfm-tracker/config.json`
- 格式：JSON，自动管理刷新周期重置
