# Risk Assessment Framework

## Risk Levels

| Level | Score | Description | Typical Characteristics |
|-------|-------|-------------|------------------------|
| **Low** | 0-3 | Blue-chip, battle-tested | TVL > $1B, Audited, 2+ years live |
| **Medium** | 4-6 | Established but some risk | TVL $100M-$1B, Audited, 1+ year live |
| **High** | 7-10 | Experimental or new | TVL < $100M, No audit, < 1 year live |

## Risk Factors

### 1. Protocol Maturity (0-3 points)

| Criteria | Points |
|----------|--------|
| Live > 2 years with no major exploits | 0 |
| Live 1-2 years | 1 |
| Live < 1 year | 2 |
| Live < 3 months | 3 |

### 2. Audit Status (0-3 points)

| Criteria | Points |
|----------|--------|
| Multiple audits from top firms (OpenZeppelin, Trail of Bits, etc.) | 0 |
| Single audit from reputable firm | 1 |
| Community audit only | 2 |
| No audit | 3 |

### 3. TVL Size (0-2 points)

| TVL | Points |
|-----|--------|
| > $1 billion | 0 |
| $100M - $1B | 1 |
| < $100M | 2 |

### 4. Decentralization (0-2 points)

| Criteria | Points |
|----------|--------|
| DAO governance, no admin keys or timelocked | 0 |
| Timelocked admin keys (> 48h) | 1 |
| Admin keys, no timelock | 2 |

## Risk Calculation

```
Risk Score = Protocol Maturity + Audit Status + TVL Size + Decentralization
```

### Examples

| Protocol | Maturity | Audit | TVL | Decentralization | Total | Level |
|----------|----------|-------|-----|------------------|-------|-------|
| Aave V3 | 0 | 0 | 0 | 1 | 1 | Low |
| Compound | 0 | 0 | 0 | 0 | 0 | Low |
| New Lending Protocol | 3 | 3 | 2 | 2 | 10 | High |

## Risk-Adjusted APY

When comparing opportunities, consider risk-adjusted returns:

```
Risk-Adjusted APY = Nominal APY × (1 - Risk Score / 20)
```

### Example

| Protocol | APY | Risk Score | Risk-Adjusted APY |
|----------|-----|------------|-------------------|
| Aave USDC | 5% | 1 | 4.75% |
| New Protocol | 20% | 8 | 12% |

## Special Risk Flags

Additional risk factors that should be noted but not scored:

- ⚠️ **Fork Risk**: Protocol is a fork of another protocol with issues
- ⚠️ **Oracle Risk**: Uses custom oracle instead of Chainlink
- ⚠️ **Leverage Risk**: Involves leverage or looping
- ⚠️ **Illicit Risk**: Protocol in sanctioned jurisdiction
- ⚠️ **Regulatory Risk**: Under regulatory scrutiny

## Usage in Discovery

When running `find_opportunities.py`:

```bash
# Only show low-risk opportunities
python scripts/discovery/find_opportunities.py --max-risk low

# Filter by minimum TVL (in USD)
python scripts/discovery/find_opportunities.py --min-tvl 1000000

# Require audit
python scripts/discovery/find_opportunities.py --require-audit
```