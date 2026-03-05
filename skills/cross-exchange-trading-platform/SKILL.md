---
name: gate-crossex
version: 1.0.0
description: Gate CrossEx 跨交易所统一交易接口技能 - 支持币安、欧易、Gate.io 统一账户交易
author: Gate.io 开发者团队
license: MIT
tags:
  - trading
  - cryptocurrency
  - cross-exchange
  - gate.io
  - binance
  - okx
  - api
  - quantification

requires:
  - python >= 3.7
  - requests

capabilities:
  - 跨所账户管理
  - 资产划转
  - 订单管理（下单、撤单、改单）
  - 仓位查询
  - 市场数据查询
  - 闪兑交易

env_vars:
  GATE_API_KEY: API 密钥（必需）
  GATE_API_SECRET: API 签名密钥（必需）

config_paths:
  - ~/.openclaw/credentials/gate.json
  - ~/.gate/credentials.json

binaries:
  - openssl: 签名加密

permissions:
  - needs_credentials: true
  - network_access: true

always: false
---

# Gate CrossEx Skill

Gate CrossEx 是 Gate.io 推出的跨交易所交易平台技能，允许用户通过统一账户在多个主流交易所（币安、欧易、Gate.io）进行交易，提供完整的账户管理、资产划转、下单和仓位管理功能。

## 核心价值

- **跨所保证金共用** - 打破资金孤岛，一份保证金多所共用，头寸盈亏互抵
- **统一 API 标准** - 单套 API 管理全所资产与头寸，极简化部署与运维
- **全局风控体系** - 统一风控规则体系，监控多市场联动风险
- **多市场覆盖** - 接入 550+ 主流交易所市场，捕捉全网交易机会

## 支持的交易所

- **BINANCE** - 币安
- **OKX** - 欧易
- **GATE** - Gate.io

## 支持的交易类型

- 现货交易（Spot）
- 全仓杠杆（Cross Margin）
- U 本位永续合约（USDT Perpetual Futures）

---

## 配置说明

### 1. API Key 配置

在使用本技能前，需要配置 Gate CrossEx API 凭证：

#### 方法 1：环境变量（推荐）

```bash
export GATE_API_KEY="your_api_key_here"
export GATE_API_SECRET="your_api_secret_here"
```

#### 方法 2：配置文件

将 API 凭证保存到 `~/.openclaw/credentials/gate.json`：

```json
{
  "apiKey": "your_api_key_here",
  "secretKey": "your_api_secret_here"
}
```

**⚠️ 安全提示**：
- 确保配置文件权限为 `600`（仅所有者可读写）
- 不要在版本控制中提交 API 密钥
- 建议使用受限权限的 API Key

### 2. 开通 CrossEx 账户

1. 登录 Gate.io 账户
2. 在顶部菜单栏的【交易-跨所交易】中开通跨所账户
3. 进入【账户管理】→ 【APIv4 Keys】
4. 创建新的 API Key，需勾选 **跨所交易权限**

### 3. API 签名机制

Gate CrossEx 使用 **HMAC-SHA512** 签名算法：

```python
import time
import hashlib
import hmac

def gen_sign(method, url, query_string=None, payload_string=None):
    key = os.getenv('GATE_API_KEY')
    secret = os.getenv('GATE_API_SECRET')

    t = str(int(time.time()))
    m = hashlib.sha512()
    m.update((payload_string or '').encode('utf-8'))
    hashed_payload = m.hexdigest()

    s = '%s\n%s\n%s\n%s\n%s' % (
        method, url, query_string or '', hashed_payload, t
    )

    sign = hmac.new(
        secret.encode('utf-8'),
        s.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()

    return {
        'KEY': key,
        'Timestamp': t,
        'SIGN': sign,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
```

---

## API 接口

### 基础信息

- **实盘交易**: `https://api.gateio.ws/api/v4/crossex`

### 主要功能模块

#### 1. 公共接口（无需认证）

