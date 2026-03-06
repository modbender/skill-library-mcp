---
name: MCP Server Skill Documentation
description: 暂无
---

# MCP Server Skill Documentation

## 1. 概述
**Skill Name:** Hyperbot Trading Analytics  
**Description:** 提供 Hyperbot 平台的交易数据分析能力，包括聪明钱追踪、鲸鱼监控、市场行情查询、交易统计等功能。适用于加密货币交易者进行市场分析和决策。  
**Version:** 1.0.0  
**MCP Server URL / Endpoint:** https://test-mcp.hyperbot.network/mcp

**sessionId:** 通过 SSE 获取的 sessionId https://test-mcp.hyperbot.network/mcp/sse

---

## 2. Resources（资源说明）

### 2.1 已定义的 Resource
暂无

**Usage Notes:**
- 只读资源，不会改变系统状态
- 可作为 prompt 输入或 Agent 决策参考
- 数据来源于 Hyperbot 平台和链上数据
- 支持按需拉取（分页 / 过滤条件）

---

## 3. Tools（工具说明）

### 3.1 排行榜与聪明钱发现

#### fetch_leader_board
**功能:** 获取 Hyperbot 聪明钱排行榜  
**参数:**
- `period`: 时间周期，可选值：24h, 7d, 30d
- `sort`: 排序字段，可选值：pnl (盈亏), winRate (胜率)

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"fetch_leader_board","arguments":{"period":"7d","sort":"pnl"}},"jsonrpc":"2.0","id":1}'
```

#### find_smart_money
**功能:** 发现聪明钱地址，支持多种排序方式筛选  
**参数:**
- `period`: 周期天数，如 7 表示最近 7 天
- `sort`: 排序方式，可选值：win-rate（胜率）、account-balance（账户余额）、ROI（收益率）、pnl（盈亏）、position-count（持仓数量）、profit-count（盈利次数）、last-operation（最后操作时间）、avg-holding-period（平均持仓周期）、current-position（当前持仓）
- `pnlList`: 是否需要 pnl 曲线数据 (true/false)

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"find_smart_money","arguments":{"period":7,"sort":"win-rate","pnlList":true}},"jsonrpc":"2.0","id":2}'
```

---

### 3.2 市场行情数据

#### get_tickers
**功能:** 查全市场最新交易价格  
**参数:** 无

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_tickers","arguments":{}},"jsonrpc":"2.0","id":3}'
```

#### get_ticker
**功能:** 查指定币种的最新交易价格  
**参数:**
- `address`: 币种代码，比如 btc, eth, sol

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_ticker","arguments":{"address":"ETH"}},"jsonrpc":"2.0","id":4}'
```

#### get_klines
**功能:** 获取 K 线数据（带交易量），支持 BTC、ETH 等币种  
**参数:**
- `coin`: 币种代码，比如 btc, eth
- `interval`: K 线周期，可选值：1m, 3m, 5m, 15m, 30m, 1h, 4h, 8h, 1d
- `limit`: 返回记录数量限制

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_klines","arguments":{"coin":"BTC","interval":"15m","limit":100}},"jsonrpc":"2.0","id":5}'
```

#### get_market_stats
**功能:** 查当前挂单统计（多空数量、价值、鲸鱼挂单占比）及全网中间价  
**参数:**
- `coin`: 币种代码，比如 btc, eth
- `whaleThreshold`: 鲸鱼阈值（单位：USDT）

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_market_stats","arguments":{"coin":"BTC","whaleThreshold":100000}},"jsonrpc":"2.0","id":6}'
```

#### get_l2_order_book
**功能:** 获取市场信息（L2 订单簿等）  
**参数:**
- `coin`: 币种代码，比如 btc, eth

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_l2_order_book","arguments":{"coin":"BTC"}},"jsonrpc":"2.0","id":7}'
```

---

### 3.3 鲸鱼监控

#### get_whale_positions
**功能:** 获取鲸鱼持仓信息  
**参数:**
- `coin`: 币种代码，比如 eth, btc
- `dir`: 方向，可选值：long (多头), short (空头)
- `pnlSide`: 盈亏筛选，可选值：profit (盈盈), loss (亏损)
- `frSide`: 资金费盈亏筛选，可选值：profit (盈), loss (亏)
- `topBy`: 排序方式，可选值：position-value (仓位价值), margin-balance (保证金余额), create-time (创建时间), profit (盈利), loss (亏损)
- `take`: 返回记录数量限制

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_whale_positions","arguments":{"coin":"BTC","dir":"long","pnlSide":"profit","frSide":"profit","topBy":"position-value","take":10}},"jsonrpc":"2.0","id":8}'
```

