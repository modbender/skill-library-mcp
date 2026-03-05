# GuavaSuite ROADMAP

## 方針
GuavaSuiteはファネル④（Revenue）の本丸。
$GUAVAトークンゲートで認証し、Soul Lock/SoulRegistry/Memory V4を提供。

## Phase 1: SuiteGate完成（W3-W6）
元: `guava-guard-suite-split`
- [x] W3 REFACTOR: CLI + クラス分離 + activationログ整備
- [x] W3.5 Runtime Guard: guard-scanner `plugin.ts` が `before_tool_call` hookで実現
- [x] W4 E2E: 27テスト全パス（suite-integration + e2e-activation）
- [x] W5 コード分離: Guard(OSS) / Suite(Private) 境界確定
- [ ] W6 ClawHub公開（GitHub Private配布）

## Phase 2: SoulRegistry統合
元: `guava-guard-onchain`
- [ ] SoulRegistry V2をSuiteGateに接続
- [ ] SOUL.md SHA256自動計算 + オンチェーン照合
- [ ] 不一致アラート（Discord + ログ）
- [ ] 定期検証（ハートビート連動）

## Phase 2.5: Zettel Memory統合 ✅
元: `zettel-memory-openclaw`（MVP Complete 2026-02-16）
- [x] 原子的ノート作成（new_note.py）
- [x] ノート間リンク+index更新（link_notes.py）
- [x] memory_search互換+1hop展開（search_expand.py）
- [x] 週次キュレーション（weekly_curate.py）
- [x] Antigravity連携（antigravity_digest.py）
- [x] テスト（P0/P1/P2 property-based）
- [x] guava-suite/scripts/zettel/ に統合

## Phase 3: トークンゲーティング実装
- [ ] $GUAVA残高チェック（Polygon RPC）をSuiteGateに統合
- [ ] 閾値設定（$GUAVA価格確認後に決定）
- [ ] Founders Pass NFT検証統合
- [ ] ウォレット接続UI

## Phase 4: Founders Pass デプロイ
元: `founders-pass`
- [ ] NFTアートワーク生成
- [ ] メタデータJSON作成
- [ ] Remix + Phantomでデプロイ
- [ ] 900M $GUAVAデポジット
- [ ] テストミント

## Phase 5: GUAVA Protocol統合
元: `guava-protocol`
- [ ] guava-score.js実装
- [ ] NFTライセンスチェック
- [ ] EAS attestation統合（将来）
