# QST Memory v1.6 Changelog

## 基於莊子(Qin州牧)反饋的改進

### ✅ 已完成 (高優先級)

#### 1. 附錄索引處理腳本
- **文件**: `scripts/index_appendix.py`
- **功能**: 自動提取 QST 附錄中的關鍵概念
- **支持概念**: 意識旋量孤子、夸克渦旋、三旋鈕、本體層、顯現層
- **輸出**: 獨立索引文件 + 自動導入記憶庫

**用法**:
```bash
python scripts/index_appendix.py QST_CSS.md --category QST_Physics
```

#### 2. 樹狀搜索完整路徑顯示
- **改進**: tree_search.py 輸出格式
- **之前**: `Path: QST`
- **現在**: 
  ```
  📁 完整路徑: QST → Physics → E8
     層次: L3 分層
  
     📂 L1 (根): QST
     ├ 📂 L2 (次): Physics
     └ 📂 L3 (葉): E8
  ```

**測試結果**:
```bash
$ python scripts/tree_search.py "E8 物理"
📁 完整路徑: QST → Physics → E8
   層次: L3 分層

   📂 L1 (根): QST
 ├ 📂 L2 (次): Physics
 └ 📂 L3 (葉): E8

🔑 關鍵詞: QST, E8, 標準模型, torsion, Standard Model, dark matter...
📊 找到 10 條記憶
```

---

### 📝 計劃實現 (優先級2-3)

#### 3. Hybrid 搜索文檔補充
- 添加使用範例到 SKILL.md
- 說明 Tree + Semantic 結合邏輯

#### 4. 記憶關聯功能
- 在 memory 格式中添加 `related_memories: [#ID]` 字段
- 顯示: 「相關記憶：#5, #6」

#### 5. 記憶編輯功能
```bash
python qst_memory.py edit #ID --content "..."
```

#### 6. 統計改進
- 按 L2/L3 細分分類統計
- 時間分佈統計（本周/本月/今年）

---

## 版本計劃

| 版本 | 目標 | 時間 |
|------|------|------|
| v1.5.4 | 附錄索引 + 樹狀改進 | 2026-02-15 |
| v1.6.0 | Hybrid文檔 + 記憶關聯 | 待定 |
| v1.7.0 | 編輯功能 + 統計改進 | 待定 |

---

*李斯丞相 2026-02-15*
