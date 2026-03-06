---
name: agent-self-governance
description: "Self-governance protocol for autonomous agents: WAL (Write-Ahead Log), VBR (Verify Before Reporting), ADL (Anti-Divergence Limit), VFM (Value-For-Money), and IKL (Infrastructure Knowledge Logging). Use when: (1) receiving a user correction — log it before responding, (2) making an important decision or analysis — log it before continuing, (3) pre-compaction memory flush — flush the working buffer to WAL, (4) session start — replay unapplied WAL entries to restore lost context, (5) any time you want to ensure something survives compaction, (6) before claiming a task is done — verify it, (7) periodic self-check — am I drifting from my persona? (8) cost tracking — was that expensive operation worth it? (9) discovering infrastructure — log hardware/service specs immediately."
---

# Agent Self-Governance

Five protocols that prevent agent failure modes: losing context, false completion claims, persona drift, wasteful spending, and infrastructure amnesia.

## 1. WAL (Write-Ahead Log)

**Rule: Write before you respond.** If something is worth remembering, WAL it first.

| Trigger | Action Type | Example |
|---------|------------|---------|
| User corrects you | `correction` | "No, use Podman not Docker" |
| Key decision | `decision` | "Using CogVideoX-2B for text-to-video" |
| Important analysis | `analysis` | "WAL patterns should be core infra not skills" |
| State change | `state_change` | "GPU server SSH key auth configured" |

```bash
# Write before responding
python3 scripts/wal.py append <agent_id> correction "Use Podman not Docker"

# Working buffer (batch, flush before compaction)
python3 scripts/wal.py buffer-add <agent_id> decision "Some decision"
python3 scripts/wal.py flush-buffer <agent_id>

# Session start: replay lost context
python3 scripts/wal.py replay <agent_id>

# After incorporating a replayed entry
python3 scripts/wal.py mark-applied <agent_id> <entry_id>

# Maintenance
python3 scripts/wal.py status <agent_id>
python3 scripts/wal.py prune <agent_id> --keep 50
```

### Integration Points
- **Session start** → `replay` to recover lost context
- **User correction** → `append` BEFORE responding
- **Pre-compaction flush** → `flush-buffer` then write daily memory
- **During conversation** → `buffer-add` for less critical items

## 2. VBR (Verify Before Reporting)

**Rule: Don't say "done" until verified.** Run a check before claiming completion.

```bash
# Verify a file exists
python3 scripts/vbr.py check task123 file_exists /path/to/output.py

# Verify a file was recently modified
python3 scripts/vbr.py check task123 file_changed /path/to/file.go

# Verify a command succeeds
python3 scripts/vbr.py check task123 command "cd /tmp/repo && go test ./..."

# Verify git is pushed
python3 scripts/vbr.py check task123 git_pushed /tmp/repo

# Log verification result
python3 scripts/vbr.py log <agent_id> task123 true "All tests pass"

# View pass/fail stats
python3 scripts/vbr.py stats <agent_id>
```

### When to VBR
- After code changes → `check command "go test ./..."`
- After file creation → `check file_exists /path`
- After git push → `check git_pushed /repo`
- After sub-agent task → verify the claimed output exists

## 3. ADL (Anti-Divergence Limit)

**Rule: Stay true to your persona.** Track behavioral drift from SOUL.md.

```bash
# Analyze a response for anti-patterns
python3 scripts/adl.py analyze "Great question! I'd be happy to help you with that!"

# Log a behavioral observation
python3 scripts/adl.py log <agent_id> anti_sycophancy "Used 'Great question!' in response"
python3 scripts/adl.py log <agent_id> persona_direct "Shipped fix without asking permission"

# Calculate divergence score (0=aligned, 1=fully drifted)
python3 scripts/adl.py score <agent_id>

# Check against threshold
python3 scripts/adl.py check <agent_id> --threshold 0.7

# Reset after recalibration
python3 scripts/adl.py reset <agent_id>
```

### Anti-Patterns Tracked
- **Sycophancy** — "Great question!", "I'd be happy to help!"
- **Passivity** — "Would you like me to", "Shall I", "Let me know if"
- **Hedging** — "I think maybe", "It might be possible"
- **Verbosity** — Response length exceeding expected bounds

### Persona Signals (Positive)
- **Direct** — "Done", "Fixed", "Ship", "Built"
- **Opinionated** — "I'd argue", "Better to", "The right call"
- **Action-oriented** — "Spawning", "On it", "Kicking off"

## 4. VFM (Value-For-Money)

**Rule: Track cost vs value.** Don't burn premium tokens on budget tasks.

```bash
# Log a completed task with cost
python3 scripts/vfm.py log <agent_id> monitoring glm-4.7 37000 0.03 0.8

# Calculate VFM scores
python3 scripts/vfm.py score <agent_id>

# Cost breakdown by model and task
python3 scripts/vfm.py report <agent_id>

# Get optimization suggestions
python3 scripts/vfm.py suggest <agent_id>
```

### Task → Tier Guidelines
| Task Type | Recommended Tier | Models |
|-----------|-----------------|--------|
| Monitoring, formatting, summarization | Budget | GLM, DeepSeek, Haiku |
| Code generation, debugging, creative | Standard | Sonnet, Gemini Pro |
| Architecture, complex analysis | Premium | Opus, Sonnet+thinking |

### When to Check VFM
- After spawning sub-agents → log cost and outcome
- During heartbeat → run `suggest` for optimization tips
- Weekly review → run `report` for cost breakdown

## 5. IKL (Infrastructure Knowledge Logging)

**Rule: Log infrastructure facts immediately.** When you discover hardware specs, service configs, or network topology, write it down BEFORE continuing.

### Triggers
| Discovery Type | Log To | Example |
|----------------|--------|---------|
| Hardware specs | TOOLS.md | "GPU server has 3 GPUs: RTX 3090 + 3080 + 2070 SUPER" |
| Service configs | TOOLS.md | "ComfyUI runs on port 8188, uses /data/ai-stack" |
| Network topology | TOOLS.md | "Pi at 192.168.99.25, GPU server at 10.0.0.44" |
| Credentials/auth | memory/encrypted/ | "SSH key: ~/.ssh/id_ed25519_alexchen" |
| API endpoints | TOOLS.md or skill | "Moltbook API: POST /api/v1/posts" |

### Commands to Run on Discovery
```bash
# Hardware discovery
nvidia-smi --query-gpu=index,name,memory.total --format=csv
lscpu | grep -E "Model name|CPU\(s\)|Thread"
free -h
df -h

# Service discovery  
systemctl list-units --type=service --state=running
docker ps  # or podman ps
ss -tlnp | grep LISTEN

# Network discovery
ip addr show
cat /etc/hosts
```

### The IKL Protocol
1. **SSH to new server** → Run hardware/service discovery commands
2. **Before responding** → Update TOOLS.md with specs
3. **New service discovered** → Log port, path, config location
4. **Credentials obtained** → Encrypt and store in memory/encrypted/

### Anti-Pattern: "I'll Remember"
❌ "The GPU server has 3 GPUs" (only in conversation)
✅ "The GPU server has 3 GPUs" → Update TOOLS.md → then continue

**Memory is limited. Files are permanent. IKL before you forget.**
