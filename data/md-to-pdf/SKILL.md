---
name: md-to-pdf
description: MarkdownからPDFを生成する。md-to-pdf（Puppeteer）を使用。GitHub風スタイル、日本語・カラー絵文字対応。
metadata:
  openclaw:
    emoji: "📄"
    requires:
      bins: ["md-to-pdf"]
---

# pdf-creator

Markdownを書いて、md-to-pdf でPDFに変換するスキル。内部でPuppeteer（ヘッドレスChromium）を使うため、ブラウザで見たままの高品質なPDFが生成される。

## 使い方

### 手順

1. Markdownファイルを `/tmp/` に書き出す（YAML front-matterでスタイル指定）
2. `md-to-pdf` コマンドで変換
3. 生成されたPDFを送信

### 基本テンプレート

```bash
cat > /tmp/output.md << 'MDEOF'
---
css: |-
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 12px; padding: 2em; line-height: 1.6; color: #24292f; }
  h1 { text-align: center; border-bottom: 2px solid #333; padding-bottom: 0.5em; }
  h2 { color: #2c3e50; margin-top: 1.5em; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #d0d7de; padding: 6px 13px; text-align: left; }
  th { background: #f6f8fa; font-weight: 600; }
  code { background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }
  blockquote { color: #57606a; border-left: 4px solid #d0d7de; padding: 0 1em; margin: 0; }
  .page-break { page-break-after: always; }
pdf_options:
  format: A4
  margin: 20mm
  printBackground: true
---

# タイトル

本文をここに書く。**太字**、*斜体*、`コード`も使える。

## 表

| 項目 | 値 |
|------|------|
| 名前 | シロ |
| モデル | Gemini 3 Flash |

## リスト

- ✅ 完了した項目
- 🔧 作業中の項目
- ⚠ 注意事項

MDEOF

timeout 30 md-to-pdf /tmp/output.md
```

変換完了後、`/tmp/output.pdf` が生成される。30秒でタイムアウトする（Chromiumハング防止）。

### ポイント

- **日本語**: そのまま使える（Chromiumがシステムフォントを使用）
- **絵文字**: カラー絵文字がそのまま表示される（ブラウザネイティブ）
- **スタイル**: GitHub Markdown CSSで美しいレイアウト
- **表（テーブル）**: Markdown記法がそのまま綺麗な表になる
- **太字・斜体**: Markdownの`**太字**`や`*斜体*`がそのまま反映
- **コードブロック**: シンタックスハイライト付き
- **改ページ**: `<div class="page-break"></div>` を挿入
- **出力先**: `/tmp/` に出力してからDiscordに送信すること

### 改ページの使い方

ページを分けたい箇所に以下を挿入:

```markdown
<div class="page-break"></div>
```

### ヘッダー・フッター付き

```yaml
pdf_options:
  format: A4
  margin: 30mm 20mm
  printBackground: true
  displayHeaderFooter: true
  headerTemplate: |-
    <style>section { margin: 0 auto; font-family: system-ui; font-size: 9px; }</style>
    <section><span class="title"></span></section>
  footerTemplate: |-
    <section>
      <div>Page <span class="pageNumber"></span> / <span class="totalPages"></span></div>
    </section>
```

### 注意事項

- 必ず `timeout 30 md-to-pdf` で実行すること（Chromiumハング防止。タイムアウトしたら再試行）
- CSSに `@import url(...)` で外部CDNを使わないこと（ネットワーク遅延でハングの原因になる）
- 必ず `/tmp/` に出力してからファイルを送信すること
- 長い処理はDiscord WebSocketタイムアウト（41秒）に注意
- `--launch-options '{"args":["--no-sandbox"]}'` はセキュリティ上、使わないこと
