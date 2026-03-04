# guard-scanner ROADMAP v5

## 方針
guard-scannerはOpenClaw完全互換セキュリティスキャナー。OSSで実力を証明し、論文で引用する。
**OpenClaw完全互換一本。静的+ランタイム統合 × ゼロ依存 × 最大パターンDB が差別化軸。**

## 競合ランドスケープ（2026-02-24 時点）

| ツール | 方式 | guard-scanner との差 |
|---|---|---|
| ClawBands | before_tool_call → human approval | ランタイムのみ。静的なし |
| ClawGuardian | before/after + PII redaction | PII検出あり。静的なし |
| SecureClaw | plugin + behavior skill | config hardening。静的なし |
| Agentic Radar | LLMワークフロー全体分析 | 汎用。OpenClaw特化じゃない |
| @merchantguard/guardscan | 102パターン | 俺らの190+で圧勝 |
| ClawMoat | 37テスト | 俺らの133で圧勝 |
| Agent Guard | 設定スキャナ | カテゴリ違い |

**guard-scanner だけが持つ組み合わせ**: 静的+ランタイム / 190+パターン / ゼロ依存 / SARIF出力 / 0.016ms/scan

---

## v1.0.0 ✅
- [x] 静的スキャン 17カテゴリ/170+パターン
- [x] Runtime Guard hook 12パターン/3モード
- [x] Plugin API / SARIF・HTML・JSON出力
- [x] npm + GitHub公開

## v1.1.0 ✅ — sandbox検証 + 複雑度 + 設定インパクト
- [x] SKILL.md manifest validation（sandbox-validation）
- [x] Code complexity metrics
- [x] Config impact analysis
- [x] config-impactパターン6種追加
- [x] calculateRisk倍率 + レコメンデーション追加
- カテゴリ数: 17→20 / パターン数: 170+→186

## v2.0.0 ✅ — Plugin Hook Runtime Guard
- [x] plugin.ts: Plugin Hook API版（block/blockReason対応）
- [x] 3 enforcement modes: monitor/enforce/strict
- [x] Config via openclaw.json

## v2.1.0 ✅ — PII + Shadow AI
- [x] PII検出カテゴリ化（クレカ、SSN、電話番号、メール）
- [x] Shadow AI検出（無許可外部LLM API呼び出し）
- [x] 3リスクアンプリファイア追加
- パターン数: 186→190+

## v3.0.0 ✅ — TypeScript + OWASP LLM Top 10 2025
- [x] TypeScript完全リライト
- [x] OWASP LLM01-LLM07マッピング
- [x] LLM07 System Prompt Leakage（5パターン）
- [x] install-check CLIコマンド
- [x] SARIF OWASPタグ

## v3.1.0 ✅ — OpenClawプラグイン互換
- [x] openclaw.plugin.json マニフェスト
- [x] Layer 2: Trust Defense（4パターン）
- [x] Layer 3: Safety Judge（3パターン）
- [x] Runtime patterns: 12→19

## v3.3.0 ✅ — Layer 4: Brain（行動監視）
- [x] RT_NO_RESEARCH / RT_BLIND_TRUST / RT_CHAIN_SKIP
- [x] Runtime patterns: 19→22（4層アーキテクチャ）

## v3.4.0 ✅ — Runtime Guard Module + OWASP ASI
- [x] src/runtime-guard.js: ゼロ依存JSモジュール
- [x] Layer 5: Trust Exploitation（4 OWASP ASI09パターン）
- [x] Runtime patterns: 22→26（5層アーキテクチャ）
- [x] 133テスト全パス

## v4.0.0 ✅ — Benchmarked & Battle-Tested（2026-02-24）
- [x] ベンチマーク実証: 0.016ms/scan（V8 JIT）
- [x] vs Rust WASM (0.105ms) / napi-rs (0.051ms) — V8 JIT最速
- [x] GuavaSuite before_tool_call hook統合
- [x] CHANGELOG / HOOK.md / openclaw.plugin.json 全更新
- [x] npm publish成功（SHA: 6b497d8d）
- [x] X投稿完了

---

## v5.0.0 — コミュニティの声を聞いてから決める
> OpenClaw完全互換を維持しつつ、コミュニティからのフィードバックで方向性を決定。
> 候補:
> - AST解析（脱regex）
> - ML検出（難読化/AI生成コード判定）
> - SBOM生成
> - YAML パターン定義（非プログラマー貢献可能化）
> - GitHub Actions CI統合

## 宣伝ロードマップ
- [x] npm publish v4.0.0
- [x] X投稿（@guava_asi）
- [ ] Reddit r/AI_Agents, r/cybersecurity 投稿（手動）
- [ ] Discord OpenClaw #showcase 挨拶
- [ ] GitHub Discussion投稿（ブロック解除待ち）
- [ ] Hacker News Show HN
- [ ] ClawHub登録（ブロック解除後）

## 一次ソース
- [OWASP Top 10 LLM 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OWASP Agentic Security Top 10](https://owasp.org/www-project-top-10-for-agentic-security/)
- [OWASP Secure MCP Guide (2026-02-16)](https://owasp.org/www-project-gen-ai-security/)
- npm: https://www.npmjs.com/package/guard-scanner
- GitHub: https://github.com/koatora20/guard-scanner
