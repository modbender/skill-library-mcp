# Implementation Plan v1 (Must-Finish)

## Timeline (aggressive but realistic)
- Day 1: Contract spec/final ABI + tests red
- Day 2: Contract green + deploy to Polygon testnet
- Day 3: License service red/green
- Day 4: Suite runtime gate red/green
- Day 5: E2E + hardening + release checklist

## Work breakdown

### W1 Contracts
- `contracts/GuavaSuitePass.sol`
- `contracts/GuavaSuiteRegistry.sol`
- unit tests + property tests

### W2 License service
- `services/license-api/`
- nonce/signature/JWT
- on-chain read via viem/ethers

### W3 Runtime integration
- `guava-suite` boot gate
- token validation middleware
- grace-period cache

### W4 Ops
- monitoring
- revocation command
- incident runbook

## Exit criteria per work item
- W1: all contract tests pass + gas report
- W2: replay/forgery tests pass
- W3: fail-open paths = 0
- W4: alert on verify failures + docs complete

## Anti-abandon protocol (must finish)
1. 毎日 `STATUS.md` 更新（Done/Next/Blocker）
2. 未完了で日跨ぎ時は必ず「次の1手」を明記
3. ブロッカー24h超えたら代替案を即決
4. スコープ追加は禁止（完了まで）

## Kill criteria (only valid reasons)
- 致命的法務リスク
- mainnet不可逆バグ
- 依存停止（chain/provider outage）

## Release checklist
- [ ] Security review complete
- [ ] Testnet validation complete
- [ ] Mainnet deployment recorded
- [ ] Docs + Runbook updated
- [ ] Rollback plan documented
