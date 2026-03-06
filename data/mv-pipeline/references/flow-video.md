# Flow Video Generation (Browser Automation)

Google AI Ultra 契約で Veo 3.1 Fast が Included（クレジット消費なし）。

## 前提条件
- Google AI Ultra 契約済み
- Chrome で `labs.google/flow` にログイン済み
- OpenClaw Browser Relay（Chrome拡張）が有効

## 操作手順

### 1. ブラウザ接続
```
browser action=start profile=chrome
browser action=open profile=chrome url=https://labs.google/fx/ja/tools/flow
```

### 2. プロジェクト選択/作成
```
browser action=snapshot  → プロジェクトリンク or 新規作成ボタン確認
browser action=act kind=click ref=<project_link>
```

### 3. 動画生成
```
browser action=snapshot  → プロンプト入力欄・作成ボタンのref取得
browser action=act kind=type ref=<prompt_box> text="プロンプト"
browser action=act kind=click ref=<create_button>
```

### 4. 完了確認
```
# 3-5分後
browser action=snapshot  → 進捗確認（100%で完了）
```

### 5. ダウンロード
```
# 動画カードをホバー → ダウンロードメニュー
browser action=act kind=hover ref=<video_card>
browser action=act kind=click ref=<download_button>
browser action=act kind=click ref=<1080p_option>  # "capture 元のサイズ（720p）" or "high_res アップスケール（1080p）"
```

ファイルは `~/Downloads/` に保存。`mv` でプロジェクトに移動。

## UI要素マッピング

| 要素 | 識別 | 用途 |
|------|------|------|
| プロンプト入力 | `textbox "テキストを使用して動画を生成します…"` | 入力 |
| 作成ボタン | `button "arrow_forward 作成"` | 生成開始 |
| 設定 | `button "tune 設定"` | モデル・出力数変更 |

## 設定推奨値
- モデル: Veo 3.1 - Fast
- 縦横比: 横向き (16:9)
- 出力数: 2 (良い方を選ぶ)

## ダウンロード解像度

| オプション | 解像度 | コスト |
|-----------|--------|--------|
| GIF アニメーション | 270p | 無料 |
| 元のサイズ | 720p | 無料 |
| アップスケール | 1080p | Included (Ultra) |
| アップスケール 4K | 4K | 50 credits |

**MV用推奨: 1080p**

## 連続生成
- 生成中でも次のプロンプトを投入可能
- 各動画の進捗が%で表示
- 全完了後にまとめてダウンロード推奨

## コスト
Google AI Ultra $125/月 定額。Veo 3.1 Fast は Included。
Vertex AI 比で MV 1本あたり ¥40,000 → ¥0。
