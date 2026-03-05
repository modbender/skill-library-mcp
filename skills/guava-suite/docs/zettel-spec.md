# SPEC.md — Zettel Memory MVP for OpenClaw

## 1. Storage Layout

- `memory/notes/<id>.md` 原子的ノート本体
- `memory/notes/index.md` ノート一覧 + 主要リンク

## 2. Note Frontmatter

```yaml
id: zettel-YYYYMMDD-HHMMSS
title: <short title>
tags: [tag1, tag2]
entities: [entity1, entity2]
source: memory/YYYY-MM-DD.md#Lx-Ly
created_at: ISO8601
updated_at: ISO8601
supersedes: null
links: []
confidence: 0.7
```

## 3. Workflows

### A) New Note
`new_note.py` でタイトル・本文・タグ等を受け取り、ノート作成。

### B) Link
`link_notes.py` で最新ノートと既存ノートのキーワード重なりを計算。
閾値以上で `links` に相互追記。

### C) Index
`link_notes.py` 実行時に `index.md` を再生成（新しい順）。

## 4. Evolution (Supersedes)
更新版ノート作成時は `--supersedes <old_id>` を指定。
旧ノートは残し、新ノートが置換関係を持つ。

## 5. Safety
- 既存メモリは削除しない
- 上書きは対象ノート限定
- JSON/Markdown破損時は処理中断
