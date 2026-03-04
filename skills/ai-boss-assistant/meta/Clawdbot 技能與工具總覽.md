# Clawdbot Skills ＋ 工具盤點
> 整理你現在這個環境的 **Skills（高階能力包）** 和 **工具（底層 function / CLI）**：有哪些、在做什麼、怎麼用。

---

## 1. Skills（高階能力包）

這些是 Clawdbot 的「技能模組」，通常背後會呼叫一組 CLI 或 API。你喊到對應場景時，我會優先看能不能用這些技能來處理。

### 1.1 工作與自動化相關

#### `coding-agent`
- **功能**：呼叫外部 Coding Agent（Codex CLI / Claude Code / OpenCode / Pi Coding Agent），幫忙做程式開發、重構、除錯。
- **用處**：
  - 大型重構、跨多檔案專案
  - 需要長時間跑測試、工具鏈的任務
- **怎麼用**：
  - 你說：「幫我重構整個 edumind-api 專案」，我會用 coding-agent 開一個背景 session，讓它專心跑，最後再回報結果。

#### `cron`（Gateway 內建，不是 skill 檔，但很重要）
- **功能**：排程任務（每日 9 點行程提醒就是用這個）。
- **用處**：
  - 每日行程提醒
  - 每週摘要
- **怎麼用**：
  - 透過 Gateway 後台 New Job UI 建 job，或之後用 `clawdbot cron add` 指令。

---

### 1.2 Google / 文件相關

#### `gog`
- **功能**：Google Workspace CLI（Gmail / Calendar / Drive / Contacts / Docs / Sheets）。
- **用處**：
  - 幫你排行程、查行程、寄信
  - 找 Drive 檔案、開 Docs、讀 Sheets
- **怎麼用（例）：**
  - 建行程：
    ```bash
    gog calendar create primary \
      --summary "Meeting" \
      --from "2026-02-01T21:00:00+08:00" \
      --to   "2026-02-01T22:00:00+08:00" \
      --account aiagentg888@gmail.com
    ```
  - 寄信：
    ```bash
    gog gmail send \
      --account jackychen0615@gmail.com \
      --to someone@example.com \
      --subject "Test" \
      --body "Hello"
    ```

#### `ai-pdf-builder`
- **功能**：從 Markdown 產專業 PDF（whitepaper、memo、termsheet 等），可用 AI 強化內容。
- **用處**：
  - 有完整 LaTeX 環境時，可一鍵從 md 生 PDF 報告、白皮書。
- **怎麼用（例）：**
  ```bash
  npx ai-pdf-builder generate report ./doc.md -o output.pdf
  ```
  > 現在這台機器 LaTeX/xelatex 路徑還沒完全搞定，所以我會優先建 md，PDF 用你自己的編輯器匯出，比較穩。

#### `notion`
- **功能**：操作 Notion API（建立 / 更新頁面、資料庫）。
- **用處**：
  - 之後可把老闆的會議紀錄、週報寫進 Notion 空間。

---

### 1.3 通訊與平台相關

#### `slack`
- **功能**：控制 Slack（反應、pin、發訊息等）。
- **用處**：
  - 幫老闆在 Slack 發公告、加 reaction、整理頻道。

#### `bluebubbles`
- **功能**：Clawdbot 外掛，用 BlueBubbles 收發 iMessage。
- **用處**：
  - 之後可以讓 AI 協助處理 iMessage 對話。

#### `imsg`
- **功能**：本地 iMessage 控制（傳訊、查歷史）。

#### `discord`
- **功能**：Discord 相關操作。

#### `voice-call`
- **功能**：語音通話相關（視實際配置）。

---

### 1.4 檔案 / 媒體 / 裝置相關

#### `camsnap`
- **功能**：從 RTSP/ONVIF 攝影機擷取畫面或影片片段。
- **用處**：
  - 監控畫面截圖、記錄。

#### `video-frames`
- **功能**：從影片擷取 frame。

#### `nano-pdf`
- **功能**：簡易 PDF 操作（視安裝內容）。

#### `sag` / `sherpa-onnx-tts`
- **功能**：文字轉語音（TTS）。
- **用處**：
  - 之後可以讓老闆用「聽」的方式收摘要。

