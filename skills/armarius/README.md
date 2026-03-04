# Armarius — OpenClaw Skill

**Cryptographic prompt injection prevention for AI agents.**

This skill teaches your OpenClaw agent how to integrate [Armarius](https://github.com/tatlantis/armarius)
into Python-based agent workflows — protecting them from prompt injection at the
architectural level through Ed25519 cryptographic verification.

## What It Does

When you ask your agent about prompt injection, securing tool outputs, or protecting
against hijacking via emails/web pages/documents, this skill activates and guides
you through integrating Armarius.

## Supported Frameworks

- Any Python agent (decorator pattern)
- LangChain (`ShieldedAgentExecutor`, `shield_tools`)
- AutoGen / OpenAI Agents SDK adapters — coming soon

## Requirements

- Python ≥ 3.9
- `pip install armarius` (installs PyNaCl automatically)

## Quick Test

```bash
pip install armarius
git clone https://github.com/tatlantis/armarius
python armarius/demo/simple_agent.py
```

## Author

Created by [Fred Giovannitti](https://github.com/tatlantis).
Built in collaboration with Claude (Anthropic).

## Links

- GitHub: https://github.com/tatlantis/armarius
- Issues: https://github.com/tatlantis/armarius/issues
- License: MIT
