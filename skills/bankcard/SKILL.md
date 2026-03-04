---
name: jisu-bankcard
description: 使用极速数据银行卡归属地查询 API，通过银行卡号查询银行、归属地信息，并鉴定银行卡号真伪。
metadata: { "openclaw": { "emoji": "💳", "requires": { "bins": ["python3"], "env": ["JISU_API_KEY"] }, "primaryEnv": "JISU_API_KEY" } }
---

# 极速数据银行卡归属地查询（Jisu Bankcard）

基于 [银行卡归属地查询 API](https://www.jisuapi.com/api/bankcard) 的 OpenClaw 技能，通过银行卡号查询银行、归属地信息，并鉴定银行卡号真伪。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/bankcard

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/bankcard/bankcard.py`

## 使用方式

传入一个 JSON 字符串，包含银行卡号：

```bash
python3 skills/bankcard/bankcard.py '{"bankcard":"6212261202011584349"}'
```

## 请求参数（传入 JSON）

| 字段名   | 类型   | 必填 | 说明     |
|----------|--------|------|----------|
| bankcard | string | 是   | 银行卡号 |

示例：

```json
{
  "bankcard": "6212261202011584349"
}
```

## 返回结果示例

脚本直接输出接口的 `result` 字段（JSON），典型结构：

```json
{
  "bankcard": "6212261202011594349",
  "name": "牡丹卡普卡",
  "province": "浙江",
  "city": "杭州",
  "type": "借记卡",
  "len": "19",
  "bank": "中国工商银行",
  "logo": "http://www.jisuapi.com/api/bankcard/upload/80/2.png",
  "tel": "95588",
  "website": "http://www.icbc.com.cn",
  "iscorrect": "0"
}
```

返回字段说明：

| 参数名    | 类型   | 说明                           |
|-----------|--------|--------------------------------|
| bankcard  | string | 银行卡号                       |
| name      | string | 卡名称                         |
| province  | string | 省                             |
| city      | string | 市                             |
| type      | string | 银行卡类型                     |
| len       | string | 卡号长度                       |
| bank      | string | 银行名称                       |
| logo      | string | 银行 logo（80/120/200 等尺寸） |
| tel       | string | 银行电话                       |
| website   | string | 银行网站                       |
| iscorrect | string | 卡号校验是否正确：1 正确，0 错误 |

错误时脚本输出形如：

```json
{
  "error": "api_error",
  "code": 202,
  "message": "银行卡号不正确"
}
```

## 常见错误码

来自 [官方银行卡 API 文档](https://www.jisuapi.com/api/bankcard)：

**业务错误码：**

| 代号 | 说明           |
|------|----------------|
| 201  | 银行卡号为空   |
| 202  | 银行卡号不正确 |
| 210  | 没有信息       |

**系统错误码：**

| 代号 | 说明                   |
|------|------------------------|
| 101  | APPKEY 为空或不存在    |
| 102  | APPKEY 已过期          |
| 103  | APPKEY 无请求此数据权限 |
| 104  | 请求超过次数限制       |
| 105  | IP 被禁止              |
| 106  | IP 请求超过限制        |
| 107  | 接口维护中             |
| 108  | 接口已停用             |

## 在 OpenClaw 中的推荐用法

1. 用户例如：「查一下卡号 6212261202011584349 是哪个银行的。」  
2. 代理构造：`python3 skills/bankcard/bankcard.py '{"bankcard":"6212261202011584349"}'`。  
3. 解析返回的 JSON，为用户总结：银行名称、归属地（省/市）、卡类型、卡号是否校验通过等。
