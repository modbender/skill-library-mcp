---
name: okx-market-api
description: |
  OKX Web3 Wallet Market API 技能 - 用于查询加密货币代币价格、市场数据和交易信息。
  当用户需要以下功能时使用此技能：
  - 查询代币实时价格、K线数据、交易记录
  - 获取综合币价（聚合多数据源的指数价格）
  - 搜索代币、获取代币详情、查看代币排行榜
  - 获取持仓大户信息
  触发词包括：代币价格、币价、K线、candlestick、行情、market data、OKX API、DEX 数据、
  链上数据、token price、index price、token search、holder 等。
  支持 Solana、EVM、Sui 等多链生态，覆盖 100+ DEX 和 CEX 数据源。
---

# OKX Web3 Wallet Market API

本技能用于调用 OKX Web3 Wallet 的 Market API，获取加密货币代币的价格、交易、K线等市场数据。

## API 基础信息

- **Base URL**: `https://web3.okx.com`
- **认证方式**: 需要在 Header 中传入以下字段：
  - `OK-ACCESS-KEY`: API Key
  - `OK-ACCESS-SIGN`: 签名（HMAC SHA256）
  - `OK-ACCESS-PASSPHRASE`: API 密码短语
  - `OK-ACCESS-TIMESTAMP`: 请求时间戳（ISO 8601 格式）
  - `Content-Type: application/json`（POST 请求）

## 签名生成方法

```python
import hmac
import hashlib
import base64
from datetime import datetime

def generate_signature(timestamp, method, request_path, body, secret_key):
    """
    生成 OKX API 签名
    timestamp: ISO 8601 格式时间戳，如 '2023-10-18T12:21:41.274Z'
    method: HTTP 方法 (GET/POST)
    request_path: 请求路径，如 '/api/v6/dex/market/candles'
    body: 请求体（POST 时为 JSON 字符串，GET 时为空字符串）
    secret_key: API Secret
    """
    message = timestamp + method.upper() + request_path + body
    mac = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    return base64.b64encode(mac.digest()).decode('utf-8')
```

## 常用链标识 (chainIndex)

| chainIndex | 区块链 |
|------------|--------|
| 0 | Bitcoin |
| 1 | Ethereum |
| 10 | Optimism |
| 56 | BSC (BNB Chain) |
| 66 | OKX Chain |
| 137 | Polygon |
| 324 | zkSync Era |
| 501 | Solana |
| 42161 | Arbitrum One |
| 43114 | Avalanche C-Chain |

---

## 一、行情价格 API (Market Price API)

### 1.1 获取 K 线数据 (Get Candlesticks)

获取代币的 K 线图数据，最多返回 1,440 条记录。

**请求**
```
GET https://web3.okx.com/api/v6/dex/market/candles
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chainIndex | String | 是 | 链标识，如 `1` 表示 Ethereum |
| tokenContractAddress | String | 是 | 代币合约地址（EVM 链需使用小写） |
| after | String | 否 | 返回该时间戳之前的数据 |
| before | String | 否 | 返回该时间戳之后的数据 |
| bar | String | 否 | K 线周期，默认 `1m`。可选：`1s/1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M` |
| limit | String | 否 | 返回数量，最大 299，默认 100 |

**响应数据格式**: `[ts, o, h, l, c, vol, volUsd, confirm]`
- `ts`: 开盘时间（Unix 毫秒时间戳）
- `o`: 开盘价
- `h`: 最高价
- `l`: 最低价
- `c`: 收盘价
- `vol`: 交易量（基础货币）
- `volUsd`: 交易量（USD）
- `confirm`: 是否完成（0=未完成, 1=已完成）

**示例**
```bash
curl -X GET 'https://web3.okx.com/api/v6/dex/market/candles?chainIndex=66&tokenContractAddress=0x382bb369d343125bfb2117af9c149795c6c65c50' \
  -H 'OK-ACCESS-KEY: your-api-key' \
  -H 'OK-ACCESS-SIGN: your-signature' \
  -H 'OK-ACCESS-PASSPHRASE: your-passphrase' \
  -H 'OK-ACCESS-TIMESTAMP: 2023-10-18T12:21:41.274Z'
```

### 1.2 获取历史 K 线 (Get Candlesticks History)

获取历史 K 线数据（不包含未完成的 K 线）。

**请求**
```
GET https://web3.okx.com/api/v6/dex/market/historical-candles
```

参数与 1.1 相同。

### 1.3 获取最近交易 (Get Trades)

获取代币的最近交易记录。

**请求**
```
GET https://web3.okx.com/api/v6/dex/market/trades
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chainIndex | String | 是 | 链标识 |
| tokenContractAddress | String | 是 | 代币合约地址 |

