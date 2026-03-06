---
name: SkillGuard - 安全掃描技能
description: 在安裝任何新技能前，先執行安全掃描以確認風險等級。保護 AI 語境的整體安全性。
---

# SkillGuard - 安全掃描技能

> AI 語境下的技能安全掃描與驗證工具

## 🛡️ 目標

在安裝任何新技能前，先執行安全掃描以確認風險等級。保護 AI 語境的整體安全性。

## 📋 使用方式

### 簡易指令（在 OpenClaw 環境中）

```bash
# 掃描技能目錄
skillguard scan /路徑/到/要掃描/目錄

# 掃描所有已安裝技能
skillguard scan --all

# 掃描並直接安裝
skillguard --auto-install 找到的技能
```

## 🔍 掃描項目

- **惡意程式碼檢測** - 關鍵 API 呼叫
- **外部連結驗證** - 確認沒有可疑外掛
- **權限請求檢查** - 评估資料存取需求
- **依賴性分析** - 確保版本兼容性
- **授權合規性** - SPDX/License 檢查

## 📊 回報格式

```json
{
  "skill": "skill-name",
  "status": "clean|warning|critical",
  "issues": {
    "critical": [],
    "warning": [],
    "info": []
  },
  "recommendation": "...",
  "risk_level": "1-10"
}
```

## ⛔ 標準操作守則

1. **先掃描，再安裝**
2. **所有掃描結果需經審查**
3. **Critical 險者不可安裝**
4. **Warning 險者需要先理解風險才能安裝**
5. **保留完整審查記錄**

## 🔧 系統整合

SkillGuard 作為 OpenClaw AI 的核心安全守護工具，所有技能安裝自動觸發預掃描流程。

--- v1.0.0 | 安全第一