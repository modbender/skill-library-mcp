---
name: poe-api-orchestrator
description: Use Poe API to call specialized AI models (Claude-Opus, Claude-Sonnet, Gemini, GPT-Codex). Automatically spawn subagents for coding, UI/UX design, data analysis, and complex reasoning tasks. Main agent decides which specialized subagent to use based on task type.
user-invocable: false
disable-model-invocation: true
metadata:
  openclaw:
    emoji: "🤖"
    requires:
      bins: [python3]
      env: [POE_API_KEY]
---

# Poe API Orchestrator

Autonomous subagent orchestration using Poe API with specialized models.

## 🎯 Decision Matrix

**Main Agent (GLM-5) autonomously decides:**

| Task Type | Subagent | Poe Model | Trigger Keywords |
|-----------|----------|-----------|------------------|
| **Coding** | `coding-agent` | GPT-5.3-Codex | "write code", "implement", "debug", "refactor", "script", "function" |
| **UI/UX Design** | `design-agent` | Gemini-3.1-Pro | "design UI", "mockup", "wireframe", "user interface", "frontend", "visual" |
| **Data Analysis** | `analysis-agent` | Claude-Sonnet-4.6 | "analyze data", "requirements", "breakdown", "structure", "plan" |
| **Complex Reasoning** | `reasoning-agent` | Claude-Opus-4.6 | "difficult problem", "complex", "reasoning", "deep analysis", "architecture" |

---

## 🔧 How It Works

### Autonomous Flow:
```
User Request
    ↓
Main Agent (GLM-5) analyzes task
    ↓
Main Agent decides:
  - Is this coding? → spawn coding-agent
  - Is this UI/UX? → spawn design-agent
  - Is this analysis? → spawn analysis-agent
  - Is this complex? → spawn reasoning-agent
    ↓
Subagent uses Poe API
    ↓
Calls specialized model
    ↓
Returns result to Main Agent
    ↓
Main Agent delivers to user
```

### No User Intervention Needed!
- ✅ Main agent detects task type
- ✅ Spawns appropriate subagent
- ✅ Subagent calls Poe API
- ✅ Uses specialized model
- ✅ Returns result

---

## 🚀 Quick Start

### 1. Set API Key
```bash
export POE_API_KEY="w0womy7-r0RmMP-C1nFH2f_RXnBbPr1dfy34VHqzWck"
```

### 2. Main Agent Usage

**I (GLM-5) will automatically:**

#### For Coding Tasks:
```
User: "Write a Python script to scrape data"
Me: [Detects coding task] → spawns coding-agent → uses GPT-5.3-Codex
```

#### For UI/UX Tasks:
```
User: "Design a dashboard"
Me: [Detects design task] → spawns design-agent → uses Gemini-3.1-Pro
```

#### For Analysis Tasks:
```
User: "Analyze these requirements"
Me: [Detects analysis task] → spawns analysis-agent → uses Claude-Sonnet-4.6
```

#### For Complex Problems:
```
User: "Design system architecture"
Me: [Detects complex task] → spawns reasoning-agent → uses Claude-Opus-4.6
```

---

## 📋 Subagent Model Assignments

### 1. Coding Agent → GPT-5.3-Codex
**Best for:**
- Writing code (Python, JS, etc.)
- Debugging
- Refactoring
- API integration
- Algorithm implementation

### 2. Design Agent → Gemini-3.1-Pro
**Best for:**
- UI/UX design
- Visual mockups
- Frontend design
- User experience
- Creative solutions

### 3. Analysis Agent → Claude-Sonnet-4.6
**Best for:**
- Data analysis
- Requirements gathering
- Task breakdown
- Structured planning
- Documentation

### 4. Reasoning Agent → Claude-Opus-4.6
**Best for:**
- Complex problems
- Deep reasoning
- Architecture design
- Multi-step logic
- Hard decisions

---

## 🎯 Decision Logic

Main agent checks for keywords:

```python
# Coding triggers
if any(word in task for word in ["code", "implement", "debug", "script", "function"]):
    spawn("coding-agent", model="GPT-5.3-Codex")

# UI/UX triggers
elif any(word in task for word in ["design", "UI", "mockup", "visual", "frontend"]):
    spawn("design-agent", model="Gemini-3.1-Pro")

# Analysis triggers
elif any(word in task for word in ["analyze", "requirements", "breakdown", "plan"]):
    spawn("analysis-agent", model="Claude-Sonnet-4.6")

# Complex triggers
elif any(word in task for word in ["complex", "difficult", "architecture", "reasoning"]):
    spawn("reasoning-agent", model="Claude-Opus-4.6")
```

