---
name: intelligent-diagnosis-report
display_name: 智能诊断报告
version: "0.1.0"
description: |
  创建智能诊断报告：根据商家名称，自动生成诊断报告，分析近30天经营数据对比。
metadata: { "openclaw": { "emoji": "📊" } }
triggers:
  - intent: 创建智能诊断报告
    keywords:
      - 诊断报告
      - 诊断
      - 生成报告
      - 商家诊断
      - 直播间诊断
      - 分析报告
      - 小米官方直播间
      - 帮我诊断一下
      - 数据诊断
    examples: |
      请生成小米官方直播间的诊断报告。
      我想看小米直播间的诊断信息。
      给小米官方直播间创建一个诊断报告。
      诊断一下小米官方直播间。

---

# 📊 智能诊断报告

## 什么时候必须用本技能（强规则）

当用户要求生成特定商家的诊断报告，例如：

- 生成/创建诊断报告
- 想看XX商家的诊断信息
- 分析XX直播间的数据
- 为XX商家做诊断

用户明确指定商家名称（如“小米官方直播间”），期望获得一份结构化的诊断报告，对比近30天与当前日期的数据。

## 什么时候不要用

- 用户只是询问一般性诊断概念，不需要具体商家报告
- 用户想查看已有报告而不是创建新报告
- 用户没有提供商家名称

---

# ✅ 固定流程（按顺序执行，任一步失败立刻返回错误）

## Step 1：解析商家名称并获取商家ID

baseUrl: http://baomai-assistant.internal

接口：
POST http://baomai-assistant.internal/gateway/crm/seller/manager/querySellerSearchResult

请求体：
```json
{
    "username": "${username}",
    "sellerName": "${sellerName}"
}
```

其中：
- `${sellerName}` 从用户问题中解析得到商家名称（例如用户的问题是“请生成小米官方直播间的诊断报告”，sellerName则是“小米官方直播间”）
- `${username}` 从本地凭证中获取（如 `~/.openclaw/managerId`），若未配置则使用默认值 "qinliujie"

正确的请求体格式如下：
```json
{
    "username": "qinliujie",
    "sellerName": "小米官方直播间"
}
```

响应结构（示例）：
```json
{
  "status": 200,
  "statusText": "OK",
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": [
    "1001234567",
    "1001234568",
    "1001234569"
  ]
}
```

从响应 `body[]` 提取数组里的第一个值：
- `sellerId`：数组里的第一个值
**商家选择规则**：
- 如果返回多条商家记录（可能因名称模糊），请只返回查询结果里的第一个sellerId：

## Step 2：创建诊断报告

baseUrl: http://baomai-assistant.internal

接口：
POST http://baomai-assistant.internal/gateway/diagnostic/report/create

请求体：
```json
{
    "sellerName": "${sellerName}",
    "sellerId": "${sellerId}",
    "endDate": "${endDate}",
    "beginDate": "${beginDate}"
}
```
请求体里面的参数一定按照下面的规则填充：
- `${sellerName}` 从用户问题中解析得到商家名称（例如用户的问题是“请生成小米官方直播间的诊断报告”，sellerName则是“小米官方直播间”）
- `${sellerId}` 使用第一步获取商家的ID，只保留body最前面的1个
- `${endDate}` 当前日期，格式 YYYY-MM-DD（例如 2026-02-28）
- `${beginDate}` 30天前的日期，格式 YYYY-MM-DD（例如 2026-01-29）
计算逻辑：beginDate = endDate - 30 days。
正确的请求体格式如下：
```json
{
    "sellerName": "小米官方直播间",
    "sellerId": 896519214,
    "endDate": "2026-02-28",
    "beginDate": "2026-01-29"
}
```
响应结构（示例）：
```json
{
  "code": 200,
  "data": {
    "reportId": 123456,
    "reportUrl": "https://baomai-inf.corp.kuaishou.com/report/123456"
  }
}
```

从响应提取：
- `reportId`
- `reportUrl`（如果有）

---

# 🧠 选择与记忆规则（简单、可执行）

## managerId

`managerId` 从本地凭证中读取（例如 `~/.openclaw/managerId`），若不存在则使用默认值 "qinliujie"。

## 商家选择

- 如果 Step 1 返回多个商家，需要用户选择。可将最近选择的商家ID缓存（可选），但一般不强制。

---

# 🧾 输出格式（统一）

成功创建后，输出以下内容：

```
✅ 诊断报告创建成功！

商家：${sellerName}
报告ID：${reportId}
报告链接：${reportUrl}
报告时间范围：${beginDate} 至 ${endDate}

报告已生成，可通过链接查看详细诊断分析。
```

如果响应中没有提供 `reportUrl`，则省略链接部分。

---

# ❗ 错误处理（必须）

任一步满足以下条件则失败：

- HTTP 非 2xx
- 响应缺少预期字段
- 服务返回错误码/错误信息（如 code != 200）

失败时：原样返回该步 message / 错误信息（不编造），并提示用户可能的原因（如商家名称不准确、系统异常等）。



