---
name: jisu-train
description: 使用极速数据火车查询 API，支持站站时刻查询、车次经停查询和余票查询，返回出发到达时间、用时、票价与余票数量等信息。
metadata: { "openclaw": { "emoji": "🚆", "requires": { "bins": ["python3"], "env": ["JISU_API_KEY"] }, "primaryEnv": "JISU_API_KEY" } }
---

# 极速数据火车查询（Jisu Train）

基于 [火车查询 API](https://www.jisuapi.com/api/train/) 的 OpenClaw 技能，支持：

- **站站查询**（`/train/station2s`）
- **车次查询**（`/train/line`）
- **余票查询**（`/train/ticket`）

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/train/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/train/train.py`

## 使用方式

### 1. 站站查询（/train/station2s）

```bash
python3 skills/train/train.py station2s '{"start":"杭州","end":"北京","ishigh":0}'
```

可选参数 `date`（不填则按接口默认）：

```bash
python3 skills/train/train.py station2s '{"start":"杭州","end":"北京","ishigh":0,"date":"2025-04-03"}'
```

### 2. 车次查询（/train/line）

```bash
python3 skills/train/train.py line '{"trainno":"G34"}'
```

可选参数 `date`：

```bash
python3 skills/train/train.py line '{"trainno":"G34","date":"2025-04-04"}'
```

### 3. 余票查询（/train/ticket）

```bash
python3 skills/train/train.py ticket '{"start":"杭州","end":"北京","date":"2015-10-20"}'
```

## 请求参数

### 站站查询

| 字段名  | 类型   | 必填 | 说明       |
|---------|--------|------|------------|
| start   | string | 是   | 出发站（中文） |
| end     | string | 是   | 到达站（中文） |
| ishigh  | int    | 否   | 是否高铁（0/1） |
| date    | string | 否   | 日期（可选） |

### 车次查询

| 字段名  | 类型   | 必填 | 说明     |
|---------|--------|------|----------|
| trainno | string | 是   | 车次号   |
| date    | string | 否   | 日期（可选） |

### 余票查询

| 字段名 | 类型   | 必填 | 说明       |
|--------|--------|------|------------|
| start  | string | 是   | 出发站（中文） |
| end    | string | 是   | 到达站（中文） |
| date   | string | 是   | 日期，格式如 `2015-10-20` |

## 返回结果示例（节选）

### 站站查询

```json
[
  {
    "trainno": "G34",
    "type": "高铁",
    "station": "杭州东",
    "endstation": "北京南",
    "departuretime": "07:18",
    "arrivaltime": "13:07",
    "costtime": "5时49分",
    "distance": "1279",
    "priceyd": "907.0",
    "priceed": "538.5"
  }
]
```

### 车次查询

```json
{
  "trainno": "G34",
  "type": "高铁",
  "list": [
    {
      "sequenceno": "1",
      "station": "杭州东",
      "arrivaltime": "-",
      "departuretime": "07:18",
      "stoptime": "0"
    }
  ]
}
```

### 余票查询

```json
[
  {
    "trainno": "G42",
    "type": "高铁",
    "station": "杭州东",
    "endstation": "北京南",
    "departuretime": "09:26",
    "arrivaltime": "16:06",
    "costtime": "06:40",
    "numsw": "6",
    "numyd": "无",
    "numed": "无"
  }
]
```

## 常见错误码

来源于 [官方火车文档](https://www.jisuapi.com/api/train/)：

| 代号 | 说明                 |
|------|----------------------|
| 201  | 车次为空             |
| 202  | 始发站或到达站为空   |
| 203  | 没有信息             |

## 在 OpenClaw 中的推荐用法

1. 用户提问：「帮我查杭州到北京今天有哪些高铁？」  
2. 代理构造 JSON：`{"start":"杭州","end":"北京","ishigh":1}` 并调用：  
   `python3 skills/train/train.py station2s '{"start":"杭州","end":"北京","ishigh":1}'`  
3. 从返回结果中挑选合适车次（出发时间/到达时间/用时/票价），再用 `line` 查看经停站，或用 `ticket` 查询余票数量。  

