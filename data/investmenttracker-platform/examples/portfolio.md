# 投资组合示例

## 基本查询

### 获取完整投资组合
```bash
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 获取投资组合摘要
```bash
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio/summary" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 获取特定资产持仓
```bash
# 查询比特币持仓
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio/BTC" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"

# 查询苹果股票持仓
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio/AAPL" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

## 响应示例

### 完整投资组合响应
```json
{
  "status": "success",
  "data": {
    "portfolio_id": "port_123456",
    "owner": "user_789",
    "total_value": 125000.50,
    "total_invested": 100000.00,
    "total_return": 25000.50,
    "return_percentage": 25.0,
    "last_updated": "2026-02-16T12:00:00Z",
    "assets": [
      {
        "symbol": "BTC",
        "name": "Bitcoin",
        "asset_type": "crypto",
        "quantity": 0.5,
        "current_price": 45000.00,
        "current_value": 22500.00,
        "cost_basis": 20000.00,
        "average_cost": 40000.00,
        "unrealized_gain": 2500.00,
        "unrealized_gain_percentage": 12.5,
        "weight": 18.0,
        "allocation": {
          "percentage": 18.0,
          "target": 20.0,
          "deviation": -2.0
        }
      },
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_type": "stock",
        "quantity": 10,
        "current_price": 175.50,
        "current_value": 1755.00,
        "cost_basis": 1500.00,
        "average_cost": 150.00,
        "unrealized_gain": 255.00,
        "unrealized_gain_percentage": 17.0,
        "weight": 1.4,
        "allocation": {
          "percentage": 1.4,
          "target": 2.0,
          "deviation": -0.6
        }
      },
      {
        "symbol": "ETH",
        "name": "Ethereum",
        "asset_type": "crypto",
        "quantity": 2.5,
        "current_price": 2500.00,
        "current_value": 6250.00,
        "cost_basis": 5000.00,
        "average_cost": 2000.00,
        "unrealized_gain": 1250.00,
        "unrealized_gain_percentage": 25.0,
        "weight": 5.0,
        "allocation": {
          "percentage": 5.0,
          "target": 5.0,
          "deviation": 0.0
        }
      }
    ],
    "summary": {
      "by_asset_type": {
        "crypto": 28750.00,
        "stock": 1755.00,
        "cash": 94595.50
      },
      "by_risk_level": {
        "high": 28750.00,
        "medium": 1755.00,
        "low": 94595.50
      },
      "performance": {
        "daily_change": 1250.50,
        "daily_change_percentage": 1.01,
        "weekly_change": 5250.25,
        "weekly_change_percentage": 4.38,
        "monthly_change": 12500.75,
        "monthly_change_percentage": 11.11
      }
    }
  }
}
```

### 投资组合摘要响应
```json
{
  "status": "success",
  "data": {
    "total_value": 125000.50,
    "total_invested": 100000.00,
    "total_return": 25000.50,
    "return_percentage": 25.0,
    "asset_count": 3,
    "last_updated": "2026-02-16T12:00:00Z",
    "top_holdings": [
      {
        "symbol": "BTC",
        "name": "Bitcoin",
        "value": 22500.00,
        "weight": 18.0,
        "return_percentage": 12.5
      },
      {
        "symbol": "ETH",
        "name": "Ethereum",
        "value": 6250.00,
        "weight": 5.0,
        "return_percentage": 25.0
      },
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "value": 1755.00,
        "weight": 1.4,
        "return_percentage": 17.0
      }
    ],
    "performance_metrics": {
      "sharpe_ratio": 1.25,
      "volatility": 15.2,
      "max_drawdown": -8.5,
      "beta": 0.85
    }
  }
}
```

## 使用场景

### 场景1：每日投资组合检查
```bash
# 获取今日投资组合概览
echo "=== 今日投资组合概览 ==="
curl -s "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio/summary" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes" | jq '.data'
```

### 场景2：资产配置分析
```bash
# 分析资产配置情况
echo "=== 资产配置分析 ==="
curl -s "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes" | \
  jq '.data.assets[] | {symbol: .symbol, type: .asset_type, value: .current_value, weight: .weight}'
```

### 场景3：收益表现监控
```bash
# 监控投资收益表现
echo "=== 收益表现监控 ==="
curl -s "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes" | \
  jq '.data.summary.performance'
```

## 高级查询参数

### 按时间范围筛选
```bash
# 获取特定时间段的投资组合快照
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio?start_date=2026-01-01&end_date=2026-02-16" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 按资产类型筛选
```bash
# 只获取加密货币持仓
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio?asset_type=crypto" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 获取详细分析
```bash
# 获取包含详细分析的投资组合数据
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio?include_analysis=true" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

## 错误处理

### 常见错误响应
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_TOKEN",
    "message": "无效的认证令牌",
    "details": "请检查API密钥是否正确"
  }
}
```

```json
{
  "status": "error",
  "error": {
    "code": "ASSET_NOT_FOUND",
    "message": "资产未找到",
    "details": "符号 'XYZ' 不在投资组合中"
  }
}
```

## 最佳实践

1. **定期查询**：建议每天查询一次投资组合数据
2. **缓存结果**：对不频繁变化的数据使用缓存
3. **错误重试**：实现指数退避重试机制
4. **数据验证**：验证API响应的数据完整性
5. **安全存储**：安全存储API密钥和敏感数据