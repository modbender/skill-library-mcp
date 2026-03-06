---
name: check-bookings-phone
description: 检查携程旅行app预售订单的日期可用性。通过ADB连接Android设备，自动化操作携程app，遍历"未使用 预售订单"中的每个订单，查询指定日期范围内每天的预约状态（可约、约满、补差价等）。当用户提到检查携程订单、查看预售订单可用日期、查酒店预约状态时触发此skill。
---

# 携程预售订单日期可用性检查

通过 midscene.js 驱动 ADB 连接的 Android 设备，自动化操作携程旅行 app，遍历预售订单并提取指定日期的预约状态。

## Setup（首次使用时执行）

Skill 目录：本文件所在目录（下称 `$SKILL_DIR`）。

**1. 安装依赖**

```bash
cd $SKILL_DIR && npm install
```

**2. 配置环境变量**

在系统环境变量或 `$SKILL_DIR/.env` 中设置以下变量：

**火山引擎 Doubao（推荐）：**

```
MIDSCENE_MODEL_API_KEY=<your-api-key>
MIDSCENE_MODEL_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
MIDSCENE_MODEL_NAME=doubao-seed-2-0-lite-260215
MIDSCENE_USE_DOUBAO_VISION=true
```

> 模型配置请参考 [midscene.js 文档](https://midscenejs.com/choose-a-model.html)。

**OpenClaw 用户：** 可在 `~/.openclaw/openclaw.json` 中配置环境变量，安装时会自动注入。

## 运行

```bash
cd $SKILL_DIR && npx tsx scripts/checkBookings.ts --from 2026-05-01 --to 2026-05-05
```

参数说明：
- `--from` — 起始日期，格式 YYYY-MM-DD，默认 2026-05-01
- `--to` — 结束日期，格式 YYYY-MM-DD，默认 2026-05-05

支持跨月查询（如 4月28日到5月3日），脚本会自动按月滚动日历并分别提取。

## 安装到 OpenClaw

```bash
npx skills add <repo-path> -a openclaw
```

## 前置条件

- Android 设备已通过 USB 连接并开启 ADB 调试（`adb devices` 能看到设备）
- 携程旅行 app 已安装且已登录

## 自动化流程

脚本按以下屏幕顺序操作，每一屏的处理时间会被记录并在结束时汇总打印：

1. **第1屏（我的页面）**：检测或导航到携程"我的"页面，点击"全部订单"
2. **第2屏（全部订单）**：点击"未使用 预售订单"选项
3. **第3屏（订单列表）**：查询订单总数，逐个点击"在线预约"
4. **第4屏（订单详情）**：点击"立即预约"打开日期选择器
5. **第5屏（日期选择）**：滚动到目标月份，提取每日预约状态
6. 关闭日期选择器 → 返回订单列表 → 处理下一个订单

## 输出

控制台打印每个订单在目标日期范围内的状态，例如：

```
订单 1: 南京某酒店
  5月1日: 约满
  5月2日: 剩1间 补¥200
  5月3日: 可约
```

末尾打印每一屏的处理耗时和总耗时。

## 使用示例

```bash
# 查询5月1日-5日（默认）
npx tsx scripts/checkBookings.ts

# 查询五一到五四
npx tsx scripts/checkBookings.ts --from 2026-05-01 --to 2026-05-04

# 跨月查询：4月28日到5月3日
npx tsx scripts/checkBookings.ts --from 2026-04-28 --to 2026-05-03

# 查询端午假期
npx tsx scripts/checkBookings.ts --from 2026-06-25 --to 2026-06-27
```
