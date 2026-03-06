# RPC Endpoints Reference

List of RPC providers for Solana and BNB Chain trading.

## Solana RPCs

### Public (Free)

**Solana Foundation**
- URL: `https://api.mainnet-beta.solana.com`
- Rate Limit: ~10 req/sec
- Reliability: Medium
- Best For: Testing, low-frequency queries

**Solana Devnet** (Testing)
- URL: `https://api.devnet.solana.com`
- Rate Limit: ~10 req/sec
- Free: Yes

### Private (Paid)

**Helius**
- Website: https://helius.dev
- Free Tier: 50 req/sec
- Paid Plans: $99-$999/month
- Features: Enhanced APIs, webhooks, NFT data
- Reliability: High
- Best For: Production bots

**QuickNode**
- Website: https://quicknode.com
- Free Tier: 25 req/sec (limited)
- Paid Plans: $49-$299/month
- Features: Global endpoints, analytics
- Reliability: High
- Best For: Low-latency trading

**Alchemy**
- Website: https://alchemy.com
- Free Tier: Limited requests
- Paid Plans: Custom pricing
- Features: Enhanced APIs, debugging
- Reliability: High

**Ankr**
- Website: https://ankr.com
- Free Tier: 500 req/day
- Paid Plans: $50+/month
- Features: Multi-chain support
- Reliability: Medium

**GenesysGo (Closed beta)**
- Website: https://genesysgo.com
- Features: Premium Solana RPC
- Reliability: Very High

### Configuration Example

```python
import os

# Use environment variable
RPC_URL = os.getenv(
    "SOLANA_RPC_URL",
    "https://api.mainnet-beta.solana.com"  # Fallback
)

# For production, use private RPC
if os.getenv("ENV") == "production":
    RPC_URL = "https://rpc.helius.xyz/?api-key=YOUR_KEY"
```

---

## BNB Chain RPCs

### Public (Free)

**Binance Official**
- Primary: `https://bsc-dataseed1.binance.org`
- Backup 1: `https://bsc-dataseed2.binance.org`
- Backup 2: `https://bsc-dataseed3.binance.org`
- Backup 3: `https://bsc-dataseed4.binance.org`
- Rate Limit: Variable (throttled)
- Reliability: Medium-High

**Community Nodes**
- `https://bsc-dataseed1.defibit.io`
- `https://bsc-dataseed1.ninicoin.io`
- Rate Limit: Variable
- Reliability: Medium

**Testnet**
- URL: `https://data-seed-prebsc-1-s1.binance.org:8545`
- Chain ID: 97
- Free: Yes

### Private (Paid)

**QuickNode**
- Website: https://quicknode.com
- Paid Plans: $49-$299/month
- Features: Global endpoints, BSC archive nodes
- Reliability: High
- Best For: Low-latency trading

**Ankr**
- Website: https://ankr.com
- Free Tier: 500 req/day
- Paid Plans: $50+/month
- Features: Multi-chain, load balancing
- Reliability: Medium-High

**GetBlock**
- Website: https://getblock.io
- Free Tier: 40k req/day
- Paid Plans: $50-$500/month
- Features: Shared & dedicated nodes
- Reliability: High

**NodeReal**
- Website: https://nodereal.io
- Free Tier: Limited
- Paid Plans: Custom
- Features: MegaNode (enhanced BSC RPC)
- Reliability: Very High

### Configuration Example

```python
import os
from web3 import Web3

# RPC rotation for reliability
BSC_RPCS = [
    "https://bsc-dataseed1.binance.org",
    "https://bsc-dataseed2.binance.org",
    "https://bsc-dataseed3.binance.org"
]

def get_web3():
    """Get Web3 instance with RPC rotation."""
    for rpc in BSC_RPCS:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={'timeout': 10}))
            if w3.is_connected():
                return w3
        except Exception:
            continue
    
    raise RuntimeError("All RPCs failed")
```

---

## Rate Limiting Best Practices

### 1. Implement Retry Logic

```python
import time
from functools import wraps

def retry_on_rpc_error(max_retries=3, delay=1):
    """Retry decorator for RPC calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"RPC error, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(delay * (attempt + 1))
        return wrapper
    return decorator

@retry_on_rpc_error(max_retries=3)
def get_token_price(token):
    # RPC call here
    pass
```

### 2. Use Request Pooling

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests

def get_session():
    """Get requests session with retry strategy."""
    session = requests.Session()
    
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session

session = get_session()
response = session.get("https://api.mainnet-beta.solana.com", json={...})
```

### 3. Caching

```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_token_price_cached(token, timestamp):
    """Cache prices for 60 seconds."""
    return get_token_price(token)

# Use with current minute as cache key
current_minute = int(time.time() / 60)
price = get_token_price_cached("TOKEN_ADDRESS", current_minute)
```

---

## Monitoring RPC Health

```python
def check_rpc_health(rpc_url: str, chain: str) -> dict:
    """
    Check RPC endpoint health.
    
    Returns:
        dict with latency, block height, status
    """
    import time
    
    start = time.time()
    
    try:
        if chain == "solana":
            from solana.rpc.api import Client
            client = Client(rpc_url, timeout=5)
            slot = client.get_slot().value
            latency = (time.time() - start) * 1000
            
            return {
                "status": "healthy",
                "latency_ms": latency,
                "block_height": slot,
                "url": rpc_url
            }
        
        elif chain == "bnb":
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 5}))
            block = w3.eth.block_number
            latency = (time.time() - start) * 1000
            
            return {
                "status": "healthy",
                "latency_ms": latency,
                "block_height": block,
                "url": rpc_url
            }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "url": rpc_url
        }

# Monitor multiple RPCs
rpcs = [
    "https://api.mainnet-beta.solana.com",
    "https://rpc.helius.xyz/?api-key=KEY"
]

for rpc in rpcs:
    health = check_rpc_health(rpc, "solana")
    print(f"{rpc}: {health['status']} ({health.get('latency_ms', 'N/A')}ms)")
```

---

## Cost Comparison

### Solana RPCs (Monthly Cost)

| Provider | Free Tier | Paid Tier | Req/Month (Paid) |
|----------|-----------|-----------|------------------|
| Solana Public | ✅ Limited | N/A | ~1M |
| Helius | 50 req/sec | $99 | ~130M |
| QuickNode | 25 req/sec | $49-$299 | ~65M-250M |
| Ankr | 500/day | $50 | ~1.3M |

### BNB Chain RPCs (Monthly Cost)

| Provider | Free Tier | Paid Tier | Req/Month (Paid) |
|----------|-----------|-----------|------------------|
| Binance Public | ✅ Throttled | N/A | Variable |
| QuickNode | ❌ | $49-$299 | ~65M-250M |
| Ankr | 500/day | $50 | ~1.3M |
| GetBlock | 40k/day | $50-$500 | ~1.2M-15M |

---

## Recommendations

### For Development/Testing
- Solana: Public RPC or Helius free tier
- BNB: Binance public RPCs

### For Low-Frequency Trading
- Solana: Helius ($99/month)
- BNB: QuickNode ($49/month)

### For High-Frequency Trading
- Solana: QuickNode or GenesysGo
- BNB: NodeReal MegaNode

### For Production Bots
- Use at least 2 RPC providers (failover)
- Monitor latency and health
- Set up alerts for downtime
