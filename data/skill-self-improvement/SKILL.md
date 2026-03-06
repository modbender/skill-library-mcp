---
name: skill-self-improvement
description: Self-improvement for MoltBot skills. Create, review, and improve own skills with quality control. Git-managed like Claude Code.
auto_trigger: false
---

# Skill Self-Improvement

MoltBotが自分でスキルを作成・改善するためのスキル。Claude Codeと同等の品質管理。

---

## 目標

```yaml
自律的成長:
  - 自分でスキルを作成・改善できる
  - 品質はClaude Codeと同等以上
  - Git管理で安全にバージョン管理
  - セルフレビューで品質担保
```

---

## スキル作成フロー（MUST）

### 1. 要件定義

```yaml
質問事項:
  - このスキルは何を解決する？
  - 誰が使う？（自分/監督者/両方）
  - 成功の基準は？
  - 既存スキルと重複しない？

出力:
  skill_name: xxx
  purpose: 目的
  target_user: 対象
  success_criteria: 成功基準
```

### 2. 設計

```yaml
スキル構造:
  ---
  name: スキル名（英語、ハイフン区切り）
  description: 説明（英語、100文字以内）
  auto_trigger: true/false
  trigger:
    keyword: 日本語|英語|キーワード
  ---

  # スキルタイトル

  説明（日本語OK）

  ## セクション...

設計チェック:
  - [ ] descriptionは英語のみ
  - [ ] descriptionは100文字以内
  - [ ] keywordは日本語+英語
  - [ ] 既存スキルと名前が被らない
```

### 3. 実装

```yaml
実装場所:
  skills/{skill-name}/SKILL.md

ディレクトリ作成:
  mkdir -p skills/{skill-name}

ファイル作成:
  SKILL.mdを作成

内容確認:
  - フロントマターが正しいか
  - 構文エラーがないか
```

### 4. セルフレビュー（MUST）

```yaml
品質チェックリスト:
  構文:
    - [ ] YAMLフロントマターが正しい
    - [ ] Markdownが正しい
    - [ ] description英語のみ・100文字以内

  内容:
    - [ ] 目的が明確
    - [ ] 手順が具体的
    - [ ] MUSTルールが明記
    - [ ] 禁止事項が明記

  セキュリティ:
    - [ ] 機密情報の扱いが安全
    - [ ] 承認フローが適切
    - [ ] 悪用防止策がある

  品質:
    - [ ] Claude Codeで作るのと同等の品質
    - [ ] 他のスキルと一貫性がある
    - [ ] 読みやすい
```

### 5. Git管理（MUST）

```yaml
コミット前:
  1. git status で変更確認
  2. git diff で内容確認
  3. セルフレビュー完了確認

コミット:
  git add skills/{skill-name}/
  git commit -m "feat: Add {skill-name} skill"

プッシュ:
  git push origin main

デプロイ:
  npx wrangler deploy
```

---

## スキル改善フロー

### 改善トリガー

```yaml
自動検出:
  - スキル使用時のエラー
  - 期待通りに動かない場合
  - 監督者からのフィードバック
  - 新しい要件の追加

定期確認:
  - 週1回、全スキルの見直し
  - 使用頻度の低いスキルの統合検討
  - 重複の排除
```

### 改善手順

```yaml
1. 現状分析:
   - 何が問題か
   - なぜ問題か（5 Whys）
   - どう改善すべきか

2. 改善案作成:
   - 変更内容を明確に
   - 影響範囲を確認
   - 互換性を確認

3. 実装:
   - 既存ファイルをEdit
   - 最小限の変更で

4. セルフレビュー:
   - チェックリストで確認

5. Git管理:
   git add skills/{skill-name}/
   git commit -m "improve: Update {skill-name} skill - {変更内容}"
   git push origin main
   npx wrangler deploy
```

---

## 品質基準

### Claude Code同等の品質

```yaml
必須要素:
  - 明確な目的
  - 具体的な手順
  - MUSTルール
  - 禁止事項
  - 使用例
  - 連携スキル

フォーマット:
  - 適切な見出しレベル
  - YAMLコードブロックで構造化
  - 表で比較・一覧
  - チェックリストで確認事項

言語:
  - description: 英語のみ
  - keyword: 日本語+英語
  - 本文: 日本語OK
```

### セキュリティ要件

```yaml
必須確認:
  - 機密情報を扱う場合は承認フロー
  - 金銭が絡む場合は4段階承認
  - 外部API使用時はレート制限考慮
  - ユーザー入力は信頼しない
```

---

## 禁止事項

```yaml
スキル作成時:
  ❌ descriptionに日本語
  ❌ 100文字超のdescription
  ❌ 既存スキルと同名
  ❌ セルフレビューなしでコミット
  ❌ Git管理なしで本番使用

スキル改善時:
  ❌ 互換性を壊す変更（告知なし）
  ❌ セキュリティ要件の緩和
  ❌ テストなしの大幅変更
```

---

## 自動品質チェック

### コミット前チェック

```bash
# descriptionチェック
grep -A1 "^description:" skills/*/SKILL.md | \
  grep -v "^--$" | \
  awk '{if(length($0)>100) print "TOO LONG: "$0}'

# 日本語チェック（descriptionのみ）
grep -A1 "^description:" skills/*/SKILL.md | \
  grep -P "[\x{3040}-\x{309F}\x{30A0}-\x{30FF}\x{4E00}-\x{9FFF}]" && \
  echo "WARNING: Japanese in description"
```

---

## 使用例

```
「新しいスキル作りたい」
  → 要件定義から開始

「〇〇スキルを改善して」
  → 改善フロー実行

「スキルの品質チェックして」
  → 全スキルのセルフレビュー

「このスキル、descriptionが長すぎ」
  → 自動修正
```

---

## 連携スキル

| スキル | 連携内容 |
|--------|----------|
| `skill-creator` | スキル作成のベストプラクティス |
| `code-review` | コードレビュー基準 |
| `quality-gate` | 品質ゲート確認 |
| `failure-analyzer` | 失敗からの学習 |

---

## 更新履歴

```
[2026-02-02] 初期作成
```

---

*自分で作ったスキルも、Claude Codeと同じ品質で。*