```bash
# 查询币对信息
GET /rule/symbols

# 查询风险限额信息
GET /rule/risk_limits

# 查询划转币种支持
GET /rule/support_currencies
```

#### 2. 账户管理（需要认证）

```bash
# 查询账户资产
GET /accounts

# 查询杠杆仓位
GET /position/margin

# 查询合约仓位
GET /position/futures
```

#### 3. 资金划转（需要认证）

```bash
# 资金划转
POST /wallet/transfers

# 查询资金划转历史
GET /wallet/transfers
```

#### 4. 订单管理（需要认证）

```bash
# 下单
POST /orders

# 撤单
DELETE /orders

# 改单
PUT /orders/{order_id}

# 查询订单详情
GET /orders/{order_id}

# 查询当前所有挂单
GET /orders
```

#### 5. 闪兑交易（需要认证）

```bash
# 闪兑询价
POST /convert/quote

# 闪兑交易
POST /convert/execute
```

---

## 使用示例

### Python 示例

```python
# coding: utf-8
import os
import time
import hashlib
import hmac
import requests

# 从环境变量获取 API 凭证
API_KEY = os.getenv('GATE_API_KEY')
API_SECRET = os.getenv('GATE_API_SECRET')

def gen_sign(method, url, query_string=None, payload_string=None):
    """生成 Gate CrossEx API 签名"""
    t = str(int(time.time()))
    m = hashlib.sha512()
    m.update((payload_string or '').encode('utf-8'))
    hashed_payload = m.hexdigest()

    s = '%s\n%s\n%s\n%s\n%s' % (
        method, url, query_string or '', hashed_payload, t
    )

    sign = hmac.new(
        API_SECRET.encode('utf-8'),
        s.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()

    return {
        'KEY': API_KEY,
        'Timestamp': t,
        'SIGN': sign,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

# 查询账户资产
host = 'https://api.gateio.ws'
prefix = '/api/v4/crossex'
url = '/accounts'
headers = gen_sign('GET', prefix + url)

response = requests.get(host + prefix + url, headers=headers)
print(response.json())
```

### Shell 示例

```bash
#!/bin/bash

# 使用 openssl 生成签名
API_KEY="your_api_key"
API_SECRET="your_api_secret"
TIMESTAMP=$(date +%s)
PAYLOAD_HASH=$(echo -n "" | openssl dgst -sha512 -hex | awk '{print $2}')

SIGNATURE_STRING="GET\n/api/v4/crossex/rule/symbols\n\n${PAYLOAD_HASH}\n${TIMESTAMP}"
SIGNATURE=$(echo -n "${SIGNATURE_STRING}" | openssl dgst -sha512 -hmac "${API_SECRET}" -hex | awk '{print $2}')

# 查询币对信息
curl -X GET "https://api.gateio.ws/api/v4/crossex/rule/symbols" \
  -H "KEY: ${API_KEY}" \
  -H "Timestamp: ${TIMESTAMP}" \
  -H "SIGN: ${SIGNATURE}" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json"
```

### 使用场景示例

#### 场景 1：跨所价差套利

```python
# 查询不同交易所的 BTC 价格
symbols = ["BINANCE_FUTURE_BTC_USDT", "OKX_FUTURE_BTC_USDT", "GATE_FUTURE_BTC_USDT"]

for symbol in symbols:
    response = requests.get(f"{host}{prefix}/rule/symbols?symbols={symbol}")
    print(f"{symbol}: {response.json()}")
```

#### 场景 2：统一账户资产查询

```python
# 查询跨所账户总资产
response = requests.get(f"{host}{prefix}/accounts", headers=headers)
account_data = response.json()

print(f"总资产: {account_data.get('total_balance')} USDT")
print(f"可用保证金: {account_data.get('available_margin')} USDT")
```

#### 场景 3：跨所资金划转

```python
# 从统一账户划转到子账户
transfer_data = {
    "currency": "USDT",
    "amount": "1000",
    "from": "UNIFIED",
    "to": "BINANCE"
}

response = requests.post(
    f"{host}{prefix}/wallet/transfers",
    headers=headers,
    json=transfer_data
)
print(response.json())
```

