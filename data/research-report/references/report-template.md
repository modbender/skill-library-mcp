# Technical Report Template

## Structure Guidelines

### 1. Executive Summary (100-150 words)
- One paragraph overview
- What problem does this solve?
- Key innovation in one sentence
- Main result/achievement

### 2. Motivation
**2.1 Problem Statement**
- What gap/challenge exists?
- Why is it hard? (technical constraints)
- Real-world impact

**2.2 Why This Matters**
- Applications
- Who benefits?
- State of field before this work

### 3. Background
**3.1 Prerequisites** (explain intuitively)
- Key concepts the reader needs
- Use analogies where possible
- Link to foundational papers

**3.2 Related Work**
- Timeline of approaches
- Compare in a table if possible
- What this work improves

### 4. Core Method
**4.1 Architecture Overview**
- High-level diagram (Mermaid or ASCII)
- Data flow description
- Component responsibilities

**4.2 Key Innovations**
- What's novel?
- Why does it work?
- Mathematical intuition (not just formulas)

**4.3 Implementation Details**
- Critical hyperparameters
- Architecture choices
- Trade-offs made

### 5. Code Analysis
**5.1 Project Structure**
```
project/
├── key_module/      # What it does
├── training/        # What it does
└── utils/           # What it does
```

**5.2 Key Components Walkthrough**
For each important file:
- Purpose in one sentence
- Input/output shapes
- Key functions with line references

**5.3 Data Flow Example**
Walk through one forward pass step by step

### 6. Experiments
**6.1 Setup**
- Hardware (GPU, RAM)
- Dataset
- Hyperparameters (table format)
- Baselines compared

**6.2 Results**
- Main results table
- Ablation studies
- Qualitative examples

**6.3 Analysis**
- Why do results look like this?
- Failure modes
- Surprising findings

### 7. Troubleshooting
Common issues and solutions:
```
Problem: XYZ error
Cause: ...
Fix: ...
```

### 8. References
Format:
- Papers: Authors, Venue, Year, arXiv ID
- Code: GitHub URL + commit hash
- Docs: URL + access date

---

## Writing Principles

1. **Progressive Disclosure**: Start simple, add details gradually
2. **Concrete Before Abstract**: Examples before theory
3. **Visual Anchors**: Diagrams every 2-3 sections
4. **Code Snippets**: Show, don't just tell
5. **Anticipate Questions**: Address "why?" before asked

## Common Pitfalls

❌ Too much jargon without explanation
❌ Equations without intuition
❌ No comparison to baselines
❌ Missing reproduction details
❌ Walls of text without breaks

✅ Use analogies ("like X but for Y")
✅ Include "why this matters" callouts
✅ Add troubleshooting from experience
✅ Link to runnable code
✅ Version everything

---

## Iteration Checklist

For each revision pass:

- [ ] Add more intuitive explanations
- [ ] Include missing diagrams
- [ ] Expand code walkthrough
- [ ] Add troubleshooting tips
- [ ] Verify all links work
- [ ] Check math notation consistency
- [ ] Add cross-references
- [ ] Improve formatting/tables
