# Supported Chains

This document lists all supported blockchain networks in the ApeChain Reader skill, their reliability status, and known issues.

## Chain Status Legend

✅ **RELIABLE** - Consistently working, recommended for production use  
🟡 **INTERMITTENT** - Works but may have occasional timeouts or performance issues  
❌ **PROBLEMATIC** - Frequent issues, use with caution  

---

## Supported Networks

### ✅ ApeChain (Primary)
- **Chain ID:** 33139
- **RPC:** `https://apechain.calderachain.xyz/http`
- **Symbol:** APE
- **Explorer:** [apescan.io](https://apescan.io)
- **Status:** ✅ RELIABLE
- **Notes:** Primary target chain, consistently fast responses (<1s), excellent reliability
- **Recommended:** Primary choice for all operations

### ✅ Ethereum Mainnet
- **Chain ID:** 1
- **RPC:** `https://eth.llamarpc.com`
- **Symbol:** ETH
- **Explorer:** [etherscan.io](https://etherscan.io)
- **Status:** ✅ RELIABLE
- **Notes:** Stable performance, good for high-value addresses, moderate response times
- **Recommended:** Reliable for production use

### ✅ Base
- **Chain ID:** 8453
- **RPC:** `https://base.llamarpc.com`
- **Symbol:** ETH
- **Explorer:** [basescan.org](https://basescan.org)
- **Status:** ✅ RELIABLE
- **Notes:** Fast responses, growing ecosystem, good reliability
- **Recommended:** Reliable for production use

### ✅ Arbitrum One
- **Chain ID:** 42161
- **RPC:** `https://arb1.arbitrum.io/rpc`
- **Symbol:** ETH
- **Explorer:** [arbiscan.io](https://arbiscan.io)
- **Status:** ✅ RELIABLE
- **Notes:** Fast and reliable, official RPC endpoint
- **Recommended:** Reliable for production use

### 🟡 Polygon
- **Chain ID:** 137
- **RPC:** `https://polygon.llamarpc.com`
- **Symbol:** MATIC
- **Explorer:** [polygonscan.com](https://polygonscan.com)
- **Status:** 🟡 INTERMITTENT
- **Notes:** Frequent timeouts during testing, RPC endpoint may be unreliable
- **Recommendation:** Use with retry logic, consider alternative RPC endpoints
- **Alternative RPCs:** 
  - `https://polygon-rpc.com`
  - `https://rpc-mainnet.maticvigil.com`

### 🟡 Optimism
- **Chain ID:** 10
- **RPC:** `https://optimism.llamarpc.com`
- **Symbol:** ETH
- **Explorer:** [optimistic.etherscan.io](https://optimistic.etherscan.io)
- **Status:** 🟡 INTERMITTENT
- **Notes:** Timeout issues observed during testing
- **Recommendation:** Use with retry logic, consider alternative RPC endpoints
- **Alternative RPCs:** 
  - `https://mainnet.optimism.io`
  - `https://opt-mainnet.g.alchemy.com/v2/demo`

### 🟡 BNB Smart Chain (BSC)
- **Chain ID:** 56
- **RPC:** `https://bsc.llamarpc.com`
- **Symbol:** BNB
- **Explorer:** [bscscan.com](https://bscscan.com)
- **Status:** 🟡 INTERMITTENT
- **Notes:** Timeout issues observed, may need alternative endpoints
- **Recommendation:** Use with caution, consider alternative RPC endpoints
- **Alternative RPCs:** 
  - `https://bsc-dataseed.binance.org`
  - `https://bsc-dataseed1.defibit.io`

### 🟡 Avalanche C-Chain
- **Chain ID:** 43114
- **RPC:** `https://avalanche.drpc.org`
- **Symbol:** AVAX
- **Explorer:** [snowscan.xyz](https://snowscan.xyz)
- **Status:** 🟡 INTERMITTENT
- **Notes:** Limited testing, may have performance issues
- **Recommendation:** Test thoroughly before production use
- **Alternative RPCs:** 
  - `https://api.avax.network/ext/bc/C/rpc`
  - `https://rpc.ankr.com/avalanche`

---

## Performance Characteristics

### Response Time Expectations
- **Fast (< 1s):** ApeChain, Arbitrum
- **Good (1-2s):** Ethereum, Base
- **Variable (1-5s):** Polygon, Optimism, BSC, Avalanche

### Resource Requirements
All chains use similar resource patterns:
- **eth_getBalance:** Very fast (~100ms)
- **eth_getTransactionCount:** Fast (~200ms)
- **eth_getCode:** Fast (~200ms)
- **eth_getLogs:** Slow (1-5s, depends on block range and activity)

### Block Range Recommendations
- **ApeChain:** Up to 2M blocks (excellent performance)
- **Ethereum:** Up to 500K blocks (balance speed vs completeness)
- **L2 Networks:** Up to 1M blocks (faster block times)
- **Other Networks:** Start with 100K blocks, increase as needed

---

## Troubleshooting

### Common Issues

#### Timeout Errors
**Symptoms:** `RPC request timed out after 10000ms`  
**Solutions:**
1. Reduce block scan range (--limit parameter)
2. Retry with exponential backoff (built-in)
3. Switch to alternative RPC endpoint
4. Use different chain if cross-chain data acceptable

#### Rate Limiting
**Symptoms:** `HTTP 429: Too Many Requests`  
**Solutions:**
1. Add delays between requests
2. Use different RPC endpoint
3. Implement request queuing

#### Empty Results
**Symptoms:** No transactions/NFTs found for active addresses  
**Possible Causes:**
1. Chain mismatch (address active on different chain)
2. Block range too small
3. RPC endpoint synchronization lag

### Best Practices

1. **Always use retry logic** for intermittent chains
2. **Start with reliable chains** (ApeChain, Ethereum, Base, Arbitrum)
3. **Monitor response times** and adjust timeouts accordingly
4. **Have fallback RPC endpoints** for critical operations
5. **Cache results** where appropriate to reduce API calls

---

## Future Improvements

### Planned Enhancements
1. **Health monitoring** - Automatic endpoint health checks
2. **Auto-failover** - Switch to backup RPC on failure
3. **Dynamic timeouts** - Adjust based on historical performance
4. **Custom RPC support** - Allow user-configured endpoints
5. **Batch requests** - Combine multiple queries for efficiency

### RPC Endpoint Rotation
Consider implementing RPC endpoint pools for better reliability:

```javascript
const RPC_POOLS = {
  polygon: [
    "https://polygon.llamarpc.com",
    "https://polygon-rpc.com", 
    "https://rpc-mainnet.maticvigil.com"
  ],
  // ... other chains
};
```

---

*Last Updated: February 15, 2026*  
*Based on comprehensive testing with vitalik.eth and active ApeChain addresses*