---

### 1.5 其他整合類 Skills

#### `blucli`
- **功能**：控制 BluOS 播放設備（喇叭、音樂）。

#### `clawdhub`
- **功能**：從 Clawdhub 搜尋／安裝／更新 skills。
- **用處**：
  - 未來要找新的「訂位」「CRM」技能時，從這裡拉。

#### `mcporter`
- **功能**：直接呼叫 MCP servers/tools（HTTP or stdio）。

#### `oracle`
- **功能**：用另一個模型做 code review / 設計檢查。

#### `agent-browser`
- **功能**：headless browser 自動化（開網站、點按鈕）。
- **用處**：
  - 未來可以用來做「自動訂位」、「登入後台查數據」。

#### `solar-weather`
- **功能**：查太陽風 / 極光 / 太空天氣。

（還有一些像 weather、songsee、spotify-player 等，分別對應天氣、音樂控制，這裡不逐一展開。）

---

## 2. 底層工具（functions / CLI）

這些是我在這個環境裡可以直接呼叫的「低階工具」，用來讀檔、跑指令、傳訊息等。

### 2.1 檔案與程式執行

#### `read`
- **功能**：讀取本機檔案內容。
- **用處**：
  - 看程式碼、md 文件、設定檔。
- **怎麼用（例）：**
  - 我在背後會下：`read { path: "./some/file.md" }` 然後把內容用來分析或整理。

#### `write`
- **功能**：在本機建立或覆寫檔案。
- **用處**：
  - 幫你新建 md / code 檔、白皮書、教學文件。

#### `edit`
- **功能**：在檔案中做「精準字串取代」。
- **用處**：
  - 修改特定片段而不動其他內容（像剛剛修 `drive_download.py` 裡的 OAuth 邏輯）。

#### `exec`
- **功能**：在本機 Shell 執行指令。
- **用處**：
  - 跑 `gog ...`、`pandoc ...`、`python ...` 等
  - 用 `open` 打開檔案 / 網頁

#### `process`
- **功能**：管理長時間執行的 `exec` session（查看 log、kill 等）。
- **用處**：
  - 像剛剛 `gog auth add` 需要等 OAuth 回來，我會用 `process.log` 看進度。

---

### 2.2 Web / 搜尋

#### `web_search`
- **功能**：用 Brave Search 查網路。
- **用處**：
  - 幫你查資料、找教學、比較服務。

#### `web_fetch`
- **功能**：抓某個 URL 的內容（轉成 markdown/text）。
- **用處**：
  - 把一篇文章拉進來做摘要、整理。

---

### 2.3 訊息與排程

#### `message`
- **功能**：透過 Clawdbot 後端發訊息／檔案到各通訊平台（Telegram、Slack 等）。
- **用處**：
  - 剛剛就是用這個，把 md 檔直接傳到你 Telegram 對話。
- **怎麼用（例）：**
  ```jsonc
  {
    "action": "send",
    "channel": "telegram",
    "target": "8365775688",
    "filePath": "/Users/user/clawd/boss-ai-assistant-whitepaper.md",
    "caption": "AI 老闆助理白皮書 v0.1（Markdown）"
  }
  ```

#### `cron`
- **功能**：管理 Gateway 端排程（status/list/add/update/remove）。
- **用處**：
  - 每日 9 點行程提醒 job

---

### 2.4 記憶與多 session

#### `memory_search` / `memory_get`
- **功能**：在 `MEMORY.md` 與 `memory/*.md` 中搜尋與讀取片段。
- **用處**：
  - 記住你給我的長期規則（像「先翻 skills＋工具」那句）、過去重要決策。

#### `sessions_*` / `agents_list`
- **功能**：管理多個 agent session（spawn 子任務、跨 session 傳訊息等）。
- **用處**：
  - 之後可以開「背景 agent」去做長任務，做完再回報你。

---

### 2.5 其他

#### `tts`
- **功能**：文字轉語音（回一個音訊檔路徑）。
- **用處**：
  - 之後可以幫你產生語音版摘要、故事等。

