# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Provider Setup (provider)

**Impact:** CRITICAL
**Description:** Correct `CopilotKit` provider configuration is the foundation. Misconfiguration causes silent failures, broken agent connections, or degraded performance.

## 2. Agent Hooks (agent)

**Impact:** HIGH
**Description:** Patterns for useAgent (v2), useFrontendTool (v2), useCopilotReadable (v1), and useCopilotAction (v1). Incorrect usage causes re-render storms, stale state, or broken agent interactions.

## 3. Tool Rendering (tool)

**Impact:** HIGH
**Description:** Rules for rendering agent tool calls in the UI. Proper tool rendering is what makes CopilotKit's generative UI possible.

## 4. Context & State (state)

**Impact:** MEDIUM
**Description:** Patterns for providing context to agents and managing shared state. Good context = good agent responses.

## 5. Chat UI (ui)

**Impact:** MEDIUM
**Description:** Rules for configuring and customizing CopilotChat, CopilotSidebar, and CopilotPopup components.

## 6. Suggestions (suggestions)

**Impact:** LOW
**Description:** Patterns for configuring proactive suggestions that help users discover agent capabilities.
