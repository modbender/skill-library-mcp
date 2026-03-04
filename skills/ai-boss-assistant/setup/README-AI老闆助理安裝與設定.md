# AI 老闆助理 + Clawdbot 安裝與前置設定指南

> 給會動一點終端機的人看，說明如何在一台新的主機上：
> 1. 安裝 Clawdbot
> 2. 啟用需要的 skills
> 3. 準備授權與 API key
> 4. 放好技能包（可複製模板）並讓新 AI 開始學習

---

## 1. 安裝 Clawdbot（概念級）

1. 安裝 Node.js（建議 LTS 版）  
2. 全域安裝 Clawdbot CLI：
   ```bash
   npm install -g clawdbot
   ```
3. 啟用 Gateway（建議用系統服務）：
   ```bash
   clawdbot gateway install   # 安裝作業系統服務
   clawdbot gateway start     # 啟動 Gateway
   ```

> 實際指令可能依你的環境稍有不同，詳見官方文件：<https://docs.clawd.bot>

---

## 2. 啟用必要 Skills

在 Gateway 後台的 skills 管理頁面，建議至少啟用：

- `gog`：Google Workspace（Gmail / Calendar / Drive / Docs / Sheets）
- `agent-browser`：Browser automation（登入網站、填表、抓報表）
- `ai-pdf-builder` 或 `markdown-pdf`：從 Markdown 產 PDF（報告／教學）
- `notion`（選用）：寫入 Notion 資料庫 / 頁面
- `slack`（選用）：在 Slack 發佈訊息、加 reaction

> 規則：**先看使用者真的要用哪些服務，再開相對應的 skill**，不要一次全開。

---

## 3. 安裝對應 CLI 與工具

在這台主機上，需安裝以下命令列工具（以 macOS 為例）：

### 3.1 gog（Google Workspace CLI）

```bash
brew install steipete/tap/gogcli
```

### 3.2 agent-browser（Browser Automation CLI）

```bash
npm install -g agent-browser
agent-browser install   # 安裝 Chromium
```

### 3.3 markdown-pdf（md → PDF）

```bash
npm install -g markdown-pdf
```

> 只要 markdown-pdf 可以正常從 md 產出含中文的 PDF，就不強制依賴 LaTeX。

---

## 4. 準備授權與 API key

### 4.1 Google（gog）

1. 建立 OAuth client：  
   - 到 <https://console.cloud.google.com/apis/credentials>  
   - 建立 **Desktop app** 類型的 OAuth client  
   - 下載 JSON（例如 `client_secret_xxx.json`）。

2. 放到 Gog 預期的路徑（以 macOS 為例）：
   ```bash
   mkdir -p "$HOME/Library/Application Support/gogcli"
   mv ~/Downloads/client_secret_*.json \
     "$HOME/Library/Application Support/gogcli/credentials.json"
   ```

3. 告訴 gog 使用這個檔案：
   ```bash
   gog auth credentials "$HOME/Library/Application Support/gogcli/credentials.json"
   ```

4. 為每個帳號授權（只開需要的 services）：
   ```bash
   gog auth add you@gmail.com --services gmail,calendar,drive,docs,sheets
   gog auth list   # 確認 services 欄位
   ```

### 4.2 Brave Search（web_search，選用）

如果要用 `web_search` 查網頁，需要 Brave Search API key：

1. 到 <https://api.search.brave.com> 申請 API key。  
2. 在這台主機設定：
   ```bash
   clawdbot configure --section web
   ```
   或在 Gateway 環境變數中設定 `BRAVE_API_KEY`。

> 若不設定 Brave key，仍可使用 `agent-browser` 搭配使用者提供的網址進行網站操作。

### 4.3 其他服務（視需求）

- Slack：Bot Token / App Token
- Notion：Integration Token + Database ID
- Trello：API Key / Token

這些不需要一開始全部設定，通常會在老闆確定要用某一個整合時，再進行設定。

---

## 5. 技能包與可複製模板（關鍵）

### 5.1 原始 docs 目錄

在專案中，`docs/` 會放：

- `docs/gog/`：gog 教學與示範
- `docs/boss-assistant/`：AI 老闆助理白皮書、MVP 功能表
- `docs/meta/`：
  - `Clawdbot 技能與工具總覽.md`
  - `AI 助理通用規則模板.md`
- `docs/tasks/`：任務同步模板、生活事件模板
- `docs/browser/`：Browser Automation 備註與腳本模板

> **這些原始檔建議保留不動，當成「母版」。**

### 5.2 可複製模板資料夾

所有要給「新 AI、新主機」使用的模板，都要有一份副本放在：

```bash
可複製模板/
```

目前包含：

- `可複製模板/gog/`：gog 教學 md/PDF
- `可複製模板/老闆助理/`：
  - AI 老闆助理白皮書
  - MVP 功能表
- `可複製模板/meta/`：
  - Clawdbot 技能與工具總覽
  - AI 助理通用規則模板
- `可複製模板/tasks/`：
  - 今日待辦範本
  - 任務同步模板
  - 生活事件模板
- `可複製模板/browser/`：
  - agent-browser 限制備註
  - KKTIX 範例訂票腳本
- `可複製模板/每日會報範例/`：
  - 範例回報教學 PDF

> 規則：**不要動 docs/ 原始檔；要給新 AI 用的一律先複製到「可複製模板」裡。**

---

## 6. 讓新的 AI 助理開始學習（啟動順序）

1. **讀規則（行為層）**
   - `可複製模板/meta/AI 助理通用規則模板.md`

2. **讀技能說明（能力層）**
   - `可複製模板/meta/Clawdbot 技能與工具總覽.md`

3. **讀產品定位（AI 老闆助理做什麼）**
   - `可複製模板/老闆助理/AI 老闆助理MVP功能表.md`
   - `可複製模板/老闆助理/AI 老闆助理產品白皮書.md`

4. **讀任務與生活模板**
   - `可複製模板/tasks/今日待辦範本.md`
   - `可複製模板/tasks/生活事件模板.md`

5. **讀每日會報範例**
   - `可複製模板/每日會報範例/範例回報教學.pdf`

6. **對新老闆做前置訪談**（規則中已寫）：
   - 問生活事件類型（生日、運動、聚餐…）
   - 問提醒習慣
   - 問任務優先順序的定義

做好這些之後，新 AI 就有完整的「規則＋技能說明＋範例」，可以開始接老闆指令。