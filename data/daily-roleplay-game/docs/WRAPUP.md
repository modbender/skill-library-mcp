# WRAPUP.md — 每日收尾任务

> 脚本入口：workspace 根目录 `scripts/wrapup.sh`（本文件位于 docs/，供人工查阅）

---

## 用法

```bash
# 默认使用 workspace-role-play 目录
./scripts/wrapup.sh

# 指定工作区
./scripts/wrapup.sh /path/to/workspace
```

---

## 执行流程

1. 检查 `roleplay-active.md` 是否存在
2. 读取日期、职业名、media_prefix
3. 创建归档目录 `archive/YYYY-MM-DD-职业名/images/`
4. 复制 `roleplay-active.md`（原文件保留）
5. 移动 `guess-log.md`（如存在）
6. 移动 `${media_prefix}*.png` 图片
7. 更新 `archive/history.md`
8. 输出 `WRAPUP_OK`

---

## Cron 配置

- **执行时间**：每日 23:30
- **命令**：`<workspace-path>/scripts/wrapup.sh`
- 详细配置见 `docs/CRON_CONFIG.md`

---

## 输出示例

```
[2026-02-23 23:30:00] 日期: 2026-02-23, 职业: 高铁乘务员, 前缀: train_
[2026-02-23 23:30:00] 创建归档目录: archive/2026-02-23-高铁乘务员
[2026-02-23 23:30:00] 归档 roleplay-active.md
[2026-02-23 23:30:00] 归档 35 张图片
[2026-02-23 23:30:00] 更新 history.md: 2026-02-23 | 高铁乘务员 | 5/5
[2026-02-23 23:30:00] 收尾完成！
WRAPUP_OK
```

---

*此文件由 OpenClaw 角色扮演系统使用*
