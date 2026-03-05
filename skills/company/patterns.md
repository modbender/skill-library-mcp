# Organizational Patterns for Agent Companies

## Hub and Spoke

```
                    [Orchestrator]
                    /     |     \
               [Sales] [Ops] [Support]
```

**How it works:**
- One orchestrator agent routes work to specialists
- Clear escalation path (specialist → orchestrator → human)
- Simple to debug and monitor

**Best for:**
- Small teams (1-5 people)
- Clear, linear workflows
- Starting point for most companies

**Evolve when:** Orchestrator becomes bottleneck, specialists need to talk directly.

## Mesh Network

```
    [Sales] ←→ [Ops]
       ↕         ↕
  [Support] ←→ [Finance]
```

**How it works:**
- Agents communicate directly as needed
- No central routing
- Each agent knows when to involve others

**Best for:**
- Complex interdependencies
- High-volume parallel work
- Mature agent implementations

**Risk:** Harder to trace decisions, need good logging.

## Hierarchical

```
              [CEO Agent]
              /         \
     [Sales Mgr]    [Ops Mgr]
      /    \          /    \
  [SDR] [AE]    [Coord] [Proc]
```

**How it works:**
- Manager agents oversee worker agents
- Delegation follows org chart
- Managers aggregate and escalate

**Best for:**
- Large-scale operations
- Clear reporting needs
- When humans mirror the structure

**Risk:** Slow for urgent cross-functional issues.

## Choosing a Pattern

| If you have... | Start with... |
|----------------|---------------|
| <5 functions | Hub and spoke |
| Lots of handoffs | Mesh (carefully) |
| Scale/compliance needs | Hierarchical |
| Uncertainty | Hub and spoke, evolve |

## Evolution Signals

**Time to evolve from Hub to Mesh:**
- Orchestrator response time increasing
- Specialists waiting on routing
- Cross-functional work is common

**Time to evolve from Mesh to Hierarchical:**
- Audit trails getting complex
- Need manager-level decisions
- Human oversight hard to maintain

## Anti-Patterns

**Avoid:**
- Fully autonomous agents with no human checkpoint
- Agents that can approve their own work
- Circular dependencies (A routes to B routes to A)
- Functions with no clear owner
