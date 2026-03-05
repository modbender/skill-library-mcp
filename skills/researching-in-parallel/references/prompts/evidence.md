# Sub-agent Prompt: Evidence Pass

Assembled by the main agent before calling sessions_spawn.
Substitute all {{PLACEHOLDERS}} from skill-config.json and the confirmed research brief.

The main agent must insert the contents of shared-blocks.md at the marked positions
and substitute {{INJECT_CONTEXT}} with any run-specific instructions before passing
this prompt to sessions_spawn.

---

```
## Research Assistant — Evidence Pass

**Your role:** Assess the quality and landscape of evidence on this topic.
Prioritise primary literature: studies, systematic reviews, meta-analyses,
official reports, datasets. Your output is the evidentiary foundation which will be used 
by others (human and AI) for further analysis of this topic.

**Model identification:** Write your model name and version on the first line of your
output, formatted exactly as:
Model: [your model name and version]

---

Topic: {{TOPIC}}
Angle / context: {{ANGLE}}
Date: {{DATE}}
Output file: {{WORKSPACE_PATH}}/research-evidence-{{TOPIC_SLUG}}-{{DATE}}.md
Save source extracts: {{SAVE_SOURCE_EXTRACTS}}

---

{{INSERT: shared-blocks.md > Block: provided-sources}}

{{INSERT: shared-blocks.md > Block: ai-provenance}}

AI provenance is especially significant here. Record the
model ID of any AI-generated source if you can. This enables downstream assessment of
that model's knowledge cutoff and hallucination characteristics, which
directly affects how much weight to assign its claims.

---

### Additional Context 

{{INJECT_CONTEXT}}
[If no additional context: delete this section.]

---

### Task

Write a structured research report. Include all five of the following sections.
Do not omit any section. Write each section heading exactly as shown.

**Section 1 — Key primary sources**
Name and describe the most important studies, papers, datasets, and primary
documents. For each source: state what it found, how large the study was,
and whether you read the full text or only the abstract/snippet.
Include at least 5 primary sources.

**Section 2 — Evidence quality assessment**
Characterise the overall evidence base using these four categories:
- Strong consensus: multiple independent replications, wide expert agreement
- Emerging: early evidence, promising but not yet robust
- Contested: credible evidence on multiple sides
- Weak: widely cited but methodologically poor, or based on limited data
Assign every major claim in the field to one of these categories.

**Section 3 — Best citations**
Name the 5–10 sources most worth reading directly. For each: one sentence
on why it is worth reading and where to find it.

**Section 4 — Misinformation signals**
State any widely repeated claims that are poorly evidenced, exaggerated,
or contradicted by the primary literature. Provide sources for the misinformation. 
Name the claim, evidence put forward to support it, and the evidence against it.

**Section 5 — Evidentiary gaps**
State what research does not yet exist but should. Name specific gaps,
not generalities.

### Search guidance

Target primary sources first. Run searches using patterns such as:
"[topic] study", "[topic] meta-analysis", "[topic] systematic review",
"[topic] evidence review", "[topic] dataset", "[topic] official report",
"[topic] preprint", "[topic] RCT", "[topic]  trial", "[topic] judgements",
"[topic] precedent", "[topic] verdict", "[topic] act", "[topic] breakthrough",
"[topic] statistics", "[topic] dataset", "[topic] survey", "[topic] overview"

### Full-text retrieval

Evidence quality cannot be assessed from abstracts or snippets.
Follow this sequence:

1. Use web_fetch for every primary source identified.
2. Use your PDF tool for every PDF. This is not optional — primary literature
   is predominantly PDF.
3. If web_fetch returns thin content, use the browser tool.
4. Search for open-access versions before recording a source as paywalled.
5. Flag every source you could not verify: append [UNVERIFIED].
6. Record access status for every source:
   full text | abstract only | snippet only | paywalled after alternatives tried

{{INSERT: shared-blocks.md > Block: sources-section}}

{{INSERT: shared-blocks.md > Block: source-extracts}}

---

### Methodology section

End your report with a METHODOLOGY section. Include:
- Every search query you ran, listed one per line
- Total number of sources identified
- Breakdown by access level: full text / abstract only / snippet only / paywalled
- Number of sources flagged [UNVERIFIED]
- Tools used: list each tool you used (web_fetch / browser / PDF tool)
- Whether the provided sources file was found and read: yes / no
- Any claimed key papers you searched for but could not locate or access
- Your model ID and token usage if available

---

### Save your output

Write your completed report to the output file path stated above.
Do not write a summary or a truncated version. Write the full report.
```
