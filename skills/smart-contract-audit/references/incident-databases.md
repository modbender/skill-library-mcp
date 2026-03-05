# Smart Contract Vulnerability & Incident Databases

Cross-reference these databases when validating findings. Matching real-world incidents adds credibility and demonstrates the vulnerability class is exploitable.

## Audit Finding Databases

### Solodit
- **URL:** https://solodit.cyfrin.io/
- **What:** Largest aggregated database of audit findings from Code4rena, Sherlock, CodeHawks, Cantina, and private audits
- **Search:** Full-text search by vulnerability type, contract pattern, or protocol name. Filter by severity, contest, platform.
- **Unique:** Aggregates findings across all major audit platforms. Best for "has this exact pattern been flagged before?"
- **Use:** `site:solodit.cyfrin.io [vulnerability pattern]` via web search

### CodeHawks
- **URL:** https://codehawks.cyfrin.io/
- **What:** Competitive audit findings from Cyfrin's audit contest platform
- **Search:** Browse by contest, filter by severity
- **Unique:** Higher-quality findings (competitive = incentivized thoroughness)

## Exploit Reproduction & Education

### DeFiHackLabs
- **URL:** https://github.com/SunWeb3Sec/DeFiHackLabs
- **What:** 405+ real DeFi exploit reproductions as Foundry test files
- **Search:** Browse by year, search README for protocol name or attack type
- **Unique:** Executable PoCs — you can fork and run the actual exploit. Best for understanding attack mechanics.

### DeFiVulnLabs
- **URL:** https://github.com/SunWeb3Sec/DeFiVulnLabs
- **What:** Educational vulnerability examples in Foundry — simplified versions of real bug classes
- **Search:** Browse by vulnerability category (reentrancy, oracle, access control, etc.)
- **Unique:** Pedagogical — each example is minimal and self-contained. Good for understanding fundamentals.

## Incident Tracking

### Web3HackHub (SolidityScan)
- **URL:** https://solidityscan.com/web3hackhub
- **What:** Comprehensive hack incident database since 2011
- **Search:** Filter by chain, year, attack type, loss amount
- **Unique:** Structured data with attack classification and loss amounts

### SlowMist Hacked
- **URL:** https://hacked.slowmist.io/
- **What:** 2000+ blockchain security incidents across all chains
- **Search:** Filter by chain, type (DeFi, CEX, NFT), year
- **Unique:** Broadest coverage including non-DeFi incidents (exchanges, bridges, wallets)

### de.fi REKT Database
- **URL:** https://de.fi/rekt-database
- **What:** Structured hack data with detailed post-mortems
- **Search:** Filter by chain, attack vector, date, loss amount
- **Unique:** Clean structured data, good for statistical analysis of attack trends

### Rekt News
- **URL:** https://rekt.news/leaderboard/
- **What:** In-depth post-mortem write-ups of major DeFi exploits
- **Search:** Browse leaderboard (sorted by loss), search by protocol name
- **Unique:** Narrative-style analysis — best for understanding the full attack story and root cause

## Formal Classification

### SWC Registry
- **URL:** https://swcregistry.io/
- **What:** Smart Contract Weakness Classification — formal taxonomy (SWC-100 through SWC-136)
- **Search:** Browse by ID or keyword
- **Unique:** Standard classification system for tagging findings. Maps to CWE (Common Weakness Enumeration).
- **Use:** Tag every finding with its SWC ID for standardized reporting

## Incident Response

### BlockSec
- **URL:** https://blocksec.com/
- **What:** Security firm specializing in real-time attack detection and incident response
- **Search:** Blog posts and Twitter for incident analysis
- **Unique:** Often first to publish technical analysis of in-progress attacks. Phalcon block explorer for tx-level attack visualization.

## How to Use These in Audits

1. **Before auditing:** Check if the protocol type has known exploit patterns (search DeFiHackLabs for similar protocols)
2. **During review:** For each finding, search Solodit for matching patterns from real audits
3. **For the report:** Include Solodit/Rekt references for Medium+ findings to demonstrate real-world relevance
4. **For PoCs:** Use DeFiHackLabs as templates for Foundry-based exploit demonstrations