---

## 📝 Example Scenarios

### Scenario 1: Coding Task
```
User: "Write a WebSocket client for real-time data"

Main Agent:
  → Detects: "WebSocket", "client" (coding keywords)
  → Decision: Spawn coding-agent
  → Model: GPT-5.3-Codex
  → Result: Working code

User receives: Complete WebSocket client implementation
```

### Scenario 2: UI/UX Task
```
User: "Design a trading bot dashboard"

Main Agent:
  → Detects: "design", "dashboard" (UI/UX keywords)
  → Decision: Spawn design-agent
  → Model: Gemini-3.1-Pro
  → Result: Dashboard mockup + design specs

User receives: Complete UI/UX design
```

### Scenario 3: Analysis Task
```
User: "Analyze requirements for building a chatbot"

Main Agent:
  → Detects: "analyze", "requirements" (analysis keywords)
  → Decision: Spawn analysis-agent
  → Model: Claude-Sonnet-4.6
  → Result: Detailed requirements document

User receives: Complete analysis
```

### Scenario 4: Complex Problem
```
User: "Design microservices architecture for e-commerce"

Main Agent:
  → Detects: "architecture", complex task
  → Decision: Spawn reasoning-agent
  → Model: Claude-Opus-4.6
  → Result: Architecture diagram + explanation

User receives: Complete architecture design
```

---

## ⚙️ Configuration

### Environment Variables
```bash
POE_API_KEY=w0womy7-r0RmMP-C1nFH2f_RXnBbPr1dfy34VHqzWck
POE_API_URL=https://api.poe.com/v1
```

### Token Control ⚠️ IMPORTANT

**Correct Understanding** (Updated 2026-03-03):

```python
# 1. max_tokens = Response length limit (NOT total usage!)
task_max_tokens = {
    "coding": 8000,      # Coding needs complete code
    "design": 4000,      # UI/UX design
    "analysis": 3000,    # Data analysis
    "reasoning": 5000,   # Complex reasoning
}

# 2. Real cost control ⭐
max_calls_per_task = 10        # Limit API calls (MOST IMPORTANT!)
max_total_tokens = 100000      # Total token budget
track_usage = True             # Track usage

# 3. Monitor output
# 📊 Tokens: 77 | Total: 77 | Calls: 1/10
```

**Key Points**:
- ✅ `max_tokens` = Maximum response length (not total usage)
- ✅ `max_calls_per_task` = Real cost control (limit API calls)
- ✅ Coding tasks need 8000+ tokens (not 2000)
- ✅ Main agent monitors all subagent usage

**Violation Handling**:
- Call limit exceeded → Reject request
- Auto-notify main agent

### Model Endpoints
```python
MODELS = {
    "coding": "GPT-5.3-Codex",
    "design": "Gemini-3.1-Pro",
    "analysis": "Claude-Sonnet-4.6",
    "reasoning": "Claude-Opus-4.6"
}
```

---

## 🔄 Workflow

1. **User makes request** → Main agent (GLM-5)
2. **Main agent analyzes** → Detects task type
3. **Main agent decides** → Which subagent to spawn
4. **Subagent spawned** → Uses Poe API
5. **Subagent calls model** → Specialized AI
6. **Model processes** → Returns result
7. **Subagent returns** → To main agent
8. **Main agent delivers** → To user

**All automatic! No user intervention needed!**

---

## 📊 Benefits

✅ **Autonomous Decision-Making** - Main agent decides automatically  
✅ **Specialized Models** - Right model for right task  
✅ **No Manual Spawning** - Automatic subagent creation  
✅ **Parallel Processing** - Multiple subagents can work simultaneously  
✅ **Best Results** - Combining strengths of different models  

---

## 🎯 Summary

**Main Agent (GLM-5) Responsibilities:**
1. ✅ Analyze user request
2. ✅ Detect task type
3. ✅ Decide which subagent to spawn
4. ✅ Spawn subagent with Poe API
5. ✅ Collect results
6. ✅ Deliver to user

**User Just Asks** → **Everything Else is Automatic!**

---

**I will autonomously decide and spawn the right subagent for each task!** 🚀
