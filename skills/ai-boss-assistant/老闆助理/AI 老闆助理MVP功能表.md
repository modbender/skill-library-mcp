# AI 老闆助理 MVP 功能表

> 用來跟老闆或客戶說明：**現在就能交付什麼**，以及**接下來要做什麼**。

---

## 1. 目前可以直接交付的功能（MVP）

### 1.1 行程管理（Scheduling）

- 多帳號行事曆（`gog calendar`）
  - 幫老闆用不同帳號排會議（私人／工作）
  - 建／改／刪事件，支援地點、說明
- 每日行程提醒（Gateway cron）
  - 每天早上固定時間 → 簡短版列出「今天有什麼會 / 行程」
- 特殊行程
  - 會幫老闆確認：
    - 要不要附 Google Meet 連結
    - 要不要同步給對方（之後用 email / calendar 邀請）

### 1.2 溝通與寄信（Communication）

- Email 助理（`gog gmail`）
  - 寫信草稿（根據老闆口氣：正式／輕鬆／跟進／催款）
  - 多帳號寄信（例如：`aiagentg888`、`jackychen0615`）
  - 支援附件（`--attach 檔案路徑`）
- 範例能力
  - 幫老闆把從 Drive 下載的估價單，寄給指定客戶
  - 幫老闆寄「每日 AI 工作報告 PDF」給自己留檔

### 1.3 檔案與文件（Docs / Drive / PDF）

- Drive 檔案操作（`gog drive`）
  - 搜尋檔案（`search`）、取得 metadata（`get`）、取得連結（`url`）
  - Share 檔案：`gog drive share <fileId> --email 老闆 --role writer`
  - Download 檔案：`gog drive download <fileId> --out tmp/檔名.ext --format pdf|docx...`
- 從雲端到老闆／客戶的完整流程
  - 老闆一句話：「用 XX 帳號，把某份 Drive 檔變成 PDF 傳給我，順便寄給 Y。」
  - AI 實際做：
    1. 用 `gog drive search/get` 找 fileId
    2. 必要時用 `gog drive share` 先給老闆權限
    3. 用 `gog drive download` 拉到本機 tmp/
    4. 用 `message` 把 PDF 當附件丟回這個聊天
    5. 用 `gog gmail send --attach` 把同一個檔案寄給指定收件人
- 文檔／報告
  - 用 md 寫教學、白皮書、報告
  - 用 `markdown-pdf` 轉成中文正常的 PDF

### 1.4 規則、流程與每日會報（Meta）

- AI 行為規則
  - `docs/meta/AI 助理通用規則模板.md`：
    - 使用 skills 前要先盤點現有工具
    - 修改檔案要簡短回報變更重點
    - 每日 log 要用 `>>` 追加
    - 每晚整理「今日工作摘要＋詳細 log」，轉成 PDF 給老闆
    - 第一次完成某個技能流程，要主動告訴老闆「我可以教你怎麼自己做」
- 技能總覽
  - `docs/meta/Clawdbot 技能與工具總覽.md`：
    - 整理目前所有 skills（gog、notion、slack、agent-browser 等）的用途和例子
- 每日會報
  - `每日會報/YYYY-MM-DD_AI助理每日工作報告.pdf`：
    - 第一頁：今日重點摘要
    - 後面：完整 log 原文
  - 「可複製模板/每日會報範例/範例回報教學.pdf」：
    - 給新 AI 看「會報 PDF 應該長什麼樣」。

---

## 2. 下一階段要補的功能（Roadmap）

> 這些是老闆會有感，但目前還沒整合完整的部分。

### 2.1 任務＆專案管理（Tasks / Projects）

- 目標：
  - 從行事曆、email、聊天內容中抽出「待辦事項」
  - 做出 Today / This Week 任務清單
  - 未來接到專案板（Trello、Notion、Jira 等）
- 目前狀態：
  - 有 trello skill，但還沒定義「老闆怎麼講話 → 變成卡片／任務」的流程
- 下一步：
  - 先用 md 或 Google Sheet 做一個「一人公司老闆的 To-Do MVP」
  - 再考慮串 Trello / Notion database

### 2.2 CRM / 客戶管理 ＋ 銷售漏斗

- 目標：
  - 管理客戶名單、狀態（lead → proposal → signed）
  - 幫老闆看每週漏斗狀況
- 目前狀態：
  - 沒有專用 CRM skill（HubSpot / Pipedrive");
  - 但有 `gog sheets` 可以當最簡單的資料庫
- 下一步：
  - 做一張 Google Sheet 當「客戶名單＋狀態表」
  - 用 `gog sheets` 寫入／更新＋每週摘要

### 2.3 財務 / 報表整合（Ops）

- 目標：
  - 每週／每月幫老闆整理：營收、成本、現金流概況
  - 用人話說明「這週比較好的地方／要注意的地方」
- 目前狀態：
  - 沒有直接對接會計／金流 API 的 skill
  - 可用 Google Sheets 做初版報表
- 下一步：
  - 設計一張「營收＋成本＋來源」Sheet
  - 每週用 `gog sheets get` 拉數字 → 整理成文字摘要

### 2.4 Browser Automation（網站自動操作）

- 目標：
  - 幫老闆登入後台抓報表
  - 幫老闆去特定網站查價、比價
  - 之後才是半自動訂位
- 目前狀態：
  - 有 `agent-browser` skill，但尚未在這個環境完整串接
- 下一步：
  - 確認 agent-browser 在 daemon 環境可用
  - 做一兩個具體腳本（例如：登入某服務 → 下載 CSV 報表）

### 2.5 內部協作平台（Slack / Notion 等）

- 目標：
  - 幫老闆把週報貼到 Slack
  - 把會議紀錄寫進 Notion
- 目前狀態：
  - 有 `slack` 和 `notion` skills
  - 尚未設定實際 workspace / token
- 下一步：
  - 選一個 Slack workspace + Notion space 作為 Demo
  - 定義固定句型，例如：
    - 「幫我把這份週報貼到 Slack #weekly」
    - 「幫我把這段整理成 Notion 某個 page」

### 2.6 生活面（訂位、提醒、家人行程）

- 目標：
  - 查餐廳、寫出一段可以給店家的訊息
  - 管理重要日期（家人生日、紀念日）
- 目前狀態：
  - 沒有直接訂位 API
- 下一步：
  - 先做「查資料＋寫訊息模板」的半自動版本
  - 再看要不要串外部服務（如 OpenTable、Line Bot）

---

## 3. 要怎麼跟老闆或客戶講？（示範話術）

- 「現在這一版 AI 助理，已經可以幫你：排會、回信、整理檔案、每天晚上的工作報告。」
- 「後面我們會慢慢加上：任務管理、客戶管理、財務報表、網站自動操作，這些會分階段開。」
- 「所有規則和模板都放在 `可複製模板/` 裡，以後要複製出第二個、第三個 AI 助理，只要餵同一套模板就能學會。」
