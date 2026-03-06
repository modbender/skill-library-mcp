# Poe API Orchestrator Skill

🤖 **Autonomous subagent orchestration using Poe API with specialized AI models**

---

## ✨ Features

- **Autonomous Decision-Making**: Main agent (GLM-5) automatically detects task type and spawns appropriate subagent
- **4 Specialized Models**: Claude-Opus, Claude-Sonnet, Gemini, GPT-Codex
- **Smart Task Routing**: Automatically routes coding, design, analysis, and reasoning tasks to the best model
- **Token Control**: Built-in cost control with call limits and budget tracking
- **Zero User Intervention**: Just ask, everything else is automatic

---

## 🎯 Task-to-Model Mapping

| Task Type | Model | Trigger Keywords |
|-----------|-------|------------------|
| **Coding** | GPT-5.3-Codex | code, implement, debug, script, function |
| **UI/UX Design** | Gemini-3.1-Pro | design, UI, mockup, visual, frontend |
| **Data Analysis** | Claude-Sonnet-4.6 | analyze, requirements, breakdown, plan |
| **Complex Reasoning** | Claude-Opus-4.6 | complex, difficult, architecture, reasoning |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/calvinlam/.openclaw/workspace/skills/poe-api-orchestrator
python3 -m venv venv
source venv/bin/activate
pip install openai
```

### 2. Set API Key

```bash
export POE_API_KEY="w0womy7-r0RmMP-C1nFH2f_RXnBbPr1dfy34VHqzWck"
```

### 3. Use in Main Agent

The main agent (GLM-5) will **automatically** use this skill when detecting appropriate tasks:

```
User: "Write a Python script to scrape data"
→ Main agent detects coding task
→ Spawns coding-agent
→ Uses GPT-5.3-Codex
→ Returns complete code
```

---

## 📝 Usage Examples

### Coding Task

```python
# Automatic routing to GPT-5.3-Codex
User: "Write a WebSocket client with auto-reconnect"
→ Main agent: coding-agent (8000 tokens)
→ Result: Complete implementation
```

### UI/UX Design

```python
# Automatic routing to Gemini-3.1-Pro
User: "Design a trading bot dashboard"
→ Main agent: design-agent (4000 tokens)
→ Result: UI/UX design + mockup
```

### Data Analysis

```python
# Automatic routing to Claude-Sonnet-4.6
User: "Analyze requirements for e-commerce chatbot"
→ Main agent: analysis-agent (3000 tokens)
→ Result: Detailed requirements doc
```

### Complex Reasoning

```python
# Automatic routing to Claude-Opus-4.6
User: "Design microservices architecture for e-commerce"
→ Main agent: reasoning-agent (5000 tokens)
→ Result: Complete architecture design
```

---

## ⚙️ Configuration

### Environment Variables

```bash
POE_API_KEY=w0womy7-r0RmMP-C1nFH2f_RXnBbPr1dfy34VHqzWck
POE_API_URL=https://api.poe.com/v1
```

### Token Control

```python
# Response length (by task type)
max_tokens_coding = 8000      # Complete code
max_tokens_design = 4000      # UI/UX design
max_tokens_analysis = 3000    # Analysis
max_tokens_reasoning = 5000   # Complex reasoning

# Cost control ⭐
max_calls_per_task = 10       # API call limit (MOST IMPORTANT)
max_total_tokens = 100000     # Total budget
```

---

## 🧪 Testing

```bash
cd /home/calvinlam/.openclaw/workspace/skills/poe-api-orchestrator
source venv/bin/activate
POE_API_KEY="w0womy7-r0RmMP-C1nFH2f_RXnBbPr1dfy34VHqzWck" python3 scripts/poe_client.py
```

Expected output:
```
✅ GPT-5.3-Codex: 1.40s
✅ Gemini-3.1-Pro: 4.09s
✅ Claude-Sonnet-4.6: 2.20s
✅ Claude-Opus-4.6: 2.36s
Total tokens: 85/100000
```

---

## 📊 Performance

- **Connection Success Rate**: 100% (4/4 models)
- **Average Response Time**: 2.51s
- **Token Efficiency**: 0.085% (85/100000)
- **Status**: ✅ Production Ready

---

## 📁 File Structure

```
poe-api-orchestrator/
├── SKILL.md                    # Main skill definition
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── scripts/
│   ├── poe_client.py          # API client (OpenAI-compatible)
│   ├── subagent_helper.py     # Subagent helper functions
│   └── test_poe.py            # Test script
└── venv/                       # Python virtual environment
```

---

## 🔧 How It Works

1. **User Request** → Main agent (GLM-5)
2. **Task Detection** → Main agent analyzes keywords
3. **Subagent Spawn** → Automatic creation based on task type
4. **Poe API Call** → Subagent uses OpenAI-compatible API
5. **Model Processing** → Specialized AI processes task
6. **Result Return** → Subagent → Main agent → User

**All automatic! No manual intervention needed!**

---

## ⚠️ Important Notes

### Token Control

- **max_tokens** = Response length limit (NOT total usage)
- **Call limit** = Real cost control (max_calls_per_task)
- **Coding tasks** need 8000+ tokens (not 2000)

### Monitoring

```
📊 Tokens: 77 | Total: 77 | Calls: 1/10
```

Shows:
- Current token usage
- Total usage
- API calls / limit

---

## 📚 Related Documentation

- `TOKEN_CONTROL_EXPLAINED.md` - Detailed token control explanation
- `POE_FINAL_OPTIMIZED.md` - Final optimization report
- `POE_OPENAI_API_GUIDE.md` - OpenAI-compatible API guide

---

## 🎯 Summary

**Main Agent (GLM-5) will**:
- ✅ Automatically detect task type
- ✅ Spawn appropriate subagent
- ✅ Use specialized model
- ✅ Control token usage
- ✅ Return results

**User just asks** → **Everything else is automatic!** 🚀

---

**Version**: 1.0.0
**Status**: ✅ Production Ready
**Last Updated**: 2026-03-03
**Author**: UAT (AI Project Manager)
