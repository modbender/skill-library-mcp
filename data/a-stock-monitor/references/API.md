# API文档

## 基础信息

- **基础URL**: `http://localhost:5000/api`
- **响应格式**: JSON
- **认证**: 需要登录（默认密码：stock2024）

## 端点列表

### 1. 市场情绪 - GET /api/market/sentiment

获取全市场5000+只股票的综合情绪评分。

**请求示例**:
```bash
curl http://localhost:5000/api/market/sentiment
```

**响应示例**:
```json
{
  "status": "success",
  "score": 57,
  "level": "偏乐观",
  "emoji": "🟢",
  "description": "市场偏强，情绪稳定 · 涨停15只 跌停3只 · 强势股108只 弱势股104只 · 平均换手4.22% 波动率3.95%",
  "stats": {
    "total": 5000,
    "gainers": 2460,
    "losers": 2534,
    "limit_up": 15,
    "limit_down": 3,
    "strong_stocks": 108,
    "weak_stocks": 104,
    "avg_change": 0.35,
    "avg_turnover": 4.22,
    "avg_volatility": 3.95
  },
  "is_historical": false,
  "data_time": "2026-02-24 14:55:00",
  "demo_mode": false
}
```

**字段说明**:
- `score`: 情绪评分 (0-100)
- `level`: 情绪等级 (极度悲观/悲观/偏悲观/中性/偏乐观/乐观/极度乐观)
- `emoji`: 情绪表情
- `is_historical`: 是否为历史数据
- `demo_mode`: 是否为演示模式

### 2. 监控股票列表 - GET /api/stocks

获取所有监控股票的完整数据（含技术指标、资金流）。

**请求示例**:
```bash
curl http://localhost:5000/api/stocks
```

**响应示例**:
```json
{
  "status": "success",
  "data": [
    {
      "code": "600900",
      "name": "长江电力",
      "price": 26.85,
      "change_pct": -0.52,
      "volume": 158900000,
      "amount": 4267850000,
      "update_time": "2026-02-24 14:55:00",
      "fund_flow": {
        "main_in": -128500000,
        "super_in": -85200000,
        "big_in": -43300000,
        "mid_in": 45600000,
        "small_in": 82900000
      },
      "tech_indicators": {
        "rsi": 45.2,
        "macd": -0.15,
        "kdj_k": 38.5,
        "kdj_d": 42.1
      }
    }
  ],
  "timestamp": "2026-02-24 14:55:05"
}
```

### 3. 实时价格 - GET /api/stocks/realtime

获取监控股票的实时价格（轻量级，仅价格和涨跌）。

**请求示例**:
```bash
curl http://localhost:5000/api/stocks/realtime
```

**响应示例**:
```json
{
  "status": "success",
  "data": [
    {
      "code": "600900",
      "name": "长江电力",
      "price": 26.85,
      "change_pct": -0.52,
      "update_time": "2026-02-24 14:55:00"
    }
  ],
  "timestamp": "2026-02-24 14:55:05"
}
```

**使用场景**: 前端实时轮询（每5秒）

### 4. 股票详情 - GET /api/stock/<code>

获取单只股票的详细信息。

**请求示例**:
```bash
curl http://localhost:5000/api/stock/600900
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "code": "600900",
    "name": "长江电力",
    "price": 26.85,
    "change_pct": -0.52,
    "volume": 158900000,
    "amount": 4267850000,
    "turnover": 1.25,
    "amplitude": 2.18,
    "update_time": "2026-02-24 14:55:00",
    "fund_flow": {...},
    "tech_indicators": {...}
  }
}
```

### 5. 市场总览 - GET /api/market/overview (已废弃)

该端点已被移除，请使用 `/api/market/sentiment` 替代。

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 401 | 未授权（需要登录） |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

## 数据更新频率

| 端点 | 缓存时间 | 更新频率 |
|------|----------|----------|
| /api/market/sentiment | 30分钟 | 交易时间每5分钟 |
| /api/stocks | 实时 | 每次请求 |
| /api/stocks/realtime | 实时 | 每次请求 |
| /api/stock/<code> | 实时 | 每次请求 |

## 前端集成示例

### jQuery轮询

```javascript
// 每5秒更新实时价格
setInterval(function() {
    $.ajax({
        url: '/api/stocks/realtime',
        method: 'GET',
        success: function(response) {
            if (response.status === 'success') {
                updatePrices(response.data);
            }
        }
    });
}, 5000);
```

### 市场情绪展示

```javascript
$.ajax({
    url: '/api/market/sentiment',
    method: 'GET',
    success: function(data) {
        $('#sentimentScore').text(data.score);
        $('#sentimentLevel').text(data.level);
        $('#sentimentEmoji').text(data.emoji);
    }
});
```

## Python客户端示例

```python
import requests

# 获取市场情绪
response = requests.get('http://localhost:5000/api/market/sentiment')
sentiment = response.json()
print(f"市场情绪: {sentiment['level']} ({sentiment['score']}分)")

# 获取监控股票
response = requests.get('http://localhost:5000/api/stocks')
stocks = response.json()['data']
for stock in stocks:
    print(f"{stock['name']}: {stock['price']} ({stock['change_pct']:+.2f}%)")
```

## 认证

默认密码：`stock2024`

修改密码：编辑 `web_app.py`
```python
PASSWORD = "your_new_password"
```

## 跨域配置（CORS）

如需跨域访问，添加CORS支持：

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```
