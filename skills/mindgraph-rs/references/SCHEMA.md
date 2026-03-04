# MindGraph Schema Reference

Full node and edge type definitions. Load this file only when extracting nodes from memory files or designing graph structure.

For everyday READ/WRITE operations, use `SKILL.md` instead.

---

## Node Types (52 total)

Use the **most specific** type available. Never default to `Claim` when a more precise type applies.

### Reality layer (4 types)
| Type | Use when | Key props |
|------|----------|-----------|
| `Entity` | Named person, org, product, technology, location | `entity_type`, `description`, `identifiers` |
| `Source` | A whole file or document | `uri` (file path or URL), `title`, `source_type` |
| `Snippet` | A meaningful paragraph/section extracted from a Source | `content` (→ also set `summary` for FTS) |
| `Observation` | Something that happened or was reported at a specific time | `content`, `observed_at` (unix timestamp) |

### Epistemic layer (24 types)
| Type | Use when | Key props |
|------|----------|-----------|
| `Claim` | A currently-held belief or factual assertion | `content`, `truth_status`, `certainty_degree` |
| `Evidence` | Data, measurement, or result that supports/refutes a claim | `description`, `evidence_type`, `quantitative_value` |
| `Warrant` | A justification or reasoning principle connecting evidence to a claim | `principle`, `warrant_type`, `strength` |
| `Argument` | A reasoning chain with premise → conclusion | `summary`, `argument_type`, `strength` |
| `Hypothesis` | A proposed explanation prefaced with "may", "could", "possibly" | `statement`, `hypothesis_type`, `status` |
| `Theory` | A named framework or comprehensive explanation | `name`, `description`, `domain`, `status` |
| `Paradigm` | A dominant worldview or overarching framework in a domain | `name`, `description`, `domain` |
| `Anomaly` | A surprising finding or contradiction with expected behavior | `description`, `anomaly_type`, `severity`, `status` |
| `Method` | A research technique, procedure, or approach | `name`, `method_type`, `domain` |
| `Experiment` | A specific test or investigation | `description`, `status` |
| `Concept` | An abstract idea being defined or explained | `name`, `definition`, `domain` |
| `Assumption` | An implicit or explicit premise underlying a claim | `content`, `assumption_type`, `explicit_in_text` |
| `Question` | An open or partially-addressed question | `text`, `question_type`, `status` |
| `OpenQuestion` | An unresolved foundational question | `text`, `scope`, `status` |
| `Analogy` | A comparison between domains used to explain or argue | `description`, `source_domain`, `target_domain` |
| `Pattern` | A recurring lesson or generalizable rule | `summary` (the lesson — used for FTS) |
| `Mechanism` | A causal, functional, or structural process | `description`, `mechanism_type`, `components` |
| `Model` | An ML model or formal computational/mathematical model | `name`, `model_type`, `domain` |
| `ModelEvaluation` | An assessment of a model's performance or validity | `description` |
| `InferenceChain` | A sequence of logical steps leading to a conclusion | `summary` |
| `SensitivityAnalysis` | Analysis of how outputs change with input variation | `description` |
| `ReasoningStrategy` | A high-level approach to reasoning about a problem | `summary` |
| `Theorem` | A formally proved mathematical or logical statement | `statement`, `domain` |
| `Equation` | A mathematical or formal equation | `expression`, `domain` |

### Intent layer (6 types)
| Type | Use when | Key props |
|------|----------|-----------|
| `Goal` | Something being actively worked toward | `description`, `priority` (high/medium/low), `status`, `progress` (0-1) |
| `Project` | An ongoing or completed body of work | `name`, `description`, `status` |
| `Decision` | A made choice with rationale, incl. prioritization calls | `question`, `status`, `decision_rationale`, `reversibility` |
| `Constraint` | A binding must/must-not rule | `description`, `hard` (bool), `constraint_type` |
| `Milestone` | A specific deliverable within a Project | `description`, `status`, `due_date` |
| `Option` | An alternative considered in a Decision | `description`, `pros`, `cons`, `score` |

### Action layer (5 types)
| Type | Use when | Key props |
|------|----------|-----------|
| `Flow` | A multi-step process or workflow | `name`, `description`, `flow_type`, `step_count` |
| `FlowStep` | A single step within a Flow | `order`, `description`, `is_optional`, `is_checkpoint` |
| `Affordance` | A specific executable action available to an agent | `action_name`, `description`, `affordance_type`, `risk_level`, `reversible` |
| `Control` | A UI control or interface element | `control_type`, `label`, `selector` |
| `RiskAssessment` | An evaluation of risk for an action or plan | `risk_type`, `severity`, `likelihood`, `mitigation`, `requires_approval` |

