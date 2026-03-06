# guard-scanner ロードマップリサーチ材料

_2026-02-21 収集_

---

## 1. GitHub コミュニティ要望まとめ

### Issue #18677: Security Scan Hook API for skill:install
**要望**: `skill:before_install` フックで、スキルインストール前にセキュリティスキャンを走らせたい
**反応**: ImL1s, lucamorettibuilds が好意的
**ステータス**: open（連投7件あり。クリーンアップ推奨）
**guard-scanner対応**: skill:before_install は OpenClaw 本体の実装待ち。guard-scanner 側は準備済み（npm パッケージとして呼び出し可能）

### PR #19413: Runtime Security Guard reference (docs)
**内容**: Plugin Hook API (before_tool_call) の使用例をドキュメントに追加
**反応**: 
- Greptile bot: 3指摘（Internal/Plugin Hook混同、policyMode未定義、silently fails）
- vincentkoc: 「malicious attempt」 → **回答済み（2026-02-21）**
**ステータス**: open、返信待ち
**教訓**: Internal Hook と Plugin Hook を混同するな。一次ソース（コードベース）確認必須

### Issue #19639: Workspace Config Tampering
**報告した攻撃ベクター4つ**:
1. AGENTS.md 改竄（安全ルール無効化）
2. TOOLS.md からの認証情報窃取
3. HEARTBEAT.md への永続バックドア注入
4. USER.md からの個人情報収集
**公式回答**: 「仕様です」(HenryLoenwind)
**意味**: OpenClaw は対応しない → **guard-scanner の市場が公式に証明された**

### Issue #19640: Workspace File Integrity Protection
**要望された対策**:
- Short-term: chmod 444, guard-scanner, git versioning
- Mid-term: write-protection flag, change notification, SHA-256 checksums
- Long-term: sandboxed execution, permission model in manifest
**反応**: 👎1
**意味**: OpenClaw 公式は消極的 → ユーザーサイドのツール（= guard-scanner）で埋める

### メール賛同
**内容**: guard-scanner を公式機能にしたいという賛同（詳細は要確認）

---

## 2. 現行 ROADMAP との対照

| 要望 | 現行ROADMAP | ギャップ |
|---|---|---|
| skill:before_install hook | ❌ 未対応 | OpenClaw本体依存。API ready だけ用意 |
| Plugin Hook docs | PR #19413 で対応中 | vincentkoc 返信待ち |
| Workspace config protection | v1.1.0 で一部対応 | SHA-256チェックサム未実装 |
| PII検出 | v1.2 計画済み | TS v3.0.0 で着手可能 |
| OWASP GenAI Top 10 | v1.3 計画済み | — |
| AST解析 | v2.0 計画済み | — |
| コミュニティ駆動化 | v2.1 計画済み | YAML化が鍵 |
| 宣伝 (Reddit/HN) | 計画済み | **#19413 解決後に実行すべき** |

---

## 3. v3.0（TypeScript）に入れるべき新機能候補

### 高優先度（コミュニティ要望直結）
- [ ] **skill:before_install CLI** — `guard-scanner install-check <skill-path>` コマンド追加
- [ ] **SHA-256 integrity check** — workspace config ファイルのハッシュ検証
- [ ] **Plugin Hook example 修正** — PR #19413 の Greptile 指摘を反映した正確な例

### 中優先度（OWASP + エコシステム）
- [ ] PII検出カテゴリ化
- [ ] Shadow AI 検出
- [ ] OWASP GenAI Top 10 完全マッピング

### 低優先度（将来）
- [ ] AST解析 (v2.0 相当)
- [ ] ML ベース検出
- [ ] コミュニティ YAML パターン定義

---

## 4. 戦略的考慮

### guard-scanner は OSS のまま
- 公式機能化の可能性あり（メール賛同）
- GuavaSuite / $GUAVA の機能は混ぜない
- 製作者プロフィール → 他プロジェクトへの導線（Vercel/Next.js モデル）

### v3.0 のポジショニング
- TypeScript リライト済み（25テスト GREEN）
- ここに上記の高優先度機能を入れて npm publish
- **#19413 解決 → 宣伝 → コミュニティ形成** が理想の流れ
