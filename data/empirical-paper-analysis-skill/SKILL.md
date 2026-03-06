---
name: Empirical Paper Analysis Skill
description: "This skill enables Claude Code to deeply analyze empirical
  research papers, following a structured framework: Problem Statement → Core
  Empirical Challenges → Identification Strategy → Key Findings ..."
---

# Empirical Paper Analysis Skill

## Skill Description
This skill enables Claude Code to deeply analyze empirical research papers, following a structured framework: Problem Statement → Core Empirical Challenges → Identification Strategy → Key Findings → Academic Contribution.

## Target User
Researchers in law and economics who regularly read and analyze empirical papers in law and economics, especially with quantitative methods (econometrics, machine learning, NLP, etc.).

## Input Requirements
- PDF file of an empirical research paper
- Publication information (Authors, Journal, Date, etc)

## Analysis Framework

### 1. 问题的提出 (Problem Statement)
**Objective:** Identify the core research question and its motivation.

**Analysis Points:**

- What is the primary research question? / What problem or phenomenon is being studied?
- Why is this question important (policy relevance, theoretical gap, methodological innovation, practical value)?
- What is the economic/legal intuition behind the research design?

### 2. 实证研究的核心难题 (Core Empirical Challenges)
**Objective:** Identify the key methodological obstacles that make causal inference difficult.

**Common Challenges to Look For:**
- **Selection bias**: Observed vs unobserved outcomes (e.g., selective labels problem)
- **Omitted variable bias**: Unobserved confounders (e.g., judges' private information)
- **Endogeneity**: Reverse causality or simultaneity
- **Measurement error**: How to quantify abstract concepts (e.g., legal ideas, judicial attitudes)
- **External validity**: Generalizability concerns
- **Data limitations**: Missing counterfactuals, truncated samples, etc.

**Output Format:**
For each challenge:
- Clearly state the problem
- Explain why it matters for causal inference
- Use examples/tables to illustrate if helpful

### 3. 识别策略与方法设计 (Identification Strategy & Research Design)
**Objective:** Explain how the paper solves the empirical challenges.

**Key Elements:**
- **Identification strategy**: Natural experiment, IV, RD, DID, matching, ML+causal inference hybrid
- **Data source**: Dataset description, sample selection, time period
- **Empirical specification**: Main regression model, key variables
- **Robustness checks**: Alternative specifications, placebo tests, sensitivity analysis
- **Novel methodological contributions**: Any innovative techniques?

**Critical Analysis:**
- Are the identification assumptions plausible?
- Are there remaining threats to validity?
- How convincing is the causal interpretation?

### 4. 重要发现与结论 (Key Findings & Conclusions)
**Objective:** Summarize the main empirical results and their interpretation.

**Structure:**
- Main findings (with magnitude/significance)
- Robustness of results
- Heterogeneous effects (if any)
- Economic/legal interpretation
- Policy implications

**Format:** 
- Use bullet points for clarity
- Include key numbers (effect sizes, significance levels)
- Reference important tables/figures

### 5. 学术价值 (Academic Contribution)
**Objective:** Evaluate the paper's broader significance.

**Dimensions:**
- **Methodological innovation**: New identification strategies, measurement techniques
- **Theoretical contribution**: New insights about legal/judicial behavior, institutional design
- **Policy relevance**: Implications for legal reform, judicial training, algorithm adoption
- **Interdisciplinary impact**: Bridges law, economics, computer science
- **Future research**: Opens new questions or directions

## Output Format

Generate a structured markdown document following this template:

```markdown
# [Paper Title]

**Authors:** [List]
**Journal:** [Name, Year]
**DOI/Link:** [If available]

## 问题的提出

[Analysis following framework above]

## 实证研究的核心难题

### 难题一：[Name]
[Explanation]

### 难题二：[Name]
[Explanation]

## 识别策略与方法设计

### 数据来源
[Description]

### 识别策略
[Core identification approach]

### 方法设计
[Technical details]

## 重要发现与结论

- **发现一：** [Finding with magnitude]
- **发现二：** [Finding with magnitude]
- **政策含义：** [Implications]

## 学术价值

- **方法论贡献：** [Innovation]
- **理论贡献：** [Insights]
- **政策相关性：** [Relevance]

```

## Special Instructions

1. **Academic Tone**: Use precise academic language appropriate for PhD-level analysis. Assume familiarity with econometric concepts (DID, IV, RDD, etc.) and ML methods (GBDT, NLP, embeddings).

2. **Bilingual Output**: Primary language is Chinese (as shown in the examples), but technical terms can be included in parentheses with English abbreviation when first introduced.

3. **Mathematical Rigor**: Don't shy away from mathematical notation when describing models or identification strategies. For example:
   - Regression specifications: $Y_i = \beta_0 + \beta_1 Treatment_i + X_i'\gamma + \epsilon_i$
   - DID: $Y_{ijt} = \alpha + \beta(Post_t \times Treat_j) + \delta_j + \lambda_t + \varepsilon_{ijt}$

4. **Critical Thinking**: Don't just summarize—analyze. Question assumptions, evaluate identification strength, consider alternative explanations.

5. **Tables/Figures**: When referencing tables or figures from the paper:
   - Describe what they show conceptually
   - Highlight the most important results
   - Don't try to reproduce full tables in text

6. **Scope**: Focus on the five core sections. Don't add unnecessary sections.

## Example Workflow

1. **Read the entire paper** to understand the research question and context
2. **Extract the empirical strategy** - pay special attention to identification sections
3. **Identify the key challenges** the authors face
4. **Trace how they solve each challenge** methodologically
5. **Synthesize the findings** with appropriate interpretation
6. **Evaluate the contribution** in context of the literature
