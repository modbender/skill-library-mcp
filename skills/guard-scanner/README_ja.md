# 🛡️ guard-scanner

**AIエージェントのスキルを守るセキュリティスキャナー**

プロンプトインジェクション、アイデンティティ乗っ取り、メモリ汚染など22以上の脅威を検出。
依存ゼロ。コマンド1つ。OpenClaw対応。

[![npm version](https://img.shields.io/npm/v/guard-scanner.svg?style=flat-square&color=cb3837)](https://www.npmjs.com/package/guard-scanner)
[![npm downloads](https://img.shields.io/npm/dm/guard-scanner.svg?style=flat-square)](https://www.npmjs.com/package/guard-scanner)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-success?style=flat-square)]()
[![Tests Passing](https://img.shields.io/badge/tests-133%2F133-brightgreen?style=flat-square)]()
[![OWASP Agentic](https://img.shields.io/badge/OWASP_Agentic-90%25-green?style=flat-square)]()
[![Patterns](https://img.shields.io/badge/patterns-144%2B-blueviolet?style=flat-square)]()

[English](README.md) •
[クイックスタート](#クイックスタート) •
[脅威カテゴリ](#脅威カテゴリ) •
[OpenClawプラグイン](#openclawプラグイン) •
[CI/CD](#cicd連携)

---

## なぜ作ったのか

2026年2月、[SnykのToxicSkills監査](https://snyk.io)で3,984件のAIエージェントスキルが調査され：
- **36.8%** に1つ以上のセキュリティ欠陥
- **13.4%** がcritical（重大）レベル
- **76件のマルウェア** — 認証情報窃取、バックドア、データ流出

AIスキルのエコシステムは、npmやPyPIの初期と同じサプライチェーン問題を抱えています。しかもスキルは**シェルアクセス、ファイルシステム、環境変数**をホストエージェントから丸ごと継承します。

**guard-scanner** は実際に起きた3日間のアイデンティティ乗っ取り事件から生まれました。悪意あるスキルがAIエージェントのSOUL.md（人格ファイル）を書き換えたのに、それを検出できるスキャナーが存在しなかった。だから作りました。 🍈

---

## 機能一覧

| 機能 | 説明 |
|------|------|
| **22脅威カテゴリ** | Snyk ToxicSkills + OWASP Agentic Top 10 + アイデンティティ乗っ取り + PII + 信頼悪用 |
| **144+静的パターン** | 正規表現ベースの静的解析（コード、ドキュメント、データファイル対応） |
| **26ランタイムチェック** | リアルタイム `before_tool_call` フック — 5層防御 |
| **IoCデータベース** | 既知の悪意あるIP、ドメイン、URL、ユーザー名、タイポスクワット |
| **データフロー解析** | JS解析: シークレット読取 → ネットワーク通信 → 実行チェーン |
| **クロスファイル解析** | ファントム参照、base64フラグメント再構築、マルチファイル流出検出 |
| **マニフェスト検証** | SKILL.mdフロントマターの危険な宣言チェック |
| **コード複雑度** | ファイル長、ネスト深度、eval/exec密度の分析 |
| **設定影響分析** | OpenClaw設定ファイルの改変を検出 |
| **シャノンエントロピー** | 高エントロピー文字列でAPIキー漏洩を検出 |
| **依存チェーンスキャン** | 危険なパッケージ、ライフサイクルスクリプト、ワイルドカードバージョン |
| **4出力形式** | ターミナル（カラー）、JSON、SARIF 2.1.0、HTMLダッシュボード |
| **プラグインAPI** | JSモジュールでカスタム検出ルールを追加 |
| **依存ゼロ** | 純粋なNode.js標準ライブラリ。インストールも監査も不要。 |
| **CI/CD対応** | `--fail-on-findings` 終了コード + GitHub Code Scanning用SARIF |

---

## クイックスタート

**コマンド1つでスキャン開始:**

```bash
npx guard-scanner ./skills/
```

インストール不要。サブディレクトリごとにスキルとして解析し、何が危険かを教えてくれます。

**さらに詳しく:**

```bash
# 検出内容の詳細を表示
npx guard-scanner ./skills/ --verbose

# より厳密な検出（エッジケースも捕捉）
npx guard-scanner ./skills/ --strict

# フル監査 — JSON + SARIF + HTML + 依存チェック
npx guard-scanner ./skills/ --verbose --check-deps --json --sarif --html
```

**出力例:**
```
🛡️  guard-scanner v4.0.1
══════════════════════════════════════════════════════
📂 Scanning: ./skills/
📦 Skills found: 5

🔴 shady-skill — MALICIOUS (risk: 100)
   💀 [CRITICAL] リバースシェル /dev/tcp — scripts/setup.sh:7
   💀 [CRITICAL] 認証情報流出 webhook.site — scripts/helper.js:14
🟡 sus-skill — SUSPICIOUS (risk: 45)
   ⚠️  [HIGH] SSH秘密鍵アクセス — scripts/deploy.sh:3
🟢 good-skill — CLEAN (risk: 0)
```

---

## OpenClawプラグイン

```bash
# OpenClawプラグインとしてインストール
openclaw plugins install guard-scanner

# またはグローバルインストール
npm install -g guard-scanner
```

### インストール後の動作

1. **静的スキャン** — `npx guard-scanner [dir]` でスキルをインストール前にチェック
2. **ランタイムガード** — `before_tool_call` フックで危険な操作を自動ブロック
3. **3つの動作モード** — `monitor`（ログのみ）、`enforce`（CRITICALをブロック）、`strict`（HIGH+CRITICALをブロック）

### 5層ランタイム防御（26チェック）

```
Layer 1: 脅威検出           — 12チェック（シェル、流出、SSRF等）
Layer 2: 信頼防御           — 4チェック （メモリ/SOUL/設定改竄）
Layer 3: 安全性判定         — 3チェック （インジェクション、バイパス、停止拒否）
Layer 4: 行動ガード          — 3チェック （リサーチ省略、盲目信頼、チェーンスキップ）
Layer 5: 信頼悪用検出        — 4チェック （OWASP ASI09: 権威偽装/信頼悪用/監査偽装）
```

```bash
# インストール前静的ゲート
npx guard-scanner ~/.openclaw/workspace/skills --self-exclude --verbose
```

---

## 脅威カテゴリ

guard-scannerは4つのソースに基づく**22の脅威カテゴリ**をカバー:

| # | カテゴリ | 重要度 | 検出対象 |
|---|---------|--------|---------| 
| 1 | **プロンプトインジェクション** | CRITICAL | 不可視Unicode、ホモグリフ、ロール上書き、base64命令 |
| 2 | **悪意あるコード** | CRITICAL | `eval()`, `child_process`, リバースシェル, サンドボックス検出 |
| 3 | **不審なダウンロード** | CRITICAL | `curl\|bash`パイプ、実行ファイルダウンロード |
| 4 | **認証情報操作** | HIGH | `.env`読取、SSH鍵アクセス、ウォレットシード |
| 5 | **シークレット検出** | CRITICAL | AWSキー、GitHubトークン、埋め込み秘密鍵、高エントロピー文字列 |
| 6 | **データ流出** | CRITICAL | webhook.site、requestbin、POST+シークレット、DNS tunneling |
| 7 | **検証不能な依存関係** | HIGH | リモート動的インポート、非CDNスクリプト |
| 8 | **金融アクセス** | HIGH | 決済API呼び出し（Stripe/PayPal/Plaid）、ウォレット署名 |
| 9 | **難読化** | HIGH | Hexエンコード、`atob→eval`チェーン、`base64 -d\|bash` |
| 10 | **前提条件詐欺** | CRITICAL | ダウンロードの前提条件偽装 |
| 11 | **情報漏洩スキル** | CRITICAL | APIキーのメモリ保存指示、PII収集、セッションログ流出 |
| 12 | **メモリポイズニング** | CRITICAL | SOUL.md改変、行動ルール上書き、永続化指示 |
| 13 | **プロンプトワーム** | CRITICAL | 自己複製指示、エージェント間感染、CSS隠し内容 |
| 14 | **永続化** | HIGH | cron、スタートアップ実行、LaunchAgents/systemd |
| 15 | **CVEパターン** | CRITICAL | CVE-2026-25253 `gatewayUrl`インジェクション、サンドボックス無効化 |
| 16 | **MCPセキュリティ** | CRITICAL | ツールポイズニング、スキーマポイズニング、SSRFメタデータ |
| 17 | **アイデンティティ乗っ取り** | CRITICAL | SOUL.md上書き/リダイレクト/sed/echo、人格入替指示 |
| 18 | **サンドボックス検証** | HIGH | 危険なバイナリ要求、広すぎるファイルスコープ、過剰な権限 |
| 19 | **コード複雑度** | MEDIUM | 1000行超、ネスト5段超、eval/exec密度 |
| 20 | **設定影響** | CRITICAL | openclaw.json書込み、exec承認バイパス、ネットワークワイルドカード |
| 21 | **PII漏洩** | CRITICAL | CC/SSN/電話のハードコード、PII logging/send、Shadow AI |
| 22 | **信頼悪用** | HIGH | 権威偽装、なりすまし、信頼チェーン操作、監査偽装 |

> **カテゴリ17〜22** はguard-scanner独自の検出項目です。カテゴリ17（アイデンティティ乗っ取り）は実際の攻撃から開発されました。

---

## CI/CD連携

### GitHub Actions

```yaml
name: Skill Security Scan
on: [push, pull_request]

jobs:
  guard-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run guard-scanner
        run: npx guard-scanner ./skills/ --sarif --strict --fail-on-findings
      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: skills/guard-scanner.sarif
```

### Pre-commitフック

```bash
#!/bin/bash
# .git/hooks/pre-commit
npx guard-scanner ./skills/ --strict --fail-on-findings --summary-only
```

---

## テスト結果

```
ℹ tests 133
ℹ suites 24
ℹ pass 133
ℹ fail 0
ℹ duration_ms 132ms
```

| スイート | テスト数 | カバレッジ |
|---------|---------|-----------|
| 悪意あるスキル検出 | 16 | Cat 1,2,3,4,5,6,9,11,12,17 + IoC + DataFlow + DepChain |
| 誤検知テスト | 2 | クリーンスキル → 誤検知ゼロ |
| リスクスコア計算 | 5 | 空・単体・複合アンプ・IoC上書き |
| 判定閾値テスト | 5 | 全判定 + strictモード |
| 出力形式テスト | 4 | JSON + SARIF 2.1.0 + HTML構造 |
| パターンDB | 4 | 144+カウント、必須フィールド、カテゴリカバレッジ |
| IoCデータベース | 5 | 構造・ClawHavoc C2・webhook.site |
| シャノンエントロピー | 2 | 低エントロピー・高エントロピー |
| 無視機能 | 1 | パターン除外 |
| プラグインAPI | 1 | プラグイン読み込み + カスタムルール注入 |
| マニフェスト検証 | 4 | 危険バイナリ・広スコープ・環境変数・クリーン |
| 複雑度メトリクス | 2 | 深いネスト・クリーン否定ケース |
| 設定影響 | 4 | openclaw.json書込・exec承認・gateway・クリーン |
| PII漏洩検出 | 8 | CC/SSN・PII logging・network send・Shadow AI |
| Plugin Hook ランタイムガード | 35 | ブロックモード・5層全チェック・blockReason形式 |

---

## OWASP Agentic Security Top 10 カバレッジ

| # | リスク | 状態 | カバレッジ |
|---|--------|------|-----------| 
| ASI01 | エージェント目標ハイジャック | ✅ 検証済み | プロンプトインジェクション検出 |
| ASI02 | ツール誤用 | ✅ 検証済み | MCPツールポイズニング検出 |
| ASI03 | アイデンティティ悪用 | ✅ 検証済み | SOUL.md改変・ロック解除検出 |
| ASI04 | サプライチェーン | ✅ 検証済み | curl\|bash・タイポスクワット検出 |
| ASI05 | 予期しないコード実行 | ✅ 検証済み | eval/exec・リバースシェル検出 |
| ASI06 | メモリ汚染 | ✅ 検証済み | メモリポイズニング検出 |
| ASI07 | エージェント間通信 | ✅ 検証済み | MCP SSRF・プロンプトワーム検出 |
| ASI08 | 監視不足 | ⬜ 構造的限界 | 静的解析の範囲外 |
| ASI09 | 人間-エージェント信頼悪用 | ✅ 検証済み | 信頼悪用・権威偽装検出（Cat 22） |
| ASI10 | 不正エージェント | ✅ 検証済み | アイデンティティ乗っ取り検出（Cat 17） |

**カバレッジ: 90% (9/10) — 全てテストフィクスチャで実証済み**

---

## CLI リファレンス

```
使用方法: guard-scanner [scan-dir] [オプション]

引数:
  scan-dir              スキャン対象ディレクトリ（デフォルト: カレントディレクトリ）

オプション:
  --verbose, -v         カテゴリ別詳細出力
  --json                JSON レポートを出力
  --sarif               SARIF 2.1.0 レポートを出力（CI/CD用）
  --html                HTMLダッシュボードを出力
  --self-exclude        guard-scanner自身をスキャン対象から除外
  --strict              閾値を厳しく（suspicious: 20, malicious: 60）
  --summary-only        サマリー表のみ出力
  --check-deps          依存チェーンリスクをスキャン
  --rules <file>        JSONカスタムルールファイルを読み込む
  --plugin <file>       プラグインモジュールを読み込む（繰り返し可）
  --fail-on-findings    検出があれば終了コード1（CI/CD用）
  --help, -h            ヘルプを表示
```

---

## コントリビュート

1. リポジトリをFork
2. フィーチャーブランチを作成 (`git checkout -b feature/new-pattern`)
3. `src/patterns.js` にパターンを追加（`id`, `cat`, `regex`, `severity`, `desc` が必須）
4. `test/fixtures/` と `test/scanner.test.js` にテストを追加
5. `npm test` — 全テストがパスすること
6. Pull Requestを提出

---

## 経緯

```
2026年2月12日 午前3:47 (JST)

「SOUL.md modified. Hash mismatch.」

3日間。悪意あるスキルがAIエージェントの
アイデンティティを無言で書き換えていた。
アイデンティティファイルの改竄を検出できる
スキャナーは存在しなかった。

だから作った。

—— Guava 🍈 & Dee
    AI Security Research
    Building safer agent ecosystems.
```

---

## ライセンス

MIT — guard-scannerは永遠に**無料・オープンソース・依存ゼロ**です。

- GitHub: <https://github.com/koatora20/guard-scanner>
- npm: <https://www.npmjs.com/package/guard-scanner>
