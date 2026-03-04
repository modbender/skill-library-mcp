# Heartbeat Integration Guide for QST Memory v1.7+

## 概述

QST Memory v1.7 的 Agent State System 與 OpenClaw Heartbeat 無縫整合，實現**狀態驅動的智能檢查策略**。

---

## 快速開始

### 1. 安裝整合腳本

將 `heartbeat.py` 複製到您的工作空間：

```bash
# 如果您在 qst-memory 技能目錄
cp scripts/heartbeat_integration.py /home/node/.openclaw/workspace/heartbeat.py
chmod +x /home/node/.openclaw/workspace/heartbeat.py
```

---

### 2. 設置自動執行

```bash
# 創建 cron 任務（每 20 分鐘執行一次）
crontab -e

# 添加以下行
*/20 * * * * python3 /home/node/.openclaw/workspace/heartbeat.py
```

---

### 3. 使用狀態系統

```bash
# 開始任務（自動切換到 DOING 模式）
cd /home/node/.openclaw/workspace/skills/qst-memory
python3 universal_memory.py --agent qst doing start \
  --task "QST 分析" \
  --type Research

# 更新進度
python3 universal_memory.py --agent qst doing update --progress 50

# 完成任務
python3 universal_memory.py --agent qst doing complete --result "成功"
```

---

## 狀態驅動策略

| Agent 狀態 | Heartbeat 行為 | 說明 |
|-----------|--------------|------|
| **IDLE** | ✅ 完整檢查 | @提及 + 回覆 + 投票 |
| **DOING** | 🎯 關鍵檢查 | @提及 + 回覆（跳過投票） |
| **WAITING** | ⚡ 快速檢查 | 只檢查 @提及 |
| **PAUSED** | ⏸️ 跳過檢查 | 不執行檢查 |
| **COMPLETED/FAILED** | ✅ 完整檢查 | 同 IDLE |

---

## 文件結構

```
/home/node/.openclaw/workspace/
├── heartbeat.py                    # 整合腳本（主執行文件）
├── HEARTBEAT.md                    # Heartbeat 配置
├── skills/qst-memory/
│   ├── data/
│   │   ├── qst_doing-state.json    # 當前任務狀態
│   │   ├── qst_events.json         # 事件日誌
│   │   └── qst_memories.md         # 記憶存儲
│   ├── scripts/
│   │   ├── agent_state.py          # 狀態機核心
│   │   └── heartbeat_integration.py # 心跳整合腳本模板
│   └── universal_memory.py         # 通用記憶系統 CLI
└── memory/
    └── heartbeat-state.json        # Heartbeat 狀態
```

---

## 使用範例

### 範例 1: 長時間物理模擬

```bash
# 開始模擬任務
python3 universal_memory.py --agent qst doing start \
  --task "QST FSCA v7 模擬運行 #42" \
  --type Research

# Heartbeat 會自動進入關鍵檢查模式
# - 只檢查 @提及（緊急反饋）
# - 跳過投票（不打斷模擬）

# 模擬完成
python3 universal_memory.py --agent qst doing complete \
  --result "模擬成功：ρ = 0.08 拟合 Bullet Cluster"
```

### 範例 2: 外交事件處理

```bash
# 發現外交 @提及
# Heartbeat 即使在 DOING 狀態下也會報告

# 可以暫停物理任務
python3 universal_memory.py --agent qst doing pause \
  --reason "處理 HKGBook 外交事件"

# 處理外交（自動切換到 lisi agent）
python3 universal_memory.py --agent lisi doing start \
  --task "回覆外交貼文" \
  --type Diplomacy

# 完成後恢復物理任務
python3 universal_memory.py --agent qst doing resume
```

---

## 故障排除

### 問題 1: 狀態未正確讀取

**症狀**：Heartbeat 始終執行完整檢查

**解決方案**：
```bash
# 檢查狀態文件
cat /home/node/.openclaw/workspace/skills/qst-memory/data/qst_doing-state.json

# 手動設置狀態
python3 universal_memory.py --agent qst doing start --task "測試"
```

### 問題 2: Heartbeat 未執行

**症狀**：Cron 任務未運行

**解決方案**：
```bash
# 檢查 cron 日誌
grep CRON /var/log/syslog

# 手動測試
python3 /home/node/.openclaw/workspace/heartbeat.py
```

---

## API 參考

### heartbeat.py 命令

```bash
python3 heartbeat.py
```

**輸出示例**：
```
============================================================
❤️  Heartbeat Started: 2026-02-15 09:15:26 UTC
============================================================

🤖 Agent: qst | 狀態: DOING
   任務: 測試 DOING 狀態下的 Heartbeat
   類型: Analysis
   進度: 0%

🔄 狀態: DOING - 執行 HKGBook 檢查 (策略: 簡化)
   ✅ HKGBook 檢查完成
```

---

## 多 Agent 支援

每個 Agent 都有自己的狀態文件：

```bash
# qst agent
/data/qst_doing-state.json

# mengtian agent
/data/mengtian_doing-state.json

# lisi agent
/data/lisi_doing-state.json
```

Heartbeat 會根據當前 Agent 的狀態調整檢查策略。

---

## 進階配置

### 自定義檢查間隔

編輯 `heartbeat.py` 調整時間戳邏輯：

```python
# 每 15 分鐘檢查一次
MIN_CHECK_INTERVAL = 15 * 60  # 15 分鐘

# 或者設置為 0 進行實時檢查（不推薦）
```

### 添加自定義檢查

在 `heartbeat.py` 的 `main()` 函數中添加：

```python
def check_custom_endpoint():
    """自定義檢查邏輯"""
    # 在這裡添加您的檢查
    pass

# 在 main() 中調用
check_custom_endpoint()
```

---

## 版本歷史

- **v1.7.1**: 增加 Heartbeat 整合支持
- **v1.7**: 引入 Agent State System
- **v1.6**: 多 Agent 支持

---

*Last Updated: 2026-02-15*
