# 分析报告示例

## 分析功能概览

### 获取收益分析
```bash
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/returns" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 获取风险分析
```bash
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/risk" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 获取表现分析
```bash
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/performance" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 获取综合报告
```bash
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/full" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

## 响应示例

### 收益分析响应
```json
{
  "status": "success",
  "data": {
    "returns_analysis": {
      "time_period": "2026-01-01 to 2026-02-16",
      "total_return": 25000.50,
      "total_return_percentage": 25.0,
      "annualized_return": 18.5,
      "time_weighted_return": 22.3,
      "money_weighted_return": 20.8,
      "returns_by_period": {
        "daily": 0.42,
        "weekly": 2.15,
        "monthly": 8.75,
        "quarterly": 15.2,
        "yearly": 25.0
      },
      "returns_by_asset": [
        {
          "symbol": "BTC",
          "name": "Bitcoin",
          "return_amount": 2500.00,
          "return_percentage": 12.5,
          "contribution": 10.0
        },
        {
          "symbol": "ETH",
          "name": "Ethereum",
          "return_amount": 1250.00,
          "return_percentage": 25.0,
          "contribution": 5.0
        },
        {
          "symbol": "AAPL",
          "name": "Apple Inc.",
          "return_amount": 255.00,
          "return_percentage": 17.0,
          "contribution": 1.0
        }
      ],
      "benchmark_comparison": {
        "benchmark": "S&P 500",
        "benchmark_return": 8.2,
        "outperformance": 16.8,
        "alpha": 12.5,
        "information_ratio": 1.8
      }
    }
  }
}
```

### 风险分析响应
```json
{
  "status": "success",
  "data": {
    "risk_analysis": {
      "volatility_metrics": {
        "portfolio_volatility": 15.2,
        "benchmark_volatility": 12.8,
        "beta": 0.85,
        "correlation_with_benchmark": 0.72
      },
      "drawdown_analysis": {
        "current_drawdown": -2.1,
        "max_drawdown": -15.8,
        "max_drawdown_date": "2025-10-15",
        "recovery_period_days": 42,
        "calmar_ratio": 1.17
      },
      "value_at_risk": {
        "var_95_1d": -3.2,
        "var_99_1d": -5.8,
        "var_95_1m": -12.5,
        "var_99_1m": -18.2,
        "conditional_var": -7.5
      },
      "risk_decomposition": {
        "by_asset": [
          {
            "symbol": "BTC",
            "risk_contribution": 45.2,
            "marginal_risk": 12.8,
            "component_risk": 6.9
          },
          {
            "symbol": "ETH",
            "risk_contribution": 25.8,
            "marginal_risk": 8.5,
            "component_risk": 3.9
          },
          {
            "symbol": "AAPL",
            "risk_contribution": 5.2,
            "marginal_risk": 2.1,
            "component_risk": 0.8
          }
        ],
        "by_factor": {
          "market_risk": 68.5,
          "size_risk": 12.8,
          "value_risk": 8.2,
          "momentum_risk": 5.5,
          "idiosyncratic_risk": 5.0
        }
      },
      "stress_test_results": {
        "scenarios": [
          {
            "name": "Market Crash (-20%)",
            "portfolio_impact": -16.8,
            "worst_asset": "BTC",
            "worst_asset_impact": -25.2
          },
          {
            "name": "Interest Rate Hike",
            "portfolio_impact": -8.5,
            "worst_asset": "Bonds",
            "worst_asset_impact": -12.8
          },
          {
            "name": "Tech Sector Decline",
            "portfolio_impact": -5.2,
            "worst_asset": "AAPL",
            "worst_asset_impact": -15.8
          }
        ]
      }
    }
  }
}
```

### 表现分析响应
```json
{
  "status": "success",
  "data": {
    "performance_analysis": {
      "key_metrics": {
        "sharpe_ratio": 1.25,
        "sortino_ratio": 1.85,
        "treynor_ratio": 0.18,
        "jensen_alpha": 2.8,
        "information_ratio": 1.8,
        "up_capture": 112.5,
        "down_capture": 85.2
      },
      "performance_attribution": {
        "allocation_effect": 3.2,
        "selection_effect": 8.5,
        "interaction_effect": 1.8,
        "total_active_return": 13.5,
        "total_benchmark_return": 8.2
      },
      "rolling_performance": {
        "periods": [
          {
            "period": "1M",
            "portfolio_return": 8.75,
            "benchmark_return": 3.2,
            "outperformance": 5.55
          },
          {
            "period": "3M",
            "portfolio_return": 15.2,
            "benchmark_return": 6.8,
            "outperformance": 8.4
          },
          {
            "period": "6M",
            "portfolio_return": 22.8,
            "benchmark_return": 10.5,
            "outperformance": 12.3
          },
          {
            "period": "1Y",
            "portfolio_return": 25.0,
            "benchmark_return": 8.2,
            "outperformance": 16.8
          }
        ]
      },
      "consistency_analysis": {
        "positive_months": 9,
        "negative_months": 3,
        "win_rate": 75.0,
        "average_win": 3.2,
        "average_loss": -2.1,
        "profit_factor": 2.8
      }
    }
  }
}
```

