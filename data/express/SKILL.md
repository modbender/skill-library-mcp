---
name: jisu-express
description: 使用极速数据快递查询 API 查询快递物流轨迹、签收状态，支持自动识别快递公司及顺丰/中通/跨越手机号后四位校验。
metadata: { "openclaw": { "emoji": "📦", "requires": { "bins": ["python3"], "env": ["JISU_API_KEY"] }, "primaryEnv": "JISU_API_KEY" } }
---

# 极速数据快递查询（Jisu Express）

基于 [快递查询 API](https://www.jisuapi.com/api/express) 的 OpenClaw 技能，用于查询快递物流轨迹、签收状态等信息，支持自动识别快递公司，以及顺丰/中通/跨越的手机号后四位校验。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/express

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/express/express.py`

## 使用方式

### 1. 基本查询（自动识别快递公司）

```bash
python3 skills/express/express.py '{"number":"70303808964270","type":"auto"}'
```

### 2. 指定快递公司

```bash
python3 skills/express/express.py '{"number":"4303200322000","type":"yunda"}'
```

### 3. 顺丰 / 中通 / 跨越（需手机号后四位）

```bash
python3 skills/express/express.py '{"number":"931658943036","type":"sfexpress","mobile":"1234"}'
```

### 4. 查询支持的快递公司列表（/express/type）

```bash
python3 skills/express/express.py type
```

返回值为数组，每项形如：

```json
{
  "name": "德邦",
  "type": "DEPPON",
  "letter": "D",
  "tel": "95353",
  "number": "330060412"
}
```

## 请求参数（查询时传入 JSON）

| 字段名  | 类型   | 必填 | 说明                                             |
|--------|--------|------|--------------------------------------------------|
| number | string | 是   | 快递单号                                         |
| type   | string | 否   | 快递公司代号，默认 `auto` 自动识别               |
| mobile | string | 否   | 收/寄件人手机号后四位（顺丰 / 中通 / 跨越必填）  |

示例：

```json
{
  "number": "4303200322000",
  "type": "yunda"
}
```

## 返回结果示例

脚本直接输出接口的 `result` 字段，典型结构：

```json
{
  "number": "4303200322000",
  "type": "yunda",
  "typename": "韵达快运",
  "logo": "https://api.jisuapi.com/express/static/images/logo/80/yunda.png",
  "list": [
    {
      "time": "2019-12-30 20:24:51",
      "status": "北京分拨中心进行装车扫描，发往：辽宁大连分拨中心"
    },
    {
      "time": "2019-12-30 01:18:48",
      "status": "北京分拨中心进行中转集包扫描，发往：辽宁大连分拨中心"
    }
  ],
  "deliverystatus": 3,
  "issign": 1
}
```

错误时输出示例：

```json
{
  "error": "api_error",
  "code": 206,
  "message": "快递单号错误"
}
```

## 常见错误码

来自 [官方快递文档](https://www.jisuapi.com/api/express) 的业务错误码：

| 代号 | 说明                 |
|------|----------------------|
| 201  | 快递单号为空         |
| 202  | 快递公司为空         |
| 203  | 快递公司不存在       |
| 204  | 快递公司识别失败     |
| 205  | 没有信息             |
| 206  | 快递单号错误         |
| 208  | 单号没有信息（扣次） |
| 220  | 需要手机号后四位     |

系统错误码：

| 代号 | 说明                    |
|------|-------------------------|
| 101  | APPKEY 为空或不存在     |
| 102  | APPKEY 已过期           |
| 103  | APPKEY 无请求权限       |
| 104  | 请求超过次数限制        |
| 105  | IP 被禁止               |

## 在 OpenClaw 中的推荐用法

1. 用户例如：「帮我查一下单号 `4303200322000` 的快递，应该是韵达。」  
2. 代理构造：`python3 skills/express/express.py '{"number":"4303200322000","type":"yunda"}'`。  
3. 解析返回的 JSON，为用户总结：当前状态、是否签收、最近几条轨迹等。
