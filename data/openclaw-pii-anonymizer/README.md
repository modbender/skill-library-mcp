# OpenClaw PII Anonymizer Protocol

## Overview
Scrubs sensitive data before external LLM calls. Integrates with OpenClaw tools (memory_search, exec, web_search).

## Quick Start
1. `ollama pull phi3:mini`
2. `chmod +x privacy-anonymize.sh`
3. `./privacy-anonymize.sh "Test [PII]"`

## OpenClaw Hooks
- Prepend to tool calls: `anonymized=\$(./privacy-anonymize.sh \"\$query\")`
- HEARTBEAT.md: Sanitize MEMORY.md snippets.

## VM/Host
- VM: `OLLAMA_URL=http://localhost:11434`
- Host Ollama: `OLLAMA_URL=http://10.0.2.2:11434`

## License
MIT - Free for OpenClaw community.
