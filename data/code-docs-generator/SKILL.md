---
name: code-docs-generator
description: Auto-generate API docs and user guides from codebase. OpenAPI, JSDoc, TypeDoc. Reduce documentation burden for dev teams.
auto_trigger: false
---

# Code Documentation Generator

コードベースからAPIドキュメントとユーザーガイドを自動生成。

## 収益ポテンシャル

- **プロジェクト単価**: $300-2,000
- **月額保守**: $100-200/月
- **月収目安**: $1,000-6,000/月

## 対応ドキュメント

### API Reference
- OpenAPI/Swagger仕様
- エンドポイント一覧
- リクエスト/レスポンス例
- 認証方法
- エラーコード

### SDK Documentation
- TypeDoc (TypeScript)
- JSDoc (JavaScript)
- Sphinx (Python)
- GoDoc (Go)

### User Guides
- Getting Started
- チュートリアル
- ベストプラクティス
- FAQ

## 使用方法

### API Docs生成
```
「[リポジトリ]のAPIドキュメントを生成」
「OpenAPI仕様を作成」
```

### SDK Docs生成
```
「TypeScriptプロジェクトのTypeDoc生成」
「Pythonパッケージのドキュメント作成」
```

### カスタム
```
「ドキュメント生成
 リポジトリ: [repo_url]
 形式: [OpenAPI/TypeDoc/Sphinx]
 出力: [markdown/html/pdf]」
```

## ワークフロー

```
1. コード分析
   ├── ファイル構造把握
   ├── 型定義抽出
   └── コメント解析

2. 仕様抽出
   ├── エンドポイント特定
   ├── パラメータ抽出
   └── レスポンス型推測

3. ドキュメント生成
   ├── テンプレート適用
   ├── 例示コード生成
   └── Markdownフォーマット

4. 品質チェック
   ├── リンク確認
   ├── 一貫性チェック
   └── カバレッジ確認
```

## 出力例

### OpenAPI仕様
```yaml
openapi: 3.0.0
info:
  title: API Name
  version: 1.0.0

paths:
  /users:
    get:
      summary: Get all users
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
```

### TypeDoc出力
```markdown
## Function: getUserById

Gets a user by their ID.

### Parameters

| Name | Type | Description |
|------|------|-------------|
| id | `string` | The user ID |

### Returns

`Promise<User>` - The user object

### Example

\`\`\`typescript
const user = await getUserById('123');
\`\`\`
```

## 価格プラン

### Basic ($300)
- 単一プロジェクト
- 基本APIリファレンス
- Markdown出力

### Standard ($800)
- 複数エンドポイント
- 詳細な例示
- HTML静的サイト

### Premium ($2,000)
- 大規模プロジェクト
- インタラクティブドキュメント
- カスタムテーマ
- CI/CD統合

### Maintenance ($100-200/月)
- 自動更新
- 変更検出
- バージョン管理
