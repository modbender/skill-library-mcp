---
name: jisu-parts
description: 使用极速数据汽车配件OE信息查询 API，查询配件品牌、原厂零件号模糊搜索、零件号对应销售车型、替换件等信息。
metadata: { "openclaw": { "emoji": "🔧", "requires": { "bins": ["python3"], "env": ["JISU_API_KEY"] }, "primaryEnv": "JISU_API_KEY" } }
---

# 极速数据汽车配件OE信息查询（Jisu Parts）

基于 [汽车配件OE信息查询 API](https://www.jisuapi.com/api/parts/) 的 OpenClaw 技能，提供：

- **配件品牌**（`/parts/brand`）：获取配件品牌列表
- **原厂零件号模糊搜索**（`/parts/search`）：按零件号搜索 OE 信息及多品牌匹配
- **零件号查销售车型**（`/parts/salecar`）：查某零件号/品牌/零件 ID 对应的销售车型
- **查询替换件**（`/parts/replace`）：查某原厂件的替换件、品牌件

可用于对话中回答「这个零件号有哪些品牌在用」「L8WD807065K 适配哪些车」「04E115561C 的替换件有哪些」等问题。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/parts/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/parts/parts.py`

## 使用方式

### 1. 配件品牌（brand）

```bash
python3 skills/parts/parts.py brand
```

### 2. 原厂零件号模糊搜索（search）

```bash
python3 skills/parts/parts.py search '{"number":"L8WD807065KGRU"}'
```

### 3. 零件号查销售车型（salecar）

```bash
# 零件号 + 品牌ID
python3 skills/parts/parts.py salecar '{"number":"L8WD807065KGRU","brandid":219}'

# 仅品牌ID 或 仅零件ID 也可
python3 skills/parts/parts.py salecar '{"partsid":23064200}'
```

### 4. 查询替换件（replace）

```bash
# 零件号 + 品牌ID
python3 skills/parts/parts.py replace '{"number":"01402917258","brandid":10}'

# 或零件ID
python3 skills/parts/parts.py replace '{"partsid":12656367}'
```

## 请求参数摘要

| 子命令   | 必填/组合说明                    | 参数说明                          |
|----------|----------------------------------|-----------------------------------|
| brand    | 无参数                           | —                                 |
| search   | number（必填）                   | 零件号                            |
| salecar  | number / brandid / partsid 任选一或组合 | number、brandid、partsid 至少传一个 |
| replace  | partsid 或 number+brandid        | number、brandid、partsid 任选一组 |

## 返回结果说明

脚本直接输出接口的 `result` 字段（JSON）：

- **brand**：数组，每项含 `brandid`、`name`。
- **search**：对象，含 `list` 数组，每项含 `partsid`、`number`、`number2`、`brand`、`name`、`stdname`、`marketprice`、`remark` 等。
- **salecar**：对象，含 `brandid`、`number`、`number2`、`partsid`、`brand` 及 `list`（销售车型列表，含 `carid`、`fullname`、`price`、`yeartype`、`listdate`、`productionstate`、`salestate`、`sizetype`、`displacement`、`geartype` 等）。
- **replace**：对象，含 `partsid`、`name`、`brand`、`brandid`、`number` 及 `list`（替换件列表，含 `partsid`、`number`、`name`、`stdname`、`brandid`、`brand` 等）。

错误时输出形如：

```json
{
  "error": "api_error",
  "code": 202,
  "message": "配件ID错误"
}
```

## 常见错误码

来自 [官方汽车配件OE文档](https://www.jisuapi.com/api/parts/)：

| 代号 | 说明                 |
|------|----------------------|
| 201  | 零件ID和零件号不能都为空 |
| 202  | 配件ID错误           |
| 220  | 没有信息             |

系统错误码：101 APPKEY 为空或不存在、102 已过期、103 无权限、104 超过次数限制、105 IP 被禁止、106 IP 超限、107 接口维护中、108 接口已停用。

## 在 OpenClaw 中的推荐用法

1. 用户：「有哪些配件品牌？」→ `parts.py brand`。  
2. 用户：「零件号 L8WD807065KGRU 有哪些品牌？」→ `parts.py search '{"number":"L8WD807065KGRU"}'`。  
3. 用户：「这个零件能用在哪些车上？」→ 先 search 或确定 brandid/partsid，再 `parts.py salecar '{"number":"...","brandid":219}'`。  
4. 用户：「04E115561C 的替换件」→ `parts.py replace '{"number":"04E115561C","brandid":10}'` 或按零件 ID 查询，解析返回的 `list` 为用户总结。
