# Clawdbot 技能說明

## 技能分類

### 指南型技能（無執行檔）
這些技能只是提供 Agent 操作指南，實際功能由 Agent 內建工具完成：

| 技能名稱 | 說明 |
|---------|------|
| `filesystem` | 檔案系統操作指南（listing、search、batch、tree） |
| `adaptive-suite` | 多功能助手指南（coder、PM、web dev、data analyst） |

### 工具型技能（有執行檔/CLI）
這些技能提供獨立的 CLI 工具：

| 技能名稱 | 說明 | 安裝需求 |
|---------|------|---------|
| `agent-browser` | 無頭瀏覽器自動化 | `npx playwright install` |
| `clawdhub` | 技能市場 CLI（search/install/publish） | npm 已包含 |
| `gog` | Google Workspace CLI | OAuth 設定 |
| `imsg` | iMessage CLI | macOS + 權限 |
| `blucli` | BluOS 音響控制 | 區網內有 BluOS 設備 |

### 參考型技能
提供特定領域知識：

| 技能名稱 | 說明 |
|---------|------|
| `github` | GitHub `gh` CLI 使用指南 |
| `weather` | 天氣查詢（免 API key） |
| `notion` | Notion API 操作 |

## 如何使用

1. **查看可用技能**：技能列表在系統 prompt 的 `<available_skills>` 區塊
2. **啟用技能**：在 Gateway UI 勾選 → 重啟 Gateway 或開新 Session
3. **測試技能**：直接問 Agent「用 XXX 技能做 YYY」

## 常見問題

### 技能啟用了但指令找不到？
- 可能是「指南型技能」，沒有獨立執行檔
- Agent 會用內建的 `exec`、`read`、`write` 等工具完成任務

### agent-browser 報錯 Playwright？
```bash
npx playwright install
```

---

*Last updated: 2026-02-02*
