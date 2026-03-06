---
name: symbolic-memory
description: Stateless symbolic memory effect for LLM agents using SQL facts + canonical semantics, activated via symbols and JIT meaning (PostgreSQL + Ollama).
metadata: {"openclaw":{"emoji":"🧠","homepage":"https://github.com/Th3Hypn0tist/random/blob/main/LLM-symbolic-memory.md","requires":{"bins":["psql","python3"],"env":["PG_DSN","OLLAMA_HOST","OLLAMA_MODEL"],"config":[]}}}
user-invocable: true
version: 1.0
---

# symbolic-memory

## Purpose

Provide a stateless symbolic memory workflow:
- Store facts + canonical semantics in PostgreSQL
- Expose references as symbols
- Activate meaning just-in-time (budgeted)
- Send only activated facts to the LLM (Ollama)

Rule:
Store semantics. Compute meaning. Never confuse the two.

NOTE

This skill does not rely on agent-local persistent memory for long-term state.

Durable knowledge is stored in a shared, versioned symbolic memory substrate
(as defined in the JIT Symbolic Memory design pattern).

The skill may operate without symbolic memory, but long-term coherence
and multi-agent consistency are only guaranteed when it is present.

## Design pattern

https://github.com/Th3Hypn0tist/random/blob/main/jit-symbolic-memory-design-pattern
