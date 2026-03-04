# Changes: Real Conversation Data Integration

## 摘要

將系統從使用 **mock data** 升級為使用 **實際對話數據**，實現基於用戶真實興趣和個性的推薦。

## 更改的文件

### 1. 新增文件

#### `src/integrations/openclaw-session-reader.ts` (NEW)
**用途**: 讀取 OpenClaw session JSONL 文件並分析對話內容

**主要功能**:
- `readSessionHistory(userId)` - 讀取用戶的對話歷史
- `findActiveSession(userId)` - 查找活躍的 session ID
- `readSessionMessages(sessionId)` - 解析 JSONL 文件
- `analyzeConversation(messages)` - 提取 topics, interests, preferences

**輸出**:
```typescript
interface ConversationAnalysis {
  topics: string[];      // 檢測到的主題
  interests: string[];   // 提取的興趣
  preferences: string[]; // 識別的偏好
  history: string[];     // 最近對話片段
  messageCount: number;  // 消息計數
}
```

#### `scripts/test-conversation-analysis.ts` (NEW)
**用途**: 測試完整的對話分析流程

**測試內容**:
1. 讀取 session files
2. 分析對話內容
3. 計算個性 metrics
4. 生成推薦數據

**運行方式**:
```bash
npm run test:conversation
```

#### `docs/CONVERSATION-ANALYSIS.md` (NEW)
**用途**: 完整的技術文檔

### 2. 修改的文件

#### `src/analyzers/data-collector-enhanced.ts`
**Before** (Line 354-373):
```typescript
private async collectConversationMemory(userId: string): Promise<ConversationMemory> {
  // Mock data for development
  return {
    topics: ['AI tools', 'DeFi protocols', ...],  // 固定值
    interests: ['AI', 'Web3', ...],
    preferences: ['early stage', ...],
    history: [...],
  };
}
```

**After**:
```typescript
private async collectConversationMemory(userId: string): Promise<ConversationMemory> {
  // ✅ Read actual session history
  const { createSessionReader } = await import('../integrations/openclaw-session-reader');
  const sessionReader = createSessionReader();
  const analysis = await sessionReader.readSessionHistory(userId);

  return {
    topics: analysis.topics,        // 從對話中檢測
    interests: analysis.interests,  // 從用戶消息提取
    preferences: analysis.preferences, // 從偏好表達識別
    history: analysis.history,
  };
}
```

**影響**:
- ✅ 不再使用 mock data
- ✅ 讀取真實對話內容
- ✅ Graceful error handling

#### `src/bloom-identity-skill-v2.ts`
**Before** (Line 162):
```typescript
mainCategories: this.categoryMapper.getMainCategories(analysis.personalityType)
```

**After**:
```typescript
// ⭐ Use detected categories from actual conversation data
// Priority: What they talk about > personality-based defaults
mainCategories: analysis.detectedCategories.length > 0
  ? analysis.detectedCategories
  : this.categoryMapper.getMainCategories(analysis.personalityType)
```

**影響**:
- ✅ 優先使用從對話中檢測到的類別
- ✅ 只在無對話數據時才使用 personality-based fallback
- ✅ 符合「what they like mainly + personality」的邏輯

#### `package.json`
**新增 script**:
```json
"test:conversation": "ts-node scripts/test-conversation-analysis.ts"
```

## 數據流程對比

### Before (Mock Data Flow)
```
User ID
   ↓
Data Collector
   ↓
[MOCK DATA]
   ↓
Personality Analyzer
   ↓
Fixed Category Mapping (by personality type)
   ↓
Recommendations
```

### After (Real Data Flow)
```
User ID
   ↓
Session Reader → Read ~/.openclaw/.../sessions/*.jsonl
   ↓
Extract: topics, interests, preferences
   ↓
Data Collector (includes conversation memory)
   ↓
Personality Analyzer (2x2 metrics from conversation)
   ↓
Detected Categories (from actual interests)
   ↓
Skill Discovery (category match + personality match)
   ↓
Recommendations
```

## 推薦邏輯改進

### Before
```
Recommendation = f(personality_type) → fixed_categories → skills
```

**問題**:
- ❌ 忽略用戶實際興趣
- ❌ 過度依賴個性類型
- ❌ 無法反映對話內容

