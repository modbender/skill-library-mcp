# Token Economics Analyzer

Evaluate token and digital asset economics for business decisions. Covers utility tokens, governance tokens, loyalty points, and tokenized assets.

## When to Use
- Evaluating a token-based product or partnership
- Designing tokenomics for a new product launch
- Assessing token treasury risk exposure
- Due diligence on token-incentivized vendor platforms

## Framework

### 1. Token Classification (5 Types)
| Type | Examples | Key Risk | Business Use |
|------|----------|----------|-------------|
| Utility | API credits, compute tokens | Demand volatility | Pay-per-use vendor pricing |
| Governance | DAO votes, protocol tokens | Concentration risk | Vendor influence, roadmap control |
| Payment | Stablecoins, settlement tokens | Regulatory, counterparty | Cross-border payments, payroll |
| Security | Revenue-share tokens, equity tokens | Securities law compliance | Fundraising, employee comp |
| Loyalty/Reward | Points, cashback tokens | Liability accounting | Customer retention, engagement |

### 2. Tokenomics Health Score (0-100)

Score each dimension 0-20:

**Supply Mechanics (0-20)**
- Fixed vs inflationary supply
- Emission schedule and vesting
- Burn mechanisms
- Current circulating vs total supply ratio

**Demand Drivers (0-20)**
- Real utility (not just speculation)
- Number of active use cases
- Revenue correlation
- Network effect strength

**Distribution (0-20)**
- Team/insider allocation (red flag if >30%)
- Vesting schedules for large holders
- Concentration (top 10 wallets %)
- Public vs private sale ratio

**Governance (0-20)**
- Voting mechanism fairness
- Proposal threshold accessibility
- Treasury management transparency
- Fork/exit rights

**Regulatory Posture (0-20)**
- Howey test assessment
- Jurisdiction clarity
- KYC/AML compliance
- Tax treatment documentation

**Scoring:**
- 80-100: Strong fundamentals, proceed with confidence
- 60-79: Acceptable with risk mitigation
- 40-59: Significant concerns, negotiate protections
- Below 40: Walk away or demand restructuring

### 3. Business Decision Matrix

**Should We Accept This Token as Payment?**
- Daily volume > 10x your expected monthly receipts? Yes
- Listed on 3+ regulated exchanges? Yes
- Stablecoin or pegged? Lower risk
- Score above 60? Proceed with hedging strategy

**Should We Hold Token Treasury?**
- Never hold >5% of company liquid assets in any single token
- Convert to stablecoin or fiat within 48 hours unless strategic hold
- Set automatic rebalancing triggers at +/-15%

**Should We Launch a Token?**
- Do you have real utility that requires a token? (Not just fundraising)
- Can you sustain demand without speculation?
- Legal budget of $50K-$200K for compliance?
- If all three = no, use traditional pricing instead

### 4. Vendor Token Lock-In Assessment

When a vendor uses token-based pricing:
- Calculate true USD cost per unit over 12 months
- Compare to non-token alternatives
- Assess token price volatility impact on budget
- Check if vendor holds majority supply (price manipulation risk)
- Review token unlock schedule for supply shock risk

### 5. Red Flags (Immediate Walk-Away)

1. Team allocation >40% with <2 year vesting
2. No audit of smart contracts
3. Anonymous team with no legal entity
4. Token required but adds no functional value
5. Circular tokenomics (token rewards for holding token)
6. No clear revenue model beyond token sales
7. Jurisdiction shopping to avoid regulation

### 6. Cost Framework

| Action | Small Business | Mid-Market | Enterprise |
|--------|---------------|-----------|-----------|
| Token evaluation (one-time) | $2K-$5K | $5K-$15K | $15K-$50K |
| Tokenomics design | $15K-$40K | $40K-$120K | $120K-$500K |
| Legal compliance (US) | $25K-$75K | $75K-$200K | $200K-$1M+ |
| Smart contract audit | $10K-$30K | $30K-$80K | $80K-$250K |
| Ongoing treasury management | $2K-$8K/mo | $8K-$25K/mo | $25K-$100K/mo |

### 7. Industry Applications

| Industry | Token Use Case | Risk Level | ROI Potential |
|----------|---------------|-----------|--------------|
| Fintech | Payment rails, lending | High (regulatory) | $500K-$5M/yr |
| SaaS | Usage-based compute credits | Medium | $100K-$800K/yr |
| Ecommerce | Loyalty programs, cross-border | Medium | $200K-$1.2M/yr |
| Real Estate | Tokenized fractional ownership | High (securities) | $1M-$10M+ |
| Healthcare | Data marketplace tokens | High (HIPAA + securities) | $300K-$2M/yr |
| Legal | Smart contract automation | Medium | $150K-$600K/yr |
| Manufacturing | Supply chain provenance | Low-Medium | $200K-$900K/yr |
| Construction | Milestone payment tokens | Medium | $100K-$500K/yr |
| Recruitment | Credential verification | Low | $50K-$300K/yr |
| Professional Services | Client billing tokens | Low-Medium | $80K-$400K/yr |

## Output Format

Present findings as:
1. Token Classification + Health Score (0-100)
2. Business Decision (accept/hold/launch/walk away)
3. Risk factors with mitigation steps
4. Cost estimates for recommended path
5. 90-day action plan

## Resources

- [AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) — Find where your business is losing money to inefficient processes
- [Industry Context Packs](https://afrexai-cto.github.io/context-packs/) — $47 per industry, covers tokenomics within each vertical
- [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/) — Deploy your own analysis agent in 5 minutes
