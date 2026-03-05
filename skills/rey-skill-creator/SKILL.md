---
name: rey-skill-creator
description: Creates new OpenClaw skills following best practices. Interactive workflow for use case definition, frontmatter generation, instruction writing, and validation. Use when user says "create skill", "new skill", "make a skill", or needs to build a skill from scratch.
auto_trigger: false
---

# Skill Creator - OpenClaw Skills Best Practices

OpenClaw用のスキルを作成するためのガイド。公式ベストプラクティスに基づく。

## ワークフロー

### Phase 1: ユースケース定義

ユーザーに2-3個の具体的なユースケースを聞く:

```
このスキルでどんなワークフローを実現したいですか？

例:
ユースケース: [名前]
トリガー: ユーザーが「[具体的なフレーズ]」と言った時
ステップ:
1. [最初のアクション]
2. [次のアクション]
結果: [期待する成果]
```

### Phase 2: Frontmatter生成

**必須フィールド:**
- `name`: kebab-case、最大64文字、フォルダ名と一致
- `description`: WHAT + WHEN + トリガーフレーズ、最大1024文字

**オプションフィールド:**
- `auto_trigger`: true/false（自動起動するか）
- `allowed-tools`: ツールアクセス制限
- `metadata`: author, version等

**description の書き方:**
```
[何をするか]. [主な機能]. Use when user says "[trigger1]", "[trigger2]", "[trigger3]", or [一般的な状況].
```

**良い例:**
```yaml
description: Analyzes design files and generates documentation. Use when user says "design specs", "component docs", or needs design handoff.
```

**悪い例（避ける）:**
```yaml
# 曖昧すぎる
description: Helps with projects.

# トリガーがない
description: Creates sophisticated documentation systems.
```

### Phase 3: 指示を書く

**構造テンプレート:**
```markdown
# [スキル名]

## 目的
[このスキルが何をするか1-2文]

## 手順

### Step 1: [最初のステップ]
何が起こるかの明確な説明。

例:
\`\`\`bash
[コマンド例]
\`\`\`

### Step 2: [次のステップ]
...

## 例

### 例1: [一般的なシナリオ]
ユーザー: "[リクエスト例]"
アクション:
1. [アクション1]
2. [アクション2]
結果: [成果]

## トラブルシューティング

### エラー: [よくあるエラー]
原因: [なぜ起こるか]
解決: [修正方法]
```

### Phase 4: バリデーションチェックリスト

作成前に確認:

**ファイル構造:**
- [ ] フォルダ名がkebab-case
- [ ] SKILL.mdファイルが存在
- [ ] スキルフォルダにREADME.mdがない

**Frontmatter:**
- [ ] `---`デリミタがある
- [ ] `name`: kebab-case、スペースなし、大文字なし
- [ ] `name`: フォルダ名と一致
- [ ] `description`: WHATとWHENを含む
- [ ] `description`: 1024文字以下
- [ ] XMLタグ（< >）がない

**指示:**
- [ ] 明確でアクション可能
- [ ] エラーハンドリングあり
- [ ] 例が含まれている
- [ ] 500行以下

### Phase 5: スキル作成

```bash
# フォルダ作成
mkdir -p skills/[skill-name]

# SKILL.md作成
# （内容を書く）

# 確認
ls skills/[skill-name]/SKILL.md
```

---

## 禁止パターン

| パターン | 禁止理由 |
|---------|----------|
| スペース入りの名前 | 読み込めない |
| 大文字入りの名前 | 読み込めない |
| "claude"/"anthropic"で始まる名前 | 予約済み |
| frontmatterにXMLタグ | セキュリティリスク |
| スキルフォルダにREADME.md | 読み込み混乱 |
| descriptionにトリガーなし | 自動起動しない |
| 本文500行超 | パフォーマンス問題 |

---

## クイックテンプレート

### テンプレート1: ワークフロー自動化
```yaml
---
name: [workflow-name]
description: [Xワークフローを自動化]. Use when user says "[trigger1]", "[trigger2]".
auto_trigger: true
---

# [ワークフロー名]

## 目的
[何を自動化するか]

## 手順
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

### テンプレート2: セキュリティスキャナー
```yaml
---
name: [security-topic]-scanner
description: Detects [脆弱性タイプ]. Use when user says "[trigger1]", "[trigger2]".
auto_trigger: true
---

# [セキュリティトピック] Scanner

## 検出対象
1. [脆弱性1]
2. [脆弱性2]

## スキャン手順
[スキャン方法]

## 修正方法
[修正方法]
```

### テンプレート3: SNS連携
```yaml
---
name: [platform]-poster
description: Posts content to [platform]. Use when user says "[trigger1]", "[trigger2]".
auto_trigger: false
---

# [Platform] Poster

## 前提条件
- [認証情報が設定済み]

## ワークフロー
1. コンテンツ準備
2. 投稿
3. 結果確認
```

---

## 成功基準

スキル作成後にテスト:

1. **トリガー**: 関連クエリで読み込まれるか？
2. **機能**: 正しい出力が得られるか？
3. **過剰トリガーなし**: 無関係なトピックで読み込まれないか？
