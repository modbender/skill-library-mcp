# Claw Conductor v2.1 ![Claw Composer Icon](claw-composer-small.png)

**Build Complete Projects with a Single Request**

Transform complex development requests into working software through intelligent multi-model orchestration. Claw Conductor decomposes your request, routes subtasks to optimal AI models, executes in parallel, and delivers a complete project.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Version](https://img.shields.io/badge/version-2.1.0-green.svg)](https://github.com/johnsonfarmsus/claw-conductor/releases)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-blue)](https://openclaw.ai)

## 🚀 What is This?

Claw Conductor is a **full autonomous development orchestrator** that transforms a single Discord message into a complete, working software project.

### The Problem

Building software requires multiple AI models for different tasks:
- **Database design** → Best with Mistral Devstral (256K context)
- **Unit tests** → Best with Llama 3.3 70B (test generation expert)
- **Frontend UI** → Best with Mistral Devstral (near-Claude quality)
- **API endpoints** → Best with Llama or Mistral
- **Research** → Best with Perplexity (internet access)

Manually coordinating these models is tedious and error-prone.

### The Solution

**Single Discord request:**
```
@OpenClaw use claw-conductor to build a towing dispatch system with:
- Customer portal for requesting service
- Driver dashboard for accepting jobs
- Admin panel for managing users
- Real-time location tracking
```

**Claw Conductor automatically:**
1. ✨ **Decomposes** into 8 subtasks with dependencies
2. 🎯 **Routes** each to the optimal model (Mistral/Llama/Perplexity)
3. ⚡ **Executes** up to 5 tasks in parallel
4. 📦 **Consolidates** results, runs tests, commits to git
5. 🐙 **Pushes** complete project to GitHub

**Result:** Working dispatch system in ~45 minutes, zero manual intervention.

---

## ✨ What's New in v2.1

🤖 **Always-On Triage**: Automatically classifies requests as simple questions vs development tasks
💬 **Discord Integration**: Auto-maps Discord channels to project workspaces in `/root/projects`
⚡ **Dual-Mode Response**: Fast answers for questions, full orchestration for development
🎯 **Smart Routing**: Simple mode uses fast models, development mode uses full pipeline
🔧 **User Overrides**: Force classification with `!simple` or `!dev` flags
📋 **Path Announcements**: Visual indicators (📋 Simple / 🔧 Development) show routing decisions
🌍 **Project-Aware**: All responses know their workspace, channel, and context
🎨 **Multi-Project**: Handle multiple concurrent requests across different Discord channels

---

## 📋 Complete Workflow

```
Discord Message in #calculator-app channel
    ↓
1. Context Detection & Triage
   ├─ Discord Integration: Maps #calculator-app → /root/projects/calculator-app
   ├─ Request Classification: "Build a calculator app" → DEVELOPMENT
   ├─ Path Announcement: 🔧 Development mode - full orchestration
   └─ Route to: Full decomposition pipeline
    ↓
2. AI-Powered Task Decomposition (Development Mode)
   ├─ Uses best-rated model (auto-selected or configured)
   ├─ Task 1: Calculator logic (backend-development, complexity: 2)
   ├─ Task 2: UI components (frontend-development, complexity: 2)
   └─ Task 3: Unit tests (unit-test-generation, complexity: 2)
    ↓
3. Intelligent Routing
   ├─ Task 1 → Llama 3.3 70B (score: 87/100)
   ├─ Task 2 → Mistral Devstral (score: 95/100)
   └─ Task 3 → Llama 3.3 70B (score: 95/100)
    ↓
4. Project Initialization
   ├─ Workspace: /root/projects/calculator-app/ (from Discord mapping)
   ├─ Initializes git repository
   ├─ Creates GitHub repo: {user}/calculator-app
   └─ Registers OpenClaw agent
    ↓
5. Parallel Execution (max 5 concurrent)
   ├─ Worker 1: Task 1 (Llama) → Running
   ├─ Worker 2: Task 2 (Devstral) → Running
   └─ Worker 3: Task 3 (Llama) → Running
    ↓
6. Result Consolidation
   ├─ Merges all code changes
   ├─ Runs npm test (passes)
   ├─ Commits: "feat: calculator-app - 3 tasks completed"
   └─ Pushes to github.com/{user}/calculator-app
    ↓
✅ Complete project delivered in ~8 minutes
```

---

## 🎯 Key Features

### Always-On Triage & Discord Integration

**The Problem:** Not every Discord message needs full orchestration. Questions like "What's the status?" shouldn't trigger decomposition.

**The Solution:** Claw Conductor acts as an **always-on layer** that intelligently routes requests:

#### Triage Classification
- **Simple Mode** (📋): Questions, status checks, explanations → Fast model response
- **Development Mode** (🔧): Build, fix, implement requests → Full orchestration pipeline

#### Discord Channel Mapping
```
Discord #scientific-calculator → /root/projects/scientific-calculator
Discord #dispatch-suite → /root/projects/dispatch-suite
Discord #satire-news → /root/projects/satire-news
```

Each Discord channel in "Active Projects" category automatically maps to its project workspace.

#### User Overrides
```
@OpenClaw !simple Build a calculator  → Forces simple mode (just answers)
@OpenClaw !dev What is this project?  → Forces development mode (probably errors)
```

#### Example Flows

**Simple Request:**
```
User: "What files are in this project?"
  → 📋 Simple response mode
  → Fast answer from Mistral Devstral (project-aware)
  → Response in ~2 seconds
```

**Development Request:**
```
User: "Add user authentication with email verification"
  → 🔧 Development mode - full orchestration
  → Decompose into 5 tasks
  → Execute in parallel
  → Complete project in ~15 minutes
```

### AI-Powered Task Decomposition

- **Intelligent Analysis**: Uses AI models to analyze complex requests and break them into structured tasks
- **Auto-Selection**: Automatically picks the best model from your registry (or manual override)
- **Fallback Strategy**: Falls back to second-best model on failure
- **Structured Output**: Generates tasks with categories, complexity ratings, dependencies, and file targets

### Intelligent Multi-Model Routing

- **Capability-Based Scoring**: 1-5 star ratings per model per task category
- **Complexity Analysis**: Hard ceilings prevent overwhelming models
- **Cost Optimization**: Prefers free models when capabilities equal
- **Experience Tracking**: Learns which models perform best over time

### Parallel Task Execution

- **Worker Pool**: Up to 5 tasks running simultaneously
- **Dependency-Aware**: Database tasks complete before auth tasks
- **File Conflict Detection**: Tasks touching same files run sequentially
- **Multi-Project Support**: Handle multiple concurrent project requests

### Complete Project Delivery

- **Auto-Setup**: Creates workspace, git repo, GitHub repo
- **Test Execution**: Runs pytest, npm test, etc.
- **Conventional Commits**: Clean git history with co-authorship
- **GitHub Integration**: Automatic push on completion

---

## 🛠️ Installation

### Quick Start

```bash
# On your OpenClaw server
cd ~/.openclaw/skills
git clone https://github.com/johnsonfarmsus/claw-conductor.git
cd claw-conductor
chmod +x scripts/*.sh scripts/*.py
./scripts/setup.sh
```

The wizard will:
1. Detect your configured OpenClaw models
2. Ask about cost structure (free vs paid)
3. Create personalized agent-registry.json
4. Set routing preferences

### Manual Setup

```bash
# Copy example configuration
cp config/agent-registry.example.json config/agent-registry.json

# Add your models
python3 scripts/update-capability.py \
  --agent mistral-devstral-2512 \
  --category frontend-development \
  --rating 5 \
  --max-complexity 5
```

---

## 📚 Usage

### Simple Request

```
@OpenClaw use claw-conductor to build a calculator with:
- Basic operations (add, subtract, multiply, divide)
- Clean UI
- Unit tests
```

**Result:**
- 3 tasks decomposed
- 2 models used (Mistral + Llama)
- Completed in ~8 minutes
- GitHub repo created and pushed

### Complex Request

```
@OpenClaw use claw-conductor to build a towing dispatch system with:
- Customer portal for requesting service
- Driver dashboard for accepting jobs
- Admin panel for managing users
- Real-time location tracking
- Payment integration
```

**Result:**
- 8 tasks decomposed (database, auth, UIs, API, tracking, tests, docs)
- 3 models used (Mistral, Llama, Perplexity)
- Completed in ~45 minutes
- Full working application on GitHub

### Testing the Router

```bash
# Test decomposition and routing (dry run)
cd scripts
python3 orchestrator.py

# Test with custom request
python3 decomposer.py "Build a blog system with comments"

# Test routing for specific task
python3 router.py --test
```

---

## 🎓 How It Works

### 1. Task Decomposition

Analyzes your request and breaks into categorized subtasks:

```python
Request: "Build user registration with email verification"

Subtasks:
├─ Database schema (database-operations, complexity: 3)
├─ Registration API (api-development, complexity: 3)
├─ Email verification (backend-development, complexity: 4)
├─ Registration UI (frontend-development, complexity: 2)
└─ Unit tests (unit-test-generation, complexity: 3)
```

**Dependencies:** API depends on database, UI depends on API, tests depend on all

### 2. Intelligent Routing

Each task scored 0-100 against all models:

```
Example: API Development (complexity: 3)

Mistral Devstral 2512:
  Rating: 4★ (40 pts)
  Complexity fit: Can handle 3 (40 pts)
  Experience: 0 tasks (0 pts)
  Cost: Free tier (10 pts)
  Total: 90/100

Llama 3.3 70B:
  Rating: 4★ (40 pts)
  Complexity fit: Can handle 4 (40 pts)
  Experience: 2 tasks (2 pts)
  Cost: Free (10 pts)
  Total: 92/100 ✅ Winner
```

### 3. Parallel Execution

```
Worker Pool (max 5 concurrent):

Worker 1: Database schema (Mistral) → Running
Worker 2: Registration UI (Devstral) → Running
Worker 3: Tests (Llama) → Queued (waits for API)
Worker 4: -
Worker 5: -

After database completes:
Worker 1: Registration API (Llama) → Running

After API completes:
Worker 1: Tests (Llama) → Running
```

### 4. Result Consolidation

```bash
# After all tasks complete:
1. Check git status for conflicts → None
2. Run tests: npm test → ✅ Passed
3. Commit: "feat: user-registration - 5 tasks completed"
4. Push to github.com/{user}/user-registration
5. Report to Discord: "✅ Project completed!"
```

---

## 🔧 Configuration

### Agent Registry

`config/agent-registry.json`:

```json
{
  "user_config": {
    "cost_tracking_enabled": true,
    "prefer_free_when_equal": true,
    "max_parallel_tasks": 5,
    "fallback": {
      "enabled": true,
      "retry_delay_seconds": 2
    }
  },
  "agents": {
    "mistral-devstral-2512": {
      "model_id": "mistral/devstral-2512",
      "enabled": true,
      "user_cost": {
        "type": "free-tier"
      },
      "capabilities": {
        "frontend-development": {
          "rating": 5,
          "max_complexity": 5
        }
      }
    }
  }
}
```

### Task Categories (23 Standard)

- code-generation-new-features
- bug-detection-fixes
- multi-file-refactoring
- unit-test-generation
- api-development
- frontend-development
- backend-development
- database-operations
- security-fixes
- documentation-generation
- performance-optimization
- algorithm-implementation
- And more...

See [`config/task-categories.json`](config/task-categories.json)

---

## 📊 Supported Models

### Default Profiles

| Model | Provider | Cost | Best For |
|-------|----------|------|----------|
| **Mistral Devstral 2512** | Mistral | Free tier | Multi-file refactoring, frontend, 256K context |
| **Llama 3.3 70B** | OpenRouter | Free | Unit tests, algorithms, boilerplate |
| **Perplexity Sonar** | Perplexity | $1/M tokens | Research, documentation, exploration |
| **Claude Sonnet 4.5** | Anthropic | $3-15/M | Complex architecture (future) |
| **GPT-4 Turbo** | OpenAI | $10-30/M | General purpose (future) |

See [`config/defaults/`](config/defaults/) for all profiles.

---

## 🎯 Examples

### Example 1: Calculator

**Request:** Build a calculator with operations and tests

**Decomposition:**
- Task 1: Calculator logic (Llama)
- Task 2: UI components (Devstral)
- Task 3: Unit tests (Llama)

**Result:** 3 tasks, 8 minutes, pushed to GitHub

### Example 2: Blog API

**Request:** REST API for blog with auth and docs

**Decomposition:**
- Task 1: Database schema (Mistral)
- Task 2: Auth system (Mistral)
- Task 3: CRUD endpoints (Llama)
- Task 4: Swagger docs (Perplexity)
- Task 5: Integration tests (Llama)

**Result:** 5 tasks, 20 minutes, API-first design

### Example 3: Dispatch System

**Request:** Full towing dispatch with portals and tracking

**Decomposition:**
- Task 1: Database (Mistral)
- Task 2: Auth (Mistral)
- Task 3-5: UIs for customer/driver/admin (Devstral)
- Task 6: REST API (Llama)
- Task 7: Real-time tracking (Mistral)
- Task 8: Tests (Llama)

**Result:** 8 tasks, 45 minutes, full application

---

## 🔍 Advanced Features

### Conservative Fallback

If a task fails:
1. Try primary model (attempt 1)
2. Try primary model (attempt 2)
3. Try first runner-up (attempt 3)
4. Try first runner-up (attempt 4)
5. Give up, report to Discord

### File Conflict Detection

```
Task 1: Modify src/api/users.js → Running
Task 2: Modify src/api/users.js → Queued (waits)
Task 3: Modify src/ui/home.js → Running (independent)
```

### Multi-Project Concurrency

```
Project A: Dispatch System (3 tasks running)
Project B: Calculator (2 tasks running)
───────────────────────────────────────────
Total: 5 tasks (at global max_parallel_tasks)
```

---

## 📖 Documentation

- **[SKILL.md](SKILL.md)** - Complete usage guide for OpenClaw
- **[docs/orchestration-design.md](docs/orchestration-design.md)** - Architecture details
- **[examples/](examples/)** - Working examples with walkthroughs
- **[config/](config/)** - Configuration reference

---

## 🤝 Contributing

We welcome contributions!

1. **Share benchmark data** - Help improve capability ratings
2. **Add model profiles** - Support more AI models
3. **Improve decomposition** - Better task breakdown logic
4. **Report issues** - Help us fix bugs

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

---

## 📄 License

GNU AGPL v3 - See [`LICENSE`](LICENSE)

This copyleft license requires anyone running a modified version on a server to make source code available to users.

---

## 🙏 Acknowledgments

- Capability ratings from [SWE-bench](https://www.swebench.com/), [HumanEval](https://github.com/openai/human-eval), and real-world testing
- Built for the [OpenClaw](https://openclaw.ai) ecosystem
- Published on [ClawHub.ai](https://www.clawhub.ai/skills/claw-conductor)

---

## 🔗 Links

- **GitHub**: [johnsonfarmsus/claw-conductor](https://github.com/johnsonfarmsus/claw-conductor)
- **ClawHub**: [clawhub.ai/skills/claw-conductor](https://www.clawhub.ai/skills/claw-conductor)
- **OpenClaw Docs**: [openclaw.ai](https://openclaw.ai)

---

**Made with 🎼 for autonomous development**

*Stop manually coordinating AI models. Let the Conductor orchestrate.*
