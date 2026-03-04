# TASKLIST_TWADA_V2

## Objective
GuavaSuite token-gate を t-wada（Red→Green→Refactor）で完遂する。

## Phase 1 (W1) Contracts — ✅ Done
- [x] GuavaSuitePass / Registry / MockToken 実装
- [x] テスト 5 passing

## Phase 2 (W2) License API — ✅ Done
### RED ✅
- [x] nonce再利用を拒否するテスト
- [x] 不正署名を拒否するテスト
- [x] 期限切れトークンを拒否するテスト
- [x] pass未保有アドレスを拒否するテスト
### GREEN ✅
- [x] `/license/challenge` 実装（nonce発行）
- [x] `/license/verify` 実装（署名 + 所有確認 + JWT発行）
### REFACTOR ✅ (2026-02-17)
- [x] service層分離（NonceStore / SignatureVerifier / TokenIssuer）
- [x] エラーモデル統一（errors.js + LicenseError）
- [x] EIP-712署名検証（stub + ethers DI対応）
- [x] JWT発行（jsonwebtoken）
- [x] HTTPサーバー（Node built-in http）
- [x] テスト: 5ファイル28本全PASS + Hardhat 5本 = 33本全GREEN

## Phase 3 (W3) Runtime Gate — 🚧 REFACTOR残り (2026-02-17〜)
### RED ✅
- [x] JWT失効時にsuite停止・guard継続テスト
- [x] network障害時grace期間テスト
- [x] grace期間超過時fail-closedテスト
### GREEN ✅
- [x] SuiteGate middleware実装（fail-closed + grace period）
- [x] Grace period cache実装（graceDeadline状態管理）
- [x] check()でgrace deadline優先の修正（fail-closed保証）
- [x] テスト: 6ファイル38本全PASS
### REFACTOR
- [ ] activationログ整備
- [ ] guard-only fallbackの動作確認E2Eテスト

## Phase 4 (W4) E2E + Hardening
- [ ] testnetで購入→検証→有効化→失効
- [ ] Hardhat fork modeでPolygon Mainnet $GUAVA統合テスト
- [ ] Runbook更新
- [ ] Release checklist完了

## Guardrails
- 実装前に必ずリサーチ（仕様/脆弱性）
- 1コミット1意図
- 失敗はfixlog/STATUSへ即反映

## 引き継ぎメモ（後輩AIへ）
- テスト実行: `cd services/license-api && npm test`（vitest 38本）
- コントラクトテスト: `npx hardhat test`（5本）
- HTTPサーバー起動: `JWT_SECRET=xxx node src/server.js`（port 3100）
- プロジェクト設計書: `docs/` フォルダ参照（ARCH_SPLIT, ADR-001, TOKEN_GATE_SPEC）
- SuiteGateの設計: fail-closed（suiteEnabled=false, guardEnabled=true always）
- Grace period: networkFailure()後、graceMs以内はsuite継続、超過でfail-closed
