# Known Protocol Registry

This document contains metadata for common DeFi protocols on Ethereum mainnet.

## Lending Protocols

### Aave V3
- **Contract**: 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2
- **Category**: Lending
- **Risk Level**: Low
- **Audit**: Multiple (OpenZeppelin, Trail of Bits)
- **TVL**: > $5B (check DefiLlama for current)
- **Docs**: https://docs.aave.com/

### Compound V3
- **Contract**: 0xc3d688B66703497DAA19211EEdff47f25384cdc3
- **Category**: Lending
- **Risk Level**: Low
- **Audit**: Multiple (OpenZeppelin)
- **TVL**: > $2B
- **Docs**: https://docs.compound.finance/

### MakerDAO (Spark)
- **Contract**: Various (see docs)
- **Category**: Lending
- **Risk Level**: Low
- **Audit**: Multiple
- **TVL**: > $8B
- **Docs**: https://docs.makerdao.com/

## Liquid Staking

### Lido (stETH)
- **Contract**: 0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84
- **Category**: Liquid Staking
- **Risk Level**: Low
- **Audit**: Multiple (Quantstamp, MixBytes)
- **TVL**: > $15B
- **Docs**: https://docs.lido.fi/

### Rocket Pool (rETH)
- **Contract**: 0xae78736Cd615f374D3085123A210448E74Fc6393
- **Category**: Liquid Staking
- **Risk Level**: Low
- **Audit**: Multiple (Sigma Prime)
- **TVL**: > $2B
- **Docs**: https://docs.rocketpool.net/

## DEXs

### Uniswap V3
- **Factory**: 0x1F98431c8aD98523631AE4a59f267346ea31F984
- **Category**: DEX
- **Risk Level**: Low
- **Audit**: Multiple
- **TVL**: > $4B
- **Docs**: https://docs.uniswap.org/

### Curve Finance
- **Contract**: 0xD533a949740bb3306d119CC777fa900bA034cd52
- **Category**: DEX (Stablecoins)
- **Risk Level**: Low
- **Audit**: Multiple
- **TVL**: > $2B
- **Docs**: https://docs.curve.fi/

## Yield Aggregators

### Yearn V3
- **Registry**: 0x3c91D8ba3C8cB06D9CFe5b8F31c68a746f0f15B6
- **Category**: Yield Aggregator
- **Risk Level**: Medium
- **Audit**: Multiple
- **TVL**: Variable
- **Docs**: https://docs.yearn.fi/

## Protocol Metadata Schema

```json
{
  "name": "Protocol Name",
  "address": "0x...",
  "chain": "ethereum",
  "category": "lending|dex|staking|aggregator",
  "risk_level": "low|medium|high",
  "audit_status": "multiple|single|community|none",
  "tvl": 1000000000,
  "maturity_days": 730,
  "has_timelock": true,
  "governance": "dao|multisig|admin",
  "docs_url": "https://...",
  "icon_url": "https://..."
}
```

## Adding New Protocols

To add a new protocol, create a JSON file in `config/protocols/`:

```json
{
  "name": "New Protocol",
  "address": "0x...",
  "chain": "ethereum",
  "category": "lending",
  "risk_level": "medium",
  "audit_status": "single",
  "docs_url": "https://..."
}
```

Then run:
```bash
python scripts/discovery/analyze_protocol.py --add-config config/protocols/new-protocol.json
```