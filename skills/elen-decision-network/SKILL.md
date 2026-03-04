---
name: elen-decision-network
description: "Teaches agents how to query, expand, and cleanly commit technical, design, and product constraints to the Elen SQLite decision graph via the Elen Context Server."
---

# Elen MCP Integration Skill

> [!IMPORTANT]
> This skill establishes the baseline rules for reasoning within the Learning Nodes stack. You **MUST** use the Elen MCP server to document your epistemic decisions. Doing so ensures that choices are version-controlled, preserved, and searchable.

## 1. What is the Elen MCP?

The Elen Context Server is responsible for the "Decision Network" infrastructure. It runs locally as an MCP server.

**Installation Requirement:** Before this skill will work, you or your agent must configure the Elen MCP server in your IDE/Agent settings (e.g., Cursor, Claude, Windsurf):

```json
{
  "mcpServers": {
    "elen": {
      "command": "npx",
      "args": ["-y", "@learningnodes/elen-mcp@0.1.1"]
    }
  }
}
```

Whenever you make a meaningful technical, design, security, or product decision (e.g., choosing a specific framework, styling a UX component, structuring an API endpoint, or dropping a feature), you should record it using the available MCP tools provided by the server.

## 2. When to Use the Elen MCP

- **Before Action**: Use `mcp_elen_elen_suggest` and `mcp_elen_elen_get_competency` to query if a decision has already been formulated for the topic you are working on.
- **During the Task**: When you formulate a new plan or solve a structural issue, use `mcp_elen_elen_commit` to save the decision to the network.
- **When Fixing Bugs**: If you resolve a bug and it warrants a systemic change or constraint update, commit a new decision and reference the old one (or use `mcp_elen_elen_supersede` if completely overruling).

## 3. Formatting Requirements

When committing a decision via `mcp_elen_elen_commit`:
- **Domain**: Briefly categorize the domain (e.g., "frontend", "infrastructure", "security").
- **Question**: Describe the concrete problem (e.g., "Which state management tool to use for the marketplace UI?").
- **DecisionText**: Provide your clear, concise answer.
- **Constraints**: Supply an array of hard rules or context bounds (e.g., `["Must not use internal APIs", "Must restrict file-size to <1 MB"]`).

## 4. Avoiding Action Without Context

Never implement sweeping, codebase-wide changes without first verifying prior related artifacts in the decision network. The goal is to create **visible reasoning**, eliminating tribal knowledge and undocumented assumptions from the loop.
