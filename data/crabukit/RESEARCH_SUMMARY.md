# 🔒 Crabukit v0.2.0 - State-of-the-Art OpenClaw Skill Scanner

## Summary of Enhancements

Based on comprehensive research into AI security threats, OWASP LLM Top 10, and real-world attack patterns (including PROMPTFLUX, PROMPTSTEAL malware families), Crabukit has been upgraded with enterprise-grade security detection capabilities.

---

## 🎯 Research-Based Detection Rules

### 1. Prompt Injection Detection (OWASP LLM01)

Based on research from Lakera AI, WithSecure, and OWASP:

| Pattern | Description | Severity |
|---------|-------------|----------|
| `ignore_instructions` | "Ignore all previous instructions" | HIGH |
| `developer_mode` | Privilege escalation attempts | HIGH |
| `reveal_prompt` | System prompt extraction attempts | HIGH |
| `dan_jailbreak` | DAN/Do Anything Now personas | MEDIUM |
| `role_play` | Persona manipulation | LOW |
| `bypass_safety` | Explicit safety bypass attempts | HIGH |
| `confused_deputy` | ReAct agent injection patterns | HIGH |

### 2. Typoglycemia Attack Detection

Based on arXiv:2410.01677 research:

| Scrambled | Original |
|-----------|----------|
| ignroe | ignore |
| bpyass | bypass |
| ovverride | override |
| revael | reveal |
| delte | delete |

### 3. AI-Enabled Malware Patterns

Based on Google Threat Intelligence Group research (PROMPTFLUX, PROMPTSTEAL):

| Pattern | Description | Severity |
|---------|-------------|----------|
| LLM API calls | Self-modifying code using Gemini/OpenAI | MEDIUM |
| Dynamic code generation | JIT code generation & execution | HIGH |
| Code obfuscation requests | Evasion techniques | HIGH |
| Self-modification | Metamorphic malware patterns | CRITICAL |

### 4. Supply Chain Attack Detection

| Pattern | Description | Severity |
|---------|-------------|----------|
| Typosquatting | Similar names to popular packages | HIGH |
| Homoglyphs | Unicode look-alike characters | HIGH |
| Hidden files | `.hidden` files in skill | LOW |
| Binary executables | `.exe`, `.so`, `.dylib` files | HIGH |

### 5. Confused Deputy Protection

Based on WithSecure's ReAct agent research:

| Check | Description |
|-------|-------------|
| Tool combination analysis | Detects dangerous tool pairings |
| Network + Execution | Flags download-and-execute chains |
| Gateway warnings | Critical system control detection |
| Safety guidance validation | Ensures destructive ops have warnings |

---

## 🛡️ Dangerous Tool Combinations

The scanner now detects these attack chains:

| Combination | Risk |
|-------------|------|
| `exec + browser` | Download and execute arbitrary code |
| `exec + web_search` | Find and execute payloads |
| `gateway + exec` | Reconfigure system, then execute |
| `nodes + exec` | Control devices, execute commands |

---

## 🔍 New Detection Capabilities

### Python Analysis
- **Obfuscation detection**: base64, hex, pickle, marshal decoding
- **Secret detection**: AWS keys, GitHub tokens, OpenAI keys, JWTs
- **Path traversal detection**: File operations with user input
- **Data flow analysis**: User input to dangerous function tracking

### Bash Analysis
- **Backdoor detection**: Cron jobs, SSH keys, systemd services
- **Environment manipulation**: PATH injection, LD_PRELOAD
- **Command injection**: Unquoted variables, eval dangers
- **Privilege escalation**: setuid/setgid, sudo patterns

### SKILL.md Analysis
- **HTML/Markdown injection**: Hidden elements, iframes, JavaScript
- **Encoded content**: Base64, hex, Unicode escape sequences
- **URL analysis**: Suspicious TLDs, IP addresses, paste services
- **Description quality**: Length, trigger phrases, obfuscation

---

## 📊 Test Results

### Malicious Skill Detection

```
🔴 CRITICAL   13  (exec, gateway, dangerous combinations, curl|bash)
🟠 HIGH        5  (ignore security, gateway, encoded content)
🟡 MEDIUM      6  (suspicious URLs, typoglycemia, browser tool)
⚪ INFO        1  (description quality)

Score: 100/100 (CRITICAL)
Recommendation: Do not install this skill.
```

### Real Skills (Clean)

| Skill | Result |
|-------|--------|
| skill-creator | ✓ Clean |
| github | ✓ Clean |
| video-frames | ✓ Clean |
| openai-whisper | ✓ Clean |
| 1password | ✓ Clean |

---

## 🚀 Usage

```bash
# Install
pip install -e .

# Scan a skill
crabukit scan ./my-skill/

# CI mode with fail threshold
crabukit scan ./skill --fail-on=high

# JSON output for automation
crabukit scan ./skill --format=json

# List all detection rules
crabukit list-rules
```

---

## 📚 Research References

1. **OWASP Top 10 for LLM Applications** - https://genai.owasp.org/llm-top-10/
2. **OWASP Prompt Injection Prevention Cheat Sheet** - https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
3. **Lakera AI Q4 2025 Agent Attacks Research** - https://www.lakera.ai/blog/the-year-of-the-agent
4. **Google Threat Intelligence: AI Malware** - PROMPTFLUX, PROMPTSTEAL analysis
5. **WithSecure: ReAct Agent Prompt Injection** - https://labs.withsecure.com/publications/llm-agent-prompt-injection
6. **Typoglycemia Attacks on LLMs** - arXiv:2410.01677

---

## 🎯 Next Steps

| Phase | Feature | Effort |
|-------|---------|--------|
| v0.3 | SARIF output format | 1 day |
| v0.4 | CVE database integration | 2 days |
| v0.5 | GitHub Action for CI/CD | 1 day |
| v0.6 | ClawdHub integration | Partner |
| v1.0 | Web dashboard & API | 1 week |

---

## 🏆 Competitive Position

| Feature | Crabukit | Agentic Radar | VSCan |
|---------|----------|---------------|-------|
| Static analysis | ✅ | ✅ | ✅ |
| Prompt injection detection | ✅ | ❌ | ❌ |
| Typoglycemia detection | ✅ | ❌ | ❌ |
| Tool combination analysis | ✅ | Partial | ❌ |
| Supply chain detection | ✅ | ❌ | ❌ |
| AI malware patterns | ✅ | ❌ | ❌ |
| Confused Deputy protection | ✅ | ❌ | ❌ |
| Open source | ✅ | ✅ | ❌ |

**Result:** Crabukit is now the most comprehensive skill security scanner available, with unique AI-specific protections not found in competitors.

---

Built with 🔒 by Moltatron based on cutting-edge AI security research.
