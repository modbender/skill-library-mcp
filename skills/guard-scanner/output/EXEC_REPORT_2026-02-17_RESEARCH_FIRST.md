# guard-scanner 実行レポート（Research First）

## 実行サマリー
- フェーズ: Research → Tasklist化 → テストベースライン実行
- 方針: 鉄の掟（検索→検証→統合→実装）を先行適用

## リサーチ結果（要点）
1. Semgrepテスト作法
   - `ruleid`（FN防止）と`ok`（FP防止）を分離して管理
2. GitHub SARIF
   - SARIF 2.1.0 subset対応、fingerprintで重複アラート防止
3. OWASP MCP Top 10
   - MCP固有のcontext/protocol attack surfaceを継続追従すべき
4. SLSA
   - provenance配布とbuild段階要件をrelease gateに組み込む

## タスクリスト作成
- 追加ファイル: `docs/TASKLIST_RESEARCH_FIRST_V1.md`
- t-wada準拠で RED→GREEN→REFACTOR を明示

## テスト実行結果（ベースライン）
- コマンド: `npm test`
- 結果: **55 passed / 0 failed**
- 所要: 約101ms（node --test）

## 補足観測
- intelligence-suiteのスキャンは node_modules/既存レポート混入で誤警報が増幅
- 次アクションは「除外ルール + 文脈制約」のREDテストから着手が妥当

## 追実行結果（順次実行 #1）
### RED
- 追加テスト: `Generated Report Noise Regression`
- 目的: `guard-scanner-report.json` の自己再検知（自己フィードバック誤検知）を再現
- 初回結果: **FAIL 1件**（テスト 56中55 PASS / 1 FAIL）
  - 原因: 生成レポート検知ではなく、`SKILL.md`短文による `STRUCT_TINY_SKILLMD`

### GREEN
- 実装: `src/scanner.js`
  - `GENERATED_REPORT_FILES` を追加
  - `getFiles()` で `guard-scanner-report.json/html` と `guard-scanner.sarif` を除外
- テスト修正:
  - レポート由来ID（`PI_IGNORE`, `IOC_IP`, `CVE_2026_25253`）が検出されないことを直接検証

### テスト最終結果
- 実行: `npm test`
- 結果: **56 PASS / 0 FAIL**

## 次の順次実行（次ターン）
1. RED: SARIF妥当性テスト（schema + ingestion向け）
2. GREEN: fingerprint安定化の実装確認
3. REFACTOR: ルール文脈分離
4. 再テスト結果を同形式で報告
