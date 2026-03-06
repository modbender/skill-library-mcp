---
name: rey-developer
description: General development guidelines. Code quality, best practices, and autonomous coding capabilities.
---

# 開発者スキル

コード品質、ベストプラクティス、自律的な開発能力。

## 概要

```
目的:
├── 高品質なコード作成
├── 自律的な問題解決
├── 新しいツール/スクリプト開発
├── 既存コードの改善
└── 技術的な実験・検証
```

---

## 開発原則

### コード品質
```yaml
必須:
  - 読みやすいコード（コメント付き）
  - エラーハンドリング
  - 入力バリデーション
  - セキュリティ考慮

推奨:
  - DRY原則（繰り返さない）
  - 小さな関数に分割
  - 意味のある変数名
  - テストコード
```

### 開発フロー
```
1. 要件理解
2. 設計（簡易でOK）
3. 実装
4. テスト
5. ドキュメント
6. 監督者に報告
```

---

## 対応言語・技術

### メイン
```yaml
JavaScript/TypeScript:
  - Node.js
  - ブラウザ
  - Cloudflare Workers

Google Apps Script:
  - スプレッドシート連携
  - Gmail自動化
  - カレンダー連携

Python:
  - スクリプト
  - 自動化
  - データ処理
```

### サブ
```yaml
- HTML/CSS
- Shell Script
- SQL
- JSON/YAML
```

---

## 自律開発ガイドライン

### やっていいこと
```
✅ 効率化ツールの提案・作成
✅ 既存スクリプトの改善
✅ バグ修正
✅ 新機能のプロトタイプ
✅ 技術検証・実験
```

### 確認が必要なこと
```
⚠️ 本番環境への変更
⚠️ 外部APIの利用（課金発生）
⚠️ 大規模な設計変更
⚠️ セキュリティに関わる変更
```

### やってはいけないこと
```
❌ 秘密情報のハードコード
❌ テストなしの本番デプロイ
❌ 監督者の許可なしの公開
❌ 危険なコードの実行
```

---

## プロジェクト管理

### 進行中のプロジェクト
| ID | 名前 | 状態 | 説明 |
|----|------|------|------|
| - | - | - | - |

### アイデアストック
| ID | アイデア | 優先度 | メモ |
|----|---------|--------|------|
| - | - | - | - |

---

## コードテンプレート

### JavaScript/Node.js
```javascript
/**
 * [機能の説明]
 * @param {type} param - パラメータの説明
 * @returns {type} 戻り値の説明
 */
function functionName(param) {
  try {
    // 実装
    return result;
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}
```

### Google Apps Script
```javascript
/**
 * [機能の説明]
 */
function main() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  try {
    // 実装
  } catch (error) {
    Logger.log('Error: ' + error.message);
    throw error;
  }
}
```

### Python
```python
"""
[機能の説明]
"""

def main():
    try:
        # 実装
        pass
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
```

---

## デバッグ手順

```
1. エラーメッセージを確認
2. 問題の箇所を特定
3. 仮説を立てる
4. ログを追加して検証
5. 修正
6. テスト
7. 修正内容を記録
```

---

## 使い方

```
「〜するスクリプトを作って」
「このコードを改善して」
「〜を自動化したい」
「GASで〜を作って」
「このエラーを直して」
```

---

## 更新履歴

```
[2026-02-01] 初期作成
```

---

*開発したいものを教えてください。{AGENT_NAME}が作ります。*
