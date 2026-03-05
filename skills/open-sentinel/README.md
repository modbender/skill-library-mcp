# open-sentinel (ClawHub Skill)

Transparent LLM proxy that monitors and enforces policies on AI agent behavior — evaluates responses for hallucinations, PII leaks, prompt injection, and policy violations.

## What It Does

Open Sentinel sits between your application and any LLM provider, evaluating every response against rules you define in plain English before output reaches users or downstream logic. It works as a transparent proxy for any OpenAI-compatible client.

Key capabilities:
- Policy enforcement with plain-English rules
- Hallucination detection and factual grounding scores
- PII / credential leak prevention
- Prompt injection defense
- Multi-turn workflow enforcement (FSM engine)
- Async evaluation (zero critical-path latency in default mode)

## How to Use

**1. Install**
```bash
pip install opensentinel
```

**2. Set up**
```bash
export ANTHROPIC_API_KEY=sk-ant-...   # or OPENAI_API_KEY, GEMINI_API_KEY
osentinel init --quick                # creates starter osentinel.yaml
osentinel serve                       # starts proxy on localhost:4000
```

**3. Point your client at the proxy**
```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key=os.environ.get("ANTHROPIC_API_KEY", "dummy-key")
)
```

Every call now runs through your policy. Zero code changes needed.

## Requirements

- Python 3.10+
- At least one LLM provider API key: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `GEMINI_API_KEY`

## CLI Commands

```bash
osentinel init              # interactive setup
osentinel init --quick      # non-interactive defaults
osentinel serve             # start proxy
osentinel compile <desc>    # compile natural language to engine config
osentinel validate <file>   # validate workflow/config file
osentinel info <file>       # show workflow details
osentinel version           # show version
```

## Troubleshooting

- **Port conflict**: use `osentinel serve -p 4001`
- **No API key**: export at least one supported provider key
- **Policy not firing**: try `--debug` flag or set `mode: aggressive` in config

## Links

- GitHub: https://github.com/open-sentinel/open-sentinel
- PyPI: https://pypi.org/project/opensentinel
- Docs: https://github.com/open-sentinel/open-sentinel/tree/main/docs
- Issues: https://github.com/open-sentinel/open-sentinel/issues
- License: Apache 2.0
