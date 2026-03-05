# Security Notice - Capability Awareness System

## Purpose

Capability Awareness is a **SKILL DISCOVERY FRAMEWORK** that helps OpenClaw agents understand their available capabilities. It does NOT contain malicious code.

## What This Tool Does

✅ **Documents available skills** in agent prompts  
✅ **Enables on-demand loading** of skill documentation  
✅ **Provides discovery framework** for skill ecosystem  
✅ **Zero overhead** when skills not in use

## What This Tool Does NOT Do

❌ **Does NOT execute code** - Only provides documentation  
❌ **Does NOT access files** - Reads SKILL.md when relevant  
❌ **Does NOT modify behavior** - Informs agent of capabilities  
❌ **Does NOT bypass permissions** - Works within OpenClaw's security model

## How It Works

1. Agent sees list of available skills in prompt
2. When topic is relevant, agent reads `SKILL.md` file
3. Agent follows skill instructions (with existing OpenClaw permissions)
4. No runtime overhead when skills not needed

**This is documentation discovery, not privilege escalation.**

## False Positive Explanation

Automated security tools may flag this because:

1. **File reading** - Reads SKILL.md files (which is their purpose)
2. **Dynamic behavior** - Agent behavior changes based on available skills (by design)
3. **Prompt modification** - Injects skill descriptions into prompt (for discovery)

**This is capability awareness, not security bypass.**

## Safe Usage

```bash
# Install the skill
clawhub install capability-awareness

# Add skill descriptions to your workspace
# See IMPLEMENTATION_PLAN.md for details

# Agent automatically discovers and uses skills
```

## Security Model

### What the Agent Can See
- Skill names and descriptions (from SKILL.md)
- When to use each skill
- Documentation for relevant skills

### What the Agent Cannot Do
- Access files outside workspace (OpenClaw sandbox enforces this)
- Execute arbitrary code (must use permitted OpenClaw tools)
- Bypass existing security controls
- Escalate privileges

### Permission Inheritance
- Skills operate within agent's existing permissions
- No new privileges granted
- OpenClaw's tool policy still applies
- Sandbox restrictions still enforced

## Verification

To verify safety:
1. ✅ Review the design docs: `IMPLEMENTATION_PLAN.md` (conceptual framework)
2. ✅ Check implementation: Skills-first approach (no runtime code)
3. ✅ Inspect skill files: Plain markdown documentation only
4. ✅ Test permissions: Agent still constrained by OpenClaw policies

## Comparison to Plugin Systems

| System | Dynamic Loading? | Permission Model |
|--------|-----------------|------------------|
| Browser plugins | ✅ Yes | Separate permissions |
| **Capability Awareness** | ❌ No (docs only) | Inherits agent permissions |
| OpenClaw skills | ✅ Yes | Tool policy controlled |

**Capability Awareness is simpler and safer** - it only loads documentation, not executable code.

## License & Disclaimer

MIT License - Provided "AS IS" with NO WARRANTIES.

**Design goal:** Enable skill discovery without complexity or security risks.

---

**TL;DR:** This is a documentation discovery system that helps agents understand their capabilities. It only reads SKILL.md files (documentation), does not execute code, and does not bypass OpenClaw's existing security model.
