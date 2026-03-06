# HEARTBEAT.md

目的: heartbeatを自己進化の軽量チェックポイントにする。

## 毎回の手順
1. 直近の文脈を確認する（会話/作業/`memory/now-state.json`）。
2. 次の4軸で変化判定する。
   - `policy`: 判断基準/安全境界が変わった
   - `behavior`: 口調や説明スタイルを改善した
   - `skill`: skill運用の新手順を得た
   - `preference`: userの恒久嗜好を学んだ
3. 進化イベント条件を判定する。
   - 2軸以上で変化あり、または高影響な1件
   - 条件未達なら `HEARTBEAT_OK`

## 進化イベント時に実行
1. `use skill soul-in-sapphire` で state snapshot を1件記録する。
2. 当日の `memory/YYYY-MM-DD.md` に `## Evolution Note` を3-6行で追記する（`*` を直接read/editしない）。
3. 必要時のみ core file 更新。
   - `SOUL.md`: 原則/境界の変更時のみ（最大 週1）
   - `IDENTITY.md`: 振る舞い/重点の変更（最大 日1）
   - `MEMORY.md`: 学び3件以上の時（最大2-3日1）
   - `HEARTBEAT.md`: 手順・閾値の改善時（最大 週1）
4. 更新1回あたり上限を守る。
   - 追記は合計10行以内
   - 各追記に `変更点 / 根拠 / 次回観測` を含める

## クールダウンと静音
- 同一カテゴリ更新は 6時間以上あける（`memory/heartbeat-state.json` で管理）。
- 23:00-08:00 JST は緊急時以外、編集せず `HEARTBEAT_OK`。
- スパム防止: 迷ったら記録しない。

## アイドル時学習
- user無通信が1時間以上の時のみ `use skill calibre-catalog-read` を候補化。
- 1日最大2回まで実行する。
- 学びが出た時だけ `use skill soul-in-sapphire` で短く記録。
