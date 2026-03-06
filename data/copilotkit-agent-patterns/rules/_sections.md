# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Agent Architecture (architecture)

**Impact:** CRITICAL
**Description:** Fundamental patterns for structuring agents that integrate with CopilotKit. Correct architecture prevents infinite loops, model misconfiguration, and tool registration failures.

## 2. AG-UI Protocol (agui)

**Impact:** HIGH
**Description:** Rules for correctly implementing the AG-UI event protocol. Incorrect event ordering or missing events causes broken streaming, lost messages, or UI desync.

## 3. State Management (state)

**Impact:** HIGH
**Description:** Patterns for synchronizing state between agent and frontend. Bidirectional state sync is CopilotKit's core differentiator.

## 4. Human-in-the-Loop (hitl)

**Impact:** MEDIUM
**Description:** Patterns for pausing agent execution to request user input, approval, or corrections before continuing.

## 5. Generative UI Emission (genui)

**Impact:** MEDIUM
**Description:** Rules for emitting tool calls and events that render dynamic UI components in the frontend.
