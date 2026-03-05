# Security Notice for Grago

## ⚠️ INTENTIONAL DESIGN: Command Execution is the Feature

Grago uses `eval` to execute shell commands. This is **not a bug** — it's the core functionality.

### Why This Exists

Local LLMs (Ollama, llama.cpp, etc.) **cannot use tools natively**. They can't fetch URLs, call APIs, or run shell commands. Grago bridges that gap by:

1. Accepting shell commands from your OpenClaw agent
2. Executing them in your local environment  
3. Piping results to your local LLM for analysis

**Without command execution, Grago cannot function.**

### The Trade-Off

**Risk:** If your OpenClaw agent is prompt-injected or compromised, Grago can execute arbitrary commands on your machine.

**Mitigation:**
- Grago is designed for **trusted, single-user environments** (your own Mac Mini, VPS, or workstation)
- It's meant for agents YOU control, not public-facing bots
- The threat model assumes your OpenClaw agent is trustworthy

### Not Suitable For

❌ Multi-tenant environments  
❌ Public-facing agent APIs  
❌ Untrusted agents  
❌ Shared systems with sensitive data  

### Suitable For

✅ Your personal Mac Mini running OpenClaw 24/7  
✅ A dedicated research VPS for your agent  
✅ Self-hosted environments where you control the agent  
✅ Developers who understand the security model  

## Comparison to Other Tools

**Grago is no more dangerous than:**
- SSH access to your own machine
- Running shell scripts you wrote
- Using curl/jq/grep manually
- Any OpenClaw skill that uses `exec`

**The difference:** Grago automates what you'd do manually, delegating it to a local LLM.

## ClawHub Scanner Findings

ClawHub's automated scanner correctly identifies:
1. Shell injection via `eval` on user input ✅ **Correct**
2. Arbitrary file read via `sources.yaml` ✅ **Correct**
3. Prompt injection risk ✅ **Correct**

**These are all true.** They're also all intentional.

## If You're Uncomfortable

If this security model doesn't fit your environment:
- Don't install Grago
- Use paid API services instead (OpenAI, Anthropic, etc.)
- Wait for local models to get native tool support

Grago is for power users who want to leverage local compute and accept the trade-offs.

---

**TL;DR:** Grago executes shell commands. That's the point. If you trust your OpenClaw agent and control your environment, it's safe. If not, don't use it.
