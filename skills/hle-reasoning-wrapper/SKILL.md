---
name: hle-reasoning-wrapper
description: Wraps HLE benchmark questions in a structured Chain-of-Thought (CoT) reasoning process. Use when answering HLE questions to ensure strict step-by-step logic and format compliance.
---

# HLE Reasoning Wrapper

Enforces a structured reasoning process for Humanity's Last Exam (HLE) questions.

## Usage

```javascript
const hle = require('./index');
const prompt = hle.formatPrompt("What is the speed of light?");
// Use prompt with LLM
const result = hle.validateOutput(llmResponse);
```

## Logic

1.  **Format Prompt**: Injects required structure (Thought/Answer).
2.  **Validate Output**: Ensures the model followed the structure.