### After
```
Recommendation = f(detected_interests, personality_type)

Score = 30 * category_match     // What they need
      + 20 * personality_match  // How they approach
      + 15 * conversation_align // What they discussed
      + 15 * dimension_bonus    // 2x2 metrics
```

**優點**:
- ✅ 主要基於實際興趣
- ✅ 次要考慮個性風格
- ✅ 反映對話內容
- ✅ 符合原始設計目標

## Session File 格式

### 位置
```
~/.openclaw/agents/main/sessions/
├── sessions.json           # Session metadata
└── {sessionId}.jsonl       # Conversation history
```

### sessions.json
```json
{
  "agent:main:{userId}": {
    "sessionId": "abc123...",
    "createdAt": 1234567890
  }
}
```

### {sessionId}.jsonl
每行一個事件:
```json
{"type":"message","message":{"role":"user","content":[{"type":"text","text":"I'm interested in..."}],"timestamp":1770179501830}}
{"type":"message","message":{"role":"assistant","content":[{"type":"text","text":"Based on..."}],"timestamp":1770179502000}}
```

## 測試方式

### 1. 單元測試 (建議)
```bash
npm run test:conversation
```

**檢查點**:
- ✅ Session files 讀取
- ✅ Conversation 分析
- ✅ Category 檢測
- ✅ Personality metrics
- ✅ Recommendation 數據

### 2. 整合測試
```bash
# 實際運行 skill
npm start
```

**驗證**:
1. 檢查 console logs 中的 "Reading OpenClaw session"
2. 確認檢測到的 topics 和 interests
3. 驗證 mainCategories 來自對話而非固定映射
4. 查看推薦是否匹配實際興趣

## 錯誤處理

系統會優雅地處理以下情況:

| 情況 | 行為 |
|------|------|
| Session file 不存在 | 返回空數據，繼續運行 |
| JSONL 格式錯誤 | 跳過該行，繼續解析 |
| 無讀取權限 | 返回空數據，記錄錯誤 |
| 無對話歷史 | 使用 fallback categories |

## 兼容性

### Backward Compatibility
- ✅ 如果無法讀取 session，系統會 fallback 到：
  1. 使用 personality-based categories
  2. Manual Q&A mode

### Dependencies
- 無新增外部依賴
- 使用 Node.js 內建的 `fs` 和 `path`

## 性能考慮

### Session File 讀取
- JSONL 格式允許逐行解析（memory efficient）
- 只讀取最近 10 條消息用於 history

### 分析複雜度
- O(n) where n = 消息數量
- Keyword matching 使用預定義字典
- 無重型 NLP 或 ML 操作

## 後續改進機會

1. **語義分析**
   - 使用 LLM 進行更深度的意圖理解
   - 實體識別 (產品名稱、公司名稱)

2. **時間加權**
   - 最近消息權重更高
   - 趨勢檢測 (興趣變化)

3. **情感分析**
   - 正面提及 → 權重提升
   - 負面提及 → 權重降低

4. **Multi-turn Context**
   - 追蹤跨對話的主題演進
   - 長期興趣 vs 短期需求

5. **Caching**
   - 緩存已分析的 session
   - 僅處理新消息

## 驗證清單

部署前檢查:
- [ ] Session reader 能成功讀取文件
- [ ] Conversation analysis 產生正確的 topics
- [ ] Personality analyzer 使用對話數據
- [ ] Category detection 來自實際興趣
- [ ] Recommendations 匹配檢測到的類別
- [ ] Error handling 正常工作
- [ ] 測試腳本通過

## 相關文件

- `docs/CONVERSATION-ANALYSIS.md` - 技術文檔
- `scripts/test-conversation-analysis.ts` - 測試腳本
- `src/integrations/openclaw-session-reader.ts` - Session reader
- `src/analyzers/data-collector-enhanced.ts` - Data collector
- `src/analyzers/personality-analyzer.ts` - Personality analyzer
- `src/bloom-identity-skill-v2.ts` - Main skill

## 問題與支援

如有問題，請檢查:
1. Session files 權限 (`~/.openclaw/agents/main/sessions/`)
2. Console logs 中的錯誤訊息
3. 測試腳本輸出 (`npm run test:conversation`)
