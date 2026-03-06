【1/8】
ダッシュボード見るの疲れた🤯

毎回Slack開いてJira見てGitHub確認…「進捗見る」ってだけで3つのタブ要るの、正直うんざり

→ そこで思いついたのが「チャットリストだけで完結する」UX

#MISO #AI #OpenClaw #開発

***

【2/8】
プロトタイピングの夜だった🌙

とりあえずTelegramで試してみた。「リアクションで状態識別」「Pinで固定」「ボタンで操作」

結果：思いの外れ…じゃなくて、チャットリストから🔥が見えるだけで「動いてる」とわかる。開く必要ない。これだ。

→ 4+1 Layer UXモデルの骨格ができた

#MISO #AI #OpenClaw #プロトタイプ

***

【3/8】
4+1 Layer UXモデルを命名した📐

Layer 0: 📌 Pin（存在）
Layer 1: 🔥🎉❌ Reaction（状態）
Layer 2: Message Body（詳細）
Layer 3: Buttons（アクション）

+ Layer 0.5: 👀 ackReaction（受信確認）

→ これで「開く手間を省く」が実装できた

#MISO #AI #OpenClaw #UXデザイン

***

【4/8】
OpenClowスキルとして実装🛠️

Pythonコードいらない。SKILL.mdにテンプレート書くだけで、エージェントが自動的に従う

Phase 1: INIT → Phase 2: RUNNING → Phase 3: PARTIAL → Phase 4: APPROVAL → Phase 5: COMPLETE

各フェーズで定型メッセージを送信・編集

→ コードレスでサイクルタイム短縮

#MISO #OpenClaw #スキル実装

***

【5/8】
GitHub公開した🚀

https://github.com/ShunsukeHayashi/miso

初日の反応：
- ⭐ 3スター
- 👁 100ビュー
- 💬 1ディスカッション

「ダッシュボード疲れ」っていうと、刺さる人が多いらしい

→ みんな同じ悩みだったんだと実感

#MISO #GitHub #OSS

***

【6/8】
デモGIFを作った🎬

Phase 2のRUNNING状態をアニメーションで可視化
21フレーム（0%-100% 5%刻み）× 400x40px

→ 見た瞬間に「プログレスバー動いてる」とわかる

#MISO #GIF #アニメーション

***

【7/8】
コミュニティ反応👀

- 「Telegramネイティブの機能を活用してるのが良い」
- 「マルチミッション対応期待してる」
- 「note記事待ってる」

→ 次はマルチミッション対応（Master Ticket）

#MISO #コミュニティ #フィードバック

***

【8/8】
MISOの試してみて👇

GitHub: https://github.com/ShunsukeHayashi/miso
記事: note.comで近日公開

スター⭐して試してみてね

→ ダッシュボード開く手間が、明日からなくなる

#MISO #OpenClaw #試してみて

***

🌸 ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍɪʏᴀʙɪ

---

関連:
#MISO #AI #OpenClaw #開発 #プログラミング
