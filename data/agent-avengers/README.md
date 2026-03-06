# Agent Avengers

🦸 **All-in-One Multi-Agent Orchestration**

> [한국어 README](./README-kr.md)

## Installation

```bash
clawhub install agent-avengers
```

Or clone directly:
```bash
git clone https://github.com/oozoofrog/agent-avengers.git ~/.openclaw/workspace/skills/agent-avengers
```

## Usage

```
Avengers assemble! [complex task description]
```

## Examples

```
Avengers assemble! Analyze competitors A, B, and C, then create a comparison report
```

```
Avengers assemble! Build a full-stack todo app with React frontend and Node.js backend
```

## How It Works

1. **Decompose** — Break down the task into subtasks
2. **Compose** — Assign specialized agents to each subtask
3. **Execute** — Run in parallel or sequential order
4. **Consolidate** — Collect and merge results
5. **Report** — Deliver final output

## Agent Types

| Type | Role |
|------|------|
| 🔬 Researcher | Investigation, data collection |
| 🔍 Analyst | Analysis, pattern discovery |
| 🖊️ Writer | Documentation, content creation |
| 💻 Coder | Code implementation |
| ✅ Reviewer | Quality review |
| 🔧 Integrator | Result consolidation |

## Agent Modes

| Mode | Description |
|------|-------------|
| 🔷 Existing | Use registered agents (watson, picasso, etc.) |
| 🔶 Spawned | Create one-off sub-agents on demand |
| 🟣 Multi-Profile | Involve other OpenClaw bot instances |
| 🔷🔶🟣 Hybrid | Combine all modes (recommended) |

## Emergent Collaboration Patterns

- 🗳️ **Competitive Draft** — Multiple agents work independently, best solution wins
- 🎭 **Role Rotation** — Agents swap roles each round
- ⚔️ **Adversarial Collaboration** — Creator vs Critic iterations
- 🧬 **Evolutionary Selection** — Solutions crossbreed and evolve
- 🐝 **Swarm Intelligence** — Many micro-agents tackle small chunks
- 🔗 **Chain Relay** — Output → Input chaining
- 💭 **Consensus Protocol** — Unanimous agreement required
- 🎪 **Cross-Domain Jam** — Combine different expertise areas
- 🪞 **Meta Observer** — Agent watches and coaches the team
- ⏰ **Temporal Split** — Short/mid/long-term parallel approaches
- 🎰 **Task Auction** — Confidence-based bidding
- 🧠 **Shared Memory** — Real-time discovery sharing

## Configuration

`avengers.yaml`:
```yaml
maxAgents: 5
timeoutMinutes: 120
retryCount: 2
defaultModel: sonnet
```

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/assemble.py` | Task decomposition & plan generation |
| `scripts/execute.py` | Generate execution commands |
| `scripts/monitor.py` | Progress monitoring (supports --watch) |
| `scripts/consolidate.py` | Result consolidation |

## License

MIT
