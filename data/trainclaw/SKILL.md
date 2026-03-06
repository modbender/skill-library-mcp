---
name: trainclaw
description: 车票查询AI助手 — 余票查询、经停站查询、中转换乘方案。支持车次类型筛选、时间窗口、排序、多种输出格式(text/json/csv)。纯命令行单次调用模式。 12306 Train Ticket Query — remaining tickets, route stops, transfer plans. Supports train type filter, time window, sorting, multiple output formats.
version: 0.0.3
icon: 🚄
---

# TrainClaw 🚄 - 车票查询AI助手

## 概述

调用 `trainclaw.py` 查询中国铁路余票、经停站和中转信息。单次调用模式——运行一次、返回结果、退出。

## 触发方式

用户提到火车票、高铁票、动车票、车次查询、经停站、中转换乘等关键词时触发。

### 快速示例

- **"查一下明天北京到上海的高铁票"** → 余票查询
- **"G1033 经停哪些站？"** → 经停站查询
- **"从深圳到拉萨怎么中转？"** → 中转查询
- **"南京到上海的动车，上午出发，按时长排序"** → 带筛选的余票查询

## 工作流程

```
用户说："查明天北京到上海的高铁"
    ↓
提取参数：出发=北京，到达=上海，日期=明天，类型=G
    ↓
执行命令：
  python trainclaw.py query -f 北京 -t 上海 -d 2026-03-04 --type G
    ↓
返回余票信息（text 格式，直接展示给用户）
```

## 四个子命令

### 1. 余票查询 (query / filter)

查询两站之间的余票信息，支持筛选和排序。

```bash
# 基础查询
python trainclaw.py query -f 北京 -t 上海

# 完整参数
python trainclaw.py query -f 北京 -t 上海 -d 2026-03-04 \
  --type G --earliest 8 --latest 18 --sort duration -n 10 -o text
```

### 2. 经停站查询 (route)

查询某车次的所有经停站信息。

```bash
python trainclaw.py route -c G1033 -d 2026-03-04
python trainclaw.py route -c G1 -d 2026-03-04 -o json
```

### 3. 中转查询 (transfer)

查询需要换乘的中转方案。

```bash
# 自动推荐中转站
python trainclaw.py transfer -f 深圳 -t 拉萨 -n 5

# 指定中转站
python trainclaw.py transfer -f 深圳 -t 拉萨 -m 西安 -d 2026-03-04
```

## 参数说明

### 通用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-d, --date` | 查询日期 (yyyy-MM-dd) | 今天 |
| `-o, --format` | 输出格式: text / json / csv | text |

### 筛选参数 (query / transfer)

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-f, --from` | 出发站（站名/城市名/三字母代码） | **必填** |
| `-t, --to` | 到达站（站名/城市名/三字母代码） | **必填** |
| `--type` | 车次类型筛选（见下表） | 不筛选 |
| `--earliest` | 最早出发小时 (0-24) | 0 |
| `--latest` | 最晚出发小时 (0-24) | 24 |
| `--sort` | 排序: startTime / arriveTime / duration | 不排序 |
| `--reverse` | 倒序排列 | 否 |
| `-n, --limit` | 最大结果数 | query: 不限, transfer: 10 |

### 车次类型代码

| 代码 | 含义 |
|------|------|
| G | 高铁/城际（G/C 开头） |
| D | 动车 |
| Z | 直达特快 |
| T | 特快 |
| K | 快速 |
| O | 其他（非 GDZTK） |
| F | 复兴号 |
| S | 智能动车组 |

可组合使用，如 `--type GD` 表示高铁+动车。

## 车站名解析

支持三种输入格式，自动识别：

1. **精确站名**: `北京南`、`上海虹桥`、`南京南` → 直接匹配
2. **城市名**: `北京`、`上海`、`南京` → 匹配该城市代表站
3. **三字母代码**: `BJP`、`SHH`、`NJH` → 直接使用

## 输出格式

### text 格式（默认，推荐给用户阅读）
```
车次 | 出发站→到达站 | 出发→到达 | 历时 | 席位信息 | 标签
G25 | 北京南→上海虹桥 | 17:00→21:18 | 04:18 | 商务座:1张/2318.0元, 一等座:有票/1060.0元 | 复兴号
```

### json 格式（推荐程序处理）
完整 JSON 数组，包含所有字段。

### csv 格式（仅 query 支持）
标准 CSV，含表头行。

## 文件位置

- **主程序**: `trainclaw.py`
- **配置文件**: `config.py`
- **缓存目录**: `cache/`（车站数据自动缓存 7 天）

## 注意事项

1. **日期限制**: 仅支持查询今天及未来 15 天内的车票
2. **网络依赖**: 首次运行需下载车站数据（~3000 站），之后使用本地缓存
3. **错误输出**: 错误信息输出到 stderr，数据输出到 stdout，支持管道操作
4. **中转限制**: 中转查询结果取决于 12306 的推荐，非所有组合都有结果
5. **依赖**: 仅需 Python 3.8+ 和 `requests` 库

## 使用场景示例

### 日常查票
```
用户: "明天北京到上海有什么高铁？"
→ python trainclaw.py query -f 北京 -t 上海 -d {明天日期} --type G
```

### 时间筛选
```
用户: "上午 8 点到 12 点从南京到杭州的动车"
→ python trainclaw.py query -f 南京 -t 杭州 --type D --earliest 8 --latest 12
```

### 查经停站
```
用户: "G1033 都停哪些站？"
→ python trainclaw.py route -c G1033 -d {今天日期}
```

### 中转方案
```
用户: "从北京怎么坐火车去成都？"
→ python trainclaw.py transfer -f 北京 -t 成都 -n 5
```
