# AI Agent Frameworks Comparison

## Quick Selection Matrix

| Framework | Best For | Learning Curve | Maturity |
|-----------|----------|----------------|----------|
| **LangChain** | Prototyping, many integrations | Medium | High |
| **LangGraph** | Complex stateful workflows | High | Medium |
| **AutoGen** | Multi-agent collaboration | Medium | High |
| **CrewAI** | Role-based agent teams | Low | Medium |
| **OpenAI Assistants** | Simple tool-use, managed infra | Low | High |
| **Anthropic Claude** | Direct API, MCP tools | Low | High |
| **Raw SDK** | Production, full control | Varies | N/A |

## Detailed Comparison

### LangChain
- **Philosophy:** Batteries-included, modular chains
- **Strengths:** Huge ecosystem, many integrations, good docs
- **Weaknesses:** Heavy for simple tasks, abstraction overhead
- **Use when:** Prototyping, need many integrations fast

### LangGraph
- **Philosophy:** Graph-based state machines for agents
- **Strengths:** Complex workflows, error recovery, state management
- **Weaknesses:** Steep learning curve, overkill for simple agents
- **Use when:** Long-running stateful agents, complex branching

### AutoGen (Microsoft)
- **Philosophy:** Multi-agent conversations
- **Strengths:** Async, human-in-loop, agent collaboration
- **Weaknesses:** Complex setup, still evolving
- **Use when:** Research, enterprise multi-agent systems

### CrewAI
- **Philosophy:** Role-based agent teams mimicking human orgs
- **Strengths:** Natural task division, easy to understand
- **Weaknesses:** Less mature, limited advanced features
- **Use when:** Business workflows, team-like agent structures

### OpenAI Assistants API
- **Philosophy:** Managed agent infrastructure
- **Strengths:** Simple, managed memory, built-in tools
- **Weaknesses:** Vendor lock-in, less customization
- **Use when:** Quick prototypes, don't want infrastructure

## Framework Selection Flowchart

```
Do you need multiple specialized agents?
├─ Yes → Do they need complex coordination?
│        ├─ Yes → LangGraph or AutoGen
│        └─ No → CrewAI
└─ No → Do you need many integrations quickly?
         ├─ Yes → LangChain
         └─ No → Do you want managed infrastructure?
                  ├─ Yes → OpenAI Assistants
                  └─ No → Raw SDK (OpenAI/Anthropic)
```

## Learning Path Recommendation

1. **Start with raw SDK** — Understand primitives (tool calls, streaming, context)
2. **Add LangGraph** — Learn state machines for complex flows
3. **Specialize** — Pick framework based on actual use case

## Framework-Agnostic Principles

Regardless of framework:
- **Keep prompts external** — Don't bury them in code
- **Make tools stateless** — Side effects should be predictable
- **Log everything** — Tool calls, decisions, errors
- **Test adversarially** — Prompt injection, edge cases
- **Monitor costs** — Token usage adds up fast
