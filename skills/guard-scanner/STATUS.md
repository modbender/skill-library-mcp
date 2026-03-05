# guard-scanner — STATUS

## ステータス: 🟢 v2.1.0 公開済み（PII検出 + Shadow AI + Plugin Hook実ブロック）

## ファネル上の位置: ② TRUST（信頼構築）

## 概要
AIエージェントのスキル脅威を検出するセキュリティスキャナー。OSS/無料。
論文で引用 → 学術権威 → ユーザー獲得の入口。

## 公開先
- **npm**: `guard-scanner@2.1.0` → `npx guard-scanner`
- **ClawHub**: `guard-scanner@2.1.0`
- **GitHub**: [koatora20/guard-scanner](https://github.com/koatora20/guard-scanner)
- **OpenClaw活動**:
  - PR #19413（docs: Runtime Security Guard リファレンス追加）
  - Issue #19639（Workspace Config Tamperingセキュリティレポート）
  - Issue #19640（Workspace File Integrity Protection RFC）
  - Issue #18677（Security Scan Hook API提案）

## スペック（v2.1.0）
- 21脅威カテゴリ / 129パターン
- **v2.1 PII Exposure検出**: ハードコードPII / PII出力・ログ / Shadow AI / PII収集指示（OWASP LLM02/06対応）
- **Plugin Hook Runtime Guard**（`plugin.ts` — `block`/`blockReason` API で実際にブロック可能）
- 2 enforcement modes（無料）: `monitor`（log only） / `enforce`（CRITICAL block）
- `strict`モード（HIGH+CRITICAL block）は **GuavaSuite専用**（$GUAVAトークンゲート）
- Legacy Internal Hook（`handler.ts`）も後方互換で保持（warn-only）
- Plugin API / SARIF・HTML・JSON出力
- ゼロ依存
- **⚠️ 非搭載**: Soul Lock / SoulRegistry / Memory Guard（→ GuavaSuite専用機能）

## テスト
- スキャナー: 64 PASS（v2.1 PII 8テスト含む）
- Plugin Hook: 35 PASS
- **合計: 99テスト / 0 FAIL**

## 進捗（2026-02-18）
- [x] 鉄の掟で事前リサーチ（Semgrep / SARIF / OWASP MCP / SLSA）
- [x] `docs/TASKLIST_RESEARCH_FIRST_V1.md` 作成（RED→GREEN→REFACTOR）
- [x] RED: 生成レポート自己再検知ノイズの再現テスト追加
- [x] GREEN: `guard-scanner-report.{json,html}` / `.sarif` をデフォルト除外
- [x] v1.1.0: sandbox-validation / complexity / config-impact 3カテゴリ追加（17→20カテゴリ）
- [x] v1.1.1: Runtime Guard hook を公式 InternalHookEvent/Handler 型に修正
- [x] **v2.0.0: Plugin Hook (`plugin.ts`) 実装 — `block`/`blockReason` で実ブロック**
- [x] **v2.1.0: PII Exposure検出（13パターン追加、21カテゴリ、Shadow AI検出）**
- [x] OpenClaw PR #19413 提出（docs-only、ファクトチェック3周済み）
- [x] OpenClaw Issue #19639, #19640 提出（脆弱性レポート+RFC）
- [x] jheeannyからの質問に全回答済み、HenryLoenwindにも返信済み
- [x] npm publish v2.0.0 完了
- [x] **npm + ClawHub publish v2.1.0 完了**（2026-02-18）
- [x] OpenClaw公式ソース検証: SKILL.md仕様・Gating・ClawHubセキュリティとguard-scannerの整合性確認済み
- [x] T4/G4実装: SARIF妥当性テスト強化 + `partialFingerprints.primaryLocationLineHash` 追加

## 次のアクション
1. **v2.2 OWASP Gen AI Top 10 全カバー**: LLM02,04,07,08,09,10
2. **コミュニティ駆動化**: Reddit/HN/X英語ポスト → スター集め → パターン貢献加速
3. OpenClaw公式メンテナーからの返答待ち
4. note.com記事: PII検出 + Shadow AI検出の紹介

## コミュニティ成果
- [x] OpenClaw Discord向け技術共有ドラフト作成: `output/OPENCLAW_DISCORD_TECHNICAL_SHARE_DRAFT_2026-02-18.md`
- [x] OpenClaw docs向けPR-readyパッチ作成: `docs/OPENCLAW_DOCS_PR_READY_PATCH.md`
- [x] #18677にdocs追加前提のフォローアップ投稿
- [x] jheeannyがguard-scanner + chmod 444の運用を開始（外部採用第一号）
