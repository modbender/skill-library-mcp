# Changelog

All notable changes to the Web3 Investor Skill will be documented in this file.

## [0.2.1] - 2026-03-04

### Added

#### Investment Preference System (B+C Hybrid Approach)
- **New Module**: `investment_profile.py` - User preference collection and filtering
  - `InvestmentProfile` class for structured preference management
  - Support for 5 key preference dimensions:
    - Chain selection (ethereum, base, arbitrum, optimism)
    - Capital token (USDC, USDT, ETH, etc.)
    - Reward preference (single/multi/none tokens)
    - Impermanent loss acceptance (True/False)
    - Underlying asset type (RWA/on-chain/mixed)
  - `get_questions()` method for Agent UI building
  - `filter_opportunities()` method for one-shot filtering
  - `explain_filtering()` for human-readable results

#### Enhanced Risk Signals
- **New fields** in `find_opportunities.py` risk_signals output:
  - `reward_type`: "none" | "single" | "multi" - Token reward structure
  - `has_il_risk`: True | False - Impermanent loss risk indicator
  - `underlying_type`: "rwa" | "onchain" | "mixed" | "unknown" - Asset backing type
- **Detection functions**:
  - `detect_reward_type()`: Analyzes rewardTokens array
  - `detect_il_risk()`: Identifies DEX LP and multi-asset volatility risks
  - `detect_underlying_type()`: Categorizes RWA vs on-chain protocols

#### Documentation Updates
- **Disclaimer added**: Clear statement that skill provides info only, not investment advice
- **Investment Preference Guide**: New section in SKILL.md with:
  - Required questions (chain, capital_token)
  - Important questions (reward preference, IL acceptance, underlying type)
  - Usage examples for InvestmentProfile class

### Fixed

- **Import bug**: `unified_search.py` Dune MCP import path issue
  - Added multi-layer fallback import mechanism
  - Supports absolute, relative, and dynamic imports

### Technical Details

**Architecture**: B+C Hybrid Approach
- **Approach B**: Standalone `InvestmentProfile` module for convenience
- **Approach C**: Enhanced `risk_signals` in existing API for flexibility
- Agents can choose: use convenience tool OR process raw signals themselves

**Backward Compatibility**: ✅ Fully maintained
- All existing APIs work unchanged
- New fields are additive only
- No breaking changes

---

## [0.2.0] - 2026-03-04

### Major Refactoring

#### Risk Assessment Redesign
- **Removed**: Local `calculate_risk_score()` function
- **Added**: `risk_signals` collection for LLM-based analysis
- **Philosophy**: Skill provides data, user's LLM makes risk judgments

#### Actionable Addresses
- **New structure**: `actionable_addresses` in opportunity output
  - `deposit_contract_candidates`: List of potential deposit contracts
  - `underlying_token_addresses`: Underlying asset addresses
  - `reward_token_addresses`: Reward token addresses
  - `has_actionable_address`: Boolean execution readiness flag
  - `primary_contract`: Main protocol contract from registry
  - `protocol_registry_match`: Whether protocol found in static registry

#### Trading Execution Optimization
- **Balance pre-check**: `check_balance_before_deposit()` function
  - Native token balance queries via RPC
  - ERC20 token balance queries
- **Deposit preview**: Calldata generation for Aave/Compound/Lido
  - `generate_aave_deposit_calldata()`
  - `generate_compound_deposit_calldata()`
- **Safe Vault v0.2.0**: Complete rewrite with CLI improvements

#### Protocol Registry
- **New file**: `config/protocols.json`
  - JSON format for reliable parsing
  - 12 protocols with metadata
  - Contract addresses and method signatures

#### Unified Search
- **Dune MCP integration**: Adapter for Dune Analytics
- **LLM-ready output**: `--llm-ready` flag for formatted prompts
- **Version tracking**: Output includes version field

---

## [0.1.0] - 2026-03-03

### Initial Release

#### Core Features
- Opportunity discovery via DefiLlama API
- Basic risk scoring (local algorithm)
- Safe Vault transaction preparation
- Whitelist and limit protection
- Portfolio indexing

#### Known Limitations (Documented)
- DefiLlama API data parsing issues
- Risk scoring algorithm accuracy concerns
- Portfolio indexer limited to basic token balances

---

## Version History Summary

| Version | Date | Key Changes |
|---------|------|-------------|
| 0.2.1 | 2026-03-04 | Investment preferences, enhanced risk signals, disclaimer |
| 0.2.0 | 2026-03-04 | Risk redesign, actionable addresses, trading optimization |
| 0.1.0 | 2026-03-03 | Initial release, basic functionality |

---

## Future Roadmap

### Phase 2 (Planned)
- Execute Dune queries for actual APY data
- Safe{Wallet} multisig integration
- Transaction history logging
- Gas optimization strategies

### Phase 3 (Roadmap)
- Insurance mechanism
- Drawdown controls
- Full autonomous mode

---

**Maintainer**: Web3 Investor Skill Team
**Repository**: https://github.com/openclaw/web3-investor
**Registry**: https://clawhub.com