#### `gateway`
- **功能**：查看／更新 Clawdbot Gateway 設定、重啟等。
- **用處**：
  - 調整 config、看狀態（會盡量少動，避免影響穩定運作）。

---

## 3. 之後遇事時，我會怎麼用這些？

照你剛剛定的規則，我之後的流程是：

1. 你丟任務。
2. 我先看 **skills＋工具** 能不能直接處理：
   - 有對應 skill（例如 gog、notion、agent-browser），就先試它。
   - 需要 CLI，就用 `exec` / `process` 實際跑，確認結果。
3. 成功 → 直接在這裡給你結果／檔案（必要時用 `message` 傳附件）。
4. skills 裡真的沒有 → 明講「目前沒有對應技能」，並建議：
   - 要裝哪類 skill（比如 CRM、訂位、會計）
   - 或我們是否要自己寫一個新的小工具（像 `drive_download.py` 那種）。

這份 md 之後如果你要，我也可以持續更新，當成「這台 Clawdbot 的功能說明書」。

---

## 4. 用戶要說什麼，我才會去啟動這些技能？

你不用記指令，只要「用自然語言」說出你要我做的事＋關鍵資訊，我會自己判斷要用哪個 skill／工具。下面是幾個關鍵類型：

### 4.1 跟 Google 有關（gog）

- **行事曆（Calendar）**
  - 你說：
    - 「幫我明天早上 10 點到 11 點，用 `aiagentg888` 安排跟 A 客戶線上會議。」
    - 「今天行程幫我列出來。」
  - 我會做：
    - 用 `gog calendar create ... --account 那個帳號` 建行程
    - 或 `gog calendar events ...` 查今天的行程

- **Gmail 寄信**
  - 你說：
    - 「用 `jackychen0615` 幫我寄一封測試信給 XXX，主旨是 …，內容是 …。」
    - 「幫我寫一封跟進信給昨天那個客戶，語氣客氣一點。」
  - 我會做：
    - 先幫你寫草稿內容
    - 再用 `gog gmail send --account ...` 實際寄出

- **Drive / Docs / Sheets**
  - 你說：
    - 「用 `aiagentg888` 幫我看最近 5 個檔案。」
    - 「幫我打開那份 Gamania 派遣需求文件。」
  - 我會做：
    - `gog drive search "*" --max 5 --account ...` 列清單
    - 幫你選或你指定後，用 `open webViewLink` 在瀏覽器打開

### 4.2 PDF / 文件

- 你說：
  - 「幫我整理一份 X 教學成 md，再給我路徑。」
  - 「幫我寫一份 AI 老闆助理白皮書草稿。」
- 我會做：
  - 用 `write` 建 md 檔
  - 優先讓你用編輯器匯出 PDF（現在這台 LaTeX 還不穩）
  - 需要的話用 `message` 把 md 傳進聊天給你

### 4.3 行程／任務自動化

- 你說：
  - 「以後每天早上 9 點，幫我簡短報告今天行程。」
  - 「幫我設一個每週五傍晚的工作週報提醒。」
- 我會做：
  - 先設計 cron job 內容（System text）
  - 再指導你在 Gateway / cron 裡建 job（或未來直接幫你呼叫 cron API）

### 4.4 查資料／網路

- 你說：
  - 「幫我查一下 Zeabur 長期費用大概多少，跟 VM 比。」
  - 「幫我看一下某個服務的文件重點。」
- 我會做：
  - 用 `web_search` 找資料
  - 必要時用 `web_fetch` 拉全文做摘要

### 4.5 其他平台／整合（Slack、Notion、瀏覽器等）

- 你說：
  - 「幫我把這段會議紀錄整理後貼到 Notion 某頁。」
  - 「幫我在 Slack 某個頻道發一則公告。」
  - 「幫我登入某網站、下載報表。」（未來用 agent-browser）
- 我會做：
  - 看有沒有對應 skill（例如 notion、slack、agent-browser）
  - 有 → 實際呼叫 skill 做動作
  - 沒有 → 回報目前缺哪種技能，建議你要不要裝／開發

---

總結：你只要負責「用人話說清楚你想要什麼＋用哪個帳號」，我會先去翻 skills＋工具，能自己做到的就直接做，做不到的才跟你說缺什麼。
