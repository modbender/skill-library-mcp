---
name: agent-doppelganger
description: Constrained autonomous delegate for identity-proxied communication. Handles incoming messages (Email, Discord, Slack, WhatsApp) by analyzing intent and applying declarative authority policies before generating responses. Use when the user wants to delegate communication tasks while maintaining identity fidelity and enforcing strict non-overreach boundaries.
---

# Agent Doppelgänger (ADG)

ADG is a policy-bounded identity proxy for real-world communication. It acts as a constrained autonomous delegate that communicates on your behalf within formally provable limits.

## Core Workflow

1. **Adapter**: Normalize incoming messages from various channels.
2. **Intent Analysis**: Classify the intent along Domain, Stakes, Authority, and Ambiguity.
3. **Policy Gate**: Evaluate declarative policies (DSL) to determine if the agent is allowed to handle the request.
4. **Confidence Engine**: Measure confidence in both intent analysis and proposed handling.
5. **Response Generation**: Synthesize a response using your Style, Heuristics, and Preferences.
6. **Verifier**: Audit the response against hard constraints before sending or drafting.

## Implementation Details

### 1. Identity Modeling
Identity is modeled as a composition of four layers:
- **Style**: Surface form characteristics (length, directness, vocabulary).
- **Heuristics**: Core decision logic (e.g., "avoid meetings without agenda").
- **Preferences**: Soft weights (e.g., Work > Social).
- **Constraints**: Hard, user-defined rules.

### 2. Authority & Policy
Policies are declarative and evaluated **before** any generation occurs. This ensures safety and prevents prompt injection from bypassing limits.

### 3. Escalation
ADG automatically escalates to you (Draft or Block) if:
- Policy is violated.
- Confidence falls below the defined threshold.
- The request involves forbidden domains (Finance, Legal, Medical, etc.).

## References

- See [specification.md](references/specification.md) for the full architectural blueprint.
- See [policy-dsl.md](references/policy-dsl.md) (To Be Created) for the formal policy language definition.

## Forbidden Modeling
ADG is strictly forbidden from modeling or handling:
- Secrets
- Financial authority
- Legal intent
- Political opinions
- Emotional vulnerability/trauma