### 综合报告响应
```json
{
  "status": "success",
  "data": {
    "comprehensive_report": {
      "report_date": "2026-02-16",
      "report_period": "2026-01-01 to 2026-02-16",
      "executive_summary": {
        "portfolio_value": 125000.50,
        "total_return": 25000.50,
        "return_percentage": 25.0,
        "risk_adjusted_return": "优秀",
        "overall_rating": "A",
        "key_insights": [
          "投资组合表现优于基准16.8%",
          "风险调整后收益表现优异（夏普比率1.25）",
          "加密货币持仓贡献了主要收益",
          "风险集中在市场风险因子"
        ]
      },
      "detailed_analysis": {
        "returns": {
          "summary": "收益表现强劲，大幅超越基准",
          "strengths": ["加密货币持仓收益突出", "股票选择效果良好"],
          "weaknesses": ["现金持仓收益较低", "债券配置不足"],
          "recommendations": ["考虑增加债券配置", "优化现金管理策略"]
        },
        "risk": {
          "summary": "风险水平适中，但集中度较高",
          "strengths": ["下行风险控制良好", "最大回撤在可接受范围"],
          "weaknesses": ["加密货币风险集中", "缺乏对冲工具"],
          "recommendations": ["分散加密货币持仓", "考虑加入对冲策略"]
        },
        "performance": {
          "summary": "风险调整后表现优异",
          "strengths": ["夏普比率优秀", "信息比率积极"],
          "weaknesses": ["在某些市场环境下表现不稳定"],
          "recommendations": ["加强市场环境适应性", "优化资产配置"]
        }
      },
      "action_items": [
        {
          "priority": "高",
          "action": "分散加密货币风险",
          "rationale": "当前加密货币持仓风险集中度过高",
          "timeline": "1个月内"
        },
        {
          "priority": "中",
          "action": "增加债券配置",
          "rationale": "改善资产配置平衡，降低整体风险",
          "timeline": "3个月内"
        },
        {
          "priority": "低",
          "action": "优化现金管理",
          "rationale": "提高现金资产收益",
          "timeline": "6个月内"
        }
      ],
      "next_review_date": "2026-03-16"
    }
  }
}
```

## 使用场景

### 场景1：生成月度投资报告
```bash
# 生成完整的月度分析报告
echo "=== 月度投资分析报告 ==="
curl -s "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/full?period=monthly" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes" | \
  jq '.data.comprehensive_report'
```

### 场景2：监控风险指标
```bash
# 监控关键风险指标
echo "=== 风险指标监控 ==="
curl -s "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/risk" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes" | \
  jq '.data.risk_analysis.volatility_metrics, .data.risk_analysis.drawdown_analysis'
```

### 场景3：评估投资表现
```bash
# 评估投资表现与基准对比
echo "=== 表现评估 ==="
curl -s "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/performance" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes" | \
  jq '.data.performance_analysis.key_metrics, .data.performance_analysis.rolling_performance'
```

## 高级查询参数

### 按时间范围分析
```bash
# 分析特定时间段的投资表现
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/returns?start_date=2026-01-01&end_date=2026-02-16" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 按分析深度
```bash
# 获取详细的分析报告
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/full?detail_level=high" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"

# 获取简化的分析报告
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/full?detail_level=low" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 按基准比较
```bash
# 使用特定基准进行比较
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/analytics/performance?benchmark=NASDAQ" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

## 分析指标说明

### 收益指标
- **总收益率**：投资组合的整体收益百分比
- **年化收益率**：折算为年率的收益率
- **时间加权收益率**：排除现金流影响的收益率
- **阿尔法**：超越基准的超额收益

### 风险指标
- **波动率**：投资组合收益的标准差
- **贝塔**：相对于市场基准的系统性风险
- **最大回撤**：从峰值到谷底的最大损失
- **在险价值**：在一定置信水平下的最大可能损失

### 表现指标
- **夏普比率**：风险调整后的收益（每单位风险的超额收益）
- **索提诺比率**：只考虑下行风险的风险调整收益
- **信息比率**：主动管理带来的超额收益与跟踪误差之比
- **捕获率**：在市场上涨/下跌时投资组合的表现

## 错误处理

### 常见错误响应
```json
{
  "status": "error",
  "error": {
    "code": "INSUFFICIENT_DATA",
    "message": "数据不足",
    "details": "至少需要30天的数据才能进行风险分析"
  }
}
```

```json
{
  "status": "error",
  "error": {
    "code": "BENCHMARK_UNAVAILABLE",
    "message": "基准不可用",
    "details": "请求的基准数据在当前时间段不可用"
  }
}
```

## 最佳实践

1. **定期分析**：建议每月进行一次完整的投资分析
2. **多维度评估**：结合收益、风险和表现多个维度进行评估
3. **基准对比**：始终与合适的基准进行比较
4. **趋势分析**：关注指标的变化趋势而不仅仅是绝对值
5. **行动导向**：分析结果应转化为具体的投资行动建议