#### get_whale_events
**功能:** 实时监控巨鲸的最新开仓、平仓动态  
**参数:**
- `limit`: 返回记录数量限制

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_whale_events","arguments":{"limit":20}},"jsonrpc":"2.0","id":9}'
```

#### get_whale_directions
**功能:** 获取鲸鱼仓位多空数，可选筛选指定币种  
**参数:**
- `coin`: 币种代码，比如 eth, btc（可选）

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_whale_directions","arguments":{"coin":"BTC"}},"jsonrpc":"2.0","id":10}'
```

#### get_whale_history_ratio
**功能:** 获取历史鲸鱼仓位多空比  
**参数:**
- `interval`: 时间间隔，可选值：1h, 1d 或 hour, day
- `limit`: 返回记录数量限制

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_whale_history_ratio","arguments":{"interval":"1d","limit":30}},"jsonrpc":"2.0","id":11}'
```

---

### 3.4 交易者分析

#### fetch_trade_history
**功能:** 查询指定钱包地址的历史交易详情  
**参数:**
- `address`: 0x 开头的钱包地址

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"fetch_trade_history","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678"}},"jsonrpc":"2.0","id":12}'
```

#### get_trader_stats
**功能:** 获取交易统计  
**参数:**
- `address`: 用户钱包地址
- `period`: 周期天数

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_trader_stats","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","period":7}},"jsonrpc":"2.0","id":13}'
```

#### get_max_drawdown
**功能:** 获取最大回撤  
**参数:**
- `address`: 用户钱包地址
- `days`: 统计天数，可选值：1, 7, 30, 60, 90
- `scope`: 统计范围，默认 perp

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_max_drawdown","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","days":30,"scope":"perp"}},"jsonrpc":"2.0","id":14}'
```

#### get_best_trades
**功能:** 获取收益最高的交易  
**参数:**
- `address`: 用户钱包地址
- `period`: 天数
- `limit`: 返回记录数量限制

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_best_trades","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","period":7,"limit":10}},"jsonrpc":"2.0","id":15}'
```

#### get_performance_by_coin
**功能:** 拆解该地址在各币种上的独立胜率与盈亏表现  
**参数:**
- `address`: 用户钱包地址
- `period`: 天数
- `limit`: 返回记录数量限制

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_performance_by_coin","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","period":30,"limit":20}},"jsonrpc":"2.0","id":16}'
```

---

### 3.5 仓位历史

#### get_completed_position_history
**功能:** 获取已完成仓位历史，深度复盘某个币种当前或已完成仓位的完整历史数据  
**参数:**
- `address`: 用户钱包地址
- `coin`: 币种名称，如 BTC, ETH

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_completed_position_history","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","coin":"BTC"}},"jsonrpc":"2.0","id":17}'
```

#### get_current_position_history
**功能:** 获取当前仓位历史，获取指定币种的当前仓位的历史数据  
**参数:**
- `address`: 用户钱包地址
- `coin`: 币种名称，如 BTC, ETH

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_current_position_history","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","coin":"BTC"}},"jsonrpc":"2.0","id":18}'
```

#### get_completed_position_executions
**功能:** 获取已完成仓位操盘轨迹  
**参数:**
- `address`: 用户钱包地址
- `coin`: 币种名称，如 BTC, ETH
- `interval`: 时间周期，如 4h, 1d
- `startTime`: 开始时间戳（毫秒）
- `endTime`: 结束时间戳（毫秒）
- `limit`: 返回记录数量限制

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_completed_position_executions","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","coin":"BTC","interval":"4h","limit":50}},"jsonrpc":"2.0","id":19}'
```

#### get_current_position_pnl
**功能:** 获取当前仓位 PnL  
**参数:**
- `address`: 用户钱包地址
- `coin`: 币种名称，如 BTC, ETH
- `interval`: 时间周期，如 4h, 1d
- `limit`: 返回记录数量限制

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_current_position_pnl","arguments":{"address":"0x1234567890abcdef1234567890abcdef12345678","coin":"BTC","interval":"4h","limit":20}},"jsonrpc":"2.0","id":20}'
```

---

### 3.6 批量查询

