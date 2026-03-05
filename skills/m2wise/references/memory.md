# Memory Subsystem

## Overview

M2Wise extracts and manages different types of memories from conversations.

## Memory Types

### Preference

User's explicit preferences and likes/dislikes.

**Detection patterns:**
- "I prefer..."
- "I like..."
- "I don't like..."
- "Please use..."
- "Don't use..."

**Example:**
```python
memory = {
    "type": "preference",
    "content": "User prefers concise Chinese answers",
    "canonical_key": "prefers_concise_chinese",
    "confidence": 0.95
}
```

### Fact

Factual information about the user.

**Detection patterns:**
- "I'm a..."
- "I work as..."
- "I have..."
- "I'm from..."

**Example:**
```python
memory = {
    "type": "fact",
    "content": "User is a software engineer with 5 years experience",
    "canonical_key": "software_engineer",
    "confidence": 0.9
}
```

### Explicit

Direct requests to remember something.

**Detection patterns:**
- "Remember that..."
- "Don't forget..."
- "Note that..."

**Example:**
```python
memory = {
    "type": "explicit",
    "content": "User hates spam emails",
    "canonical_key": "hates_spam",
    "confidence": 0.95
}
```

### Commitment

User's promises and commitments.

**Detection patterns:**
- "I will..."
- "I promise..."
- "I'm going to..."

**Example:**
```python
memory = {
    "type": "commitment",
    "content": "User will exercise every morning",
    "canonical_key": "exercise_morning",
    "deadline": "2025-12-31",
    "confidence": 0.85
}
```

## Memory Fields

```python
{
    "id": "mem_xxx",              # Unique identifier
    "user_id": "alice",           # User identifier
    "type": "preference",         # Memory type
    "content": "User likes coffee", # Raw content
    "canonical_key": "likes_coffee", # Normalized key
    "entities": ["coffee"],        # Extracted entities
    "tags": ["preference", "drink"], # Tags
    "scores": {
        "confidence": 0.95,       # Extraction confidence
        "importance": 0.8,        # Importance score
        "relevance": 0.9          # Relevance to query
    },
    "status": "active",           # active, archived, deleted
    "created_at": 1234567890,    # Unix timestamp
    "updated_at": 1234567890
}
```

## Memory Extraction

### How It Works

1. **Input**: Conversation messages
2. **Processing**: LLM extracts memories based on prompt templates
3. **Deduplication**: Similar memories are merged
4. **Storage**: Memories saved with embeddings

### Extraction Prompt

The extraction uses optimized prompts with few-shot learning:

```python
OPTIMIZED_PROMPT = """你是M2Wise记忆提取专家...

## 提取规则
- 只提取明确的用户偏好、事实、承诺
- 不提取讨论话题、问题、泛泛而谈

## 示例
### 正面示例
对话: "我喜欢喝咖啡，每天早上必须来一杯"
提取: {preference, 0.95}

### 负面示例
对话: "你觉得AI会取代程序员吗？"
提取: [] (讨论话题，不提取)
"""
```

## Memory Scoring

### Confidence Score

Based on:
- Extraction clarity
- User confirmation count
- Time decay

### Importance Score

Based on:
- Frequency of mention
- Emotional intensity
- Uniqueness

### Relevance Score

Calculated at retrieval time based on:
- Query similarity
- Recency
- Wisdom alignment