**响应字段**
- `id`: 交易 ID
- `txHashUrl`: 交易哈希链接
- `userAddress`: 用户地址
- `dexName`: DEX 名称
- `type`: 交易类型 (buy/sell)
- `changedTokenInfo`: 交易代币信息数组

---

## 二、综合币价 API (Index Price API)

综合币价是通过聚合多个第三方数据源（CEX/DEX/Oracle）计算得出的指数价格。

### 2.1 获取代币指数价格 (Get Token Index Price)

批量查询代币指数价格，每次最多 100 个。

**请求**
```
POST https://web3.okx.com/api/v6/dex/index/current-price
```

**请求体** (JSON 数组)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chainIndex | String | 是 | 链标识 |
| tokenContractAddress | String | 是 | 代币地址。传空字符串 `""` 查询原生代币 |

**响应字段**
- `price`: 代币价格
- `time`: 价格时间戳（Unix 毫秒）
- `chainIndex`: 链标识
- `tokenContractAddress`: 代币地址

**示例**
```bash
curl -X POST 'https://web3.okx.com/api/v6/dex/index/current-price' \
  -H 'Content-Type: application/json' \
  -H 'OK-ACCESS-KEY: your-api-key' \
  -H 'OK-ACCESS-SIGN: your-signature' \
  -H 'OK-ACCESS-PASSPHRASE: your-passphrase' \
  -H 'OK-ACCESS-TIMESTAMP: 2023-10-18T12:21:41.274Z' \
  -d '[
    {"chainIndex": "1", "tokenContractAddress": "0xc18360217d8f7ab5e7c516566761ea12ce7f9d72"},
    {"chainIndex": "1", "tokenContractAddress": ""}
  ]'
```

### 2.2 获取历史指数价格 (Get Historical Index Price)

查询代币的历史价格。

**请求**
```
GET https://web3.okx.com/api/v6/dex/index/historical-price
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chainIndex | String | 是 | 链标识 |
| tokenContractAddress | String | 否 | 代币地址 |
| limit | String | 否 | 返回数量 |
| begin | String | 否 | 开始时间（Unix 毫秒） |
| period | String | 否 | 周期，如 `1m/5m/1H/1D` |

---

## 三、代币 API (Token API)

### 3.1 代币搜索 (Token Search)

通过代币名称、符号或合约地址搜索代币。

**请求**
```
GET https://web3.okx.com/api/v6/dex/market/token/search
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chains | String | 是 | 链标识，多个用逗号分隔，如 `1,10,56` |
| search | String | 是 | 搜索关键词（名称/符号/地址） |

**响应字段**
- `chainIndex`: 链标识
- `tokenName`: 代币名称
- `tokenSymbol`: 代币符号
- `tokenContractAddress`: 合约地址
- `tokenLogoUrl`: 代币图标
- `decimal`: 精度
- `price`: 当前价格
- `marketCap`: 市值
- `liquidity`: 流动性
- `holders`: 持有人数
- `change`: 24H 涨跌幅
- `tagList.communityRecognized`: 是否为社区认证代币

**示例**
```bash
curl -X GET 'https://web3.okx.com/api/v6/dex/market/token/search?chains=1,10&search=weth' \
  -H 'OK-ACCESS-KEY: your-api-key' \
  -H 'OK-ACCESS-SIGN: your-signature' \
  -H 'OK-ACCESS-PASSPHRASE: your-passphrase' \
  -H 'OK-ACCESS-TIMESTAMP: 2023-10-18T12:21:41.274Z'
```

### 3.2 代币基本信息 (Token Basic Information)

获取指定代币的基本信息。

**请求**
```
POST https://web3.okx.com/api/v6/dex/market/token/basic-info
```

**请求体** (JSON 数组)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chainIndex | String | 是 | 链标识 |
| tokenContractAddress | String | 是 | 代币合约地址 |

**响应字段**
- `chainIndex`: 链标识
- `tokenName`: 代币名称
- `tokenSymbol`: 代币符号
- `tokenLogoUrl`: 图标 URL
- `decimal`: 精度
- `tagList.communityRecognized`: 是否社区认证

### 3.3 代币交易信息 (Token Trading Information)

获取代币的详细交易信息，包括价格、交易量、市值、流动性等。

**请求**
```
POST https://web3.okx.com/api/v6/dex/market/price-info
```

**请求体** (JSON 数组，最多 100 个)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chainIndex | String | 是 | 链标识 |
| tokenContractAddress | String | 是 | 代币合约地址 |

