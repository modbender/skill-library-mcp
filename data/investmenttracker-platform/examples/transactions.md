# 交易记录示例

## 基本查询

### 获取所有交易记录
```bash
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 获取最近交易记录
```bash
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions/recent" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 按交易类型筛选
```bash
# 只获取买入交易
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions?type=BUY" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"

# 只获取卖出交易
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions?type=SELL" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 按资产筛选
```bash
# 获取特定资产的交易记录
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions?symbol=BTC" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

## 响应示例

### 完整交易记录响应
```json
{
  "status": "success",
  "data": {
    "transactions": [
      {
        "id": "txn_20260216001",
        "date": "2026-02-16T10:30:00Z",
        "type": "BUY",
        "symbol": "BTC",
        "name": "Bitcoin",
        "asset_type": "crypto",
        "quantity": 0.1,
        "price": 42000.00,
        "total": 4200.00,
        "fee": 10.50,
        "exchange": "Binance",
        "wallet_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
        "status": "COMPLETED",
        "notes": "定期定投买入",
        "tags": ["dca", "long-term"]
      },
      {
        "id": "txn_20260215001",
        "date": "2026-02-15T14:20:00Z",
        "type": "SELL",
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_type": "stock",
        "quantity": 5,
        "price": 180.00,
        "total": 900.00,
        "fee": 2.25,
        "exchange": "Interactive Brokers",
        "account": "IBKR-12345",
        "status": "COMPLETED",
        "notes": "部分获利了结",
        "tags": ["profit-taking", "rebalance"]
      },
      {
        "id": "txn_20260214001",
        "date": "2026-02-14T09:15:00Z",
        "type": "BUY",
        "symbol": "ETH",
        "name": "Ethereum",
        "asset_type": "crypto",
        "quantity": 0.5,
        "price": 2400.00,
        "total": 1200.00,
        "fee": 3.00,
        "exchange": "Coinbase",
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e0BBE863FDB",
        "status": "COMPLETED",
        "notes": "加仓以太坊",
        "tags": ["accumulation", "defi"]
      },
      {
        "id": "txn_20260213001",
        "date": "2026-02-13T16:45:00Z",
        "type": "DIVIDEND",
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_type": "stock",
        "quantity": 10,
        "price": 0.24,
        "total": 2.40,
        "fee": 0.00,
        "exchange": "Interactive Brokers",
        "account": "IBKR-12345",
        "status": "COMPLETED",
        "notes": "季度股息",
        "tags": ["dividend", "income"]
      }
    ],
    "pagination": {
      "total": 4,
      "page": 1,
      "page_size": 50,
      "total_pages": 1
    },
    "summary": {
      "total_buy": 5400.00,
      "total_sell": 900.00,
      "total_dividend": 2.40,
      "total_fees": 15.75,
      "net_flow": 4502.40,
      "by_asset_type": {
        "crypto": 5400.00,
        "stock": 902.40
      },
      "by_month": {
        "2026-02": 6302.40
      }
    }
  }
}
```

### 最近交易记录响应
```json
{
  "status": "success",
  "data": {
    "transactions": [
      {
        "id": "txn_20260216001",
        "date": "2026-02-16T10:30:00Z",
        "type": "BUY",
        "symbol": "BTC",
        "quantity": 0.1,
        "price": 42000.00,
        "total": 4200.00,
        "status": "COMPLETED"
      },
      {
        "id": "txn_20260215001",
        "date": "2026-02-15T14:20:00Z",
        "type": "SELL",
        "symbol": "AAPL",
        "quantity": 5,
        "price": 180.00,
        "total": 900.00,
        "status": "COMPLETED"
      }
    ],
    "summary": {
      "last_7_days": {
        "transaction_count": 4,
        "total_volume": 6302.40,
        "buy_volume": 5400.00,
        "sell_volume": 900.00
      }
    }
  }
}
```

## 使用场景

### 场景1：查看本月交易活动
```bash
# 获取本月所有交易
echo "=== 本月交易活动 ==="
curl -s "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions?start_date=2026-02-01" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes" | \
  jq '.data.summary'
```

### 场景2：分析交易费用
```bash
# 分析交易费用支出
echo "=== 交易费用分析 ==="
curl -s "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes" | \
  jq '.data.transactions[] | {date: .date, symbol: .symbol, type: .type, fee: .fee, total: .total}'
```

### 场景3：生成交易报告
```bash
# 生成CSV格式的交易报告
echo "日期,类型,资产,数量,价格,总额,费用,状态" > transactions.csv
curl -s "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes" | \
  jq -r '.data.transactions[] | "\(.date),\(.type),\(.symbol),\(.quantity),\(.price),\(.total),\(.fee),\(.status)"' >> transactions.csv
```

## 高级查询参数

### 按时间范围筛选
```bash
# 获取特定时间段的交易记录
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions?start_date=2026-01-01&end_date=2026-02-16" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 分页查询
```bash
# 分页获取交易记录
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions?page=2&page_size=20" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 按状态筛选
```bash
# 只获取已完成的交易
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions?status=COMPLETED" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"

# 获取待处理的交易
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions?status=PENDING" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 按标签筛选
```bash
# 获取带有特定标签的交易
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions?tag=dca" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

## 交易类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| BUY | 买入资产 | 购买股票、加密货币等 |
| SELL | 卖出资产 | 出售持有的资产 |
| DIVIDEND | 股息收入 | 股票分红 |
| INTEREST | 利息收入 | 债券利息、存款利息 |
| DEPOSIT | 资金存入 | 向账户存入资金 |
| WITHDRAWAL | 资金取出 | 从账户取出资金 |
| TRANSFER | 资产转移 | 在不同账户间转移资产 |
| FEE | 费用支出 | 交易费、管理费等 |

## 错误处理

### 常见错误响应
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_DATE_FORMAT",
    "message": "无效的日期格式",
    "details": "日期格式应为 YYYY-MM-DD"
  }
}
```

```json
{
  "status": "error",
  "error": {
    "code": "NO_TRANSACTIONS_FOUND",
    "message": "未找到交易记录",
    "details": "在指定条件下未找到任何交易记录"
  }
}
```

## 最佳实践

1. **定期备份**：定期导出交易记录进行备份
2. **分类标签**：为交易添加有意义的标签便于筛选
3. **费用追踪**：密切监控交易费用对收益的影响
4. **税务准备**：保留完整的交易记录用于税务申报
5. **性能优化**：对历史交易记录使用分页查询