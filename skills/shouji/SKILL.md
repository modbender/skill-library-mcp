---
name: jisu-shouji
description: 使用极速数据手机号码归属地 API，根据手机号查询归属省市、运营商及卡类型。
metadata: { "openclaw": { "emoji": "📱", "requires": { "bins": ["python3"], "env": ["JISU_API_KEY"] }, "primaryEnv": "JISU_API_KEY" } }
---

# 极速数据手机号码归属地（Jisu Shouji）

基于 [手机号码归属地 API](https://www.jisuapi.com/api/shouji/) 的 OpenClaw 技能，
根据手机号查询其归属省市、运营商和卡类型。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/shouji/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/shouji/shouji.py`

## 使用方式

### 查询手机号码归属地

```bash
python3 skills/shouji/shouji.py '{"shouji":"13456755448"}'
```

请求 JSON 示例：

```json
{
  "shouji": "13456755448"
}
```

## 请求参数

| 字段名  | 类型   | 必填 | 说明   |
|--------|--------|------|--------|
| shouji | string | 是   | 手机号 |

## 返回结果示例

脚本直接输出接口的 `result` 字段，结构与官网示例一致（参考 [`https://www.jisuapi.com/api/shouji/`](https://www.jisuapi.com/api/shouji/)）：

```json
{
  "province": "浙江",
  "city": "杭州",
  "company": "中国移动",
  "cardtype": "GSM"
}
```

当出现错误（如手机号为空、不正确或无信息）时，脚本会输出：

```json
{
  "error": "api_error",
  "code": 202,
  "message": "手机号不正确"
}
```

## 常见错误码

来源于 [官方手机归属地文档](https://www.jisuapi.com/api/shouji/)：

| 代号 | 说明         |
|------|--------------|
| 201  | 手机号为空   |
| 202  | 手机号不正确 |
| 203  | 没有信息     |

系统错误码：

| 代号 | 说明                 |
|------|----------------------|
| 101  | APPKEY 为空或不存在  |
| 102  | APPKEY 已过期        |
| 103  | APPKEY 无请求权限    |
| 104  | 请求超过次数限制     |
| 105  | IP 被禁止            |

## 在 OpenClaw 中的推荐用法

1. 用户提供手机号（可部分打码展示给用户）：「查一下 `1345675****` 是哪里的号码，哪个运营商。」  
2. 代理构造 JSON：`{"shouji":"13456755448"}` 并调用：  
   `python3 skills/shouji/shouji.py '{"shouji":"13456755448"}'`  
3. 从返回结果中读取 `province`、`city`、`company`、`cardtype` 字段，为用户总结号码归属地和运营商类型。  

