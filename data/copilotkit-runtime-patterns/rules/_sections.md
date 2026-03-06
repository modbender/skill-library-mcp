# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Endpoint Setup (endpoint)

**Impact:** CRITICAL
**Description:** Correct endpoint configuration is required for CopilotKit to function. Misconfigured endpoints cause connection failures or broken streaming.

## 2. Agent Runners (runner)

**Impact:** HIGH
**Description:** Agent runners manage agent lifecycle and state persistence. Choosing the wrong runner causes data loss or memory leaks.

## 3. Middleware (middleware)

**Impact:** MEDIUM
**Description:** Middleware hooks for request/response processing. Used for auth, logging, context injection, and response modification.

## 4. Security (security)

**Impact:** HIGH
**Description:** Security patterns for production CopilotKit deployments. Unprotected endpoints expose your LLM and agent capabilities to abuse.

## 5. Performance (perf)

**Impact:** MEDIUM
**Description:** Optimization patterns for runtime performance, streaming, and resource management.
