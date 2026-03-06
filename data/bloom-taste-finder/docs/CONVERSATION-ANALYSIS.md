# Conversation Analysis Integration

## 概述

本文檔說明如何使用**實際對話數據**來分析用戶個性並生成推薦。系統現在會讀取 OpenClaw session files 並從對話中提取用戶的興趣和偏好。

## 數據流程

```
OpenClaw Session Files
         ↓
   Session Reader
         ↓
 Conversation Analysis
    (topics, interests, preferences)
         ↓
   Data Collector
         ↓
  Personality Analyzer
  (2x2 metrics: Conviction × Intuition)
         ↓
    Identity Data
  (personality + detected categories)
         ↓
  Skill Recommender
  (personality + interests)
         ↓
   Recommendations
```

## 關鍵組件

### 1. OpenClaw Session Reader
**文件**: `src/integrations/openclaw-session-reader.ts`

**功能**:
- 讀取 OpenClaw session JSONL 文件
- 位置: `~/.openclaw/agents/main/sessions/`
- 提取所有用戶和助手的對話消息

**輸出**:
```typescript
{
  topics: string[];      // 主要討論話題 (e.g., "AI Tools", "Crypto")
  interests: string[];   // 表達的興趣 (e.g., "machine learning", "DeFi")
  preferences: string[]; // 偏好 (e.g., "early stage", "open source")
  history: string[];     // 最近對話片段
  messageCount: number;  // 分析的消息數
}
```

**實作方式**:
```typescript
// 1. 找到 active session
const sessionId = await findActiveSession(userId);

// 2. 讀取 JSONL 文件
const messages = await readSessionMessages(sessionId);

// 3. 分析對話內容
const analysis = await analyzeConversation(messages);
```

### 2. Data Collector (Enhanced)
**文件**: `src/analyzers/data-collector-enhanced.ts`

**更新**:
- ✅ 移除 mock data
- ✅ 整合 OpenClaw Session Reader
- ✅ 從實際對話中提取數據

**方法**: `collectConversationMemory(userId)`
```typescript
private async collectConversationMemory(userId: string): Promise<ConversationMemory> {
  const sessionReader = createSessionReader();
  const analysis = await sessionReader.readSessionHistory(userId);

  return {
    topics: analysis.topics,
    interests: analysis.interests,
    preferences: analysis.preferences,
    history: analysis.history,
  };
}
```

### 3. Personality Analyzer
**文件**: `src/analyzers/personality-analyzer.ts`

**2x2 Metrics**:
1. **Conviction** (0-100)
   - High: 專注少數深度投入
   - Low: 多元探索
   - 數據來源: wallet transactions, social following

2. **Intuition** (0-100)
   - High: 願景驅動、趨勢發現者
   - Low: 數據驅動、等待驗證
   - 數據來源: 語言模式分析、對話內容

3. **Contribution** (0-100)
   - >65: The Cultivator (override)
   - 數據來源: 內容創建、社群參與、反饋

**Personality Types**:
- 💜 **The Visionary**: Conviction ≥50, Intuition ≥50
- 💚 **The Explorer**: Conviction <50, Intuition ≥50
- 🧡 **The Optimizer**: Conviction ≥50, Intuition <50
- 💙 **The Innovator**: Conviction <50, Intuition <50
- 🩵 **The Cultivator**: Contribution >65 (override)

**使用對話數據**:
```typescript
private extractAllText(userData: UserData): string {
  // Includes conversation memory!
  if (userData.conversationMemory) {
    textParts.push(...userData.conversationMemory.topics);
    textParts.push(...userData.conversationMemory.interests);
    textParts.push(...userData.conversationMemory.preferences);
    textParts.push(...userData.conversationMemory.history);
  }
  return textParts.join(' ');
}
```

### 4. Category Detection
**文件**: `src/analyzers/personality-analyzer.ts`

**方法**: `detectCategories(userData)`
- 從對話中檢測實際興趣類別
- 不再使用固定的 personality → category 映射

**更新**: `bloom-identity-skill-v2.ts`
```typescript
// ⭐ Before: Fixed mapping based on personality
mainCategories: this.categoryMapper.getMainCategories(analysis.personalityType)

// ✅ After: Detected from actual conversation
mainCategories: analysis.detectedCategories.length > 0
  ? analysis.detectedCategories
  : this.categoryMapper.getMainCategories(analysis.personalityType)
```

### 5. Skill Recommendation
**文件**: `src/bloom-identity-skill-v2.ts`

**推薦邏輯**:
```
Recommendation = f(detected_interests, personality_type)
```

**權重**:
1. **Category Match** (30 points) - 解決用戶實際需求
2. **Personality Match** (20 points) - 符合用戶行為風格
3. **Conversation Alignment** (15 points) - 相關討論話題
4. **Dimension Bonuses** (15 points) - 2x2 metrics 加成

## Session File 格式

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
每行一個 JSON 事件:
```json
{
  "type": "message",
  "message": {
    "role": "user",
    "content": [
      { "type": "text", "text": "I'm interested in AI tools..." }
    ],
    "timestamp": 1770179501830
  }
}
```

## 測試

運行測試腳本:
```bash
npm run test:conversation
```

測試腳本: `scripts/test-conversation-analysis.ts`

**測試內容**:
1. ✅ 讀取 session files
2. ✅ 分析對話內容
3. ✅ 檢測興趣類別
4. ✅ 計算 2x2 metrics
5. ✅ 生成推薦數據

## 優點

### ✅ Before (Mock Data)
```typescript
return {
  topics: ['AI tools', 'DeFi protocols', ...],  // 固定值
  interests: ['AI', 'Web3', ...],               // 固定值
  preferences: ['early stage', ...],            // 固定值
};
```

### ✅ After (Real Data)
```typescript
// 從實際對話中提取
const analysis = await sessionReader.readSessionHistory(userId);
return {
  topics: analysis.topics,        // 從對話中檢測
  interests: analysis.interests,  // 從用戶消息中提取
  preferences: analysis.preferences, // 從偏好表達中識別
};
```

## 關鍵改進

1. **Real Data** ✅
   - 從 OpenClaw session files 讀取真實對話
   - 不再使用 mock data

2. **Interest Detection** ✅
   - 從對話中檢測實際興趣
   - Category detection 基於用戶真實需求

3. **Personality Analysis** ✅
   - 2x2 metrics 使用對話語言模式
   - Contribution score 從實際互動計算

4. **Recommendation Logic** ✅
   - 主要基於檢測到的興趣 (what they like)
   - 次要考慮個性類型 (how they approach)
   - 符合原始設計: "what they like mainly + personality"

## 錯誤處理

系統會 gracefully 處理以下情況:
- ❌ Session file 不存在 → 返回空數據
- ❌ JSONL 格式錯誤 → 跳過該行
- ❌ 讀取權限問題 → 返回空數據
- ❌ 無對話歷史 → 降級到 manual Q&A

## 下一步

可能的增強:
1. 🔮 使用 LLM 進行更深度的語義分析
2. 🔮 時間加權 (recent messages > old messages)
3. 🔮 情感分析 (positive mentions boost score)
4. 🔮 實體識別 (product names, company names)
5. 🔮 Multi-turn context tracking
