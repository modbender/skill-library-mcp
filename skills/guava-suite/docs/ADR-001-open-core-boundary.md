# ADR-001: Open Core Boundary for GuavaGuard/GuavaSuite

- Status: Accepted
- Date: 2026-02-17
- Deciders: dee, guava

## Context
公開価値（再現性・信頼）と高感度防御（Soul/Hash/Memory統合）を同一コードベースで扱うと、漏洩・運用事故・主張不整合が発生しやすい。

## Decision
Open Core + Sealed Extensions を採用。
- GuavaGuard: OSS core
- GuavaSuite: private extension
- 接続は plugin API + ACL のみ

## Consequences
### Positive
- OSSの信頼性と採用性を維持
- 高感度ロジックの管理強化
- 学術主張（再現可能）と事業優位（private）を両立

### Negative
- 境界管理コスト増加
- 契約テスト・バージョン管理の運用負荷

## Implementation Rules (t-wada TDD)
1. RED: 契約テストを先に書く（境界破壊ケース含む）
2. GREEN: 最小実装で通す
3. REFACTOR: 責務分離・命名改善・重複除去
4. 常に小さく刻む（1変更1意図）

## Verification Checklist
- [ ] OSS単体で全テスト緑
- [ ] private未接続でfail-closed動作
- [ ] direct import禁止ルール有効
- [ ] plugin version handshakeテスト有効
