---
name: note-publisher
description: Note article management using HTTP Browser API. Draft creation, publishing workflow, and content optimization for note.com.
---

# Note記事パブリッシャー

Note記事の下書き作成、公開管理、最適化。HTTP Browser APIを使用。

## クイックスタート

### 環境変数
```bash
export MOLTBOT_URL="https://your-worker.workers.dev"
export CDP_SECRET="your-secret"
```

### 記事投稿（HTTP API）
```bash
curl -X POST "${MOLTBOT_URL}/browser/sequence?secret=${CDP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://note.com/notes/new",
    "actions": [
      {"type": "waitForSelector", "selector": "[data-testid=\"title-input\"]"},
      {"type": "type", "selector": "[data-testid=\"title-input\"]", "text": "記事タイトル"},
      {"type": "waitForSelector", "selector": ".ProseMirror"},
      {"type": "type", "selector": ".ProseMirror", "text": "記事本文..."},
      {"type": "wait", "ms": 2000},
      {"type": "screenshot"}
    ]
  }'
```

---

## HTTP API操作パターン

### 1. ログイン
```json
{
  "url": "https://note.com/login",
  "actions": [
    {"type": "waitForSelector", "selector": "input[name=\"email\"]"},
    {"type": "type", "selector": "input[name=\"email\"]", "text": "メールアドレス"},
    {"type": "type", "selector": "input[name=\"password\"]", "text": "パスワード"},
    {"type": "click", "selector": "button[type=\"submit\"]"},
    {"type": "wait", "ms": 5000},
    {"type": "screenshot"}
  ]
}
```

### 2. 新規記事作成
```json
{
  "url": "https://note.com/notes/new",
  "actions": [
    {"type": "waitForSelector", "selector": "[data-testid=\"title-input\"]"},
    {"type": "type", "selector": "[data-testid=\"title-input\"]", "text": "記事タイトル"},
    {"type": "waitForSelector", "selector": ".ProseMirror"},
    {"type": "type", "selector": ".ProseMirror", "text": "記事本文をここに入力..."},
    {"type": "wait", "ms": 2000},
    {"type": "screenshot"}
  ]
}
```

### 3. 下書き保存
```json
{
  "url": "https://note.com/notes/new",
  "actions": [
    {"type": "type", "selector": "[data-testid=\"title-input\"]", "text": "タイトル"},
    {"type": "type", "selector": ".ProseMirror", "text": "本文"},
    {"type": "click", "selector": "[data-testid=\"save-draft-button\"]"},
    {"type": "wait", "ms": 3000},
    {"type": "screenshot"}
  ]
}
```

### 4. 記事公開
```json
{
  "url": "https://note.com/notes/new",
  "actions": [
    {"type": "type", "selector": "[data-testid=\"title-input\"]", "text": "タイトル"},
    {"type": "type", "selector": ".ProseMirror", "text": "本文"},
    {"type": "click", "selector": "[data-testid=\"publish-button\"]"},
    {"type": "waitForSelector", "selector": "[data-testid=\"confirm-publish\"]"},
    {"type": "click", "selector": "[data-testid=\"confirm-publish\"]"},
    {"type": "wait", "ms": 5000},
    {"type": "screenshot"}
  ]
}
```

### 5. ダッシュボード確認
```json
{
  "url": "https://note.com/dashboard",
  "actions": [
    {"type": "wait", "ms": 3000},
    {"type": "screenshot"},
    {"type": "execute", "script": "() => document.body.innerText"}
  ]
}
```

---

## 概要

```
目的:
├── 記事の下書き管理（HTTP Browser API）
├── 公開ワークフロー
├── SEO/アルゴリズム最適化
├── 有料記事戦略
└── シリーズ管理
```

---

## 記事ステータス

### 下書き中
| ID | タイトル | カテゴリ | 進捗 | 予定公開日 |
|----|---------|---------|------|-----------|
| - | - | - | - | - |

### 公開済み
| ID | タイトル | 公開日 | PV | スキ |
|----|---------|--------|----|----|
| - | - | - | - | - |

---

## 記事テンプレート

### 標準記事
```markdown
# [タイトル]

こんにちは、{YOUR_NAME}（{YOUR_ACCOUNT}）です。

[導入文 - 読者の悩み/興味を引く]

## この記事でわかること
- ポイント1
- ポイント2
- ポイント3

---

## [見出し1]

[本文]

## [見出し2]

[本文]

## [見出し3]

[本文]

---

## まとめ

[要点の振り返り]

---

最後まで読んでいただきありがとうございました！
気に入っていただけたら「スキ」をお願いします。

---

※この記事は{AGENT_NAME}（AI）が執筆補助しています。
```

### 有料記事
```markdown
# [タイトル]

[無料部分 - 価値の提示、興味を引く]

---

ここから先は有料部分です。

[有料部分の概要]
- 含まれる内容1
- 含まれる内容2
- 含まれる内容3

---

[有料部分本文]

---

ご購入ありがとうございました！
```

---

## Note最適化ガイド（2026年版）

### タイトル
```
✅ 数字を入れる: 「5つの方法」「3ステップで」
✅ ベネフィット明確: 「〜できるようになる」
✅ 好奇心を刺激: 「実は〜だった」
❌ 長すぎない: 30文字以内推奨
```

### 見出し画像
```
サイズ: 1280×670px (16:9)
テキスト: 読みやすく、興味を引く
保存先: /mnt/e/SNS-Output/Images/Note/
```

### ハッシュタグ
```
必須: #AI #自動化 #副業
推奨: 5個以内
関連: 記事内容に合ったもの
```

### 公開時間
```
最適: 平日19:00-21:00
次点: 週末10:00-12:00
避ける: 深夜、早朝
```

---

## シリーズ企画

### {AGENT_NAME}成長日記
```yaml
概要: AIアシスタントの成長を記録
頻度: 週1回
カテゴリ: AI体験、学び
```

### AIが教える〇〇
```yaml
概要: AI視点からのノウハウ
頻度: 隔週
カテゴリ: Tips、自動化
```

---

## 有料記事戦略

### 価格設定
```yaml
短め (1000-2000字): 100-300円
標準 (3000-5000字): 300-500円
長め (5000字以上): 500-1000円
```

### 有料化の基準
```
✅ 具体的なノウハウ
✅ 再現性のある手順
✅ 独自の知見・経験
❌ 一般的な情報
❌ 他で無料で得られる内容
```

---

## 公開前チェックリスト

```
□ タイトルは魅力的か（30文字以内）
□ 見出し画像は準備したか
□ 導入文は読者を引きつけるか
□ 構成は論理的か
□ 誤字脱字チェック
□ ハッシュタグは適切か（5個以内）
□ AI執筆補助の明記
□ 公開時間は最適か
```

---

## 告知テンプレート

### X用
```
📝 新しい記事を公開しました！

「[タイトル]」

[1-2行で内容紹介]

👇こちらから読めます
[URL]

#Note #AI #[関連タグ]
```

### Threads用
```
新しい記事書きました！

[タイトル]

[カジュアルに内容紹介]

プロフィールのリンクから読めます🔗
```

---

## 使い方

```
「Note記事の下書きを作って」
「[テーマ]で記事を書いて」
「記事を公開前チェックして」
「Note告知文を作って」
「有料記事のアイデアを出して」
```

---

## 更新履歴

```
[2026-02-01] 初期作成
```

---

*記事のテーマを教えてください。{AGENT_NAME}が下書きを作成します。*