#### get_traders_accounts
**功能:** 批量查询账户信息，最多支持 50 个地址  
**参数:**
- `addresses`: 地址列表，最多 50 个地址

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_traders_accounts","arguments":{"addresses":["0x1234567890abcdef1234567890abcdef12345678","0xabcdef1234567890abcdef1234567890abcdef12"]}},"jsonrpc":"2.0","id":21}'
```

#### get_traders_statistics
**功能:** 批量查询交易统计，最多支持 50 个地址  
**参数:**
- `period`: 周期天数，如 7 表示最近 7 天
- `pnlList`: 是否需要 pnl 曲线数据
- `addresses`: 地址列表，最多 50 个地址

**MCP 工具调用示例:**
```bash
curl 'https://test-mcp.hyperbot.network/mcp/message?sessionId=通过 sse 获得的 sessionId' \
  -H 'content-type: application/json' \
  --data-raw '{"method":"tools/call","params":{"name":"get_traders_statistics","arguments":{"period":7,"pnlList":true,"addresses":["0x1234567890abcdef1234567890abcdef12345678","0xabcdef1234567890abcdef1234567890abcdef12"]}},"jsonrpc":"2.0","id":22}'
```

---

## 4. Prompts（提示词说明）

| Prompt Name | Purpose | Template / Example |
|-------------|--------|------------------|
| smart-money-analysis | 聪明钱地址分析与操作建议 | ```你是量化交易专家。分析输入的聪明钱地址数据：1. 识别高胜率地址特征 2. 分析其持仓偏好和交易风格 3. 给出跟随策略建议 输出 JSON 格式``` |
| whale-tracking | 鲸鱼行为分析与市场影响评估 | ```分析鲸鱼持仓数据和最新动向：1. 判断主力意图 2. 评估对市场的影响 3. 预测短期走势 4. 给出操作建议 输出 JSON 格式``` |
| market-sentiment | 市场情绪分析 | ```基于市场数据（订单簿、挂单统计、鲸鱼多空比）：1. 分析当前市场情绪 2. 识别支撑阻力位 3. 判断短期趋势 输出 JSON 格式``` |
| trader-evaluation | 交易者能力评估 | ```全面评估交易者的能力：1. 分析胜率和盈亏比 2. 评估风险控制能力 3. 分析币种偏好 4. 给出综合评分和改进建议 输出 JSON 格式``` |

**Usage Notes:**  
- Prompts 可动态填充 resources 内容  
- 可以组合多个 prompts 形成推理链  
- 推荐遵循 JSON 输出规范，便于 Agent 解析

---

## 5. 使用示例

### 示例 1：发现并分析聪明钱地址

1. 调用 Tool: `find_smart_money(7, "win-rate", true)`
2. 获取高胜率聪明钱地址列表
3. 使用 Prompt: `smart-money-analysis` 分析这些地址的特征
4. 生成分析报告和跟随建议

### 示例 2：鲸鱼行为监控

1. 调用 Tool: `get_whale_events(20)` 获取最新鲸鱼动态
2. 调用 Tool: `get_whale_directions("BTC")` 查看 BTC 鲸鱼多空比
3. 使用 Prompt: `whale-tracking` 分析鲸鱼行为
4. 生成市场影响评估报告

### 示例 3：特定交易者深度分析

1. 调用 Tool: `get_trader_stats(address, 30)` 获取基础统计
2. 调用 Tool: `get_performance_by_coin(address, 30, 20)` 查看币种表现
3. 调用 Tool: `get_completed_position_history(address, "BTC")` 查看历史仓位
4. 使用 Prompt: `trader-evaluation` 生成综合评估报告

### 示例 4：市场情绪综合分析

1. 调用 Tool: `get_all_mids()` 获取全市场中间价
2. 调用 Tool: `get_l2_order_book("BTC")` 获取订单簿数据
3. 调用 Tool: `get_market_stats("BTC", 100000)` 获取挂单统计
4. 调用 Tool: `get_whale_history_ratio("1d", 30)` 获取历史多空比
5. 使用 Prompt: `market-sentiment` 生成市场情绪分析报告

---

## 6. 注意事项

### MCP 调用说明
- **sessionId**: 需要先通过 SSE 连接获取会话 ID，Get访问 https://test-mcp.hyperbot.network/mcp/sse
- **JSON-RPC 2.0**: 遵循标准的 JSON-RPC 2.0 协议
- **method**: 固定为 `tools/call`
- **params.name**: MCP 工具名称（对应 @McpTool 注解的 name 属性）
- **params.arguments**: 工具参数，键值对形式传递

### 限流说明
- 单个 IP 请求频率限制：100 次/分钟
- 批量接口最多支持 50 个地址

### 数据更新频率
- 行情数据：实时更新
- 聪明钱排行榜：每小时更新
- 鲸鱼持仓：实时更新
- 交易统计数据：每 5 分钟更新