**响应字段**
- `price`: 最新价格
- `marketCap`: 市值
- `priceChange5M/1H/4H/24H`: 价格变化百分比
- `volume5M/1H/4H/24H`: 交易量
- `txs5M/1H/4H/24H`: 交易笔数
- `maxPrice/minPrice`: 24H 最高/最低价
- `circSupply`: 流通供应量
- `liquidity`: 流动性
- `holders`: 持有人数
- `tradeNum`: 24H 交易数量

**示例**
```bash
curl -X POST 'https://web3.okx.com/api/v6/dex/market/price-info' \
  -H 'Content-Type: application/json' \
  -H 'OK-ACCESS-KEY: your-api-key' \
  -H 'OK-ACCESS-SIGN: your-signature' \
  -H 'OK-ACCESS-PASSPHRASE: your-passphrase' \
  -H 'OK-ACCESS-TIMESTAMP: 2023-10-18T12:21:41.274Z' \
  -d '[
    {"chainIndex": "501", "tokenContractAddress": "5mbK36SZ7J19An8jFochhQS4of8g6BwUjbeCSxBSoWdp"}
  ]'
```

### 3.4 代币排行榜 (Token Ranking List)

获取代币排行榜列表。

**请求**
```
GET https://web3.okx.com/api/v6/dex/market/token/ranking
```

### 3.5 持仓大户 (Top Token Holder)

获取代币的持仓大户信息。

**请求**
```
GET https://web3.okx.com/api/v6/dex/market/token/holder
```

---

## 四、Websocket API

Websocket 服务仅对白名单用户开放。如需使用，请联系 dexapi@okx.com。

**连接地址**: 请参考官方文档

**可用频道**:
- **Price Channel**: 实时价格数据
- **Candlesticks Channel**: 实时 K 线数据
- **Trades Channel**: 实时交易数据
- **Liquidity Channel**: 流动性数据

---

## 五、错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 50000 | 系统错误 |
| 50001 | 参数错误 |
| 50002 | 签名错误 |
| 50003 | 请求频率超限 |

---

## 六、Python 示例代码

```python
import requests
import hmac
import hashlib
import base64
from datetime import datetime, timezone
import json

class OKXMarketAPI:
    def __init__(self, api_key, secret_key, passphrase):
        self.base_url = "https://web3.okx.com"
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
    
    def _get_timestamp(self):
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    def _sign(self, timestamp, method, request_path, body=''):
        message = timestamp + method + request_path + body
        mac = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode('utf-8')
    
    def _headers(self, method, request_path, body=''):
        timestamp = self._get_timestamp()
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': self._sign(timestamp, method, request_path, body),
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
    
    def get_candlesticks(self, chain_index, token_address, bar='1m', limit=100):
        """获取 K 线数据"""
        path = f'/api/v6/dex/market/candles?chainIndex={chain_index}&tokenContractAddress={token_address}&bar={bar}&limit={limit}'
        headers = self._headers('GET', path)
        response = requests.get(self.base_url + path, headers=headers)
        return response.json()
    
    def get_index_price(self, tokens):
        """
        获取代币指数价格
        tokens: [{"chainIndex": "1", "tokenContractAddress": "0x..."}]
        """
        path = '/api/v6/dex/index/current-price'
        body = json.dumps(tokens)
        headers = self._headers('POST', path, body)
        response = requests.post(self.base_url + path, headers=headers, data=body)
        return response.json()
    
    def search_token(self, chains, keyword):
        """搜索代币"""
        path = f'/api/v6/dex/market/token/search?chains={chains}&search={keyword}'
        headers = self._headers('GET', path)
        response = requests.get(self.base_url + path, headers=headers)
        return response.json()
    
    def get_token_info(self, tokens):
        """
        获取代币交易信息
        tokens: [{"chainIndex": "501", "tokenContractAddress": "..."}]
        """
        path = '/api/v6/dex/market/price-info'
        body = json.dumps(tokens)
        headers = self._headers('POST', path, body)
        response = requests.post(self.base_url + path, headers=headers, data=body)
        return response.json()


# 使用示例
if __name__ == "__main__":
    api = OKXMarketAPI(
        api_key="your-api-key",
        secret_key="your-secret-key",
        passphrase="your-passphrase"
    )
    
    # 搜索 WETH
    result = api.search_token("1,10", "weth")
    print(json.dumps(result, indent=2))
    
    # 获取 ETH 指数价格
    result = api.get_index_price([
        {"chainIndex": "1", "tokenContractAddress": ""}
    ])
    print(json.dumps(result, indent=2))
```

---

## 七、相关文档链接

- [OKX Wallet API 官方文档](https://web3.okx.com/build/dev-docs/wallet-api/what-is-wallet-api)
- [Market API 介绍](https://web3.okx.com/build/dev-docs/wallet-api/market-api-introduction)
- [支持的区块链列表](https://web3.okx.com/build/dev-docs/wallet-api/supported-chain)
