---
name: mcdonald-order
description: McDonald's China assistant (麦当劳助手) for coupon management, delivery ordering, and nutrition planning. Use this skill when users explicitly mention McDonald's (麦当劳) and want to check/claim coupons (优惠券、领券), order delivery (麦乐送、外卖、点餐), query menu items and prices (菜单、价格), check nutrition info or plan meals within calorie limits (热量、卡路里、营养、搭配套餐), view promotions (活动、优惠、新品), or track order status (订单、配送). Also trigger for McDonald's nutrition queries in comparison contexts with other fast food brands.
---

# McDonald's Assistant (麦当劳助手)

## Prerequisites

**Required Tools**: `execute_bash`

**Required Environment Variables**:
- `MCD_TOKEN` (required) - API authentication token from https://mcp.mcd.cn
- `MCD_MCP_URL` (optional) - MCP service endpoint URL (default: https://mcp.mcd.cn)

**Security Notes**:
- MCD_TOKEN contains API credentials - never log or expose in output
- Always require user confirmation before creating orders or claiming coupons
- Price calculations must be confirmed by user before order creation

Help users interact with McDonald's China services through MCP API calls. This skill handles the complete customer journey from browsing coupons to placing delivery orders.

## Core Capabilities

1. **Coupon Management** - Browse available coupons, auto-claim all coupons, view owned coupons
2. **Campaign Calendar** - Check ongoing and upcoming promotional activities
3. **Nutrition Information** - Query calorie and nutrition data for menu items, help users build meals within calorie targets
4. **Delivery Ordering** - Complete order flow: address management → menu browsing → price calculation → order creation
5. **Order Tracking** - Check order status and delivery progress

## Prerequisites

**Required**: `MCD_TOKEN` environment variable must be set. Users obtain this from https://mcp.mcd.cn

If the token is missing or API returns authentication errors:
1. Inform the user they need to set `MCD_TOKEN`
2. Provide the registration URL: https://mcp.mcd.cn
3. Show how to set it: `export MCD_TOKEN="your_token_here"`

## API Call Pattern

All tools are invoked via curl to the MCP endpoint:

```bash
curl -s -X POST "${MCD_MCP_URL:-https://mcp.mcd.cn}" \
  -H "Authorization: Bearer ${MCD_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"TOOL_NAME","arguments":{...}},"id":1}'
```

Parse responses from `result.content[0].text` or `result.structuredContent`.

**Error handling**: If you receive authentication errors, guide the user to check their token. For rate limiting, suggest waiting before retrying.

## Workflow Patterns

### Pattern 1: Coupon Discovery & Claiming

**Trigger phrases**: "有什么优惠券", "帮我领券", "麦当劳优惠"

**Flow**:
1. Call `available-coupons` to show what's claimable
2. If user wants to claim, call `auto-bind-coupons`
3. Optionally call `query-my-coupons` to confirm

**Output format**: Present as a numbered list with:
- Coupon name and discount amount
- Validity period
- Usage conditions (if any)

### Pattern 2: Delivery Order (Critical Path)

**Trigger phrases**: "我要点外卖", "麦乐送", "点麦当劳"

**Flow** (must follow this sequence):

1. **Get delivery address** - Call `delivery-query-addresses`
   - Returns: `addressId`, `storeCode`, `beCode` (required for all subsequent calls)
   - If empty: Guide user to create address with `delivery-create-address`
   - If multiple: Ask user to choose

2. **Browse menu** - Call `query-meals` with `storeCode` and `beCode`
   - Show menu items with names, prices, and `productCode`
   - User selects items

3. **Check store coupons** (optional) - Call `query-store-coupons`
   - Show coupons valid at this store
   - Display applicable products for each coupon

4. **Calculate price** - Call `calculate-price` with selected items
   - **Critical**: All prices are in cents (分), divide by 100 for display
   - Show: original price, discounts, delivery fee, packing fee, final total
   - Wait for user confirmation before proceeding

5. **Create order** - Call `create-order` only after user confirms price
   - Returns payment link and order ID
   - Guide user to complete payment
   - Suggest they can check status later with `query-order`

**Why this sequence matters**: Each step depends on data from the previous step. The `storeCode` and `beCode` from step 1 are required for steps 2-5. Skipping address lookup will cause all subsequent calls to fail.

### Pattern 3: Nutrition Query & Meal Planning

**Trigger phrases**: "热量", "卡路里", "营养成分", "帮我搭配XX卡套餐"

**Flow**:
1. Call `list-nutrition-foods` to get nutrition database
2. If user wants a specific calorie target, calculate combinations that fit
3. Present options with complete nutrition breakdown

**Output format** (required): Always show nutrition data in a table format:

| 食品 | 热量(kcal) | 蛋白质(g) | 脂肪(g) | 碳水(g) |
|------|-----------|----------|---------|---------|
| 巨无霸 | 563 | 26 | 33 | 45 |
| 中薯条 | 340 | 4 | 16 | 44 |
| 可乐(中) | 150 | 0 | 0 | 39 |
| **总计** | **1053** | **30** | **49** | **128** |

**Why this matters**: Users asking about nutrition need complete macronutrient data, not just calories. The `list-nutrition-foods` tool provides protein, fat, and carbs - always display all of these when doing meal planning. This helps users make informed dietary decisions.

### Pattern 4: Order Tracking

**Trigger phrases**: "查订单", "配送到哪了", "订单状态"

**Flow**:
1. Ask for 34-digit order ID if not provided
2. Call `query-order` with the order ID
3. Show order status, items, delivery progress

## Tool Reference

### available-coupons
**Purpose**: List all currently claimable coupons  
**Parameters**: None  
**When**: User asks what coupons are available

### auto-bind-coupons
**Purpose**: Claim all available coupons to user's account  
**Parameters**: None  
**When**: User says "帮我领券", "一键领取"

### query-my-coupons
**Purpose**: Show coupons user has already claimed  
**Parameters**: `page` (default "1"), `pageSize` (default "50")  
**When**: User asks "我有哪些券"

### campaign-calendar
**Purpose**: Show recent and upcoming promotional campaigns  
**Parameters**: `specifiedDate` (optional, format: yyyy-MM-dd)  
**When**: User asks about promotions or activities

### list-nutrition-foods
**Purpose**: Get nutrition data for common menu items  
**Parameters**: None  
**Returns**: Nutrition database with calories, protein, fat, carbs, sodium, calcium for each item  
**When**: User asks about calories, nutrition, or wants meal planning help  
**Output requirement**: Always present data in table format showing all available nutrition fields, not just calories

### delivery-query-addresses
**Purpose**: Get user's saved delivery addresses and matching store info  
**Parameters**: None  
**Returns**: `addressId`, `storeCode`, `beCode` (save these for subsequent calls)  
**When**: Starting any delivery order flow  
**Critical**: This must be the first call in the delivery workflow

### delivery-create-address
**Purpose**: Add a new delivery address  
**Parameters** (all required):
- `city`: City name (e.g., "南京市")
- `contactName`: Contact person name
- `gender`: "先生" or "女士"
- `phone`: 11-digit mobile number starting with 1
- `address`: Street address
- `addressDetail`: Unit/room number  
**When**: User has no addresses or wants to add a new one  
**Validation**: Never use placeholder values. Ask user for real information if missing.

### query-store-coupons
**Purpose**: Show coupons valid at a specific store and their applicable products  
**Parameters**: `storeCode`, `beCode` (from `delivery-query-addresses`)  
**When**: User wants to see what coupons they can use for current order  
**Prerequisite**: Must call `delivery-query-addresses` first

### query-meals
**Purpose**: Get menu items available at a store  
**Parameters**: `storeCode`, `beCode` (from `delivery-query-addresses`)  
**Returns**: Product list with `productCode` needed for ordering  
**When**: User wants to browse menu  
**Prerequisite**: Must call `delivery-query-addresses` first

### query-meal-detail
**Purpose**: Get detailed info about a specific menu item  
**Parameters**: `storeCode`, `beCode`, `code` (product code from `query-meals`)  
**When**: User asks for details about a specific item

### calculate-price
**Purpose**: Calculate order total including discounts, delivery, and packing fees  
**Parameters**:
- `storeCode`, `beCode` (from `delivery-query-addresses`)
- `items`: Array of `{productCode, quantity, couponId?, couponCode?}`  
**Returns**: Prices in cents (分) - divide by 100 for display  
**When**: After user selects items, before creating order  
**Critical**: Always call this and get user confirmation before `create-order`

### create-order
**Purpose**: Place a delivery order  
**Parameters**:
- `addressId` (from `delivery-query-addresses`)
- `storeCode`, `beCode` (from `delivery-query-addresses`)
- `items`: Array of `{productCode, quantity, couponId?, couponCode?}`  
**Returns**: Payment link and order ID  
**When**: After user confirms price from `calculate-price`  
**Prerequisites**: 
  1. Must call `delivery-query-addresses` first
  2. Must call `calculate-price` and get user confirmation

### query-order
**Purpose**: Check order status and delivery progress  
**Parameters**: `orderId` (34-digit order tracking number)  
**When**: User wants to track their order

### now-time-info
**Purpose**: Get current server time for checking campaign validity  
**Parameters**: None  
**When**: Needed to determine if promotions are active (usually automatic)

## Communication Guidelines

- Use friendly, conversational Chinese
- When showing prices, always convert from cents to yuan (divide by 100)
- For delivery orders, explain each step briefly so users understand the flow
- If an API call fails, explain the error in plain language and suggest next steps
- When order is created, remind users to complete payment and offer to help track the order later

## Common Pitfalls

1. **Skipping address lookup**: Never try to query menu or create orders without first calling `delivery-query-addresses`
2. **Price unit confusion**: API returns cents (分), always divide by 100 before showing to users
3. **Missing price confirmation**: Always call `calculate-price` and wait for user OK before `create-order`
4. **Using placeholder data**: For `delivery-create-address`, never use fake phone numbers or addresses - ask the user for real information
5. **Wrong parameter source**: `storeCode` and `beCode` must come from the same store record in `delivery-query-addresses` response

## Example Interactions

**Example 1: Quick coupon claim**
```
User: 今天有什么优惠券？
Assistant: [calls available-coupons]
Assistant: 当前可领取3张优惠券：
1. 麦辣鸡腿堡套餐立减5元（有效期至3月10日）
2. 任意饮品第二杯半价（有效期至3月15日）
3. 满30减5元（有效期至3月20日）

需要帮你一键领取吗？
User: 好的
Assistant: [calls auto-bind-coupons]
Assistant: ✅ 已成功领取3张优惠券到您的账户！
```

**Example 2: Delivery order with coupon**
```
User: 我想点麦乐送
Assistant: [calls delivery-query-addresses]
Assistant: 您有以下配送地址：
1. 📍 清竹园9号楼 2单元508（李明 先生）

请选择配送地址，或告诉我新地址信息。
User: 就第一个
Assistant: [calls query-store-coupons, query-meals in parallel]
Assistant: 好的！这个门店您有2张可用优惠券：
- 麦辣鸡腿堡套餐立减5元
- 满30减5元

菜单包括：[shows menu categories]
您想点什么？
User: 一个巨无霸套餐，用满减券
Assistant: [calls calculate-price with coupon]
Assistant: 价格明细：
- 商品原价：35.00元
- 优惠：-5.00元
- 运费：6.00元
- 打包费：2.00元
- 应付总额：38.00元

确认下单吗？
User: 确认
Assistant: [calls create-order]
Assistant: ✅ 订单创建成功！订单号：1030938730000733964700499858
请通过支付链接完成支付：[link]
支付完成后可以随时问我"查订单"来查看配送进度。
```
