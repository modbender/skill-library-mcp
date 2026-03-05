# War Room — Prompt Templates

## Token-Optimized Spawn (File-Based Context)

For proposals over 1500 words, write context to a temp file first:

```python
# Step 1: Write proposal to temp file
exec("cat > /tmp/rt_{topic}.md << 'DATA'\n{proposal_content}\nDATA")

# Step 2: Spawn with lightweight prompts
sessions_spawn(
  task="""You are the {ROLE} in an adversarial roundtable evaluation.

**Topic**: {TOPIC}

**Your task**: Read /tmp/rt_{topic}.md for the full proposal and data, then:
{DELIVERABLES}

{MANDATORY_CLOSING_QUESTION}""",
  label="{role}_{topic}_{YYYYMMDD}",
  mode="run"
)
```

Each agent prompt is ~500 tokens instead of ~3000. Agents read the shared file themselves.

## Inline Spawn (Short Proposals)

For proposals under 1500 words, inline directly:

```python
sessions_spawn(
  task="""You are the {ROLE} in an adversarial roundtable evaluation.

**Topic**: {TOPIC}

**Proposal/Data**:
{PROPOSAL}

**Your task**:
{DELIVERABLES}

{MANDATORY_CLOSING_QUESTION}""",
  label="{role}_{topic}_{YYYYMMDD}",
  mode="run"
)
```

## Model Override (Optional)

For critical roles that need deeper reasoning:

```python
sessions_spawn(
  task=...,
  label="guardian_{topic}_{date}",
  mode="run",
  model="opus"  # or "sonnet" for mid-tier
)
```

## Ruling Document Template

```markdown
# War Room #{N} — {TOPIC}

**Audit ID**: RT{N}-{TOPIC_SHORT}-{YYYYMMDD}
**Ruling**: {GO/NO-GO/REWORK} — {conditions}

## I. Participants
| Role | Label | Runtime | Key Contribution |
|------|-------|---------|-----------------|

## II. Per-Agent Findings
{Summaries with numbers}

## III. Consensus (4/5+)
{Numbered list}

## IV. Disputes and Rulings
| Dispute | Pro | Con | Ruling |

## V. Final Plan
{Concrete deliverables with numbers}

## VI. Scenario Projections
| Scenario | Probability | Outcome |

## VII. Retained Doubts
{Numbered list of honest unknowns}

## VIII. Task List
| Priority | Task | Owner | Deadline |
```

## Post-Ruling Checklist

1. Write ruling to file and git commit (include audit ID in commit message)
2. Store key decisions to long-term memory with audit ID
3. Update daily log file
4. Archive previous session files if needed