### Memory layer (5 types)
| Type | Use when | Key props |
|------|----------|-----------|
| `Session` | A conversation session | `session_id`, `summary` |
| `Trace` | A log of a specific agent action or event within a session | `description` |
| `Summary` | A condensed account of a session or document | `content` |
| `Preference` | How Shan wants things done (style, tone, process) | `key`, `value`, `explicit` (true = Shan stated it directly) |
| `MemoryPolicy` | A rule governing Jaadu's behavior | `scope`, `policy_text` |

### Agent layer (8 types)
| Type | Use when | Key props |
|------|----------|-----------|
| `Agent` | An AI agent (Jaadu, a sub-agent, an external agent) | `name`, `agent_type`, `model_id`, `capabilities`, `autonomy_level` |
| `Task` | A unit of work assigned to an agent | `description`, `task_type`, `status`, `priority`, `parent_goal_uid` |
| `Plan` | A proposed sequence of steps to accomplish a Task | `description`, `task_uid`, `status`, `step_count`, `estimated_risk` |
| `PlanStep` | A single step within a Plan | `order`, `description`, `status`, `requires_approval` |
| `Approval` | A record of an approval decision (granted or denied) | `target_uid`, `status`, `decided_by`, `reason` |
| `Policy` | An agent-level behavioral policy with explicit rules | `name`, `description`, `policy_type`, `rules`, `applies_to`, `active` |
| `Execution` | A record of an action taken by an agent | `description`, `status`, `started_at`, `completed_at`, `error`, `reversible` |
| `SafetyBudget` | A budget limiting agent actions of a certain type | `scope`, `budget_type`, `limit`, `consumed`, `remaining` |

---

## Edge Types

Use SCREAMING_SNAKE_CASE. Choose the **most specific** edge. Use `RELEVANT_TO` only as a last resort.

### Epistemic edges
| Edge | Use when |
|------|----------|
| `SUPPORTS` | Evidence/Observation backs a Claim or Hypothesis |
| `REFUTES` | Evidence contradicts a Claim |
| `CONTRADICTS` | Two Claims are in direct opposition |
| `DERIVED_FROM` | Claim extracted or inferred from a Snippet/Observation/Source |
| `EXTENDS` | One Claim/Theory builds on another |
| `JUSTIFIES` | A warrant or argument justifies a Claim |
| `ADDRESSES` | A Claim or Decision addresses a Question or Goal |

### Provenance edges
| Edge | Use when |
|------|----------|
| `AUTHORED_BY` | Work produced by an Entity |
| `PART_OF` | Snippet belongs to Source; person belongs to org; component of a whole |
| `CITED_BY` | Source cited by another Source or Claim |
| `DERIVED_FROM` | Node originated from another node |

### Intent edges
| Edge | Use when |
|------|----------|
| `MOTIVATED_BY` | Decision or Goal serves a higher Goal |
| `CONSTRAINED_BY` | Decision or Project is limited by a Constraint |
| `DECOMPOSES_INTO` | Project or Goal breaks into Milestones or sub-Goals |
| `DEPENDS_ON` | Decision depends on another Decision or Claim being true |
| `DECIDED_ON` | Decision chose a specific Option |

### Memory edges
| Edge | Use when |
|------|----------|
| `SUMMARIZES` | Summary or Session node covers another node |
| `CAPTURES_IN` | Fact captured in a Session |
| `RELEVANT_TO` | General-purpose weak link — use only when no specific edge applies |

---

## Key Distinction Rules

These are the most common mis-typings:

1. **Claim vs Observation:** "X happened on date Y" → `Observation`. "X is currently true" → `Claim`.
2. **Claim vs Decision:** "BCG X is top priority" → `Decision` (a choice). "BCG X is a consulting firm" → `Claim` (a fact).
3. **Claim vs Constraint:** "Never give salary preemptively" → `Constraint` with `hard=true`.
4. **Claim vs Preference:** "Shan prefers concise replies" → `Preference`.
5. **Claim vs Pattern:** "Axum 0.7 uses :param syntax" → `Pattern` (a generalizable lesson).
6. **Claim vs MemoryPolicy:** "Always read MEMORY.md at session start" → `MemoryPolicy`.
7. **Goal vs Decision:** "Income is Shan's #1 priority" → `Goal` (the state) + `Decision` (the prioritization act), linked `MOTIVATED_BY`.
8. **Stale facts:** Prices, application statuses → `Claim` with `truth_status=confirmed` and timestamp. Data source → `Observation` linked via `SUPPORTS`.
9. **Every Claim about an Entity** gets a `RELEVANT_TO` edge to that Entity, unless a more specific edge applies.

---

## FTS Searchability Rule

CozoDB FTS **only indexes `label` and `summary`** — not `props.content`, `props.description`, or other props fields.

**Always set `summary`** when creating nodes:
- `Project`, `Decision`, `Constraint`: copy the key description into `summary`
- `Claim`: if content is longer than the label, copy to `summary`
- `Observation`, `Snippet`: copy first 300 chars of content to `summary`
- `Pattern`: the lesson itself goes in `summary`
- `Source`: title + file path in `summary`
