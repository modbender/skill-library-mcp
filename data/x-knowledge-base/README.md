# X Knowledge Base Skill

自動將 X (Twitter) 書籤轉化為 Obsidian 知識庫，配備 AI 濃縮與交叉連結功能。

## 安裝

```bash
# 複製到 OpenClaw skills 目錄
cp -r x-knowledge-base/ ~/.openclaw/skills/

# 或使用 ClawHub
openclaw skill install x-knowledge-base
```

## 設定

1. **Jina AI**（文章擷取）
   - 免費使用
   - URL: https://r.jina.ai/http://...

2. **MiniMax API**（AI 濃縮，可選）
   - 需要 API key
   - endpoint: https://api.minimax.io/anthropic/v1/messages

3. **Brave Search API**（趨勢分析，可選）
   - 需要 API key

4. **環境變數（安全）**

```bash
export BIRD_AUTH_TOKEN="..."
export BIRD_CT0="..."
export MINIMAX_API_KEY="..."        # 可不填；不填即跳過 AI 濃縮
export MINIMAX_ENDPOINT="https://api.minimax.io/anthropic/v1/messages"
export MINIMAX_MODEL="MiniMax-M2.5"
```

## 使用

```
"檢查我的書籤" - 抓取並儲存新書籤
"今天的趨勢是什麼" - 興趣趨勢報告
```

## 工具

```bash
# 執行 AI 濃縮 + 交叉連結
python3 tools/bookmark_enhancer.py 10
```

## 輸出

- 書籤儲存於: ~/clawd/memory/bookmarks/
- Obsidian vault: ~/clawd/obsidian-vault/
