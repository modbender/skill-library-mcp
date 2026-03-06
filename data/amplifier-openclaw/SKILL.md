---
name: amplifier-openclaw
description: "Delegate complex tasks to Amplifier's multi-agent framework. Use when: (1) research/comparison needing multiple perspectives, (2) multi-file code projects, (3) architecture/design reviews, (4) user asks for deep/thorough work. NOT for: simple Q&A, quick edits, casual chat, anything needing <5s response. CLI: amplifier-openclaw."
metadata:
  {
    "openclaw":
      {
        "emoji": "⚡",
        "requires": { "bins": ["amplifier-openclaw"] },
        "install":
          [
            {
              "id": "uv",
              "kind": "uv",
              "package": "amplifier-app-openclaw @ git+https://github.com/microsoft/amplifier-app-openclaw@v1.0.5",
              "bins": ["amplifier-openclaw"],
              "label": "Install Amplifier OpenClaw integration (uv)",
            },
          ],
      },
  }
---

# Amplifier — Multi-Agent Delegation

Amplifier is a multi-agent AI framework. Delegate tasks that benefit from specialist agents, structured workflows, or parallel investigation.

## When to Delegate

**High confidence → delegate immediately:**
- "Research X and compare approaches"
- "Build a Python tool that does X"
- "Review this code for security and design"
- User says "amplifier", "deep dive", "thorough", "comprehensive"
- Task has clear subtasks benefiting from parallel agents

**Medium confidence → offer the choice:**
- "I can do a quick analysis, or delegate to Amplifier for a thorough multi-agent review."

**Low confidence → handle yourself:**
- Simple Q&A, quick code edits, casual conversation, anything needing immediate response

## Usage

### Basic Delegation

```bash
exec command:"amplifier-openclaw run 'Research the top 3 Python web frameworks' --bundle foundation" background:true timeout:600
```

### With Model Selection

Pass `--model` to override the default model:

```bash
exec command:"amplifier-openclaw run --model your-preferred-model 'Deep code review' --bundle foundation" background:true timeout:600
```

**Tip:** Pass `--model` matching the model from your OpenClaw Runtime line so Amplifier uses the same one.


### Bundles

```bash
amplifier-openclaw bundles list
```

| Bundle | Best For |
|--------|----------|
| `foundation` | General: research, analysis, planning (default) |
| `superpowers` | Multi-agent brainstorm, deep investigation |
| `coder` | Code generation, refactoring, debugging |

### Session Persistence

```bash
# Start a named session
exec command:"amplifier-openclaw run --session-name my-project 'Start building the auth module' --bundle foundation" background:true

# Resume later
exec command:"amplifier-openclaw run --resume --session-name my-project 'Now add unit tests'" background:true
```

### Modes

Amplifier supports slash-command modes in prompts. **Modes do not carry over between runs** — include the mode at the start of each prompt:

```bash
# Brainstorm mode (uses all agents)
exec command:"amplifier-openclaw run --bundle superpowers '/brainstorm How should we architect the new API?'" background:true

# Research mode
exec command:"amplifier-openclaw run --bundle foundation '/research Latest advances in RAG'" background:true
```

## JSON Output

```json
{
  "response": "The analysis found...",
  "usage": {
    "input_tokens": 28566,
    "output_tokens": 1800,
    "estimated_cost": 0.12,
    "tool_invocations": 3
  },
  "status": "completed"
}
```

## Cost Tracking

```bash
exec command:"amplifier-openclaw cost --period week"
```

Report costs only when asked or when notable (>$1).

## Interpreting Results

- **`response`**: Present to the user (the main output)
- **`error`**: Report in plain language, don't dump raw JSON
- **`usage.estimated_cost`**: May be `0.0` — don't alarm about zero
- **`status`**: "completed", "cancelled", or error state

## During Active Delegation

- **"stop"/"cancel"** → kill the background process
- **Unrelated questions** → answer yourself, don't interrupt Amplifier
- **Follow-up** → tell user you'll pass it along when current task finishes

## Install

If not already installed:

```bash
uv tool install "amplifier-app-openclaw @ git+https://github.com/microsoft/amplifier-app-openclaw@v1.0.5"
```
