---
name: m2wise
description: Memory-to-Wisdom Engine for AI agents. Use this skill to give yourself long-term memory, extract user preferences/facts from conversations, and track wisdom evolution.
emoji: 🧠
requires:
  bins: [python3, pip, m2wise-mcp]
  env: [OPENAI_API_KEY, M2WISE_SILICONFLOW_API_KEY]
---

# M2Wise - Memory-to-Wisdom Engine

> This is a skill for the OpenClaw AI Agent to enable long-term memory and self-evolving wisdom.

## 🎯 Purpose

As an AI agent, you inherently lack persistent memory across distinct sessions. The M2Wise skill bridges this gap. It allows you to:
1. **Extract and store** memories (facts, preferences, commitments) from user conversations.
2. **Retrieve** contextual memories and aggregated wisdom before answering.
3. **Consolidate** raw memories into overarching "Wisdom" (rules, schemas, and skills) during idle time.

## 🚦 When to Use This Skill

You should proactively invoke this skill in the following scenarios:
- **User expresses a preference**: e.g., "I prefer short answers", "Don't use emojis."
- **User shares a personal fact**: e.g., "I work as a Python developer", "I live in Beijing."
- **User asks you to remember**: e.g., "Remember that I hate spam."
- **Before answering complex questions**: To recall the user's past preferences or facts to personalize your response.

## 🛠️ How to Use (Agent Instructions)

You can interact with M2Wise via its Python SDK. Use your shell/execution environment to run these scripts snippet by snippet.

### 1. Installation Requirements
Make sure the environment has M2Wise installed before calling its Python API:
```bash
pip install m2wise[all]
```

### 2. Saving Memories (Online Phase)
When you detect a fact or preference in the conversation, run a quick python script to save it:
```python
from m2wise_sdk import M2WiseSDK

sdk = M2WiseSDK()
# Extract and save the user's message
sdk.add_message("current_user_id", "I prefer concise Chinese answers for technical questions")
```

### 3. Retrieving Context (Online Phase)
Before fulfilling a user's request, fetch their relevant memories:
```python
from m2wise_sdk import M2WiseSDK

sdk = M2WiseSDK()
context = sdk.get_context("current_user_id", "How should I answer this technical question?")
print("Retrieved Context:", context)
```
*Action: Read the output of this script and adapt your final response to the user based on the retrieved context.*

### 4. Background Processing (Sleep & Dream)
It is a good practice to trigger memory consolidation periodically (e.g., at the end of a long task).
```python
from m2wise_sdk import M2WiseSDK

sdk = M2WiseSDK()
# Sleep: Extracts memories and groups them into Wisdom Drafts
sdk.trigger_sleep("current_user_id")

# Dream: Verifies drafts against counterexamples and publishes them
sdk.trigger_dream("current_user_id")
```

## 🧩 MCP Server Alternative

If your OpenClaw runtime supports MCP (Model Context Protocol), you can start the M2Wise MCP server and use its native tools instead of writing Python scripts:

```bash
# Start the MCP server
m2wise-mcp --data-dir ./data
```

**Available MCP Tools:**
- `m2wise_add`: Add memory from conversation.
- `m2wise_search`: Search memories and wisdom.
- `m2wise_sleep`: Generate wisdom drafts.
- `m2wise_dream`: Verify and publish wisdom.

## 🧠 Memory and Wisdom Types You Will Encounter

- **Memories**: `preference` (likes/dislikes), `fact` (states/attributes), `commitment` (future actions).
- **Wisdoms**: `principle` (interaction guidelines), `schema` (behavioral patterns), `skill` (operational tactics).

## 🚀 Best Practices

1. **Be Proactive**: Don't wait for the user to explicitly say "remember this". If they state a strong preference, save it using `sdk.add_message()`.
2. **Context First**: For ambiguous requests, always query the memory bank first.
3. **Consolidate Often**: Run `trigger_sleep()` and `trigger_dream()` after completing a major task to ensure your wisdom evolves and stays clean.

## 🔗 Resources

- **GitHub Repository**: https://github.com/zengyi-thinking/M2Wise.git
- **Installation via OpenClaw (ClawHub)**:
  ```bash
  npx clawdhub@latest install m2wise
  ```
