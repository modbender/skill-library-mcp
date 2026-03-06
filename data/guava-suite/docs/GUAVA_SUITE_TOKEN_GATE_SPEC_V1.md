# GUAVA Suite Token-Gate Spec v1

## 0. Goal
GuavaSuite（private機能）を $GUAVA 支払いで利用可能にし、GuavaGuard OSSと明確分離したまま安全に運用する。

## 1. Product split
- OSS: `guava-guard`（無料）
- Paid: `guava-suite`（Soul/Hash/Memory統合）

## 2. Licensing model (初期)
- Access method: **Pass NFT**（ERC-721, Polygon）
- Payment token: **$GUAVA (ERC-20)**
- Purchase: ユーザーが `buyWithGuava()` を実行 → Pass NFT mint
- Runtime check: Pass NFT保有 + 署名検証でsuite有効化

## 3. Why NFT pass first
- 1ユーザー=1ライセンスを扱いやすい
- 譲渡/無効化/バージョン管理が明確
- しきい値保有型より不正共有を制御しやすい

## 4. On-chain components
### 4.1 Contracts
1) `GuavaSuitePass.sol` (ERC-721)
- mint条件: `priceGuava` を支払い
- treasuryへ$GUAVA送金
- optional: non-transferable modeフラグ（初期はtransferable=false推奨）

2) `GuavaSuiteRegistry.sol`
- contract version
- revoked token list
- feature tier mapping

### 4.2 Existing token
- $GUAVA: `0x25cBD481901990bF0ed2ff9c5F3C0d4f743AC7B8`

## 5. Off-chain architecture
### 5.1 License service (minimal)
- endpoint: `/license/challenge` nonce発行
- endpoint: `/license/verify` 署名検証 + on-chain保有確認
- issue: 短命JWT（machine-bound）

### 5.2 Suite runtime
- 起動時にJWT検証
- 定期再検証（例: 24h）
- 検証失敗時: fail-closed（suite機能停止、guardは継続）

## 6. Security controls
- Nonce 1回限り
- JWT短命 + machine fingerprint
- rate limit
- revocation list
- 監査ログ（activation/deactivation）

## 7. TDD plan (t-wada)
RED→GREEN→REFACTORで全工程

### Stage A: Contract tests
- buyWithGuava success/failure
- insufficient allowance
- revoked pass rejected
- transfer policy checks

### Stage B: License service tests
- nonce replay rejected
- invalid signature rejected
- pass owner accepted
- expired token rejected

### Stage C: Runtime integration tests
- pass valid => suite enabled
- pass invalid => suite disabled / guard alive
- network fail => cached token within grace only

## 8. Delivery phases
1) P1 Spec + contracts skeleton
2) P2 Contract implementation + tests
3) P3 License service + tests
4) P4 Suite runtime gate + tests
5) P5 E2E testnet dry-run
6) P6 Mainnet release

## 9. Definition of Done
- [ ] 全テスト緑（contracts/service/runtime）
- [ ] testnetで購入→有効化→失効フロー実証
- [ ] mainnetデプロイTx記録
- [ ] OSSとprivateの境界監査完了
- [ ] Runbook更新

## 10. Non-negotiables
- suite検証失敗時は必ず停止（fail-closed）
- guard OSSは常に利用可能
- secretをチャットに貼らない
