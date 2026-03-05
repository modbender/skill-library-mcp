# Research Pipeline — Vibe Research

## Phase 1: Gap Identification

**Goal:** Find what's unknown, contested, or under-explored.

### Process
1. Receive research question from human
2. Scan existing literature (100+ sources minimum)
3. Identify:
   - Established consensus
   - Active debates
   - Unexplored territories
   - Methodological gaps

### Output
```markdown
## Knowledge Gap Analysis: [Topic]

### Established (High confidence)
- [Fact 1] — supported by [n] sources
- [Fact 2] — supported by [n] sources

### Contested (Debate exists)
- [Claim] — [Source A] argues X, [Source B] argues Y

### Unexplored (Opportunity)
- [Gap 1] — no literature found addressing this
- [Gap 2] — mentioned but not studied

### Recommended Focus
[Which gap to pursue and why]
```

---

## Phase 2: Literature Synthesis

**Goal:** Build comprehensive understanding from sources.

### Process
1. Retrieve relevant papers, articles, data
2. Extract key claims with citations
3. Cross-reference findings
4. Identify patterns and contradictions
5. Build knowledge graph of concepts

### Techniques
- Vector search for semantic similarity
- Citation network analysis
- Claim extraction and verification
- Temporal analysis (how has understanding evolved?)

### Output
Synthesized summary with:
- Key findings (cited)
- Methodology patterns across studies
- Consensus vs. outlier views
- Quality assessment of sources

---

## Phase 3: Hypothesis Generation

**Goal:** Propose testable claims that address identified gaps.

### Process
1. Review gaps and synthesis
2. Generate candidate hypotheses
3. Evaluate each for:
   - Testability (can we verify/falsify?)
   - Novelty (does it add knowledge?)
   - Feasibility (can we execute with available resources?)
4. Rank and recommend

### Output
```markdown
## Hypothesis Candidates

### H1: [Statement]
- Testability: [High/Medium/Low]
- Evidence for: [existing support]
- Evidence against: [existing challenges]
- Test approach: [brief methodology]

### H2: [Statement]
...

### Recommendation
Pursue H[n] because [reasoning]
```

---

## Phase 4: Analysis Design

**Goal:** Define rigorous methodology to test hypothesis.

### Components
1. Data requirements
2. Analytical methods
3. Success criteria
4. Potential confounds
5. Reproducibility plan

### Output
Research protocol document with clear steps

---

## Phase 5: Execution

**Goal:** Run the analysis and gather results.

### Agent responsibilities
- Execute defined methodology
- Log all steps and decisions
- Flag anomalies or unexpected findings
- Iterate if initial results are inconclusive

### Human checkpoints
- Validate methodology before execution
- Review intermediate results
- Approve course corrections

---

## Phase 6: Synthesis

**Goal:** Transform findings into actionable knowledge.

### Output formats
- Executive summary (1 page)
- Full research report (with methodology)
- Citation list
- Reproducibility package (code, data, steps)

### Structure
1. Question addressed
2. Methodology used
3. Key findings
4. Limitations
5. Implications
6. Future directions
