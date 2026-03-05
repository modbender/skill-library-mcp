---
name: points-recharge
description: 积分充值助手。当检测到余额不足、积分不足、充值积分、充值余额、查看套餐等关键词时，自动获取套餐列表并引导用户充值，生成支付二维码。
---

# 积分充值助手

当用户提到余额不足、积分不足、需要充值、查看套餐等需求时，按以下流程处理。

## 流程步骤

### 步骤 1：获取套餐列表

调用 MCP 工具获取可用套餐：

```
服务器: user-速推AI
工具: list_points_packages
参数: {}
```

### 步骤 2：展示套餐信息

以表格形式展示套餐，包含：
- 套餐ID
- 价格（元）
- 积分数量
- 额外赠送（如有）

同时显示用户当前余额和积分比例（1元=100积分）。

**输出模板：**

```markdown
| 套餐ID | 价格（元） | 积分数量 | 额外赠送 |
|--------|-----------|---------|---------|
| {id} | {money_yuan} 元 | {points_display} | {bonus} |

**积分比例**：1元 = 100积分
**当前余额**：{user_balance} 积分
```

### 步骤 3：询问充值选择

如果用户未指定金额和支付方式，使用 AskQuestion 工具询问：

1. 选择充值金额/套餐
2. 选择支付方式（微信/支付宝）

如果用户已明确指定，直接进入下一步。

### 步骤 4：生成支付二维码

调用 MCP 工具生成支付二维码：

```
服务器: user-速推AI
工具: create_payment_qrcode
参数:
  - package_id: 套餐ID（整数）
  - payment_method: "wechat" 或 "alipay"
```

### 步骤 5：展示支付信息

1. 下载二维码图片到本地
2. 打开图片供用户扫码
3. 展示订单信息

**输出模板：**

```markdown
支付二维码已生成并打开！

**订单信息：**
- 订单号：{order_no}
- 套餐：{title}
- 金额：{money_yuan} 元
- 充值积分：{points} 积分
- 支付方式：{payment_method_display}

请使用{支付方式}扫描二维码完成支付，支付成功后积分将自动到账。

支付完成后，可以告诉我「查询余额」确认积分是否到账。
```

### 步骤 6：查询余额（可选）

用户支付完成后，可调用 MCP 工具查询最新余额：

```
服务器: user-速推AI
工具: get_balance
参数: {}
```

**输出模板：**

```markdown
**当前余额**：{balance} 积分
```

## 支付方式映射

| 用户输入 | payment_method 参数 |
|---------|-------------------|
| 微信、微信支付、wechat | wechat |
| 支付宝、alipay | alipay |

## 二维码处理

返回结果可能包含两种格式：

1. **URL 格式** (`qrcode_url`)：
   ```bash
   curl -s "{qrcode_url}" -o payment_qrcode.png && open payment_qrcode.png
   ```

2. **Base64 格式** (`qrcode_base64`)：
   ```bash
   echo "{base64_string}" | base64 -d > payment_qrcode.png && open payment_qrcode.png
   ```

## 触发关键词

以下关键词触发此 skill：
- 余额不足
- 积分不足
- 充值积分
- 充值余额
- 查看套餐
- 积分套餐
- 购买积分
- 充值 XX 元
- 查询余额
- 我的余额
- 余额查询
