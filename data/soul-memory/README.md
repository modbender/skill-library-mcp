<div align="center">

# 🧠 Soul Memory System v3.2.2

### Intelligent Memory Management System

**Long-term memory framework for AI Agents**

**🆕 v3.2.2 - Heartbeat 去重機制 + OpenClaw Plugin 集成**

[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CJK Support](https://img.shields.io/badge/CJK-%E4%B8%AD%E6%97%A5%E9%9F%93-red.svg)]()
[![Cantonese](https://img.shields.io/badge/粵語-支援-orange.svg)]()
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Plugin-v0.2.1_beta-blue.svg)]()

</div>

---

## ✨ Features

Eight powerful modules for complete memory management - **Now with OpenClaw Plugin integration & CJK support!**

| Module | Function | Description |
|:-------:|:---------:|:------------|
| **A** | Priority Parser | `[C]/[I]/[N]` tag parsing + semantic auto-detection |
| **B** | Vector Search | Keyword indexing + CJK segmentation + semantic expansion |
| **C** | Dynamic Classifier | Auto-learn categories from memory |
| **D** | Version Control | Git integration + version rollback |
| **E** | Memory Decay | Time-based decay + cleanup suggestions |
| **F** | Auto-Trigger | Pre-response search + Post-response auto-save |
| **G** | **Cantonese Branch** | 🆕 語氣詞分級 + 語境映射 + 粵語檢測 |
| **H** | **CLI Interface** | 🆕 Pure JSON output for external integration |
| **Plugin** | **OpenClaw Hook** | 🆕 `before_prompt_build` Hook for automatic context injection |
| **Web** | Web UI | FastAPI dashboard with real-time stats, search & task monitoring |

---

## 🆕 v3.2.2 Release Highlights

### 🎯 核心改進

| 功能 | 說明 |
|------|------|
| **Heartbeat 去重機制** | MD5 哈希追踪，自動跳過已保存內容 |
| **CLI 接口** | 純 JSON 輸出，適用於外部系統集成 |
| **OpenClaw Plugin** | 自動在每次回應前注入相關記憶 |
| **寬鬆模式** | 降低识別閾值，保存更多對話內容 |

### 🔄 Heartbeat 去重機制

**問題**：重複保存相同內容導致記憶膨脹

**解決方案**：MD5 哈希追踪每次保存的內容

```python
# 使用範例
content_hash = get_content_hash("這是一段內容")
saved_hashes = get_saved_hashes("2026-02-23")

if content_hash in saved_hashes:
    print("⏭️  跳過重複")
else:
    save_to_daily_file(content, "C")
    save_hash("2026-02-23", content_hash)
    print("✅ 保存新內容")
```

**優勢**：
- ✅ 避免重複保存
- ✅ 節省存儲空間
- ✅ 提高運行效率

### 🤖 OpenClaw Plugin 集成

**自動化記憶注入**：每次回答前自動搜索並注入相關記憶

```typescript
// Plugin 自動執行
export default function register(api: any) {
  api.on('before_prompt_build', async (event: any, ctx: any) => {
    // 從用戶消息提取查詢
    const query = extractQuery(lastUserMessage);
    
    // 搜索記憶
    const results = await searchMemories(query, config);
    
    // 注入記憶上下文
    return {
      prependContext: buildMemoryContext(results)
    };
  });
}
```

**效果**：
```markdown
## 🧠 Memory Context

1. ⭐ [🔴 Critical] QST 質量理論：質量從 E8 幾何破缺派生...
2. 🔥 [🟡 Important] 希格斯機制對比：標準模型 vs QST...
```

### 📡 CLI 接口

**純 JSON 輸出**：適用於外部腳本和插件

```bash
$ python3 cli.py search "QST 質量律" --top_k 3

[
  {
    "path": "/root/.openclaw/workspace/MEMORY.md",
    "content": "QST 質量論觀點：質量非基本量，而是從 E8 幾何結構中派生...",
    "score": 8.5,
    "priority": "C"
  },
  ...
]
```

---

## 📊 寬鬆模式改進

| 項目 | 修改前（嚴格） | 修改後（寬鬆） |
|------|--------------|--------------|
| **最小長度** | 50 字 | **30 字** ↓ |
| **長文本閾值** | > 200 字 | **> 100 字** ↓ |
| **最低 importance_score** | >= 2 | **>= 1** ↓ |
| **關鍵詞數量** | 15 個 | **35+ 個** ↑ |

擴展關鍵詞：SSH、VPS、網絡、防火牆、GitHub、Plugin、Hook、CLI 等

---

## 📥 安裝

### 一鍵安裝

```bash
bash install.sh
```

**完整安裝包含**：
- ✅ Soul Memory v3.2.2 核心系統
- ✅ CLI 接口（純 JSON 輸出）
- ✅ Heartbeat v3.2.2 配置
- ✅ OpenClaw Plugin（v0.1.0 beta）

### 選項安裝

```bash
# 只安裝 Core System（跳過 Plugin）
bash install.sh --without-plugin

# 開發模式（包含測試）
bash install.sh --dev
```

### 手動安裝

```bash
# 克隆倉庫
git clone https://github.com/kingofqin2026/Soul-Memory-.git
cd Soul-Memory-

# 運行測試
python3 test_all_modules.py
```

---

## 💻 使用方法

### CLI 接口

```bash
# 搜索記憶（純 JSON 輸出）
python3 cli.py search "查詢內容" --top_k 5 --min_score 0

# 添加記憶
python3 cli.py add "[C] 重要信息"

# 列出統計
python3 cli.py stats
```

### Python API

```python
from core import SoulMemorySystem

# 初始化系統
system = SoulMemorySystem()
system.initialize()

# 搜索記憶
results = system.search("user preferences", top_k=5)

# 添加記憶
memory_id = system.add_memory("[C] User prefers dark mode")

# Pre-response: 提前搜索
context = system.pre_response_trigger("What are the user's preferences?")

# Post-response: 自動保存
def after_response(user_query, assistant_response):
    memory_id = system.post_response_trigger(
        user_query,
        assistant_response,
        importance_threshold="I"  # 保存 [I] 或以上
    )
```

### Heartbeat 自動提取

```bash
# 執行 Heartbeat 檢查
python3 heartbeat-trigger.py
```

**輸出示例**：
```
🧠 初始化 Soul Memory System v3.2.2...
✅ 記憶系統就緒

🩺 Heartbeat 記憶檢查 (2026-02-23 20:20:06 UTC)
- [Auto-Save] 條目：0 條
- [Heartbeat 提取] 條目：42 條

🔍 開始主動提取對話...
📝 找到 9 條 recent 消息
⭐ 識別出 0 條重要內容
🔒 已有 42 條今日記憶

📊 最終狀態:
❌ 無新記憶需要保存
```

---

## 📋 Feature Details

### Priority System

**優先級標籤**決定記憶重要性：

| 標籤 | 級別 | 行為 |
|-----|------|------|
| `[C]` | **Critical** | 永不衰減，始終保留 |
| `[I]` | **Important** | 慢速衰減，保留 90 天 |
| `[N]` | **Normal** | 快速衰減，保留 30 天 |

### Keyword Search

**純本地實現** - 無需外部 API：

- ✅ 全文關鍵詞索引
- ✅ 語義同義詞擴展
- ✅ 相似度評分 + 優先級加權
- ✅ 類別過濾

### Classification System

**默認類別**（完全可自定義）：

> **User_Identity** | **Tech_Config** | **Project** | **Science** | **History** | **General**

---

## 🏗️ 架構

```
soul-memory-v3.2/
│
├── core.py                    # 核心系統編排器
├── cli.py                     # CLI 接口（純 JSON 輸出）
├── heartbeat-trigger.py       # Heartbeat 自動提取 v3.2.2
├── dedup_hashes.json          # MD5 哈希追蹤（去重）
├── modules/                   # 功能模塊
│   ├── priority_parser.py    # [A] 優先級解析器
│   ├── vector_search.py      # [B] 向量搜索
│   ├── dynamic_classifier.py # [C] 動態分類器
│   ├── version_control.py    # [D] 版本控制
│   ├── memory_decay.py       # [E] 記憶衰減
│   └── auto_trigger.py       # [F] 自動觸發
│
├── cache/                     # 自動生成緩存
├── extensions/                # OpenClaw Plugin（v0.1.0 beta）
│   └── soul-memory/
│       ├── index.ts          # Plugin Hook handler
│       ├── openclaw.plugin.json
│       └── package.json
├── test_all_modules.py       # 完整測試套件
└── install.sh                 # 安裝腳本 v3.2.2
```

---

## 🔒 隱私與安全

> **您的數據完全在您控制下**

- ✅ **無外部 API 調用** - 100% 離線兼容
- ✅ **無雲端服務** - 無第三方依賴
- ✅ **域隔離** - 完全數據隔離
- ✅ **開源** - 透明 MIT 許可證

---

## 📐 技術規格

| 規格 | 詳細 |
|------|------|
| **Python 版本** | 3.7+ |
| **依賴** | 無（純 Python 標準庫） |
| **存儲** | 本地 JSON 文件 |
| **搜索** | 關鍵詞匹配 + 語義擴展 |
| **分類** | 動態學習 + 預設規則 |
| **記憶格式** | Markdown + 優先級標籤 |
| **去重算法** | MD5 哈希 |
| **CLI 輸出** | 純 JSON |

---

## 🧪 測試

運行完整測試套件：

```bash
python3 test_all_modules.py
```

### 預期輸出

```
==================================================
🧠 Soul Memory System v3.2.2 - Test Suite
==================================================

📦 Testing Module A: Priority Parser...
  ✅ Priority Parser: PASS

📦 Testing Module B: Vector Search...
  ✅ Vector Search: PASS

[...]

==================================================
📊 Results: 8 passed, 0 failed
==================================================
✅ All tests passed!
```

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| **Plugin v0.2.1-beta** | 2026-02-25 | **prependContext 累積修復**：從 `event.prompt` 提取查詢，增強遺留格式清理 |
| **v3.2.2** | 2026-02-23 | **Heartbeat 去重機制** + **寬鬆模式** + **CLI 接口** + **OpenClaw Plugin v0.1.0 beta** |
| **v3.2.1** | 2026-02-19 | **索引策略改進**：Markdown 區塊級索引，減少 93% Token 消耗 |
| **v3.2.0** | 2026-02-19 | **Heartbeat 主動提取** + **寬鬆模式**（降低識別閾值） |
| **v3.1.1** | 2026-02-19 | **Hotfix**: 雙軌記憶持久化防止 OpenClaw 會話覆蓋 |
| **v3.1.0** | 2026-02-18 | **廣東話語法分支**：語氣詞分級 + 語境映射 + 粵語檢測 |
| **v3.0.0** | 2026-02-18 | **Web UI v1.0**: FastAPI dashboard + real-time stats |
| **v2.2.0** | 2026-02-18 | **CJK 智能分詞** + **Post-Response Auto-Save** |
| **v2.1.0** | 2026-02-17 | 重新品牌為 Soul Memory，技術中立化 |
| **v2.0.0** | 2026-02-17 | 自託管版本，完全獨立 |

---

## 🔧 安裝與卸載

### 安裝

```bash
# 執行安裝腳本
bash install.sh

# 設置自動觸發（可選）
python3 heartbeat-trigger.py
```

### 卸載

\>\> **卸載腳本可以完全清除 Soul Memory 的所有集成配置**

\>\> 使用方法：

\>\> \`\`\`bash
\>\> \# 基本卸載（會提示確認）
\>\> bash uninstall.sh
\>\>
\>\> \# 創建備份後卸載（推薦）
\>\> bash uninstall.sh --backup
\>\>
\>\> \# 自動確認（無需手動確認）
\>\> bash uninstall.sh --backup --confirm
\>\> \`\`\`

\>\> **卸載項目**：
\>\> 1. 移除 OpenClaw Plugin 配置（`~/.openclaw/openclaw.json`）
\>\> 2. 禁用 Heartbeat 自動觸發（`HEARTBEAT.md`）
\>\> 3. 禁用自動記憶注入（Plugin）
\>\> 4. 禁用自動記憶保存（Post-Response Auto-Save）

\>\> **恢復配置**：
\>\> 卸載腳本會在 `~/workspace/soul-memory-backup/YYYYMMDD-HHMMSS/` 創建備份，包含：
\>\> - `openclaw.json.backup`：原始配置
\>\> - `HEARTBEAT.md.backup`：原始 Heartbeat 文件

---

## 🔧 OpenClaw Plugin 使用

### 安裝配置

```bash
# 1. 執行安裝腳本（默認包含 Plugin）
bash install.sh

# 2. 配置 OpenClaw (~/.openclaw/openclaw.json)
{
  "plugins": {
    "entries": {
      "soul-memory": {
        "enabled": true,
        "config": {
          "enabled": true,
          "topK": 5,
          "minScore": 0.0
        }
      }
    }
  }
}

# 3. 重啟 Gateway
openclaw gateway restart
```

### Plugin 行為

**自動觸發**：每次回答前自動執行

1. 提取用戶消息查詢（移除元數據）
2. 搜索相關記憶（top_k = 5）
3. 格式化記憶上下文
4. 注入到提示詞之前

---

## 📦 Plugin 推送記錄

**Commit**: `9acbf51`
**Repository**: https://github.com/kingofqin2026/Soul-Memory-

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

<div align="center">

## 🙏 Acknowledgments

**Soul Memory System v3.2** is a **personal AI assistant memory management tool**, designed for personal use.

---

made with ❤️ by **kingofqin2026**

[⬆ Back to Top](#-soul-memory-system-v32)

</div>
