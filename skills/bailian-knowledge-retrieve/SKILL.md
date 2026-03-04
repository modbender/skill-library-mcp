---
name: bailian-knowledgebase-retrieve
description: Bailian KnowledgeBase(Provided by Alibaba ModelStdio) offers to retrieve any proprietary data that have been vectorized in the hosted knowledgebases. It returns multidocs, concise KB retrieval results for LLMs.
homepage: https://bailian.console.aliyun.com/cn-beijing?tab=app#/knowledge-base
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["python3"],"env":["DASHSCOPE_API_KEY","KNOWLEDGEBASE_ID"]},"primaryEnv":"DASHSCOPE_API_KEY"}}
---

# Bailian KnowledgeBase Retrieve

Vector-based hosted KnowledgeBase with Bailian Embedding/Rerank API. Designed for AI agents and chatbots - returns clean, relevant content in your proprietary datahub.

## Retrieve(Search)

```bash
python3 {baseDir}/scripts/retrieve.py "query"
python3 {baseDir}/scripts/retrieve.py "query" 3
```

## Options

- `<count>`: Number of results (default: 5, max: 20)
- `<query>`: User Query for KB Retrieval