---

## 错误处理

### 错误响应格式

```json
{
  "label": "COMMON_PARAM_BIND_ERROR",
  "message": "参数非法，请查阅api文档"
}
```

### 常见错误码

| Label | 含义 |
|-------|------|
| `COMMON_PARAM_BIND_ERROR` | 参数非法 |
| `TRADE_UNSUPPORTED_OPERATION` | 当前操作不被允许 |
| `USER_NOT_EXIST` | 用户不存在 |
| `TRADE_INVALID_SYMBOL` | 当前 symbol 不支持 |
| `TRADE_ORDER_NOT_FOUND_ERROR` | 订单不存在或已终态 |
| `MARGIN_ORDER_NOT_SUPPORT` | 分所模式暂不支持现货杠杆功能 |

### 错误处理示例

```python
import requests

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
except requests.HTTPError as e:
    error_data = response.json()
    label = error_data.get('label')

    if label == 'INVALID_API_KEY':
        print("❌ API Key 无效或已过期")
    elif label == 'TRADE_UNSUPPORTED_OPERATION':
        print("❌ 当前操作不被支持")
    else:
        print(f"❌ 请求失败: {error_data}")
```

---

## 安全建议

### 1. API Key 权限管理

- ✅ **只读权限** - 用于查询账户和市场数据
- ✅ **受限交易权限** - 禁止提现，仅允许交易
- ❌ **避免全权限** - 不要授予提现权限给交易机器人

### 2. IP 白名单

- 每个 Key 最多可配置 20 个 IPv4 地址
- 建议在 Gate.io 后台配置 IP 白名单
- 不支持 IP 地址段配置

### 3. 密钥存储

```bash
# 设置正确的文件权限
chmod 600 ~/.openclaw/credentials/gate.json
```

### 4. 最小资金原则

- 使用独立的子账户进行自动化交易
- 仅保留必要的测试资金
- 定期审查交易日志

---

## 技术支持

### 官方文档

- [Gate CrossEx API 文档](https://www.gate.com/docs/developers/crossex)
- [Gate API v4 文档](https://www.gate.com/docs/developers/apiv4)
- [Gate CrossEx 产品页面](https://www.gate.com/zh/crossex)
- [帮助中心 - CrossEx 功能说明](https://www.gate.com/help/crossex/functional)

### 技术支持

- **在线工单**: 登录后提交工单
- **邮件支持**: [mm@gate.com](mailto:mm@gate.com)

### 联系时请准备

1. 问题描述
2. Gate UID
3. 请求 URI 和参数
4. 错误代码
5. 响应内容

**⚠️ 重要提示**：
> 永远不要向任何人（包括客服）透露您的 API Key 或 Secret。
> 如果 API Key 意外泄露，请立即删除并重新创建。

---

## 更新日志

### v1.0.0 (2026-02-23)

- ✅ CrossEx Skill 首次发布
- ✅ 支持跨多个交易所的统一账户管理
- ✅ 支持跨交易所资产划转
- ✅ 提供跨交易所下单和管理功能
- ✅ 支持合约和杠杆交易的仓位管理
- ✅ 提供市场数据查询（交易对、风险限额等）
- ✅ 支持账户设置（仓位模式、账户模式、杠杆倍数）
- ✅ 提供 Python 和 Shell 完整示例代码

---

## 免责声明

数字货币交易具有极高风险，市场价格可能在短时间内大幅波动。本技能仅供学习和研究目的，使用本技能进行实盘交易的一切风险由使用者自行承担。

**请确保您：**

1. ✅ 充分了解数字货币交易风险
2. ✅ 仅使用可承受损失的资金
3. ✅ 遵守当地法律法规
4. ✅ 妥善保管 API 密钥

---

**文档版本**: v1.0.0
**最后更新**: 2026-02-23
**维护者**: Gate.io 开发者团队
**许可协议**: MIT License
